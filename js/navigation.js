/* Inline at the end of the header to avoid a menu layout shift on first paint. */
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

})();
