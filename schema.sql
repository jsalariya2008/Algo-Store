-- ============================================================
--  ALGO Streetwear – MySQL Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS algo_store CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE algo_store;

-- ── Users ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100)         NOT NULL,
    email         VARCHAR(150) UNIQUE  NOT NULL,
    password_hash VARCHAR(255)         NOT NULL,
    is_admin      TINYINT(1) DEFAULT 0,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Products ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(200)         NOT NULL,
    price       DECIMAL(10,2)        NOT NULL,
    description TEXT,
    category    VARCHAR(100)         DEFAULT 'Apparel',
    stock       INT                  DEFAULT 0,
    image_url   VARCHAR(500)         DEFAULT '',
    image_url2  VARCHAR(500)         DEFAULT '',
    is_active   TINYINT(1) DEFAULT 1,
    is_upcoming TINYINT(1) DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Cart ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cart (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT          NOT NULL,
    product_id INT          NOT NULL,
    qty        INT DEFAULT 1,
    size       VARCHAR(10) DEFAULT 'M',
    added_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- ── Orders ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orders (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT,
    total_amount DECIMAL(10,2) NOT NULL,
    status       ENUM('pending','confirmed','shipped','delivered','cancelled') DEFAULT 'pending',
    address      TEXT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    order_id   INT NOT NULL,
    product_id INT NOT NULL,
    qty        INT NOT NULL,
    size       VARCHAR(10),
    price      DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id)   REFERENCES orders(id)   ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- ── Seed Data ──────────────────────────────────────────────
INSERT INTO users (name, email, password_hash, is_admin) VALUES
('Admin', 'admin@algo.in', 'pbkdf2:sha256:600000$abc$placeholder', 1);

INSERT INTO products (name, price, description, category, stock, image_url) VALUES
('BHARAT FIRE TEE', 1299.00, 'Bold graphic tee inspired by the flames of revolution. 100% cotton, oversized fit.', 'T-Shirts', 50, ''),
('STREET SUTRA HOODIE', 2499.00, 'A hoodie that tells a story. Heavyweight fleece with hand-drawn print.', 'Hoodies', 30, ''),
('DILLI NIGHTS BOMBER', 3299.00, 'Varsity-style bomber jacket with embroidered cultural motifs.', 'Jackets', 20, ''),
('CHAI CULTURE TOTE', 799.00, 'Canvas tote with bold chai-culture artwork. Statement street carry.', 'Accessories', 100, ''),
('AZAD CARGO PANTS', 2199.00, 'Wide-leg cargo with contrast stitching and street utility pockets.', 'Bottoms', 40, ''),
('RANGREZ OVERSHIRT', 1799.00, 'Linen overshirt dyed in earthy block-print tones. Limited run.', 'Shirts', 25, ''),
('JUGAAD JOGGERS', 1599.00, 'Relaxed joggers with embroidered side-panel art. All-day comfort.', 'Bottoms', 35, ''),
('NAQQASH CAP', 599.00, 'Structured 6-panel cap with embroidered ALGO crest. Adjustable fit.', 'Accessories', 80, ''),
('LAFANGA LONGSLEEVE', 1399.00, 'Heavyweight long sleeve with vintage-wash treatment and back graphic.', 'T-Shirts', 45, ''),
('GALI HOODIE', 2799.00, 'Premium French terry hoodie, screen-printed street poetry on back.', 'Hoodies', 28, '');

INSERT INTO products (name, price, description, category, stock, image_url, is_active, is_upcoming) VALUES
('KHAYAL DROP VOL.2', 1899.00, 'Next drop. Something new. Something raw.', 'T-Shirts', 0, '', 0, 1),
('MITTI COLLECTION', 2599.00, 'Earthy tones. Real textures. Coming soon.', 'Jackets', 0, '', 0, 1),
('BAZAAR SERIES', 1499.00, 'For the streets. Of the streets.', 'Accessories', 0, '', 0, 1),
('DESI PUNK HOODIE', 3199.00, 'Chaos and calm in one garment.', 'Hoodies', 0, '', 0, 1),
('SAFAR JACKET', 4499.00, 'Built for the journey. Wherever it takes you.', 'Jackets', 0, '', 0, 1);

-- ── Done ───────────────────────────────────────────────────
SELECT 'ALGO database initialized successfully' AS status;
