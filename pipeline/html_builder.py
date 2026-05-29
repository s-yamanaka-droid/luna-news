"""
Now on AIr — HTML Builder v5
vigil.css (Jordan Chicago Design) の DOM 構造に完全準拠
"""
from datetime import datetime
from pathlib import Path
import json

SITE_DIR = Path(__file__).parent.parent / "docs"

WEEKDAYS_EN = ["MON","TUE","WED","THU","FRI","SAT","SUN"]
WEEKDAYS_LONG = ["MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY","SATURDAY","SUNDAY"]
MONTHS_EN = ["JANUARY","FEBRUARY","MARCH","APRIL","MAY","JUNE",
             "JULY","AUGUST","SEPTEMBER","OCTOBER","NOVEMBER","DECEMBER"]

# Now on AIr — Jordan Chicago デザインシステム用フォント（全ページ共通）
FONTS_VIGIL = (
    "https://fonts.googleapis.com/css2?"
    "family=Barlow+Condensed:wght@600;700;800;900&"
    "family=JetBrains+Mono:wght@400;500;600;700;800&"
    "family=Noto+Sans+JP:wght@400;500;700&"
    "family=Noto+Serif+JP:wght@400;600;700&display=swap"
)
FONTS_DETAIL = FONTS_VIGIL  # 共通化

# ブランドマーク HTML スニペット
BRAND_NAV  = '<em class="dot-r">●</em>Now on <em class="brand-ai">AI</em><span class="brand-r">r</span>'
BRAND_FULL = 'Now on <span style="color:var(--red);font-style:normal;">AI</span><span style="color:var(--mute);">r</span>'

INTERACTIVE_JS = """
<!-- Article Modal -->
<div id="article-modal">
  <div id="modal-box">
    <div class="modal-head">
      <span id="modal-cat"></span>
      <button id="modal-close">✕ CLOSE</button>
    </div>
    <div id="modal-slide-wrap" style="display:none;margin:0;overflow:hidden;border-bottom:1px solid var(--rule-2);">
      <img id="modal-slide-img" src="" alt="" style="width:100%;display:block;" />
    </div>
    <div class="modal-body">
      <h2 id="modal-title"></h2>
      <p id="modal-lede"></p>
      <div id="modal-kp"></div>
      <div id="modal-pull"></div>
      <div id="modal-bizapp">
        <div class="bizapp-head">💡 ビジネス活用ポイント</div>
        <div class="bizapp-summary" id="modal-bizapp-summary"></div>
        <ul class="bizapp-actions" id="modal-bizapp-actions"></ul>
      </div>
      <div id="modal-quickstart">
        <div class="qs-head">⚡ 明日からできる｜個人事業主・社長向け</div>
        <div class="qs-headline" id="qs-headline"></div>
        <div class="qs-meta">
          <div class="qs-tool"><span class="qs-label">推奨ツール</span> <a id="qs-tool-link" href="#" target="_blank" rel="noopener"></a> <span id="qs-cost" class="qs-cost"></span></div>
          <div class="qs-time"><span class="qs-label">所要時間</span> <span id="qs-time"></span></div>
        </div>
        <div class="qs-steps-wrap">
          <div class="qs-section-label">3ステップで試す</div>
          <ol class="qs-steps" id="qs-steps"></ol>
        </div>
        <div class="qs-prompt-wrap">
          <div class="qs-section-label">📋 コピペで使えるプロンプト</div>
          <div class="qs-prompt" id="qs-prompt"></div>
          <button class="qs-copy-btn" id="qs-copy-btn">📋 プロンプトをコピー</button>
        </div>
        <div class="qs-roi" id="qs-roi"></div>
      </div>
      <div class="modal-foot">
        <span id="modal-src"></span>
        <a id="modal-link" href="#" target="_blank" rel="noopener">元記事を読む →</a>
      </div>
    </div>
  </div>
</div>

<!-- Image Lightbox -->
<div class="lightbox-overlay" id="lightbox">
  <button class="lightbox-close" id="lightbox-close">× CLOSE</button>
  <img src="" id="lightbox-img" alt="" />
</div>

<script>
(function(){
  /* ── modal ── */
  var modal=document.getElementById('article-modal');
  var box=document.getElementById('modal-box');

  function openModal(card){
    var d=card.dataset;
    document.getElementById('modal-cat').textContent=d.category||'';
    document.getElementById('modal-title').textContent=d.title||'';
    document.getElementById('modal-lede').textContent=d.lede||'';
    document.getElementById('modal-src').textContent='SOURCE: '+(d.source||'');
    var linkEl=document.getElementById('modal-link');
    linkEl.href=d.link||'#';

    /* Gemini slide image */
    var slideWrap=document.getElementById('modal-slide-wrap');
    var slideImg=document.getElementById('modal-slide-img');
    if(d.slide){
      slideImg.src=d.slide; slideImg.alt=d.title||'';
      slideWrap.style.display='block';
    } else { slideWrap.style.display='none'; slideImg.src=''; }

    /* keypoints */
    var kpEl=document.getElementById('modal-kp');
    kpEl.innerHTML='';
    try{
      var kps=JSON.parse(d.keypoints||'[]');
      if(kps.length){
        var ul=document.createElement('ul');
        kps.forEach(function(kp,i){
          var li=document.createElement('li');
          var num=document.createElement('span');
          num.className='kp-num';
          num.textContent=String(i+1).padStart(2,'0');
          li.appendChild(num);
          li.appendChild(document.createTextNode(kp));
          ul.appendChild(li);
        });
        kpEl.appendChild(ul);
      }
    }catch(e){}

    /* pull */
    var pullEl=document.getElementById('modal-pull');
    if(d.pull){pullEl.textContent='「'+d.pull+'」';pullEl.style.display='block';}
    else{pullEl.style.display='none';}

    /* bizapp */
    var bizEl=document.getElementById('modal-bizapp');
    try{
      var biz=JSON.parse(d.bizapp||'null');
      if(biz&&biz.summary){
        document.getElementById('modal-bizapp-summary').textContent=biz.summary;
        var baList=document.getElementById('modal-bizapp-actions');
        baList.innerHTML='';
        var icons=['🏢','🤝','👁'];
        (biz.actions||[]).forEach(function(act,i){
          var li=document.createElement('li');
          var ic=document.createElement('span');
          ic.className='ba-icon';ic.textContent=icons[i]||'→';
          li.appendChild(ic);li.appendChild(document.createTextNode(act));
          baList.appendChild(li);
        });
        bizEl.style.display='block';
      } else { bizEl.style.display='none'; }
    }catch(e){ bizEl.style.display='none'; }

    /* quickstart */
    var qsEl=document.getElementById('modal-quickstart');
    try{
      var qs=JSON.parse(d.quickstart||'null');
      if(qs&&qs.headline){
        document.getElementById('qs-headline').textContent=qs.headline;
        var toolLink=document.getElementById('qs-tool-link');
        toolLink.textContent=(qs.tool&&qs.tool.name)||'';
        toolLink.href=(qs.tool&&qs.tool.url)||'#';
        document.getElementById('qs-cost').textContent=(qs.tool&&qs.tool.cost)?'· '+qs.tool.cost:'';
        document.getElementById('qs-time').textContent=qs.time||'';
        var stepsEl=document.getElementById('qs-steps');
        stepsEl.innerHTML='';
        (qs.steps||[]).forEach(function(step){
          var li=document.createElement('li');
          li.textContent=step;
          stepsEl.appendChild(li);
        });
        var promptEl=document.getElementById('qs-prompt');
        promptEl.textContent=qs.prompt||'';
        var copyBtn=document.getElementById('qs-copy-btn');
        copyBtn.onclick=function(){
          navigator.clipboard.writeText(qs.prompt||'').then(function(){
            copyBtn.textContent='✓ コピー完了';
            setTimeout(function(){copyBtn.textContent='📋 プロンプトをコピー';},1800);
          });
        };
        document.getElementById('qs-roi').textContent=qs.roi?'💰 想定効果：'+qs.roi:'';
        qsEl.style.display='block';
      } else { qsEl.style.display='none'; }
    }catch(e){ qsEl.style.display='none'; }

    modal.style.display='flex';
    modal.style.pointerEvents='auto';
    requestAnimationFrame(function(){
      modal.style.background='rgba(0,0,0,.72)';
      box.classList.add('is-open');
    });
    document.body.style.overflow='hidden';
  }

  function closeModal(){
    modal.style.background='rgba(0,0,0,0)';
    box.classList.remove('is-open');
    setTimeout(function(){modal.style.display='none';modal.style.pointerEvents='none';},280);
    document.body.style.overflow='';
  }

  document.getElementById('modal-close').addEventListener('click',closeModal);
  modal.addEventListener('click',function(e){if(e.target===modal)closeModal();});

  /* card click → modal */
  document.querySelectorAll('.img-card[data-title],.tcard[data-title]').forEach(function(card){
    card.addEventListener('click',function(e){
      if(e.target.tagName==='A')return;
      openModal(card);
    });
  });

  /* ── category filter ── */
  document.querySelectorAll('.filter-pill').forEach(function(pill){
    pill.addEventListener('click',function(){
      var cat=pill.dataset.cat;
      document.querySelectorAll('.filter-pill').forEach(function(p){p.classList.remove('active');});
      pill.classList.add('active');
      document.querySelectorAll('.tcard').forEach(function(c){
        if(!cat||c.dataset.category===cat||cat==='ALL'){
          c.style.opacity='1'; c.style.pointerEvents=''; c.style.transform='';
        } else {
          c.style.opacity='.2'; c.style.pointerEvents='none'; c.style.transform='scale(.97)';
        }
      });
    });
  });

  /* ── image lightbox ── */
  var overlay=document.getElementById('lightbox');
  var img=document.getElementById('lightbox-img');
  var close=document.getElementById('lightbox-close');
  document.querySelectorAll('.zoom-image').forEach(function(el){
    el.addEventListener('click',function(e){e.stopPropagation();
      img.src=''; overlay.classList.add('is-open');
      setTimeout(function(){ img.src=el.dataset.src; img.alt=el.dataset.alt||''; },20);
    });
  });
  function closeBox(){
    img.style.opacity='0'; img.style.transform='scale(0.93)';
    setTimeout(function(){ overlay.classList.remove('is-open'); img.src=''; img.style.opacity=''; img.style.transform=''; },300);
  }
  close.addEventListener('click',closeBox);
  overlay.addEventListener('click',function(e){if(e.target===overlay)closeBox();});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'){closeBox();closeModal();}});

  /* ── scroll fade-in: .daily-topic (デイリーページ専用) ── */
  var fadeEls=document.querySelectorAll('.daily-topic');
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(entries){
      entries.forEach(function(e){if(e.isIntersecting){e.target.classList.add('is-visible');io.unobserve(e.target);}});
    },{threshold:0.05,rootMargin:'0px 0px -24px 0px'});
    fadeEls.forEach(function(el){io.observe(el);});
  } else { fadeEls.forEach(function(el){el.classList.add('is-visible');}); }

  /* ── dispatch ticker ── */
  var row=document.querySelector('.dispatch');
  if(row && row.dataset.ticker!=='off'){
    var inner=row.innerHTML; row.innerHTML=inner+inner;
    var pos=0,spd=0.4;
    (function tick(){pos+=spd;if(pos>=row.scrollWidth/2)pos=0;row.scrollLeft=pos;requestAnimationFrame(tick);})();
  }
})();
</script>
"""


CSS_VER = "v5"

SITE_URL = "https://nowonair.vercel.app/"
OG_IMAGE = SITE_URL + "assets/og-cover.png"  # 1200x630 OGPカバー

def _head(title, desc, css_path, fonts, canonical=None, og_image=None, asset_prefix="./"):
    canonical = canonical or SITE_URL
    og_image = og_image or OG_IMAGE
    jsonld = (
        '{"@context":"https://schema.org","@type":"NewsMediaOrganization",'
        '"name":"Now on AIr","alternateName":"ナウオンエアー",'
        f'"url":"{SITE_URL}","logo":"{OG_IMAGE}",'
        '"description":"AI業界のモーニングインテリジェンス。毎朝6:30に最新AIニュースを図解で配信。",'
        '"founder":{"@type":"Person","name":"山中秀斗"},'
        '"publisher":{"@type":"Organization","name":"TREPRO"}}'
    )
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>{title}</title>
<meta name="description" content="{desc}" />
<link rel="canonical" href="{canonical}" />
<meta name="robots" content="index,follow" />
<meta name="theme-color" content="#CE1141" />
<meta name="referrer" content="strict-origin-when-cross-origin" />
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; script-src 'self' 'unsafe-inline'; base-uri 'self'" />
<!-- OGP -->
<meta property="og:type" content="website" />
<meta property="og:site_name" content="Now on AIr" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{desc}" />
<meta property="og:url" content="{canonical}" />
<meta property="og:image" content="{og_image}" />
<meta property="og:locale" content="ja_JP" />
<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{title}" />
<meta name="twitter:description" content="{desc}" />
<meta name="twitter:image" content="{og_image}" />
<!-- Favicon -->
<link rel="icon" type="image/svg+xml" href="{asset_prefix}assets/favicon.svg" />
<link rel="apple-touch-icon" href="{asset_prefix}assets/favicon.svg" />
<script type="application/ld+json">{jsonld}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{fonts}" rel="stylesheet">
<link rel="stylesheet" href="{css_path}?{CSS_VER}" />
</head>
<body>"""


# ── INDEX PAGE ───────────────────────────────────────────────

def build_index(all_dates: list[str], today_articles: list[dict], today_str: str) -> Path:
    dt       = datetime.strptime(today_str, "%Y-%m-%d")
    issue    = str(int(dt.strftime("%m%d"))).zfill(4)
    weekday  = WEEKDAYS_EN[dt.weekday()]
    weekday_long = WEEKDAYS_LONG[dt.weekday()]
    month_en = MONTHS_EN[dt.month - 1]
    img_dir  = SITE_DIR / "assets" / "images" / today_str

    # ── dispatch bar ──
    dispatch = f"""<div class="dispatch" data-ticker="on">
  <span class="tick">NOW ON AIr</span>
  <span class="sep">/</span>
  <span>№{issue}</span>
  <span class="sep">/</span>
  <span>{today_str}</span>
  <span class="sep">/</span>
  <span>MORNING EDITION</span>
  <span class="sep">/</span>
  <span>{len(today_articles)} ITEMS</span>
  <span class="sep">/</span>
  <span class="live"><span class="dot"></span>LIVE</span>
  <span class="sep">/</span>
  <span>CURATED BY 山中秀斗</span>
  <div class="right">
    <span class="jst"><b>06:30</b> JST</span>
    <span>{weekday}</span>
  </div>
</div>"""

    # ── nav ──
    nav = f"""<nav class="main">
  <div class="brand">{BRAND_NAV}</div>
  <ul>
    <li><a href="./" class="active">TODAY</a></li>
    <li><a href="./weekly.html">WEEKLY</a></li>
    <li><a href="#archive">ARCHIVE</a></li>
    <li><a href="./cases.html">CASES</a></li>
    <li><a href="#about">ABOUT</a></li>
  </ul>
  <button class="subscribe" onclick="return false">SUBSCRIBE · 06:30 DAILY →</button>
</nav>"""

    # ── hero ──
    top = today_articles[0] if today_articles else {}
    top_title = top.get("title", "")
    top_lede  = top.get("lede", "")[:80] + "…" if len(top.get("lede","")) > 80 else top.get("lede","")

    unique_sources = len(set(a.get("source","") for a in today_articles))
    days_count = len(all_dates)

    hero = f"""<div class="hero-wrap">
  <div class="edition-line">
    <span>MORNING DISPATCH</span>
    <span class="sep">//</span>
    <span>{weekday_long}, {month_en} {dt.day}, {dt.year}</span>
    <span class="sep">//</span>
    <span>ISSUE N°{issue}</span>
    <span class="sep">//</span>
    <span>AI MORNING INTELLIGENCE · DAILY DISPATCH</span>
  </div>
  <div class="hero">
    <div class="logo-block">
      <h1>NOW ON <em class="ai">AI</em><span class="r">R</span></h1>
      <div class="sub"><b>AI MORNING INTELLIGENCE</b> · DAILY DISPATCH</div>
      <div class="tagline">
        AIの今を、毎朝<b>06:30 JST</b>に。<br>
        ニュース・モデル発表・論文・注目スレッドを、<b>朝刊として一枚に。</b>
      </div>
    </div>
    <a href="./news/{today_str}/" class="today-cta">
      <div class="ctop">
        <span>TODAY'S ISSUE</span>
        <b>● LIVE</b>
      </div>
      <h2>{dt.strftime('%m%d')}<span class="issue">MORNING EDITION · N°{issue}</span></h2>
      <div class="headline">{top_lede}</div>
      <span class="gotoday">READ TODAY'S DISPATCH →</span>
      <div class="meta-grid">
        <div><div class="k">ITEMS</div><div class="v"><em>{len(today_articles):02d}</em></div></div>
        <div><div class="k">SOURCES</div><div class="v">{unique_sources}</div></div>
        <div><div class="k">ARCHIVE</div><div class="v">{days_count}</div></div>
      </div>
    </a>
  </div>
</div>"""

    # ── stats row ──
    archive_total = sum(
        len(json.loads((SITE_DIR / "news" / d / "articles.json").read_text(encoding="utf-8")))
        if (SITE_DIR / "news" / d / "articles.json").exists() else 8
        for d in all_dates
    )
    stats = f"""<div style="max-width:1400px;margin:0 auto;padding:0 40px">
  <div class="stats-row">
    <div class="stat">
      <div class="k">TODAY</div>
      <div class="v">{len(today_articles):02d}</div>
      <div class="n">items in this issue</div>
    </div>
    <div class="stat">
      <div class="k">SOURCES</div>
      <div class="v">{unique_sources}</div>
      <div class="n">feeds monitored</div>
    </div>
    <div class="stat">
      <div class="k">ARCHIVE</div>
      <div class="v">{archive_total}</div>
      <div class="n">total articles</div>
    </div>
    <div class="stat">
      <div class="k">DAYS</div>
      <div class="v">{days_count}</div>
      <div class="n">issues published</div>
    </div>
  </div>
</div>"""

    # ── section head: today ──
    categories = list(dict.fromkeys(a.get("category","") for a in today_articles))
    pills = "".join(
        f'<span class="pill{"  red" if i==0 else ""}">{c}</span>'
        for i, c in enumerate(categories[:4])
    )
    # カテゴリフィルターボタン
    filter_btns = '<button class="filter-pill active" data-cat="ALL" style="font-family:\'JetBrains Mono\',monospace;font-size:10px;letter-spacing:.12em;padding:5px 12px;border:1px solid var(--rule-2);background:var(--ink);color:var(--paper);cursor:pointer;transition:all .15s;text-transform:uppercase;">ALL</button>'
    for cat in categories:
        filter_btns += f'<button class="filter-pill" data-cat="{cat}" style="font-family:\'JetBrains Mono\',monospace;font-size:10px;letter-spacing:.12em;padding:5px 12px;border:1px solid var(--rule-2);background:none;color:var(--ink);cursor:pointer;transition:all .15s;text-transform:uppercase;">{cat}</button>'

    section_today = f"""<div class="section-head" id="today">
  <span class="kicker">§01</span>
  <h2>Today's Dispatch</h2>
  <span class="jp">今朝の配信</span>
  <span class="count">{len(today_articles)} items</span>
  <a href="./news/{today_str}/" class="morelink">ALL {len(today_articles)} ITEMS →</a>
</div>
<div class="today-strip">
  {pills}
  <div class="bar"></div>
  <span>{today_str}</span>
</div>
<div style="max-width:1400px;margin:0 auto;padding:0 40px 20px;display:flex;gap:8px;flex-wrap:wrap;">
  {filter_btns}
</div>"""

    # ── today cards grid ──
    cards_html = _build_today_grid(today_articles, today_str, img_dir, root="./")

    # ── archive ──
    section_archive = f"""<div class="section-head" id="archive">
  <span class="kicker">§02</span>
  <h2>Archive</h2>
  <span class="jp">過去のディスパッチ</span>
  <span class="count">{days_count} issues</span>
</div>
<div class="archive">
  <div class="archive-list">"""

    for d in sorted(all_dates, reverse=True)[:30]:
        dd = datetime.strptime(d, "%Y-%m-%d")
        is_today = "today" if d == today_str else ""
        # articles.jsonから記事データ読み込み
        art_path = SITE_DIR / "news" / d / "articles.json"
        day_articles = []
        if art_path.exists():
            try:
                day_articles = json.loads(art_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        count = len(day_articles) or 8
        head = day_articles[0]["title"] if day_articles else "Morning Dispatch"
        cats = list(dict.fromkeys(a.get("category","") for a in day_articles[:3]))
        tags = "".join(f'<span>{c}</span>' for c in cats[:3])

        section_archive += f"""
    <a href="./news/{d}/" class="arow {is_today}">
      <div class="dt"><span class="day">{dd.day:02d}</span> <span class="wd">{WEEKDAYS_EN[dd.weekday()]}</span></div>
      <div class="head">{head[:60]}{"…" if len(head)>60 else ""}</div>
      <div class="items"><b>{count}</b> items</div>
      <div class="tags">{tags}</div>
      <div class="arr">→</div>
    </a>"""

    section_archive += "\n  </div>\n</div>"

    # ── about ──
    section_about = f"""<div class="section-head" id="about">
  <span class="kicker">§03</span>
  <h2>About</h2>
  <span class="jp">Now on AIrについて</span>
</div>
<div class="about">
  <div class="card-about">
    <h3>NOW ON AIr — AI Morning Intelligence</h3>
    <p>毎朝06:30 JSTにAIエージェントが自律起動し、RSS・ニュースソースを収集・要約・スライド化してGitHub Pagesに自動配信。人間の介入ほぼゼロで動くモーニングディスパッチです。</p>
    <p>PIPELINE: RSS → CLAUDE HAIKU → GEMINI SLIDES → GITHUB PAGES</p>
    <div class="deliverbox">
      <div><div class="b">CURATOR</div><div class="v">山中秀斗</div></div>
      <div><div class="b">SINCE</div><div class="v">{min(all_dates) if all_dates else today_str}</div></div>
      <div><div class="b">TIME</div><div class="v">06:30 JST</div></div>
      <div><div class="b">ISSUES</div><div class="v">{days_count}</div></div>
    </div>
  </div>
  <div class="sources">
    <h3>RSS SOURCES</h3>
    <ul>
      <li><span class="dot"></span><span class="nm">OpenAI Blog</span></li>
      <li><span class="dot"></span><span class="nm">Anthropic Blog</span></li>
      <li><span class="dot"></span><span class="nm">Google AI Blog</span></li>
      <li><span class="dot"></span><span class="nm">TechCrunch AI</span></li>
      <li><span class="dot"></span><span class="nm">The Verge AI</span></li>
      <li><span class="dot"></span><span class="nm">MIT Tech Review AI</span></li>
      <li><span class="dot"></span><span class="nm">ITmedia AI</span></li>
      <li><span class="dot"></span><span class="nm">Zenn AI</span></li>
    </ul>
  </div>
</div>"""

    # ── colophon + 運営者フッター（法的対応）──
    colophon = f"""<div class="colophon">
  <div class="left"><b>Now on <span class="brand-ai">AI</span>r</b> · AI Morning Intelligence · 山中秀斗 / TREPRO</div>
  <div class="right">{today_str} · BUILD {dt.strftime('%Y%m%d')}.0715</div>
</div>
<footer class="site-footer" style="border-top:1px solid var(--rule-2);padding:32px 24px;margin-top:40px;font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--mute);line-height:1.9;text-align:center;">
  <div style="margin-bottom:10px;">
    <a href="./privacy.html" style="color:var(--mute);margin:0 10px;text-decoration:none;border-bottom:1px solid var(--rule-2);">プライバシーポリシー</a>
    <a href="./cases.html" style="color:var(--mute);margin:0 10px;text-decoration:none;border-bottom:1px solid var(--rule-2);">AI活用事例</a>
    <a href="./weekly.html" style="color:var(--mute);margin:0 10px;text-decoration:none;border-bottom:1px solid var(--rule-2);">週次ダイジェスト</a>
  </div>
  <div>運営：株式会社TREPRO（編集責任者：山中秀斗）</div>
  <div>© {dt.strftime('%Y')} Now on AIr / TREPRO. All rights reserved.</div>
</footer>"""

    html = _head(
        "Now on AIr — AI Morning Intelligence",
        "山中秀斗が毎朝整理するAI業界のモーニングディスパッチ。",
        "./assets/vigil.css",
        FONTS_VIGIL,
    ) + INDEX_CSS + f"""
{dispatch}
{nav}
{hero}
{stats}
{section_today}
{cards_html}
{section_archive}
{section_about}
{colophon}
{INTERACTIVE_JS}
</body>
</html>"""

    out_path = SITE_DIR / "index.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def _build_today_grid(articles, date_str, img_dir, root="../../"):
    """Gemini図解画像を画面いっぱいに見せるギャラリーレイアウト"""
    img_root = f"{root}assets/images/{date_str}"

    html = """<style>
/* ── News Card Grid ── */
.ig-wrap{max-width:1400px;margin:0 auto;padding:0 24px 40px;}
.ig-featured{margin-bottom:20px;}
.ig-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;}
@media(max-width:900px){.ig-grid{grid-template-columns:repeat(2,1fr);}}
@media(max-width:560px){.ig-grid{grid-template-columns:1fr;}}

/* カード共通 */
.nc{cursor:pointer;border:1px solid var(--rule-2);transition:border-color .2s,transform .18s,box-shadow .2s;overflow:hidden;background:var(--paper);}
.nc:hover{border-color:var(--red);transform:translate(-2px,-2px);box-shadow:4px 4px 0 var(--red);}
.nc a{display:block;text-decoration:none;color:inherit;}

/* カード内部 */
.nc-head{background:linear-gradient(135deg,#0d0d1a 0%,#1a1a2e 60%,#16213e 100%);padding:24px 24px 20px;position:relative;overflow:hidden;}
.nc-head::after{content:'';position:absolute;top:-40px;right:-30px;width:140px;height:140px;border-radius:50%;background:radial-gradient(circle,rgba(206,17,65,.1),transparent 70%);}
.nc-meta{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;position:relative;z-index:1;}
.nc-num{font-family:var(--mono);font-size:11px;font-weight:800;color:rgba(255,255,255,.35);letter-spacing:.1em;}
.nc-cat{font-family:var(--mono);font-size:9px;font-weight:700;color:#CE1141;letter-spacing:1.5px;text-transform:uppercase;background:rgba(206,17,65,.15);border:1px solid rgba(206,17,65,.25);padding:3px 10px;border-radius:100px;}
.nc-title{font-family:var(--display),var(--sans);font-size:20px;font-weight:900;color:#fff;line-height:1.3;position:relative;z-index:1;}
.nc-body{padding:16px 20px 12px;}
.nc-lede{font-size:13px;color:var(--mute);line-height:1.6;margin-bottom:10px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
.nc-kps{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;}
.nc-kp{font-family:var(--mono);font-size:9px;letter-spacing:.05em;color:var(--ink-2);background:var(--paper-2);padding:3px 8px;border-radius:3px;border-left:2px solid var(--red);}
.nc-foot{display:flex;align-items:center;gap:8px;padding:8px 16px;border-top:1px solid var(--rule);}
.nc-src{font-family:var(--mono);font-size:10px;color:var(--mute);}
.nc-read{font-family:var(--mono);font-size:10px;font-weight:700;color:var(--red);margin-left:auto;letter-spacing:.08em;}

/* フィーチャード（1番目） */
.nc-feat .nc-head{padding:36px 36px 28px;}
.nc-feat .nc-title{font-size:28px;}
.nc-feat .nc-body{padding:20px 28px 14px;}
.nc-feat .nc-lede{font-size:15px;-webkit-line-clamp:3;}
.nc-feat .nc-kp{font-size:10px;}
</style>
<div class="ig-wrap">\n"""

    import json as _json

    for i, a in enumerate(articles, 1):
        title      = a.get("title", "")
        category   = a.get("category", "AI情報")
        source     = a.get("source", "")
        lede       = a.get("lede", "")
        detail_url = f"{root}news/{date_str}/#topic-{i}"
        slide_rel  = f"{img_root}/topic_{i}.png"
        slide_exists = (img_dir / f"topic_{i}.png").exists()

        kp_json    = _json.dumps(a.get("keypoints", []), ensure_ascii=False).replace('"', '&quot;')
        pull_esc   = a.get("pull","").replace('"','&quot;')
        bizapp_json = _json.dumps(a.get("bizapp", {}), ensure_ascii=False).replace('"', '&quot;')
        quickstart_json = _json.dumps(a.get("quickstart", {}), ensure_ascii=False).replace('"', '&quot;')
        data_attrs = (
            f'data-title="{title.replace(chr(34), "&quot;")}" '
            f'data-category="{category}" '
            f'data-source="{source}" '
            f'data-lede="{lede.replace(chr(34), "&quot;")}" '
            f'data-keypoints="{kp_json}" '
            f'data-pull="{pull_esc}" '
            f'data-bizapp="{bizapp_json}" '
            f'data-quickstart="{quickstart_json}" '
            f'data-link="{detail_url}" '
            f'data-slide="{slide_rel if slide_exists else ""}"'
        )

        # キーポイントタグ（最大3つ）
        kps = a.get("keypoints", [])[:3]
        kp_tags = "".join(f'<span class="nc-kp">{k[:20]}</span>' for k in kps)
        lede_esc = lede.replace('"', '&quot;')
        num = str(i).zfill(2)

        card_inner = f"""<a href="{detail_url}">
      <div class="nc-head">
        <div class="nc-meta"><span class="nc-num">{num}</span><span class="nc-cat">{category}</span></div>
        <div class="nc-title">{title}</div>
      </div>
      <div class="nc-body">
        <div class="nc-lede">{lede_esc}</div>
        <div class="nc-kps">{kp_tags}</div>
      </div>
    </a>
    <div class="nc-foot">
      <span class="nc-src">{source}</span>
      <span class="nc-read">READ →</span>
    </div>"""

        if i == 1:
            html += f"""<div class="nc nc-feat ig-featured" {data_attrs}>
    {card_inner}
</div>
<div class="ig-grid">\n"""
        else:
            html += f"""  <div class="nc ig-card" {data_attrs}>
    {card_inner}
  </div>
"""

    html += "</div>\n</div>\n"  # .ig-grid + .ig-wrap
    return html


# ── DAILY DETAIL PAGE ────────────────────────────────────────

def build_daily_page(date_str: str, articles: list[dict], issue_num: int = None) -> Path:
    dt        = datetime.strptime(date_str, "%Y-%m-%d")
    issue     = str(issue_num or int(dt.strftime("%m%d"))).zfill(4)
    weekday   = WEEKDAYS_EN[dt.weekday()]
    month_en  = MONTHS_EN[dt.month - 1]

    out_dir = SITE_DIR / "news" / date_str
    out_dir.mkdir(parents=True, exist_ok=True)
    img_dir = SITE_DIR / "assets" / "images" / date_str
    img_dir.mkdir(parents=True, exist_ok=True)

    # ── dispatch ──
    dispatch = f"""<div class="dispatch">
  <span class="tick">NOW ON AIr</span>
  <span class="sep">/</span>
  <span>№{issue}</span>
  <span class="sep">/</span>
  <span>{date_str}</span>
  <span class="sep">/</span>
  <span>MORNING EDITION</span>
  <span class="sep">/</span>
  <span>{len(articles)} ITEMS</span>
  <span class="sep">/</span>
  <span class="live"><span class="dot"></span>LIVE</span>
  <div class="right">
    <span class="jst"><b>06:30</b> JST</span>
    <span>{weekday}</span>
  </div>
</div>"""

    # ── nav ──
    nav = f"""<nav class="main">
  <div class="brand">{BRAND_NAV}</div>
  <ul>
    <li><a href="../../">HOME</a></li>
    <li><a href="./" class="active">TODAY</a></li>
    <li><a href="../../#archive">ARCHIVE</a></li>
    <li><a href="../../#about">ABOUT</a></li>
  </ul>
  <button class="subscribe" onclick="return false">SUBSCRIBE · 06:30 DAILY →</button>
</nav>"""

    # ── daily head ──
    daily_head = f"""<div class="hero-wrap">
  <div class="edition-line">
    MORNING DISPATCH
    <span class="sep">//</span>
    {WEEKDAYS_LONG[dt.weekday()]}, {month_en} {dt.day}, {dt.year}
    <span class="sep">//</span>
    ISSUE N°{issue}
  </div>
  <h1 class="date-huge">{dt.year}<span class="dot">.</span>{dt.strftime('%m')}<span class="dot">.</span>{dt.strftime('%d')}</h1>
  <div class="strap">
    <span><span class="count">{len(articles):02d}</span>&nbsp;ITEMS</span>
    <span>AI MORNING INTELLIGENCE</span>
  </div>
</div>"""

    # ── articles ──
    topics_html = ""
    for i, a in enumerate(articles, 1):
        slide_rel    = f"../../assets/images/{date_str}/topic_{i}.png"
        slide_exists = (img_dir / f"topic_{i}.png").exists()
        slide_html   = ""
        if slide_exists:
            slide_html = (
                f'      <div class="slide-img zoom-image" data-src="{slide_rel}" '
                f'data-alt="{a["title"]}" role="button" tabindex="0">\n'
                f'        <img src="{slide_rel}" alt="{a["title"]}" loading="lazy" />\n'
                f'      </div>'
            )

        kp_html = "\n".join(
            f'        <li data-i="{str(j).zfill(2)}">{kp}</li>'
            for j, kp in enumerate(a.get("keypoints", [])[:5], 1)
        )
        biz = a.get("bizapp", {})
        biz_html = ""
        if isinstance(biz, dict) and biz.get("summary"):
            icons = ["🏢", "🤝", "👁"]
            biz_actions = "".join(
                f'        <li><span class="bi">{icons[j] if j < len(icons) else "→"}</span>{act}</li>'
                for j, act in enumerate(biz.get("actions", [])[:3])
            )
            biz_html = f"""      <div class="bizapp-block">
        <div class="biz-label">💡 ビジネス活用ポイント</div>
        <div class="biz-summary">{biz["summary"]}</div>
        <ul>
{biz_actions}
        </ul>
      </div>"""

        links_html = "\n".join(
            f'        <dd><a href="{lnk}">{lnk[:55]}…</a></dd>' if len(lnk) > 55
            else f'        <dd><a href="{lnk}">{lnk}</a></dd>'
            for lnk in a.get("links", [])[:3]
        )
        likes = a.get("likes", "")
        likes_html = (
            f'        <dt>ENGAGEMENT</dt>\n'
            f'        <dd><span class="likes">{likes:,}</span>'
            f'<div class="likes-label">likes on X</div></dd>'
        ) if likes else ""

        topics_html += f"""
<article class="daily-topic" id="topic-{i}">
  <div class="container">
    <aside class="numeral">{str(i).zfill(2)}<span class="ord">TOPIC {str(i).zfill(2)} · {a.get('source','').upper()}</span></aside>
    <div class="main">
      <div class="cat-line">
        {a.get('category','AI情報')} <span class="sep">/</span> {a.get('source','')} <span class="sep">/</span> NEWS
      </div>
      <h2>{a['title']}</h2>
{slide_html}
      <p class="lede">{a.get('lede','')}</p>
      <h3>キーポイント</h3>
      <ul class="keypoints">
{kp_html}
      </ul>
      <div class="pull">{a.get('pull','')}</div>
{biz_html}
    </div>
    <aside class="side">
      <dl>
{likes_html}
        <dt>SOURCE</dt>
        <dd>{a.get('source','')}</dd>
        <dt>PUBLISHED</dt>
        <dd>{date_str}</dd>
        <dt>CATEGORY</dt>
        <dd>{a.get('category','')}</dd>
        <dt>LINKS</dt>
{links_html}
      </dl>
    </aside>
  </div>
</article>"""

    html = _head(
        f"{date_str} Morning Dispatch — Now on AIr",
        f"{date_str} の Now on AIr モーニングディスパッチ — {len(articles)}本のAI業界ニュース。",
        "../../assets/vigil.css",
        FONTS_VIGIL,
        canonical=f"{SITE_URL}news/{date_str}/",
        og_image=f"{SITE_URL}assets/images/{date_str}/topic_1.png",
        asset_prefix="../../",
    ) + DAILY_CSS + f"""
{dispatch}
{nav}
{daily_head}
{topics_html}
<div class="colophon">
  <div class="left"><b>Now on <span class="brand-ai">AI</span>r</b> · AI Morning Intelligence · 山中秀斗 / TREPRO</div>
  <div class="right">{date_str} DISPATCH</div>
</div>
{INTERACTIVE_JS}
</body>
</html>"""

    out_path = out_dir / "index.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


# インデックスページ専用インタラクションCSS
INDEX_CSS = """
<style>
/* ── tcard インタラクション ── */
.tcard[data-title]{cursor:pointer;transition:background .15s,box-shadow .2s,transform .18s,opacity .3s !important;}
.tcard[data-title]:hover{box-shadow:4px 4px 0 var(--red);transform:translate(-2px,-2px);}
.tcard[data-title]:hover h3{color:var(--red);}
.tcard[data-title]:hover .go{color:var(--red);}
.tcard h3{transition:color .15s;}

/* ── フィルターピル ── */
.filter-bar{display:flex;gap:6px;flex-wrap:wrap;align-items:center;}
.filter-pill{
  font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.12em;
  padding:6px 14px;border:1px solid var(--rule-2);background:none;color:var(--mute);
  cursor:pointer;transition:all .15s;text-transform:uppercase;
}
.filter-pill.active{background:var(--ink)!important;color:#fff!important;border-color:var(--ink)!important;}
.filter-pill:not(.active):hover{border-color:var(--red)!important;color:var(--red)!important;}

/* ── モーダル ── */
#article-modal{
  display:none;position:fixed;inset:0;z-index:2000;
  background:rgba(0,0,0,0);transition:background .25s;
  pointer-events:none;align-items:center;justify-content:center;
}
#modal-box{
  position:absolute;top:50%;left:50%;
  transform:translate(-50%,-46%) scale(.96);opacity:0;
  transition:transform .28s cubic-bezier(.22,.68,0,1.2),opacity .25s;
  background:var(--paper);
  border-top:4px solid var(--red);
  border-left:1px solid var(--rule-2);border-right:1px solid var(--rule-2);border-bottom:1px solid var(--rule-2);
  max-width:720px;width:calc(100% - 40px);max-height:90vh;overflow-y:auto;
  box-shadow:0 24px 64px rgba(0,0,0,.18);
}
#modal-box.is-open{transform:translate(-50%,-50%) scale(1);opacity:1;}
.modal-head{
  display:flex;align-items:center;justify-content:space-between;
  padding:14px 24px;border-bottom:1px solid var(--rule);
  position:sticky;top:0;background:var(--paper);z-index:1;
}
#modal-cat{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--red);font-weight:700;}
#modal-close{
  font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.1em;
  background:none;border:1px solid var(--rule-2);padding:5px 14px;
  cursor:pointer;color:var(--mute);transition:background .15s,color .15s,border-color .15s;
}
#modal-close:hover{background:var(--ink);color:#fff;border-color:var(--ink);}
.modal-body{padding:28px 32px 36px;}
#modal-title{
  font-family:'Barlow Condensed','JetBrains Mono',monospace;
  font-weight:900;font-size:28px;line-height:1.2;
  margin:0 0 16px;letter-spacing:-.01em;
}
#modal-lede{font-family:'Noto Serif JP',serif;font-size:15px;line-height:1.82;color:var(--ink-2);margin:0 0 22px;}
#modal-kp{margin:0 0 22px;}
#modal-kp ul{list-style:none;padding:0;margin:0;}
#modal-kp li{
  padding:9px 14px 9px 40px;margin-bottom:2px;
  background:var(--paper-2);border-left:2px solid transparent;
  position:relative;font-size:13px;line-height:1.65;
  transition:border-color .15s,transform .15s;
}
#modal-kp li:hover{border-left-color:var(--red);transform:translateX(3px);}
#modal-kp li .kp-num{position:absolute;left:13px;top:9px;font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--red);font-weight:700;}
#modal-pull{
  padding:14px 18px;border-left:4px solid var(--red);
  background:var(--paper-2);font-size:13px;line-height:1.75;
  color:var(--ink-2);font-style:italic;margin-bottom:24px;display:none;
}
/* ── ビジネス活用ポイント ── */
#modal-bizapp{display:none;margin-bottom:24px;}
.bizapp-head{
  font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:.22em;
  text-transform:uppercase;color:#fff;background:var(--red);
  display:inline-block;padding:4px 10px;margin-bottom:12px;font-weight:700;
}
.bizapp-summary{
  font-family:'Noto Serif JP',serif;font-size:14px;font-weight:700;
  color:var(--ink);line-height:1.65;margin-bottom:12px;
}
.bizapp-actions{list-style:none;padding:0;margin:0;}
.bizapp-actions li{
  padding:9px 12px 9px 36px;margin-bottom:2px;
  background:var(--paper-2);border-left:2px solid var(--red);
  position:relative;font-size:12.5px;line-height:1.6;color:var(--ink-2);
}
.bizapp-actions li .ba-icon{
  position:absolute;left:10px;top:9px;font-size:11px;
}
.modal-foot{
  display:flex;align-items:center;justify-content:space-between;
  flex-wrap:wrap;gap:12px;padding-top:16px;border-top:1px solid var(--rule);
}
#modal-src{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--mute);letter-spacing:.08em;}
#modal-link{
  font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.1em;font-weight:700;
  color:#fff;background:var(--red);padding:10px 22px;text-decoration:none;
  transition:background .15s,transform .15s;display:inline-block;
}
#modal-link:hover{background:var(--ink);transform:translateX(3px);}

/* ── Quickstart（明日からできる） ── */
#modal-quickstart{display:none;margin:24px 0;padding:20px 22px;background:#FFF8E5;border:2px solid #FFC107;border-left:6px solid #FF9800;}
.qs-head{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:#E65100;font-weight:800;margin-bottom:10px;}
.qs-headline{font-family:'Barlow Condensed','Noto Sans JP',sans-serif;font-size:22px;font-weight:900;line-height:1.3;color:var(--ink);margin-bottom:14px;}
.qs-meta{display:flex;flex-wrap:wrap;gap:14px;margin-bottom:16px;font-size:12px;}
.qs-tool,.qs-time{background:#fff;padding:6px 12px;border:1px solid #FFC107;}
.qs-label{font-family:'JetBrains Mono',monospace;font-size:9px;color:#888;letter-spacing:.1em;text-transform:uppercase;margin-right:6px;}
#qs-tool-link{color:#E65100;font-weight:700;text-decoration:none;border-bottom:1px solid #E65100;}
#qs-tool-link:hover{color:#BF360C;}
.qs-cost{color:#666;font-size:11px;margin-left:4px;}
#qs-time{font-weight:700;color:var(--ink);}
.qs-section-label{font-family:'JetBrains Mono',monospace;font-size:10px;color:#E65100;letter-spacing:.12em;text-transform:uppercase;font-weight:700;margin-bottom:8px;}
.qs-steps-wrap{margin-bottom:16px;}
.qs-steps{margin:0;padding:0 0 0 24px;}
.qs-steps li{font-size:13.5px;line-height:1.7;color:var(--ink);margin-bottom:4px;}
.qs-prompt-wrap{margin-bottom:14px;}
.qs-prompt{
  background:#1a1a1a;color:#f5f5f5;padding:14px 16px;font-size:12px;line-height:1.65;
  font-family:'JetBrains Mono',monospace;border-radius:0;white-space:pre-wrap;word-break:break-word;
  max-height:200px;overflow-y:auto;margin-bottom:8px;
}
.qs-copy-btn{
  font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;letter-spacing:.08em;
  background:#FF9800;color:#fff;border:none;padding:9px 20px;cursor:pointer;
  transition:background .15s;
}
.qs-copy-btn:hover{background:#E65100;}
.qs-roi{
  font-size:13px;font-weight:700;color:#E65100;padding:10px 14px;
  background:#fff;border-left:4px solid #FF9800;
}
</style>"""

# vigil.css にない detail ページ専用スタイル（inline で追加）
DAILY_CSS = """
<style>
.date-huge{font-family:'JetBrains Mono',monospace;font-weight:800;font-size:clamp(48px,10vw,112px);line-height:.9;letter-spacing:-.03em;margin:8px 0 20px;}
.date-huge .dot{color:var(--red)}
.strap{display:flex;gap:28px;flex-wrap:wrap;font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--mute);}
.strap .count{color:var(--ink);font-weight:700}
.container{max-width:1400px;margin:0 auto;padding:0 40px}
.daily-topic{padding:52px 0;border-bottom:1px solid var(--rule);position:relative;opacity:0;transform:translateY(20px);transition:opacity .5s,transform .5s;}
.daily-topic.is-visible{opacity:1;transform:none}
.daily-topic::before{content:"";position:absolute;left:0;top:0;width:3px;height:0;background:var(--red);transition:height .4s}
.daily-topic:hover::before{height:100%}
.daily-topic .container{display:grid;grid-template-columns:72px 1fr 240px;gap:36px}
.numeral{font-family:'JetBrains Mono',monospace;font-weight:800;font-size:64px;line-height:1;color:var(--rule-2);position:relative;top:-6px;transition:color .2s}
.daily-topic:hover .numeral{color:var(--red)}
.numeral .ord{display:block;font-size:9px;letter-spacing:.16em;color:var(--mute);margin-top:8px;line-height:1.4;white-space:nowrap}
.cat-line{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--red);margin-bottom:14px}
.cat-line .sep{color:var(--mute);margin:0 8px}
.main h2{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:26px;line-height:1.3;margin:0 0 18px;letter-spacing:-.01em}
.lede{font-family:'Noto Serif JP',serif;font-size:16px;line-height:1.75;margin:0 0 24px;color:var(--ink-2)}
.main h3{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.2em;text-transform:uppercase;margin:24px 0 10px;color:var(--mute)}
.keypoints{list-style:none;padding:0;margin:0 0 24px}
.keypoints li{padding:10px 14px 10px 44px;margin-bottom:2px;background:var(--paper-2);border-left:2px solid transparent;position:relative;font-size:14px;line-height:1.6;transition:border-color .15s,transform .2s}
.keypoints li:hover{border-left-color:var(--red);transform:translateX(4px)}
.keypoints li::before{content:attr(data-i);position:absolute;left:14px;top:10px;font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--red);letter-spacing:.1em}
.pull{padding:18px 22px;border-left:3px solid var(--red);background:var(--paper-2);font-size:14px;line-height:1.7;color:var(--ink-2);font-style:italic;margin-top:24px;transition:border-left-width .2s,padding-left .2s}
.pull:hover{border-left-width:6px;padding-left:19px}
.bizapp-block{margin-top:28px;border:1px solid var(--red);padding:20px 22px;}
.bizapp-block .biz-label{font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:.22em;text-transform:uppercase;color:#fff;background:var(--red);display:inline-block;padding:3px 10px;margin-bottom:12px;font-weight:700;}
.bizapp-block .biz-summary{font-size:14px;font-weight:700;color:var(--ink);line-height:1.65;margin-bottom:10px;font-family:'Noto Serif JP',serif;}
.bizapp-block ul{list-style:none;padding:0;margin:0;}
.bizapp-block li{padding:8px 10px 8px 32px;margin-bottom:2px;background:var(--paper-2);border-left:2px solid var(--red);position:relative;font-size:13px;line-height:1.6;color:var(--ink-2);}
.bizapp-block li .bi{position:absolute;left:8px;top:8px;font-size:12px;}
.slide-img{margin:20px 0;border:1px solid var(--rule-2);overflow:hidden;cursor:zoom-in;position:relative;transition:border-color .2s}
.slide-img:hover{border-color:var(--red)}
.slide-img img{width:100%;display:block;transition:transform .5s}
.slide-img:hover img{transform:scale(1.02)}
.side{font-size:13px}
.side dl{margin:0}
.side dt{font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:var(--mute);margin:18px 0 4px}
.side dt:first-child{margin-top:0}
.side dd{margin:0;word-break:break-all}
.side dd a:hover{color:var(--red)}
.likes{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:28px;color:var(--red)}
.likes-label{font-size:11px;color:var(--mute);letter-spacing:.1em;text-transform:uppercase}
.lightbox-overlay{display:flex;align-items:center;justify-content:center;position:fixed;inset:0;padding:24px;background:rgba(14,13,11,0);z-index:1000;pointer-events:none;transition:background .3s}
.lightbox-overlay.is-open{background:rgba(14,13,11,.93);pointer-events:auto}
.lightbox-overlay img{max-width:100%;max-height:90vh;object-fit:contain;opacity:0;transform:scale(.93);transition:opacity .35s,transform .35s}
.lightbox-overlay.is-open img{opacity:1;transform:scale(1)}
.lightbox-close{position:absolute;top:20px;right:24px;font-family:'JetBrains Mono',monospace;font-size:12px;color:#F7F5F2;cursor:pointer;background:none;border:1px solid rgba(247,245,242,.3);padding:6px 14px;transition:background .2s}
.lightbox-close:hover{background:var(--red)}
@media(max-width:900px){.daily-topic .container{grid-template-columns:1fr}.numeral{font-size:36px}.side{border-top:1px solid var(--rule);padding-top:20px}}
</style>"""


# ── CLI テスト ────────────────────────────────────────────────

if __name__ == "__main__":
    today = "2026-04-23"
    art_path = SITE_DIR / "news" / today / "articles.json"
    if art_path.exists():
        articles = json.loads(art_path.read_text(encoding="utf-8"))
        print(f"articles.json から {len(articles)} 件読み込み")
    else:
        articles = [
            {"title":"OpenAIがワークスペースエージェント機能をChatGPTに導入","category":"ツール更新","source":"OpenAI Blog","lede":"ChatGPTにCodex駆動のワークスペースエージェントが統合され、複雑なワークフロー自動化とクラウド実行によるチーム作業の効率化が実現。","keypoints":["Codex駆動エージェントがワークフロー自動化を実現","複数ツール連携でチーム作業をスケール"],"pull":"エージェント時代の到来により企業の生産性向上が加速。"},
        ] * 3

    p1 = build_daily_page(today, articles)
    print(f"daily: {p1}")
    p2 = build_index([today], articles, today)
    print(f"index: {p2}")
