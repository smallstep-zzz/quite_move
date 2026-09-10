(() => {
function filterDocs(q) {
  q = q.toLowerCase();
  document.querySelectorAll('#doc-nav a').forEach(a => {
    a.style.display = a.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}
window.filterDocs = filterDocs;
function toggleCode() {
  document.querySelectorAll('.article pre').forEach(p => p.classList.toggle('expand'));
}
window.toggleCode = toggleCode;

const toc = document.getElementById('toc');
const art = document.getElementById('article');
if (toc && art) {
  const hs = Array.prototype.slice.call(art.querySelectorAll('h2, h3'));
  hs.forEach((h, i) => {
    if (!h.id) h.id = 'h-' + i;
    const li = document.createElement('li');
    li.className = h.tagName === 'H3' ? 'l2' : 'l1';
    const a = document.createElement('a');
    a.href = '#' + h.id;
    a.textContent = h.textContent;
    li.appendChild(a);
    toc.appendChild(li);
  });
  function active() {
    let cur = hs[0];
    hs.forEach(h => { if (h.getBoundingClientRect().top <= 90) cur = h; });
    const c = toc.querySelector('a.current');
    if (c) c.classList.remove('current');
    hs.forEach(h => { if (h === cur) { const l = toc.querySelector('a[href="#' + h.id + '"]'); if (l) l.classList.add('current'); } });
  }
  window.addEventListener('scroll', active, { passive: true });
  active();
}
})();
