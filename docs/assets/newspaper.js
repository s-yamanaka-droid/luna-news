const toggle = document.getElementById('search-toggle');
const panel = document.getElementById('search-panel');
toggle?.addEventListener('click', () => {
  panel.hidden = !panel.hidden;
  toggle.setAttribute('aria-expanded', String(!panel.hidden));
  if (!panel.hidden) document.getElementById('article-query').focus();
});
panel?.addEventListener('submit', event => {
  event.preventDefault();
  const query = document.getElementById('article-query').value.trim().toLowerCase();
  const cards = [...document.querySelectorAll('[data-search]')];
  if (!cards.length) { location.href = '/?q=' + encodeURIComponent(query); return; }
  const unique = new Set();
  document.body.classList.toggle('searching', query !== '');
  cards.forEach(card => {
    card.hidden = query !== '' && !card.dataset.search.toLowerCase().includes(query);
    if (!card.hidden) unique.add(card.querySelector('h2 a').getAttribute('href'));
  });
  document.getElementById('search-status').textContent = `${unique.size}件の記事が見つかりました`;
});
const initial = new URLSearchParams(location.search).get('q');
if (initial) { toggle.click(); document.getElementById('article-query').value = initial; panel.requestSubmit(); }
document.querySelectorAll('.copy').forEach(button => button.addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(button.previousElementSibling.textContent); button.textContent = 'コピーしました'; }
  catch { button.textContent = '本文を選択してコピーしてください'; }
}));
