/* Progressive enhancement only: all links and content work without JavaScript. */
(() => {
  'use strict';
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  if (!('IntersectionObserver' in window) || reduce.matches) return;
  const show = element => element.classList.add('is-in');
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      show(entry.target);
      observer.unobserve(entry.target);
    }
  }, { rootMargin: '0px 0px -8% 0px' });
  for (const element of document.querySelectorAll('[data-enter]')) {
    const box = element.getBoundingClientRect();
    // Anything already on screen (or above it) stays as it is: no flash, no hidden content.
    if (box.top < innerHeight) continue;
    // Stagger by column, so a row of cards arrives left to right.
    element.style.setProperty('--i', Math.round(box.left / innerWidth * 4));
    element.classList.add('will-enter');
    observer.observe(element);
  }
  reduce.addEventListener('change', () => {
    if (!reduce.matches) return;
    observer.disconnect();
    document.querySelectorAll('.will-enter').forEach(show);
  });
})();
