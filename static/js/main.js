/* ================================================================
   ALGO — Main JavaScript
   ================================================================ */

// ── Nav scroll behavior ──────────────────────────────────────────
const nav = document.getElementById('mainNav');
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');

window.addEventListener('scroll', () => {
  if (window.scrollY > 60) {
    nav.classList.add('scrolled');
  } else {
    nav.classList.remove('scrolled');
  }
}, { passive: true });

if (hamburger) {
  hamburger.addEventListener('click', () => {
    mobileMenu.classList.toggle('open');
  });
}

// ── Toast notification ───────────────────────────────────────────
function showToast(msg, duration = 2800) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = msg;
  toast.classList.add('show');
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove('show'), duration);
}

// ── Intersection Observer — fade in elements ─────────────────────
const observerOpts = { threshold: 0.1, rootMargin: '0px 0px -40px 0px' };

const fadeObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('in-view');
      fadeObserver.unobserve(entry.target);
    }
  });
}, observerOpts);

document.querySelectorAll('.product-card, .drop-card, .manifesto__quote, .section__title').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(24px)';
  el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  fadeObserver.observe(el);
});

document.addEventListener('animationend', () => {});

// Add in-view styles
const style = document.createElement('style');
style.textContent = `.in-view { opacity: 1 !important; transform: translateY(0) !important; }`;
document.head.appendChild(style);

// Stagger product cards
const cards = document.querySelectorAll('.product-card');
cards.forEach((card, i) => {
  card.style.transitionDelay = `${i * 0.06}s`;
});

// ── Parallax on hero ─────────────────────────────────────────────
const hero = document.querySelector('.hero__bg');
if (hero) {
  window.addEventListener('scroll', () => {
    const scrolled = window.scrollY;
    hero.style.transform = `translateY(${scrolled * 0.4}px)`;
  }, { passive: true });
}

// ── Culture strip speed on hover ─────────────────────────────────
const strip = document.querySelector('.culture-strip__track');
if (strip) {
  strip.addEventListener('mouseenter', () => {
    strip.style.animationPlayState = 'paused';
  });
  strip.addEventListener('mouseleave', () => {
    strip.style.animationPlayState = 'running';
  });
}

// ── Notify button ────────────────────────────────────────────────
document.querySelectorAll('.drop-card__notify').forEach(btn => {
  btn.addEventListener('click', function () {
    this.textContent = '✓ You\'ll be notified';
    this.style.background = 'var(--red)';
    this.style.color = 'white';
    this.disabled = true;
  });
});

// ── Smooth scroll for anchor links ──────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      const offset = target.getBoundingClientRect().top + window.scrollY - 80;
      window.scrollTo({ top: offset, behavior: 'smooth' });
    }
  });
});

// ── Flash message auto-dismiss ───────────────────────────────────
setTimeout(() => {
  document.querySelectorAll('.flash').forEach(el => {
    el.style.transition = 'opacity 0.5s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 500);
  });
}, 3500);

// ── Lookbook horizontal scroll (touch) ──────────────────────────
const hScrolls = document.querySelectorAll('.lookbook-horizontal');
hScrolls.forEach(el => {
  let startX, startScrollLeft, isDragging = false;
  el.addEventListener('touchstart', e => {
    startX = e.touches[0].pageX;
    startScrollLeft = el.scrollLeft;
  }, { passive: true });
  el.addEventListener('touchmove', e => {
    const x = e.touches[0].pageX;
    el.scrollLeft = startScrollLeft - (x - startX);
  }, { passive: true });
});

// ── Cart item animation ──────────────────────────────────────────
document.querySelectorAll('.cart-item').forEach((item, i) => {
  item.style.opacity = '0';
  item.style.transform = 'translateX(-16px)';
  item.style.transition = `opacity 0.4s ease ${i * 0.08}s, transform 0.4s ease ${i * 0.08}s`;
  setTimeout(() => {
    item.style.opacity = '1';
    item.style.transform = 'translateX(0)';
  }, 50);
});

// ── Page transition ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.body.style.opacity = '0';
  document.body.style.transition = 'opacity 0.4s ease';
  requestAnimationFrame(() => {
    document.body.style.opacity = '1';
  });
});

document.querySelectorAll('a').forEach(a => {
  const href = a.getAttribute('href');
  if (href && !href.startsWith('#') && !href.startsWith('javascript') && !href.startsWith('http')) {
    a.addEventListener('click', e => {
      const url = a.href;
      if (url && url !== window.location.href) {
        e.preventDefault();
        document.body.style.opacity = '0';
        setTimeout(() => window.location.href = url, 280);
      }
    });
  }
});

// ── Active nav link ──────────────────────────────────────────────
const path = window.location.pathname;
document.querySelectorAll('.nav__link').forEach(link => {
  if (link.getAttribute('href') === path) {
    link.style.borderBottom = '1px solid currentColor';
  }
});

console.log('%cALGO', 'font-size:40px;font-weight:bold;color:#c0392b;letter-spacing:10px;');
console.log('%cWear Your Story', 'font-size:14px;color:#8b6f47;font-style:italic;');
