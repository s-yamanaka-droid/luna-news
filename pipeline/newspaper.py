"""AI newspaper: WSJ-referenced hierarchy with original branding and article data."""
from pathlib import Path
from html import escape
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'docs'
PER_ARTICLE_FROM = '2026-09-14'
BASE_URL = 'https://nowonair.vercel.app'


def esc(value):
    return escape(str(value or ''), quote=True)


def headline(value):
    return re.sub(r'「[^「」]{1,12}」', lambda m: '<span class="keep-phrase">' + m.group(0) + '</span>', esc(value))


def link(date, i):
    if date >= PER_ARTICLE_FROM:
        return f'/articles/{date}/story-{i}/'
    return f'/news/{date}/#topic-{i}'


def photo(date, i, article=None):
    # The current editorial direction uses topic-specific diagrams; older stock-like
    # imagery is kept only in the archive where it was originally published.
    if date < PER_ARTICLE_FROM and article and article.get('image') in ('research', 'infrastructure'):
        return '/assets/newspaper/' + article['image'] + '.png'
    if date == '2026-09-07':
        return {3: '/assets/newspaper/research.png', 4: '/assets/newspaper/infrastructure.png'}.get(i)
    return None


SERVICES = {
    'luna': ('Luna', '日々の判断や経験を引き継ぐ、AIの右腕。', 'https://lunatech-migration-guide.vercel.app'),
    'recruitment': ('人財・採用支援', '仕事と採用を見直し、必要な人財を考える。', 'https://lakkan-inc.vercel.app/services#people'),
    'crm': ('CRM構築', '顧客情報と、次のアクションを一つの流れに。', 'https://lakkan-inc.vercel.app/services#crm'),
    'fde': ('FDE', '現場に入り、開発から運用・改善まで伴走する。', 'https://lakkan-inc.vercel.app/services#fde'),
}


def lakkan_block(service=None):
    chosen = [(service, SERVICES[service])] if service in SERVICES else list(SERVICES.items())
    cards = ''.join(f'<a href="{esc(url)}"><span>{esc(name)}</span><p>{esc(copy)}</p><b>詳しく見る ↗</b></a>' for key, (name, copy, url) in chosen)
    return '<section class="lakkan-desk"' + (' id="lakkan"' if service is None else '') + '><div class="desk-heading"><span>Lakkan</span><div><small>FROM READING TO DOING</small><h2>知る。その先を、つくる。</h2></div></div><div class="desk-services">' + cards + '</div><p class="desk-note">事業・サービスのご案内 ｜ LunaはLunaTechのサービスです。</p></section>'


def story_body(a):
    sections = ''
    for block in a.get('body', []):
        sections += '<section><h2>' + esc(block.get('heading')) + '</h2>' + ''.join('<p>' + esc(p) + '</p>' for p in block.get('paragraphs', [])) + '</section>'
    if a.get('analysis'):
        sections += '<div class="editorial-analysis"><span class="category">本誌の考察・実務提案</span>'
        for block in a['analysis']:
            sections += '<section><h2>' + esc(block.get('heading')) + '</h2>' + ''.join('<p>' + esc(p) + '</p>' for p in block.get('paragraphs', [])) + '</section>'
        sections += '</div>'
    if a.get('actions'):
        sections += '<section class="next-actions"><h2>現場で試す3つのこと</h2><ol>' + ''.join('<li>' + esc(p) + '</li>' for p in a['actions']) + '</ol></section>'
    if a.get('service'):
        sections += lakkan_block(a['service'])
    return sections


def editorial_figure(article):
    """Render an illustrated explanation with searchable, accessible labels."""
    diagram = article.get('editorial_diagram') or {}
    if not diagram:
        return ''
    examples = ''.join(
        f'<li><h3>{esc(title)}</h3><p>{esc(detail)}</p></li>'
        for title, detail in diagram.get('examples', [])
    )
    keywords = ''.join(f'<li>{esc(title)}</li>' for title, _ in diagram.get('examples', []))
    source_url = diagram.get('source_url', '')
    source_link = (f' <a href="{esc(source_url)}" target="_blank" rel="noopener">原典を読む ↗</a>'
                   if source_url.startswith(('https://', 'http://')) else '')
    return (
        '<figure class="editorial-figure" aria-labelledby="diagram-title">'
        f'<div class="diagram-heading"><span class="diagram-kicker">{esc(diagram.get("kicker", "図解"))}</span>'
        f'<h2 id="diagram-title">{esc(diagram.get("title"))}</h2><p>{esc(diagram.get("lead"))}</p>'
        f'<ul class="diagram-keywords">{keywords}</ul></div>'
        '<picture>'
        f'<source media="(max-width:700px)" srcset="{esc(diagram.get("mobile"))}" width="1024" height="1536">'
        f'<img src="{esc(diagram.get("wide"))}" width="2172" height="724" loading="lazy" decoding="async" alt="{esc(diagram.get("alt"))}">'
        '</picture>'
        f'<ul class="diagram-examples">{examples}</ul>'
        f'<figcaption>{esc(diagram.get("note"))}{source_link}</figcaption>'
        '</figure>'
    )


def chrome(title, date, content, canonical='/', description=None, og_image=None, page_type='website'):
    description = description or 'AIの最新動向、研究、ビジネス活用を読む。Now on AIr。'
    og_image = og_image or '/assets/og-cover.png'
    absolute_url = BASE_URL + canonical
    absolute_image = BASE_URL + og_image
    edition_label = '最終公開号' if canonical == '/' else '掲載号'
    edition_age = '<span id="edition-age" role="status"></span>' if canonical == '/' else ''
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} — Now on AIr</title><meta name="description" content="{esc(description)}"><meta name="theme-color" content="#ffffff">
<link rel="canonical" href="{esc(absolute_url)}"><link rel="icon" href="/assets/favicon.svg">
<meta property="og:type" content="{esc(page_type)}"><meta property="og:title" content="{esc(title)} — Now on AIr"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{esc(absolute_url)}"><meta property="og:image" content="{esc(absolute_image)}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)} — Now on AIr"><meta name="twitter:description" content="{esc(description)}"><meta name="twitter:image" content="{esc(absolute_image)}">
<link rel="alternate" type="application/rss+xml" title="Now on AIr RSS" href="/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Libre+Caslon+Display&family=Noto+Sans+JP:wght@400;500;700;800;900&family=Noto+Serif+JP:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/newspaper.css?v=2"><link rel="stylesheet" href="/assets/editorial.css?v=2"><script src="/assets/newspaper.js?v=2" defer></script></head><body>
<a class="skip" href="#main">本文へ移動</a>
<header class="masthead"><div class="header-main"><a class="nameplate" href="/" aria-label="Now on AIr ホーム"><span class="wordmark-title">now on air</span></a><span class="nameplate-description">AIの変化を、仕事の判断に。</span>
<nav aria-label="主なページ"><a href="/">ニュース</a><a href="/#all-news">分野から探す</a><a href="/cases.html">AI活用事例</a><a href="/about.html">このサイトについて</a></nav>
<button id="search-toggle" type="button" aria-expanded="false" aria-controls="search-panel" aria-label="記事を検索">⌕</button>
<details class="mobile-navigation"><summary>メニュー</summary><div><a href="/">ニュース</a><a href="/#all-news">分野から探す</a><a href="/cases.html">AI活用事例</a><a href="/about.html">このサイトについて</a><a href="/weekly.html">週次ダイジェスト</a></div></details></div>
<div class="edition"><span>AI専門メディア</span><time id="edition-time" datetime="{date}">{edition_label} {date.replace('-', '年', 1).replace('-', '月', 1)}日</time>{edition_age}<a href="/#archive">バックナンバー →</a></div>
<form id="search-panel" hidden role="search"><label for="article-query">最新号の記事を検索</label><input id="article-query" type="search" placeholder="キーワードを入力"><button type="submit">検索</button><p id="search-status" role="status"></p></form></header>
<main id="main" class="paper">{content}</main><footer class="paper-footer"><div class="footer-company"><img src="/assets/lakkan-wordmark.png" width="1983" height="793" alt="Lakkan"><p>Now on AIrは、株式会社Lakkanが運営するAIメディアです。<br>原典と実務の間をつなぐ視点を届けます。</p></div><div class="footer-links"><a href="/">ニュース</a><a href="/weekly.html">週次ダイジェスト</a><a href="/cases.html">AI活用事例</a><a href="/about.html">このサイトについて</a><a href="/privacy.html">プライバシー</a><a href="/feed.xml">RSS購読</a></div><p>編集責任者：山中秀斗 ｜ © Now on AIr / Lakkan</p></footer></body></html>'''


def item(a, date, i, image=False, lead=False):
    media = photo(date, i, a) if image else None
    figure = f'<a class="story-photo" href="{link(date,i)}"><img src="{media}" width="1536" height="1024" alt="{esc(a.get("category"))}を表す編集イメージ" {"fetchpriority=high" if lead else "loading=lazy"}></a><span class="credit">編集イメージ / AI生成</span>' if media else ''
    return f'<article class="story {"lead-story" if lead else ""}" data-search="{esc(a.get("title"))} {esc(a.get("category"))}">{figure}<span class="category">{esc(a.get("category"))}</span><h2><a href="{link(date,i)}">{headline(a.get("title"))}</a></h2><p>{esc(a.get("lede"))}</p><span class="byline">{esc(a.get("source"))}</span></article>'


def index(dates, articles, date):
    indexed = list(enumerate(articles, 1))
    if not indexed:
        archive = ''.join(f'<a href="/news/{d}/">{esc(d)} →</a>' for d in sorted(dates, reverse=True))
        body = ('<section class="editorial-hero"><div class="hero-promise"><p class="hero-eyebrow">NOW ON AIr</p>'
                '<h1>AIの変化を、<br>仕事の判断に。</h1><p>現在、新着記事はありません。</p>'
                '<a class="hero-primary" href="#archive">過去の記事を読む →</a></div></section>'
                f'<section class="section-block" id="archive"><h2 class="section-name">バックナンバー</h2><div class="archive-grid">{archive}</div></section>')
        path = SITE / 'index.html'
        path.write_text(chrome('AIの変化を、仕事の判断に', date, body), encoding='utf-8')
        return path
    featured_number, featured = indexed[0]
    featured_url = link(date, featured_number)
    original = next((url for url in featured.get('links', []) if isinstance(url, str) and url.startswith(('https://', 'http://'))), None)
    original_link = (f'<a href="{esc(original)}" target="_blank" rel="noopener">原典を読む ↗</a>' if original else '')
    hero_image = featured.get('hero_image')
    hero_media = (
        f'<a class="hero-figure-link" href="{esc(featured_url)}" aria-label="トップ記事を読む">'
        f'<img src="{esc(hero_image)}" width="1536" height="1024" alt="{esc(featured.get("hero_image_alt"))}" loading="eager" decoding="async">'
        f'<span>{esc(featured.get("hero_image_credit") or "編集イメージ / AI生成")}</span></a>'
    ) if hero_image else ''
    rail = ''.join(
        '<article class="hero-rail-story">'
        f'<span class="category">{esc(article.get("category"))}</span>'
        f'<h3><a href="{esc(link(date, number))}">{headline(article.get("title"))}</a></h3>'
        f'<p>{esc(article.get("lede"))}</p>'
        f'<a class="hero-rail-link" href="{esc(link(date, number))}">この記事を読む →</a>'
        '</article>'
        for number, article in indexed[1:3]
    )
    rail_label = 'ほかの掲載記事'
    rail_title = 'ほかの記事'
    if not rail:
        previous_dates = sorted((value for value in dates if value < date), reverse=True)
        previous_path = SITE / 'news' / previous_dates[0] / 'articles.json' if previous_dates else None
        previous = json.loads(previous_path.read_text(encoding='utf-8')) if previous_path and previous_path.is_file() else []
        rail_label = rail_title = '過去の掲載記事'
        rail = ''.join(
            '<article class="hero-rail-story">'
            f'<span class="category">{esc(previous_dates[0])} 掲載</span>'
            f'<h3><a href="{esc(link(previous_dates[0], number))}">{headline(article.get("title"))}</a></h3>'
            f'<a class="hero-rail-link" href="{esc(link(previous_dates[0], number))}">過去の記事を読む →</a></article>'
            for number, article in enumerate(previous[:2], 1)
        ) or '<p>今号の記事は1本です。<a href="#archive">バックナンバーを読む →</a></p>'
    main_i = next((i for i, a in indexed if a.get('image')), 3 if date == '2026-09-07' and len(articles) >= 3 else 1)
    center = [x for x in indexed if x[0] in (main_i, 4)]
    if not center:
        center = indexed[:1]
    left = [x for x in indexed if x not in center][:3]
    right = [x for x in indexed if x not in center and x not in left]
    body = (
        '<section class="editorial-hero newsroom-hero" aria-label="主要ニュース">'
        '<article class="hero-feature">'
        f'<p class="hero-date"><span class="category">{esc(featured.get("category"))}</span> ｜ {esc(date)} 掲載</p>'
        f'<h1><a href="{esc(featured_url)}">{headline(featured.get("title"))}</a></h1>'
        f'<p>{esc(featured.get("lede"))}</p>'
        f'<div class="hero-feature-links">{original_link}<a href="{esc(featured_url)}">この記事を読む →</a></div>{hero_media}'
        f'</article><aside class="hero-rail" aria-label="{rail_label}"><h2>{rail_title}</h2>'
        f'{rail}</aside></section>'
        '<section class="editorial-pathways" aria-label="このサイトでできること">'
        '<a href="#all-news"><span>01</span><h2>変化を知る</h2><p>発表日と一次資料を確かめ、AIの動きを読む。</p><b>記事を探す →</b></a>'
        '<a href="#all-news"><span>02</span><h2>分野から探す</h2><p>研究、製品、業務活用、セキュリティから探す。</p><b>分野を見る →</b></a>'
        '<a href="/cases.html"><span>03</span><h2>現場に引きつける</h2><p>導入の場面や使いどころを、事例から考える。</p><b>活用事例を見る →</b></a>'
        '</section>'
        '<div class="front-label"><h2>掲載記事</h2><a href="#all-news">分野別に探す →</a></div><div class="frontpage">'
    )
    body += '<section class="news-column briefs" aria-label="主要ニュース">' + ''.join(item(a,date,i) for i,a in left) + '</section>'
    body += '<section class="news-column centerpiece" aria-label="注目記事">' + ''.join(item(a,date,i,True,j==0) for j,(i,a) in enumerate(center)) + '</section>'
    body += '<aside class="news-column sidebar"><h2 class="rail-title">AI最前線</h2>' + ''.join(item(a,date,i) for i,a in right) + '<div class="weekly-box"><span>WEEKLY DIGEST</span><h3>一週間の動きを、<br>3つの視点から。</h3><a href="/weekly.html">週次ダイジェストを読む →</a></div></aside></div>'
    groups = [('models','モデル・製品', ['新モデル発表','ツール更新']),('research','研究',['研究']),('business','ビジネス',['業界動向']),('security','セキュリティ・政策',['セキュリティ','政策・規制']),('editors','Lakkanの実務コラム',['Lakkan編集部'])]
    body += '<div id="all-news">'
    for ident, label, cats in groups:
        rows = [(i,a) for i,a in indexed if a.get('category') in cats]
        if rows:
            body += f'<section class="section-block" id="{ident}"><h2 class="section-name">{label}</h2><div class="section-stories">' + ''.join(item(a,date,i) for i,a in rows) + '</div></section>'
        else:
            body += f'<section class="section-block" id="{ident}"><h2 class="section-name">{label}</h2><p class="empty-section">今号の新着記事はありません。<a href="#archive">過去の号を読む →</a></p></section>'
    body += '</div><section class="section-block" id="archive"><h2 class="section-name">バックナンバー</h2><details><summary>過去の朝刊を読む</summary><div class="archive-grid">' + ''.join(f'<a href="/news/{d}/">{d} →</a>' for d in sorted(dates, reverse=True)) + '</div></details></section>'
    path=SITE/'index.html'
    path.write_text(chrome('AIの変化を、仕事の判断に',date,body,
                           description='AIの発表原典と実務への影響を、図解と編集者の視点で読む。Now on AIrは株式会社Lakkanが運営するAI専門メディアです。'),encoding='utf-8')
    return path


def about_page(date):
    """A crawlable operator and editorial-policy page for readers and AI search."""
    body = (
        '<div class="issue-line"><a href="/">ホーム</a> / このサイトについて</div>'
        '<article class="about-editorial"><p class="about-kicker">ABOUT NOW ON AIr</p>'
        '<h1>AIの今を、<br>仕事の判断へ。</h1>'
        '<p class="about-lead">Now on AIrは、AIの発表原典と実務の間をつなぐ、株式会社LakkanのAIメディアです。</p>'
        '<section><h2>記事で大切にすること</h2><p>発表主体が示した事実、確認できていない点、本誌の考察を分けて記します。発表日と本誌の公開・更新日を表示し、原典へ直接進めるリンクを置きます。記事制作にはAIを使用する場合があり、編集責任者が内容を確認します。</p></section>'
        '<section><h2>運営会社</h2><dl><dt>運営</dt><dd>株式会社Lakkan</dd><dt>所在地</dt><dd>東京都渋谷区神宮前六丁目23番4号</dd><dt>編集責任者</dt><dd>山中秀斗</dd><dt>公式サイト</dt><dd><a href="https://lakkan-inc.vercel.app/" target="_blank" rel="noopener">株式会社Lakkan ↗</a></dd></dl>'
        '<p>AI・業務改善、開発、Web体験、人財支援など、会社の事業については公式サイトをご覧ください。記事内の事業案内は、編集記事と区別して表示します。</p></section>'
        '<section><h2>お問い合わせ</h2><p>掲載内容についてのご連絡は、<a href="https://lakkan-inc.vercel.app/contact" target="_blank" rel="noopener">Lakkanのお問い合わせページ ↗</a>からお願いします。</p></section>'
        '</article>'
    )
    schema = {'@context': 'https://schema.org', '@type': 'AboutPage',
              'name': 'Now on AIrについて', 'url': BASE_URL + '/about.html',
              'about': {'@type': 'Organization', 'name': '株式会社Lakkan',
                        'url': 'https://lakkan-inc.vercel.app/'}}
    payload = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
    rendered = chrome('このサイトについて', date, body, '/about.html',
                      'Now on AIrの運営会社、編集方針、掲載内容とお問い合わせ先。').replace('</head>', payload + '</head>')
    path = SITE / 'about.html'
    path.write_text(rendered, encoding='utf-8')
    return path


def article_page(date, article, number, articles):
    """One permanent, crawlable URL for a story in the current publishing format."""
    href = link(date, number)
    media = photo(date, number, article)
    diagram = editorial_figure(article)
    figure = (f'<figure><img src="{esc(media)}" width="1536" height="1024" '
              f'alt="{esc(article.get("category"))}を表す編集イメージ">'
              '<figcaption>編集イメージ / AI生成</figcaption></figure>') if media else ''
    points = ''.join(f'<li>{esc(point)}</li>' for point in article.get('keypoints', []))
    sources = ''.join(f'<a href="{esc(url)}" target="_blank" rel="noopener">原典を読む ↗</a>'
                      for url in article.get('links', []) if isinstance(url, str) and url.startswith(('http://', 'https://')))
    biz = article.get('bizapp') or {}
    practical = (f'<section class="practical"><h2>ビジネスへの示唆</h2><p>{esc(biz.get("summary"))}</p><ul>'
                 + ''.join(f'<li>{esc(action)}</li>' for action in biz.get('actions', []))
                 + '</ul></section>') if biz else ''
    extra = ''
    quickstart = article.get('quickstart') or {}
    if quickstart:
        tool = quickstart.get('tool') or {}
        extra += (f'<details><summary>{esc(quickstart.get("headline", "試してみる"))}</summary>'
                  f'<p>{esc(tool.get("name"))} / {esc(quickstart.get("time"))}</p><ol>'
                  + ''.join(f'<li>{esc(step)}</li>' for step in quickstart.get('steps', []))
                  + f'</ol><pre>{esc(quickstart.get("prompt"))}</pre><button class="copy">プロンプトをコピー</button>'
                  + f'<p>{esc(quickstart.get("roi"))}</p>')
        if str(tool.get('url', '')).startswith(('https://', 'http://')):
            extra += f'<a href="{esc(tool["url"])}" target="_blank" rel="noopener">{esc(tool.get("name"))}を開く ↗</a>'
        extra += '</details>'
    icebreak = article.get('icebreak') or {}
    if icebreak:
        extra += '<details><summary>会話・商談で使う</summary>'
        extra += ''.join(f'<p>{esc(icebreak.get(key))}</p>' for key in ('hook', 'punch', 'ctx_meeting', 'ctx_chat', 'share_text'))
        extra += '</details>'
    for ext in ('webp', 'png'):
        legacy_diagram_file = SITE / 'assets' / 'images' / date / f'topic_{number}.{ext}'
        if legacy_diagram_file.exists():
            extra += (f'<details><summary>この記事の図解を見る</summary><img src="/assets/images/{date}/topic_{number}.{ext}" '
                      f'loading="lazy" alt="{esc(article.get("title"))}の図解"></details>')
            break
    published = article.get('site_published_at') or date
    modified = article.get('updated_at') or published
    source_date = article.get('published_at') or '未確認'
    kind = 'NewsArticle' if article.get('article_kind') == 'news' else 'Article'
    related = ''.join(f'<a href="{link(date, i)}">{esc(articles[i-1].get("title"))} →</a>'
                      for i in (number-1, number+1) if 1 <= i <= len(articles))
    body = (f'<div class="issue-line"><a href="/">ホーム</a> / <a href="/news/{date}/">{date} 更新号</a> / 記事</div>'
            '<div class="article-layout"><div class="article-main">'
            f'<article class="full-story"><span class="category">{esc(article.get("category"))}</span>'
            f'<h1>{headline(article.get("title"))}</h1><p class="standfirst">{esc(article.get("lede"))}</p>'
            f'<div class="article-meta">本誌公開 <time datetime="{esc(published)}">{esc(published)}</time> ｜ '
            f'本誌更新 <time datetime="{esc(modified)}">{esc(modified)}</time> ｜ '
            f'原典の発表・執筆 {esc(source_date)}</div>'
            f'<p class="editorial-credit">発行：Now on AIr 編集部（記事制作にAIを使用）｜編集責任者：山中秀斗</p>'
            f'{figure}{diagram}<div class="reading"><h2>ニュースの要点</h2><ul>{points}</ul>'
            f'<p>{esc(article.get("pull"))}</p>{story_body(article)}{practical}{extra}'
            f'<div class="source-links">{sources}</div>'
            f'<div class="article-share"><span>記事を共有</span><button type="button" class="share-article" data-share-url="{esc(href)}">共有先を選ぶ</button>'
            f'<button type="button" class="copy-link" data-share-url="{esc(href)}">リンクをコピー</button><span class="share-status" role="status"></span></div>'
            f'<nav class="related-stories" aria-label="同じ号の記事"><h2>同じ号の記事</h2>{related}</nav>'
            f'</div></article></div><aside class="article-rail"><h2>この記事の位置</h2><a href="/news/{date}/">{date}号の記事一覧 →</a>'
            '<a class="back-home" href="/">最新号へ →</a></aside></div>')
    schema = {'@context': 'https://schema.org', '@type': kind,
              'headline': article.get('title', ''), 'description': article.get('lede', ''),
              'datePublished': published, 'dateModified': modified,
              'url': BASE_URL + href,
              'mainEntityOfPage': {'@type': 'WebPage', '@id': BASE_URL + href},
              'articleSection': article.get('category', ''),
              'author': {'@type': 'Organization', 'name': 'Now on AIr 編集部'},
              'publisher': {'@type': 'Organization', 'name': '株式会社Lakkan'}}
    diagram_image = (article.get('editorial_diagram') or {}).get('wide')
    social_image = article.get('social_image') or (article.get('editorial_diagram') or {}).get('social')
    if media or diagram_image:
        schema['image'] = [BASE_URL + (media or diagram_image)]
    payload = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
    rendered = chrome(article.get('title', ''), date, body, href,
                      article.get('lede'), social_image or media or diagram_image, 'article').replace('</head>', payload + '</head>')
    path = SITE / href.lstrip('/') / 'index.html'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding='utf-8')
    return path


def daily(date, articles, issue=None):
    if date >= PER_ARTICLE_FROM:
        for number, article in enumerate(articles, 1):
            article_page(date, article, number, articles)
        previews = ''.join(f'<div id="topic-{number}">{item(article, date, number, image=True)}</div>'
                           for number, article in enumerate(articles, 1))
        body = (f'<div class="issue-line"><a href="/">ホーム</a> / {date} 更新号</div>'
                f'<section class="issue-overview"><h1>{date}号の記事</h1>'
                f'<p>各記事の要点から、原典と本誌の分析へ進めます。</p><div class="issue-stories">{previews}</div></section>')
        path = SITE / 'news' / date / 'index.html'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(chrome(f'{date} 朝刊', date, body, f'/news/{date}/',
                               f'{date}号のAIニュースと実務分析。記事ごとの原典と要点を読む。'), encoding='utf-8')
        return path
    toc=''.join(f'<a href="#topic-{i}">{esc(a.get("title"))}</a>' for i,a in enumerate(articles,1))
    body=f'<div class="issue-line"><a href="/">ホーム</a> / {date} 更新号</div><div class="article-layout"><div class="article-main">'
    for i,a in enumerate(articles,1):
        media=photo(date,i,a)
        figure=f'<figure><img src="{media}" width="1536" height="1024" alt="{esc(a.get("category"))}を表す編集イメージ"><figcaption>編集イメージ / AI生成</figcaption></figure>' if media else ''
        points=''.join(f'<li>{esc(k)}</li>' for k in a.get('keypoints',[]))
        links=''.join(f'<a href="{esc(v)}" target="_blank" rel="noopener">出典を読む ↗</a>' for v in a.get('links',[]) if isinstance(v,str) and v.startswith(('http://','https://')))
        biz=a.get('bizapp') or {}
        practical=f'<section class="practical"><h3>ビジネスへの示唆</h3><p>{esc(biz.get("summary"))}</p><ul>'+''.join(f'<li>{esc(v)}</li>' for v in biz.get('actions',[]))+'</ul></section>' if biz else ''
        extra=''
        qs=a.get('quickstart') or {}
        if qs:
            extra=f'<details><summary>{esc(qs.get("headline","試してみる"))}</summary><p>{esc((qs.get("tool") or {}).get("name"))} / {esc(qs.get("time"))}</p><ol>'+''.join(f'<li>{esc(v)}</li>' for v in qs.get('steps',[]))+f'</ol><pre>{esc(qs.get("prompt"))}</pre><button class="copy">プロンプトをコピー</button><p>{esc(qs.get("roi"))}</p></details>'
            tool = qs.get('tool') or {}
            tool_url = tool.get('url', '')
            tool_info = f'<p>{esc(tool.get("cost"))}</p>'
            if tool_url.startswith(('https://', 'http://')):
                tool_info += f'<a href="{esc(tool_url)}" target="_blank" rel="noopener">{esc(tool.get("name"))}を開く ↗</a>'
            extra = extra.replace('</details>', tool_info + '</details>')
        ib=a.get('icebreak') or {}
        if ib:
            extra+='<details><summary>会話・商談で使う</summary>'+''.join(f'<p>{esc(ib.get(k))}</p>' for k in ('hook','punch','ctx_meeting','ctx_chat','share_text'))+'</details>'
        for ext in ('webp','png'):
            if (SITE/'assets'/'images'/date/f'topic_{i}.{ext}').exists():
                extra+=f'<details><summary>この記事の図解を見る</summary><img src="/assets/images/{date}/topic_{i}.{ext}" loading="lazy" alt="{esc(a.get("title"))}の図解"></details>'
                break
        body+=f'<article class="full-story" id="topic-{i}"><span class="category">{esc(a.get("category"))}</span><h1>{headline(a.get("title"))}</h1><p class="standfirst">{esc(a.get("lede"))}</p><div class="article-meta">{esc(a.get("source"))} ｜ 発表・執筆 {esc(a.get("published_at",date))} ｜ 本誌更新 {esc(a.get("updated_at",date))}</div>{figure}<div class="reading"><h2>ニュースの要点</h2><ul>{points}</ul><p>{esc(a.get("pull"))}</p>{story_body(a)}{practical}{extra}<div class="source-links">{links}</div><a href="{"#topic-"+str(i+1) if i<len(articles) else "/"}">次の記事へ →</a></div></article>'
    body+=f'</div><aside class="article-rail"><h2>この号の記事</h2>{toc}<a class="back-home" href="/">ニュース一覧へ →</a></aside></div>'
    path=SITE/'news'/date/'index.html'
    path.parent.mkdir(parents=True,exist_ok=True)
    from html_builder import _daily_jsonld
    rendered=chrome(f'{date} 朝刊',date,body,f'/news/{date}/',
                    og_image='/assets/newspaper/research.png').replace('</head>',_daily_jsonld(date,articles)+'</head>')
    path.write_text(rendered,encoding='utf-8')
    return path
