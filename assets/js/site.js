/* Kotibhaskar Industries — shared script for product pages (no dependencies) */
(function () {
  // Mobile menu
  var burger = document.querySelector('.hamburger');
  var menu = document.getElementById('mobileMenu');
  if (burger && menu) {
    burger.addEventListener('click', function () {
      var open = menu.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    menu.addEventListener('click', function (e) { if (e.target.tagName === 'A') menu.classList.remove('open'); });
  }

  // Nav shadow on scroll (same behaviour as homepage)
  var nav = document.getElementById('main-nav');
  if (nav) {
    window.addEventListener('scroll', function () {
      nav.style.boxShadow = window.scrollY > 30 ? '0 2px 14px rgba(0,0,0,.12)' : '0 2px 10px rgba(0,0,0,.07)';
    });
  }

  // Category filter (category pages)
  var buttons = document.querySelectorAll('.filter-btn');
  var blocks = document.querySelectorAll('.group-block');
  function applyFilter(id, push) {
    var found = false;
    buttons.forEach(function (b) {
      var on = b.getAttribute('data-filter') === id;
      b.classList.toggle('active', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      if (on) found = true;
    });
    if (!found) { id = 'all'; buttons[0] && buttons[0].classList.add('active'); }
    blocks.forEach(function (bl) { bl.hidden = !(id === 'all' || bl.id === id); });
    if (push && history.replaceState) history.replaceState(null, '', id === 'all' ? location.pathname : '#' + id);
  }
  if (buttons.length) {
    buttons.forEach(function (b) {
      b.addEventListener('click', function () { applyFilter(b.getAttribute('data-filter'), true); });
    });
    applyFilter((location.hash || '#all').slice(1), false);
  }

  // Lightbox for product images
  var gallery = document.querySelectorAll('[data-lightbox]');
  if (gallery.length) {
    var lb = document.createElement('div');
    lb.className = 'lightbox';
    lb.setAttribute('role', 'dialog');
    lb.setAttribute('aria-modal', 'true');
    lb.innerHTML = '<button type="button" aria-label="Close">&times;</button><img alt="">';
    document.body.appendChild(lb);
    var lbImg = lb.querySelector('img');
    var close = function () { lb.classList.remove('open'); lbImg.removeAttribute('src'); document.body.style.overflow = ''; };
    gallery.forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        lbImg.src = a.getAttribute('href');
        lbImg.alt = a.querySelector('img') ? a.querySelector('img').alt : '';
        lb.classList.add('open');
        document.body.style.overflow = 'hidden';
      });
    });
    lb.addEventListener('click', close);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
  }

  // Print datasheet
  document.querySelectorAll('[data-print]').forEach(function (b) {
    b.addEventListener('click', function () { window.print(); });
  });
})();
