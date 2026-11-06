/* Progressive enhancement only: all links and content work without JavaScript. */
(() => {
  'use strict';
  const header = document.querySelector('.site-header');
  const toggle = document.querySelector('.menu-toggle');
  const navigation = document.querySelector('#navigation');
  if (header && toggle && navigation) {
    const compact = window.matchMedia('(max-width: 760px)');
    const close = () => {
      header.classList.remove('menu-open');
      toggle.setAttribute('aria-expanded', 'false');
    };
    toggle.hidden = false;
    header.classList.add('menu-enhanced');
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      header.classList.toggle('menu-open', open);
      toggle.setAttribute('aria-expanded', String(open));
    });
    navigation.addEventListener('click', event => {
      if (event.target.closest('a') && compact.matches) close();
    });
    header.addEventListener('keydown', event => {
      if (event.key === 'Escape' && header.classList.contains('menu-open')) {
        close();
        toggle.focus();
      }
    });
    compact.addEventListener('change', () => {
      const focusWasInMenu = navigation.contains(document.activeElement);
      close();
      if (compact.matches && focusWasInMenu) toggle.focus();
    });
  }

  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  if ('IntersectionObserver' in window && !motion.matches) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        entry.target.classList.add('is-entering');
        observer.unobserve(entry.target);
      }
    }, { threshold: 0.1 });
    document.querySelectorAll('[data-enter]').forEach(element => observer.observe(element));
    motion.addEventListener('change', () => {
      if (motion.matches) observer.disconnect();
    });
  }
})();
