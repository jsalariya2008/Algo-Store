from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename, send_from_directory
from functools import wraps
from datetime import datetime
import MySQLdb.cursors
import os
import random
import time
import hmac
import hashlib
import razorpay
import re

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

import cloudinary
import cloudinary.uploader

# ── Cloudinary ─────────────────────────────────────────────────────
cloudinary.config(
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key    = os.getenv('CLOUDINARY_API_KEY'),
    api_secret = os.getenv('CLOUDINARY_API_SECRET'),
    secure     = True
)

# ── Secret key ─────────────────────────────────────────────────────
app.secret_key = os.getenv('SECRET_KEY')

app.config['UPLOAD_FOLDER'] = 'uploads/products'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# ── MySQL ──────────────────────────────────────────────────────────
app.config['MYSQL_HOST']         = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER']         = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD']     = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB']           = os.getenv('MYSQL_DB')
app.config['MYSQL_PORT']         = int(os.getenv('MYSQL_PORT', 3306))
app.config['MYSQL_CURSORCLASS']  = 'DictCursor'
app.config['MYSQL_CHARSET']      = 'utf8mb4'
app.config['MYSQL_SSL_DISABLED'] = True

mysql = MySQL(app)

ADMIN_EMAIL = 'algowear.co@gmail.com'

app.config['MAIL_SERVER']   = 'smtp.gmail.com'
app.config['MAIL_PORT']     = 587
app.config['MAIL_USE_TLS']  = True
app.config['MAIL_USERNAME'] = ADMIN_EMAIL
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)

# ── Razorpay ───────────────────────────────────────────────────────
def get_rz_client():
    return razorpay.Client(
        auth=(os.getenv('RAZORPAY_KEY_ID'), os.getenv('RAZORPAY_KEY_SECRET'))
    )

# ── Helpers ────────────────────────────────────────────────────────
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(email, otp):
    try:
        msg = Message(
            'Your ALGO OTP Code',
            sender=ADMIN_EMAIL,
            recipients=[email]
        )
        msg.body = f'Your OTP is: {otp}\n\nValid for 10 minutes.\n\n— Team ALGO'
        mail.send(msg)
    except Exception as e:
        print(f"[OTP EMAIL ERROR] {e}")

def send_order_notification(order_id, total, payment_method, customer_name, customer_email, address='', phone=''):
    try:
        # ── Admin alert with full details ──
        admin_msg = Message(
            subject=f'New ALGO Order #{order_id} — Rs.{total}',
            sender=ADMIN_EMAIL,
            recipients=[ADMIN_EMAIL]
        )
        admin_msg.body = f'''
============================================
  NEW ORDER RECEIVED — ALGO
============================================

Order ID      : #{order_id}
Time          : {datetime.now().strftime('%d %b %Y, %I:%M %p')}

--------------------------------------------
  CUSTOMER DETAILS
--------------------------------------------
Name          : {customer_name}
Email         : {customer_email}
Phone         : {phone if phone else 'Not provided'}

--------------------------------------------
  DELIVERY ADDRESS
--------------------------------------------
{address if address else 'Not provided'}

--------------------------------------------
  ORDER DETAILS
--------------------------------------------
Amount        : Rs.{total}
Payment       : {payment_method.upper()}

--------------------------------------------
View in admin : https://algo-store.onrender.com/admin/orders
============================================
        '''
        mail.send(admin_msg)
        print(f"[MAIL] Admin notified for order #{order_id}")

        # ── Customer confirmation ──
        customer_msg = Message(
            subject=f'Your ALGO Order #{order_id} is Confirmed!',
            sender=ADMIN_EMAIL,
            recipients=[customer_email]
        )
        customer_msg.body = f'''
Hey {customer_name},

Your order has been placed successfully!

============================================
  ORDER SUMMARY
============================================
Order ID      : #{order_id}
Amount        : Rs.{total}
Payment       : {payment_method.upper()}

--------------------------------------------
  DELIVERY ADDRESS
--------------------------------------------
{address if address else 'Not provided'}
Phone         : {phone if phone else 'Not provided'}

--------------------------------------------

We'll notify you once your order ships.

Thank you for shopping with ALGO.
Wear your story.

— Team ALGO
algowear.co@gmail.com
============================================
        '''
        mail.send(customer_msg)
        print(f"[MAIL] Confirmation sent to {customer_email}")

    except Exception as e:
        print(f"[MAIL ERROR] Order #{order_id} notification failed: {str(e)}")

# ── HOMEPAGE ───────────────────────────────────────────────────────
@app.route('/')
def index():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM products WHERE is_active=1 ORDER BY created_at DESC LIMIT 6")
    featured = cur.fetchall()
    cur.execute("SELECT * FROM products WHERE is_upcoming=1 LIMIT 5")
    upcoming = cur.fetchall()
    cur.close()
    cart_count = sum(item['qty'] for item in session.get('cart', {}).values()) if session.get('cart') else 0
    return render_template('index.html', featured=featured, upcoming=upcoming, cart_count=cart_count)

# ── COLLECTION ─────────────────────────────────────────────────────
@app.route('/collection')
def collection():
    category = request.args.get('category', '')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if category:
        cur.execute("SELECT * FROM products WHERE is_active=1 AND category=%s ORDER BY created_at DESC", (category,))
    else:
        cur.execute("SELECT * FROM products WHERE is_active=1 ORDER BY created_at DESC")
    products = cur.fetchall()
    cur.execute("SELECT DISTINCT category FROM products WHERE is_active=1")
    categories = [r['category'] for r in cur.fetchall()]
    cur.close()
    cart_count = sum(item['qty'] for item in session.get('cart', {}).values()) if session.get('cart') else 0
    return render_template('collection.html', products=products, categories=categories, selected=category, cart_count=cart_count)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM products WHERE id=%s AND is_active=1", (product_id,))
    product = cur.fetchone()
    if not product:
        return redirect(url_for('collection'))
    cur.execute("SELECT * FROM products WHERE category=%s AND id != %s AND is_active=1 LIMIT 4", (product['category'], product_id))
    related = cur.fetchall()
    cur.close()
    cart_count = sum(item['qty'] for item in session.get('cart', {}).values()) if session.get('cart') else 0
    return render_template('product_detail.html', product=product, related=related, cart_count=cart_count)

# ── CART ───────────────────────────────────────────────────────────
@app.route('/cart')
def cart():
    cart_data = session.get('cart', {})
    items = []
    total = 0
    if cart_data:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        for pid, info in cart_data.items():
            cur.execute("SELECT * FROM products WHERE id=%s", (pid,))
            p = cur.fetchone()
            if p:
                subtotal = p['price'] * info['qty']
                total += subtotal
                items.append({**p, 'qty': info['qty'], 'size': info.get('size', 'M'), 'subtotal': subtotal})
        cur.close()
    cart_count = sum(item['qty'] for item in cart_data.values()) if cart_data else 0
    return render_template('cart.html', items=items, total=total, cart_count=cart_count)

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    pid  = str(data.get('product_id'))
    size = data.get('size', 'M')
    qty  = int(data.get('qty', 1))
    cart = session.get('cart', {})
    key  = f"{pid}_{size}"
    if key in cart:
        cart[key]['qty'] += qty
    else:
        cart[key] = {'product_id': pid, 'qty': qty, 'size': size}
    session['cart'] = cart
    return jsonify({'success': True, 'cart_count': sum(i['qty'] for i in cart.values())})

@app.route('/cart/remove', methods=['POST'])
def remove_from_cart():
    data = request.get_json()
    key  = data.get('key')
    cart = session.get('cart', {})
    if key in cart:
        del cart[key]
    session['cart'] = cart
    return jsonify({'success': True})

@app.route('/cart/update', methods=['POST'])
def update_cart():
    data = request.get_json()
    key  = data.get('key')
    qty  = int(data.get('qty', 1))
    cart = session.get('cart', {})
    if key in cart:
        if qty <= 0:
            del cart[key]
        else:
            cart[key]['qty'] = qty
    session['cart'] = cart
    return jsonify({'success': True})

# ── AUTH ───────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id']  = user['id']
            session['username'] = user['name']
            session['is_admin'] = bool(user['is_admin'])
            return redirect(url_for('index'))
        flash('Invalid credentials', 'error')
    cart_count = sum(item['qty'] for item in session.get('cart', {}).values()) if session.get('cart') else 0
    return render_template('auth.html', mode='login', cart_count=cart_count)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name     = request.form['name']
        email    = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            cur.close()
            flash('Email already registered', 'error')
            return redirect(url_for('signup'))
        cur.close()
        otp = generate_otp()
        session['temp_user'] = {
            'name':     name,
            'email':    email,
            'password': generate_password_hash(password)
        }
        session['otp'] = otp
        send_otp(email, otp)
        flash('OTP sent to your email', 'success')
        return redirect(url_for('verify_otp_page'))
    cart_count = sum(item['qty'] for item in session.get('cart', {}).values()) if session.get('cart') else 0
    return render_template('auth.html', mode='signup', cart_count=cart_count)

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp_page():
    if request.method == 'POST':
        user_otp = request.form['otp']
        if user_otp == session.get('otp'):
            user = session.get('temp_user')
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                (user['name'], user['email'], user['password'])
            )
            mysql.connection.commit()
            cur.close()
            session.pop('otp', None)
            session.pop('temp_user', None)
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP. Please try again.', 'error')
    return render_template('verify_otp.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ── LOOKBOOK ───────────────────────────────────────────────────────
@app.route('/lookbook')
def lookbook():
    cart_count = sum(item['qty'] for item in session.get('cart', {}).values()) if session.get('cart') else 0
    return render_template('lookbook.html', cart_count=cart_count)

# ── ADMIN ──────────────────────────────────────────────────────────
@app.route('/admin')
@admin_required
def admin():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM products ORDER BY created_at DESC")
    products = cur.fetchall()
    cur.execute("SELECT COUNT(*) as cnt FROM users")
    user_count = cur.fetchone()['cnt']
    cur.close()
    return render_template('admin.html', products=products, user_count=user_count)

@app.route('/admin/orders')
@admin_required
def admin_orders():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT o.*, u.name as customer_name, u.email as customer_email
        FROM orders o
        LEFT JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC
    """)
    orders = cur.fetchall()
    cur.close()
    return render_template('admin_orders.html', orders=orders)

@app.route('/admin/product/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    if request.method == 'POST':
        name        = request.form['name']
        price       = float(request.form['price'])
        description = request.form['description']
        category    = request.form['category']
        stock       = int(request.form['stock'])
        is_upcoming = 1 if request.form.get('is_upcoming') else 0
        image_url   = ''

        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                # Upload directly to Cloudinary
                result = cloudinary.uploader.upload(
                    file,
                    folder='algo_products',
                    transformation=[
                        {'width': 800, 'height': 1000,
                         'crop': 'fill', 'quality': 'auto'}
                    ]
                )
                image_url = result['secure_url']  # permanent HTTPS URL

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""
            INSERT INTO products (name, price, description, category, stock, image_url, is_upcoming, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
        """, (name, price, description, category, stock, image_url, is_upcoming))
        mysql.connection.commit()
        cur.close()
        flash('Product added!', 'success')
        return redirect(url_for('admin'))
    return render_template('admin_product_form.html', product=None)

@app.route('/admin/product/edit/<int:pid>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(pid):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        name        = request.form['name']
        price       = float(request.form['price'])
        description = request.form['description']
        category    = request.form['category']
        stock       = int(request.form['stock'])
        is_upcoming = 1 if request.form.get('is_upcoming') else 0
        is_active   = 1 if request.form.get('is_active') else 0

        # Check if new image uploaded
        image_url = request.form.get('existing_image', '')
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                result = cloudinary.uploader.upload(
                    file,
                    folder='algo_products',
                    transformation=[
                        {'width': 800, 'height': 1000,
                         'crop': 'fill', 'quality': 'auto'}
                    ]
                )
                image_url = result['secure_url']

        cur.execute("""
            UPDATE products SET name=%s, price=%s, description=%s, category=%s,
            stock=%s, is_upcoming=%s, is_active=%s, image_url=%s WHERE id=%s
        """, (name, price, description, category, stock, is_upcoming, is_active, image_url, pid))
        mysql.connection.commit()
        cur.close()
        flash('Product updated!', 'success')
        return redirect(url_for('admin'))

    cur.execute("SELECT * FROM products WHERE id=%s", (pid,))
    product = cur.fetchone()
    cur.close()
    return render_template('admin_product_form.html', product=product)

@app.route('/admin/product/delete/<int:pid>', methods=['POST'])
@admin_required
def admin_delete_product(pid):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("DELETE FROM products WHERE id=%s", (pid,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'success': True})

# ── UPLOADS ────────────────────────────────────────────────────────
@app.route('/uploads/products/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ── API ────────────────────────────────────────────────────────────
@app.route('/api/cart-count')
def cart_count_api():
    cart = session.get('cart', {})
    return jsonify({'count': sum(i['qty'] for i in cart.values()) if cart else 0})

@app.route('/api/new-orders-count')
@admin_required
def new_orders_count():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT COUNT(*) as cnt FROM orders WHERE status='confirmed'")
    count = cur.fetchone()['cnt']
    cur.close()
    return jsonify({'count': count})

# ── CHECKOUT ───────────────────────────────────────────────────────
@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('cart'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cart_items = []
    subtotal   = 0

    for key, item in cart.items():
        pid = item.get('product_id') or key.split('_')[0]
        cur.execute("SELECT * FROM products WHERE id=%s", (pid,))
        p = cur.fetchone()
        if p:
            sub = p['price'] * item['qty']
            subtotal += sub
            cart_items.append({
                **p,
                'qty':      item['qty'],
                'size':     item.get('size', 'M'),
                'subtotal': sub
            })

    shipping     = 0 if subtotal >= 999 else 99
    grand_total  = subtotal + shipping
    amount_paise = int(grand_total * 100)

    rz_client = get_rz_client()
    rz_order = rz_client.order.create({
        'amount':   amount_paise,
        'currency': 'INR',
        'receipt':  f"algo_{session['user_id']}_{int(time.time())}",
    })

    cur.execute("""
        INSERT INTO orders (user_id, total_amount, status, razorpay_order_id)
        VALUES (%s, %s, 'pending', %s)
    """, (session['user_id'], grand_total, rz_order['id']))
    mysql.connection.commit()
    order_id = cur.lastrowid
    cur.close()

# Store address in session temporarily for online payments
session['pending_address'] = {
    'name':  request.form.get('name', ''),
    'phone': request.form.get('phone', ''),
    'addr1': request.form.get('addr1', ''),
    'addr2': request.form.get('addr2', ''),
    'city':  request.form.get('city', ''),
    'pin':   request.form.get('pin', ''),
    'state': request.form.get('state', ''),
}

    return render_template('checkout.html',
        rz_key      = os.getenv('RAZORPAY_KEY_ID'),
        rz_order_id = rz_order['id'],
        amount      = amount_paise,
        order_id    = order_id,
        subtotal    = subtotal,
        grand_total = grand_total,
        cart_items  = cart_items,
        cart_count  = 0
    )

# ── PLACE ORDER (COD) ──────────────────────────────────────────────
@app.route('/place-order', methods=['POST'])
@login_required
def place_order():
    order_id       = request.form.get('order_id')
    payment_method = request.form.get('payment_method', 'cod')

    required = {
        'name':  request.form.get('name', '').strip(),
        'phone': request.form.get('phone', '').strip(),
        'addr1': request.form.get('addr1', '').strip(),
        'city':  request.form.get('city', '').strip(),
        'pin':   request.form.get('pin', '').strip(),
        'state': request.form.get('state', '').strip(),
    }

    for field, value in required.items():
        if not value:
            flash('Please fill in all required address fields.', 'error')
            return redirect(url_for('cart'))

    if not re.match(r'^[6-9]\d{9}$', required['phone']):
        flash('Enter a valid 10-digit mobile number.', 'error')
        return redirect(url_for('cart'))

    if not re.match(r'^\d{6}$', required['pin']):
        flash('Enter a valid 6-digit PIN code.', 'error')
        return redirect(url_for('cart'))

    if payment_method != 'cod':
        return redirect(url_for('cart'))

    addr2 = request.form.get('addr2', '').strip()

    # Full formatted address
    delivery_address = (
        f"{required['addr1']}"
        f"{', ' + addr2 if addr2 else ''}, "
        f"{required['city']}, "
        f"{required['state']} - {required['pin']}"
    )

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        UPDATE orders
        SET status='confirmed', payment_method='cod',
            address=%s, phone=%s
        WHERE id=%s AND user_id=%s
    """, (delivery_address, required['phone'], order_id, session['user_id']))
    mysql.connection.commit()

    cur.execute("SELECT email FROM users WHERE id=%s", (session['user_id'],))
    user  = cur.fetchone()
    cur.execute("SELECT total_amount FROM orders WHERE id=%s", (order_id,))
    order = cur.fetchone()
    cur.close()

    send_order_notification(
        order_id       = order_id,
        total          = order['total_amount'],
        payment_method = 'cod',
        customer_name  = required['name'],
        customer_email = user['email'],
        address        = delivery_address,
        phone          = required['phone']
    )

    session.pop('cart', None)
    return redirect(url_for('order_success', order_id=order_id))

# ── PAYMENT VERIFY ─────────────────────────────────────────────────
@app.route('/payment/verify', methods=['POST'])
@login_required
def verify_payment():
    data          = request.get_json()
    rz_order_id   = data.get('razorpay_order_id')
    rz_payment_id = data.get('razorpay_payment_id')
    rz_signature  = data.get('razorpay_signature')
    db_order_id   = data.get('order_id')

    msg      = f"{rz_order_id}|{rz_payment_id}".encode()
    secret   = os.getenv('RAZORPAY_KEY_SECRET', '').encode()
    expected = hmac.new(secret, msg, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected, rz_signature):
        return jsonify({'success': False, 'error': 'Invalid signature'}), 400

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        UPDATE orders SET
            status='confirmed',
            razorpay_payment_id=%s,
            razorpay_signature=%s,
            paid_at=NOW()
        WHERE id=%s AND user_id=%s
    """, (rz_payment_id, rz_signature, db_order_id, session['user_id']))
    mysql.connection.commit()

    cur.execute("SELECT email FROM users WHERE id=%s", (session['user_id'],))
    user = cur.fetchone()
    cur.execute("SELECT total_amount FROM orders WHERE id=%s", (db_order_id,))
    order = cur.fetchone()
    cur.close()

    send_order_notification(
        order_id       = db_order_id,
        total          = order['total_amount'],
        payment_method = 'online',
        customer_name  = session.get('username', 'Customer'),
        customer_email = user['email']
    )

    session.pop('cart', None)
    return jsonify({'success': True, 'order_id': db_order_id})

# ── RAZORPAY WEBHOOK ───────────────────────────────────────────────
@app.route('/webhook/razorpay', methods=['POST'])
def razorpay_webhook():
    webhook_secret = os.getenv('RAZORPAY_WEBHOOK_SECRET', '')
    payload        = request.get_data()
    received_sig   = request.headers.get('X-Razorpay-Signature', '')

    expected = hmac.new(
        webhook_secret.encode(), payload, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, received_sig):
        return jsonify({'error': 'Invalid webhook'}), 400

    event = request.get_json()
    if event.get('event') == 'payment.captured':
        rz_order_id = event['payload']['payment']['entity'].get('order_id')
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""
            UPDATE orders SET status='confirmed', paid_at=NOW()
            WHERE razorpay_order_id=%s AND status='pending'
        """, (rz_order_id,))
        mysql.connection.commit()
        cur.close()

    return jsonify({'status': 'ok'})

# ── ORDER SUCCESS ──────────────────────────────────────────────────
@app.route('/order/success/<int:order_id>')
@login_required
def order_success(order_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM orders WHERE id=%s AND user_id=%s",
                (order_id, session['user_id']))
    order = cur.fetchone()
    cur.close()
    return render_template('order_success.html', order=order, cart_count=0)

if __name__ == '__main__':
    app.run(debug=True)