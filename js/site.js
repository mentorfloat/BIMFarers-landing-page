/* Progressive enhancement only: all links and content work without JavaScript. */
(() => {
  'use strict';
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
