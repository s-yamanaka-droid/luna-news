"""AI newspaper: WSJ-referenced hierarchy with original branding and article data."""
from pathlib import Path
from html import escape
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'docs'


def esc(value):
    return escape(str(value or ''), quote=True)


def headline(value):
    return re.sub(r'「[^「」]{1,12}」', lambda m: '<span class="keep-phrase">' + m.group(0) + '</span>', esc(value))


def link(date, i):
    return f'/news/{date}/#topic-{i}'


def photo(date, i, article=None):
    if article and article.get('image') in ('research', 'infrastructure'):
        return '/assets/newspaper/' + article['image'] + '.png'
    if date == '2026-09-07':
        return {3: '/assets/newspaper/research.png', 4: '/assets/newspaper/infrastructure.png'}.get(i)
    return None


SERVICES = {
    'luna': ('Luna', '日々の判断や経験を引き継ぐ、AIの右腕。', 'https://lunatech-migration-guide.vercel.app'),
    'recruitment': ('人材紹介', '事業に必要な役割から、人との出会いを考える。', 'https://lakkan-inc.vercel.app/contact?topic=placement'),
    'crm': ('CRM構築', '顧客情報と、次のアクションを一つの流れに。', 'https://lakkan-inc.vercel.app/contact?topic=crm'),
    'fde': ('FDE', '現場に入り、開発から運用・改善まで伴走する。', 'https://lakkan-inc.vercel.app/contact?topic=fde'),
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


def chrome(title, date, content, canonical='/'):
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} — Now on AIr</title><meta name="description" content="AIの最新動向、研究、ビジネス活用を読む。Now on AIr。"><meta name="theme-color" content="#ffffff">
<link rel="canonical" href="https://nowonair.vercel.app{canonical}"><link rel="icon" href="/assets/favicon.svg">
<meta property="og:title" content="{esc(title)} — Now on AIr"><meta property="og:image" content="https://nowonair.vercel.app/assets/newspaper/research.png"><meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="Now on AIr RSS" href="/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Libre+Caslon+Display&family=Noto+Sans+JP:wght@400;500;700;800;900&family=Noto+Serif+JP:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/newspaper.css?v=1"><script src="/assets/newspaper.js?v=1" defer></script></head><body>
<a class="skip" href="#main">本文へ移動</a><div class="network"><div><a href="/">Now on AIr</a><a href="/weekly.html">Weekly</a><a href="/cases.html">AI活用事例</a><a href="https://lakkan-inc.vercel.app/">Lakkan</a><a class="network-right" href="/feed.xml">RSS購読</a></div></div>
<header class="masthead"><a class="nameplate" href="/">NOW ON AIr.</a><div class="edition"><span>AI & BUSINESS JOURNAL</span><a class="brand-link" href="/#lakkan">with Lakkan</a><time datetime="{date}">更新号 {date.replace('-', '年', 1).replace('-', '月', 1)}日</time><a href="/#archive">バックナンバー ▾</a></div>
<nav aria-label="カテゴリ"><a href="/">ホーム</a><a href="/#models">モデル・製品</a><a href="/#research">研究</a><a href="/#business">ビジネス</a><a href="/#security">セキュリティ</a><a href="/#lakkan">Lakkanについて</a><a href="/weekly.html">週次ダイジェスト</a><button id="search-toggle" aria-expanded="false" aria-controls="search-panel" aria-label="記事を検索">⌕</button></nav>
<form id="search-panel" hidden role="search"><label for="article-query">最新号の記事を検索</label><input id="article-query" type="search" placeholder="キーワードを入力"><button type="submit">検索</button><p id="search-status" role="status"></p></form></header>
<main id="main" class="paper">{content}</main><footer class="paper-footer"><a class="footer-name" href="/">Now on AIr.</a><div><a href="/">ニュース</a><a href="/weekly.html">週次ダイジェスト</a><a href="/cases.html">AI活用事例</a><a href="/privacy.html">プライバシーポリシー</a><a href="/feed.xml">RSS購読</a></div><p>運営：株式会社TREPRO ｜ 編集責任者：山中秀斗</p><p>© Now on AIr / TREPRO</p></footer></body></html>'''


def item(a, date, i, image=False, lead=False):
    media = photo(date, i, a) if image else None
    figure = f'<a class="story-photo" href="{link(date,i)}"><img src="{media}" width="1536" height="1024" alt="{esc(a.get("category"))}を表す編集イメージ" {"fetchpriority=high" if lead else "loading=lazy"}></a><span class="credit">編集イメージ / AI生成</span>' if media else ''
    return f'<article class="story {"lead-story" if lead else ""}" data-search="{esc(a.get("title"))} {esc(a.get("category"))}">{figure}<span class="category">{esc(a.get("category"))}</span><h2><a href="{link(date,i)}">{headline(a.get("title"))}</a></h2><p>{esc(a.get("lede"))}</p><span class="byline">{esc(a.get("source"))}</span></article>'


def index(dates, articles, date):
    indexed = list(enumerate(articles, 1))
    main_i = next((i for i, a in indexed if a.get('image')), 3 if date == '2026-09-07' and len(articles) >= 3 else 1)
    center = [x for x in indexed if x[0] in (main_i, 4)]
    if not center:
        center = indexed[:1]
    left = [x for x in indexed if x not in center][:3]
    right = [x for x in indexed if x not in center and x not in left]
    body = '<div class="front-label"><h1>AIニュース</h1><a href="#all-news">ニュース一覧 ≫</a></div><div class="frontpage">'
    body += '<section class="news-column briefs" aria-label="主要ニュース">' + ''.join(item(a,date,i) for i,a in left) + '</section>'
    body += '<section class="news-column centerpiece" aria-label="注目記事">' + ''.join(item(a,date,i,True,j==0) for j,(i,a) in enumerate(center)) + '</section>'
    body += '<aside class="news-column sidebar"><h2 class="rail-title">AI最前線</h2>' + ''.join(item(a,date,i) for i,a in right) + '<div class="weekly-box"><span>WEEKLY DIGEST</span><h3>一週間の動きを、<br>3つの視点から。</h3><a href="/weekly.html">週次ダイジェストを読む →</a></div></aside></div>'
    groups = [('models','モデル・製品', ['新モデル発表','ツール更新']),('research','研究',['研究']),('business','ビジネス',['業界動向']),('security','セキュリティ・政策',['セキュリティ','政策・規制']),('editors','Lakkanの実務コラム',['Lakkan編集部'])]
    body += lakkan_block()
    body += '<div id="all-news">'
    for ident, label, cats in groups:
        rows = [(i,a) for i,a in indexed if a.get('category') in cats]
        if rows:
            body += f'<section class="section-block" id="{ident}"><h2 class="section-name">{label}</h2><div class="section-stories">' + ''.join(item(a,date,i) for i,a in rows) + '</div></section>'
        else:
            body += f'<section class="section-block" id="{ident}"><h2 class="section-name">{label}</h2><p class="empty-section">今号の新着記事はありません。<a href="#archive">過去の号を読む →</a></p></section>'
    body += '</div><section class="section-block" id="archive"><h2 class="section-name">バックナンバー</h2><details><summary>過去の朝刊を読む</summary><div class="archive-grid">' + ''.join(f'<a href="/news/{d}/">{d} →</a>' for d in sorted(dates, reverse=True)) + '</div></details></section>'
    path=SITE/'index.html'
    path.write_text(chrome('AIニュース',date,body),encoding='utf-8')
    return path


def daily(date, articles, issue=None):
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
    rendered=chrome(f'{date} 朝刊',date,body,f'/news/{date}/').replace('</head>',_daily_jsonld(date,articles)+'</head>')
    path.write_text(rendered,encoding='utf-8')
    return path
