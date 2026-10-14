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

const edition = document.getElementById('edition-time');
const ageLabel = document.getElementById('edition-age');
if (edition?.dateTime && ageLabel) {
  const parts = new Intl.DateTimeFormat('en', {timeZone: 'Asia/Tokyo', year: 'numeric', month: '2-digit', day: '2-digit'}).formatToParts(new Date());
  const part = type => parts.find(item => item.type === type)?.value;
  const today = Date.UTC(Number(part('year')), Number(part('month')) - 1, Number(part('day')));
  const [year, month, day] = edition.dateTime.split('-').map(Number);
  const published = Date.UTC(year, month - 1, day);
  const ageDays = Math.floor((today - published) / 86400000);
  if (ageDays > 2) ageLabel.textContent = `最終公開から${ageDays}日`;
}

async function copyArticleUrl(button) {
  const url = new URL(button.dataset.shareUrl, location.origin).href;
  const status = button.parentElement.querySelector('.share-status');
  try {
    await navigator.clipboard.writeText(url);
    status.textContent = 'リンクをコピーしました';
  } catch {
    status.textContent = 'ブラウザのアドレス欄からURLをコピーしてください';
  }
}
document.querySelectorAll('.copy-link').forEach(button => button.addEventListener('click', () => copyArticleUrl(button)));
document.querySelectorAll('.share-article').forEach(button => button.addEventListener('click', async () => {
  const url = new URL(button.dataset.shareUrl, location.origin).href;
  if (!navigator.share) return copyArticleUrl(button);
  try { await navigator.share({title: document.title, url}); }
  catch (error) { if (error.name !== 'AbortError') copyArticleUrl(button); }
}));
