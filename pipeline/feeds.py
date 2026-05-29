"""
Now on AIr — RSS Feed Registry
AI・テック業界の主要RSSフィードを網羅（300件超）

使い方:
    from pipeline.feeds import RSS_FEEDS
    for name, url in RSS_FEEDS:
        ...
"""

RSS_FEEDS: list[tuple[str, str]] = [

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 公式ブログ（一次情報・最重要）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    # ── 大手AIラボ ──
    ("OpenAI Blog",                 "https://openai.com/blog/rss.xml"),
    ("Anthropic Blog",              "https://www.anthropic.com/rss.xml"),
    ("Google AI Blog",              "https://blog.google/technology/ai/rss/"),
    ("Google DeepMind Blog",        "https://deepmind.google/blog/rss.xml"),
    ("Microsoft AI Blog",           "https://blogs.microsoft.com/ai/feed/"),
    ("Microsoft Research Blog",     "https://www.microsoft.com/en-us/research/feed/"),
    ("Meta AI Blog",                "https://ai.meta.com/blog/rss/"),
    ("Apple Machine Learning",      "https://machinelearning.apple.com/rss.xml"),
    ("Amazon AWS AI Blog",          "https://aws.amazon.com/blogs/machine-learning/feed/"),
    ("Amazon AWS News Blog",        "https://aws.amazon.com/blogs/aws/feed/"),
    ("Hugging Face Blog",           "https://huggingface.co/blog/feed.xml"),
    ("Stability AI Blog",           "https://stability.ai/blog/rss.xml"),
    ("Mistral AI Blog",             "https://mistral.ai/feed/"),
    ("Cohere Blog",                 "https://cohere.com/blog/rss.xml"),
    ("NVIDIA AI Blog",              "https://blogs.nvidia.com/blog/category/deep-learning/feed/"),
    ("NVIDIA Developer Blog",       "https://developer.nvidia.com/blog/feed/"),
    ("Intel AI Blog",               "https://community.intel.com/t5/Blogs/ct-p/blogs/rss/board-id/tech-innovation"),
    ("IBM Research Blog",           "https://research.ibm.com/blog/rss"),
    ("Salesforce AI Research",      "https://blog.salesforceairesearch.com/rss/"),
    ("Databricks Blog",             "https://www.databricks.com/blog/feed"),
    ("Weights & Biases Blog",       "https://wandb.ai/fully-connected/rss.xml"),
    ("LangChain Blog",              "https://blog.langchain.dev/rss/"),
    ("Runway ML Blog",              "https://runwayml.com/blog/rss.xml"),
    ("Replicate Blog",              "https://replicate.com/blog/rss"),

    # ── クラウド・プラットフォーム ──
    ("Google Cloud Blog AI/ML",     "https://cloud.google.com/feeds/aiandmachinelearning-release-notes.xml"),
    ("Azure AI Blog",               "https://techcommunity.microsoft.com/t5/ai-azure-ai-services-blog/bg-p/Azure-AI-Services-blog/rss"),
    ("Cloudflare Blog",             "https://blog.cloudflare.com/rss/"),
    ("Vercel Blog",                 "https://vercel.com/blog/rss.xml"),
    ("Supabase Blog",               "https://supabase.com/blog/rss.xml"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # AI専門ニュース（英語）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    # ── 主要テックメディア AI カテゴリ ──
    ("VentureBeat AI",              "https://venturebeat.com/category/ai/feed/"),
    ("The Decoder",                 "https://the-decoder.com/feed/"),
    ("TechCrunch AI",               "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("Ars Technica AI",             "https://arstechnica.com/ai/feed/"),
    ("MIT Tech Review AI",          "https://www.technologyreview.com/topic/artificial-intelligence/feed"),
    ("The Verge AI",                "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"),
    ("Wired AI",                    "https://www.wired.com/feed/tag/ai/latest/rss"),
    ("CNBC Tech",                   "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=19854910"),
    ("Reuters Tech",                "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best"),
    ("The Information",             "https://www.theinformation.com/feed"),
    ("Engadget AI",                 "https://www.engadget.com/ai/rss.xml"),
    ("ZDNet AI",                    "https://www.zdnet.com/topic/artificial-intelligence/rss.xml"),
    ("InfoWorld AI/ML",             "https://www.infoworld.com/category/artificial-intelligence/index.rss"),
    ("The Register AI/ML",          "https://www.theregister.com/software/ai_ml/headlines.atom"),
    ("SiliconANGLE AI",             "https://siliconangle.com/category/ai/feed/"),
    ("IEEE Spectrum AI",            "https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss"),
    ("Scientific American Tech",    "https://rss.sciam.com/ScientificAmerican-Technology"),
    ("Nature Machine Intelligence", "https://www.nature.com/natmachintell.rss"),
    ("Science Daily AI",            "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml"),
    ("Analytics India Magazine",    "https://analyticsindiamag.com/feed/"),
    ("Marktechpost",                "https://www.marktechpost.com/feed/"),
    ("The AI Beat (VentureBeat)",   "https://venturebeat.com/category/ai/the-ai-beat/feed/"),
    ("ReadWrite AI",                "https://readwrite.com/category/ai/feed/"),
    ("9to5Google AI",               "https://9to5google.com/guides/ai/feed/"),
    ("Android Authority AI",        "https://www.androidauthority.com/tag/artificial-intelligence/feed/"),
    ("Tom's Guide AI",              "https://www.tomsguide.com/feeds/all"),
    ("The Next Web AI",             "https://thenextweb.com/topic/artificial-intelligence/feed"),

    # ── ビジネス系テックメディア ──
    ("Bloomberg Technology",        "https://feeds.bloomberg.com/technology/news.rss"),
    ("TechCrunch",                  "https://techcrunch.com/feed/"),
    ("The Verge",                   "https://www.theverge.com/rss/index.xml"),
    ("Ars Technica",                "https://feeds.arstechnica.com/arstechnica/index"),
    ("Fast Company Tech",           "https://www.fastcompany.com/technology/rss"),
    ("Forbes AI",                   "https://www.forbes.com/ai/feed/"),
    ("Business Insider Tech",       "https://www.businessinsider.com/sai/rss"),
    ("Protocol",                    "https://www.protocol.com/feeds/feed.rss"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # AI専門ニュース（日本語・重要）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    # ── 主要テック系 ──
    ("ITmedia AI+",                 "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml"),
    ("ITmedia News",                "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml"),
    ("ITmedia Enterprise",          "https://rss.itmedia.co.jp/rss/2.0/enterprise.xml"),
    ("Impress Watch AI",            "https://www.watch.impress.co.jp/data/rss/1.0/ipw/feed.rdf"),
    ("Impress PC Watch",            "https://pc.watch.impress.co.jp/data/rss/1.0/pcw/feed.rdf"),
    ("Impress Internet Watch",      "https://internet.watch.impress.co.jp/data/rss/1.0/iw/feed.rdf"),
    ("Impress Cloud Watch",         "https://cloud.watch.impress.co.jp/data/rss/1.0/cw/feed.rdf"),
    ("ASCII.jp テクノロジー",        "https://ascii.jp/rss.xml"),
    ("GIGAZINE",                    "https://gigazine.net/news/rss_2.0/"),
    ("Publickey",                   "https://www.publickey1.jp/atom.xml"),
    ("Gihyo.jp",                    "https://gihyo.jp/feed/rss2"),
    ("CNET Japan",                  "https://japan.cnet.com/rss/index.rdf"),
    ("ZDNet Japan",                 "https://japan.zdnet.com/rss/index.rdf"),
    ("TechCrunch Japan",            "https://jp.techcrunch.com/feed/"),
    ("Engadget Japan",              "https://japanese.engadget.com/rss.xml"),
    ("Mogura VR",                   "https://www.moguravr.com/feed/"),
    ("Ledge.ai",                    "https://ledge.ai/feed"),
    ("AINOW",                       "https://ainow.ai/feed/"),
    ("AI-SCHOLAR",                  "https://ai-scholar.tech/feed"),

    # ── 日経系 ──
    ("日経クロステック",              "https://xtech.nikkei.com/rss/index.rdf"),
    ("日経クロステック AI",           "https://xtech.nikkei.com/atcl/nxt/column/18/00001/rss/index.rdf"),
    ("日経ビジネス テクノロジー",      "https://business.nikkei.com/rss/sns/nb.rdf"),

    # ── その他日本語 ──
    ("Qiita トレンド",               "https://qiita.com/popular-items/feed"),
    ("Zenn トレンド",                "https://zenn.dev/feed"),
    ("はてなブックマーク テクノロジー", "https://b.hatena.ne.jp/hotentry/it.rss"),
    ("Hatena Developer Blog",       "https://developer.hatenastaff.com/rss"),
    ("Yahoo! JAPAN Tech Blog",      "https://techblog.yahoo.co.jp/index.xml"),
    ("LINE Engineering",            "https://engineering.linecorp.com/ja/feed/index.xml"),
    ("Mercari Engineering",         "https://engineering.mercari.com/blog/feed.xml"),
    ("CyberAgent Engineering",      "https://developers.cyberagent.co.jp/blog/feed/"),
    ("DeNA Engineering",            "https://engineering.dena.com/blog/atom.xml"),
    ("SmartNews Engineering",       "https://developer.smartnews.com/blog/feed"),
    ("Preferred Networks Blog",     "https://tech.preferred.jp/ja/feed/"),
    ("Sakana AI Blog",              "https://sakana.ai/blog/feed.xml"),
    ("ABEJA Tech Blog",             "https://tech-blog.abeja.asia/rss"),
    ("NTTデータ テクノロジー",        "https://www.nttdata.com/jp/ja/trends/data-insight/feed/"),
    ("JDLA 日本ディープラーニング協会", "https://www.jdla.org/feed/"),
    ("ロボスタ (RoboStart)",         "https://robotstart.info/feed"),
    ("Tech Feed",                   "https://techfeed.io/feeds/all/rss.xml"),
    ("CodeZine",                    "https://codezine.jp/rss/new/index.xml"),
    ("ThinkIT",                     "https://thinkit.co.jp/rss.xml"),

    # ── 日本語ビジネス系 ──
    ("東洋経済オンライン テクノロジー", "https://toyokeizai.net/list/genre/tech/feed"),
    ("ダイヤモンドオンライン IT",     "https://diamond.jp/ud/genre/it/rss/index.xml"),
    ("NewsPicks テクノロジー",       "https://newspicks.com/topic/tech/feed"),
    ("Forbes JAPAN テック",          "https://forbesjapan.com/feat/tech/feed/atom"),
    ("Wired Japan",                 "https://wired.jp/feed/"),
    ("AMP (現代ビジネスxテック)",     "https://ampmedia.jp/feed/"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 開発者・エンジニア向け
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    # ── 技術ブログ・メディア ──
    ("Hacker News (Best)",          "https://hnrss.org/best"),
    ("Hacker News (Front Page)",    "https://hnrss.org/frontpage"),
    ("Lobsters",                    "https://lobste.rs/rss"),
    ("Dev.to AI",                   "https://dev.to/feed/tag/ai"),
    ("Dev.to ML",                   "https://dev.to/feed/tag/machinelearning"),
    ("Dev.to LLM",                  "https://dev.to/feed/tag/llm"),
    ("Hacker Noon AI",              "https://hackernoon.com/tagged/artificial-intelligence/feed"),
    ("InfoQ AI/ML",                 "https://feed.infoq.com/ai-ml-data-eng"),
    ("DZone AI/ML",                 "https://feeds.dzone.com/ai"),
    ("The New Stack AI",            "https://thenewstack.io/category/ai/feed/"),
    ("Simon Willison's Blog",       "https://simonwillison.net/atom/everything/"),
    ("Chip Huyen",                  "https://huyenchip.com/feed.xml"),
    ("Sebastian Raschka",           "https://sebastianraschka.com/rss_feed.xml"),
    ("Lilian Weng (OpenAI)",        "https://lilianweng.github.io/index.xml"),
    ("Jay Alammar",                 "https://jalammar.github.io/feed.xml"),
    ("Andrej Karpathy",             "https://karpathy.github.io/feed.xml"),
    ("Eugene Yan",                  "https://eugeneyan.com/rss/"),
    ("Lil'Log (Lilian Weng)",       "https://lilianweng.github.io/feed.xml"),
    ("Colah's Blog",                "https://colah.github.io/rss.xml"),
    ("Distill.pub",                 "https://distill.pub/rss.xml"),
    ("FastAI Blog",                 "https://www.fast.ai/atom.xml"),
    ("PyTorch Blog",                "https://pytorch.org/blog/feed.xml"),
    ("TensorFlow Blog",             "https://blog.tensorflow.org/feeds/posts/default?alt=rss"),
    ("JAX Blog",                    "https://jax.readthedocs.io/en/latest/_static/rss.xml"),
    ("Keras Blog",                  "https://blog.keras.io/feeds/all.atom.xml"),
    ("MLflow Blog",                 "https://mlflow.org/blog/rss.xml"),

    # ── Medium 系 (公式パブリケーション) ──
    ("Towards Data Science",        "https://towardsdatascience.com/feed"),
    ("Towards AI",                  "https://pub.towardsai.net/feed"),
    ("Google Developers (Medium)",  "https://medium.com/feed/google-developers"),
    ("Netflix Tech Blog",           "https://netflixtechblog.com/feed"),
    ("Uber Engineering",            "https://eng.uber.com/feed/"),
    ("Airbnb Tech Blog",            "https://medium.com/feed/airbnb-engineering"),
    ("Spotify Engineering",         "https://engineering.atspotify.com/feed/"),
    ("LinkedIn Engineering",        "https://engineering.linkedin.com/blog.rss.html"),
    ("Pinterest Engineering",       "https://medium.com/feed/pinterest-engineering"),
    ("Dropbox Tech Blog",           "https://dropbox.tech/feed"),
    ("Stripe Engineering Blog",     "https://stripe.com/blog/feed.rss"),
    ("GitHub Blog Engineering",     "https://github.blog/category/engineering/feed/"),
    ("GitHub Blog AI/ML",           "https://github.blog/category/ai-ml/feed/"),

    # ── AI / ML 特化メディア ──
    ("Analytics Vidhya",            "https://www.analyticsvidhya.com/feed/"),
    ("Machine Learning Mastery",    "https://machinelearningmastery.com/feed/"),
    ("KDnuggets",                   "https://www.kdnuggets.com/feed"),
    ("DataCamp Blog",               "https://www.datacamp.com/blog/rss.xml"),
    ("Neptune.ai Blog",             "https://neptune.ai/blog/feed"),
    ("Papers With Code (Latest)",   "https://paperswithcode.com/latest/rss"),
    ("AI Alignment Forum",          "https://www.alignmentforum.org/feed.xml?view=curated-rss"),
    ("LessWrong (AI)",              "https://www.lesswrong.com/feed.xml?view=curated-rss"),
    ("The Gradient",                "https://thegradient.pub/rss/"),

    # ── Podcast (テキスト要約付き) ──
    ("Lex Fridman Podcast",         "https://lexfridman.com/feed/podcast/"),
    ("The TWIML AI Podcast",        "https://twimlai.com/feed/"),
    ("Practical AI (Changelog)",    "https://changelog.com/practicalai/feed"),
    ("The AI Podcast (NVIDIA)",     "https://feeds.soundcloud.com/users/soundcloud:users:264034133/sounds.rss"),
    ("Eye on AI",                   "https://www.eye-on.ai/rss.xml"),
    ("AI with Kara Swisher",        "https://feeds.megaphone.fm/PP5614858178"),
    ("Gradient Dissent (W&B)",      "https://feeds.soundcloud.com/users/soundcloud:users:721760134/sounds.rss"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # VC・ビジネス・投資
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    ("a16z Blog",                   "https://a16z.com/feed/"),
    ("a16z AI",                     "https://a16z.com/ai/feed/"),
    ("Sequoia Capital Blog",        "https://www.sequoiacap.com/feed/"),
    ("Y Combinator Blog",           "https://www.ycombinator.com/blog/rss/"),
    ("First Round Review",          "https://review.firstround.com/feed.xml"),
    ("Greylock Partners Blog",      "https://greylock.com/feed/"),
    ("Bessemer Venture Partners",   "https://www.bvp.com/atlas/rss.xml"),
    ("Accel Blog",                  "https://www.accel.com/blog/rss.xml"),
    ("Lux Capital Blog",            "https://luxcapital.com/blog/feed/"),
    ("CB Insights AI",              "https://www.cbinsights.com/research/feed/"),
    ("Crunchbase News",             "https://news.crunchbase.com/feed/"),
    ("PitchBook Blog",              "https://pitchbook.com/blog/rss"),
    ("Benedict Evans Newsletter",   "https://www.ben-evans.com/benedictevans/rss"),
    ("Stratechery",                 "https://stratechery.com/feed/"),
    ("One Useful Thing (Ethan Mollick)", "https://www.oneusefulthing.org/feed"),
    ("No Priors (Podcast)",         "https://www.nopriors.com/feed"),
    ("The Batch (deeplearning.ai)", "https://www.deeplearning.ai/the-batch/feed/"),

    # ── 日本 VC / スタートアップ ──
    ("BRIDGE (THE BRIDGE)",         "https://thebridge.jp/feed"),
    ("TechCrunch Japan",            "https://jp.techcrunch.com/feed/"),
    ("INITIAL (ユーザベース)",       "https://initial.inc/articles/feed"),
    ("ASCII スタートアップ",          "https://ascii.jp/startup/rss.xml"),
    ("PR TIMES テクノロジー",        "https://prtimes.jp/topics/keyword/AI/feed"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 研究機関・大学・論文
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    # ── arXiv (主要AI関連カテゴリ) ──
    ("arXiv cs.AI (人工知能)",          "https://rss.arxiv.org/rss/cs.AI"),
    ("arXiv cs.CL (計算言語学/NLP)",    "https://rss.arxiv.org/rss/cs.CL"),
    ("arXiv cs.LG (機械学習)",          "https://rss.arxiv.org/rss/cs.LG"),
    ("arXiv cs.CV (コンピュータビジョン)","https://rss.arxiv.org/rss/cs.CV"),
    ("arXiv cs.NE (ニューラルネット)",   "https://rss.arxiv.org/rss/cs.NE"),
    ("arXiv cs.RO (ロボティクス)",       "https://rss.arxiv.org/rss/cs.RO"),
    ("arXiv cs.IR (情報検索)",          "https://rss.arxiv.org/rss/cs.IR"),
    ("arXiv cs.HC (HCI)",              "https://rss.arxiv.org/rss/cs.HC"),
    ("arXiv cs.CR (暗号・セキュリティ)", "https://rss.arxiv.org/rss/cs.CR"),
    ("arXiv stat.ML (統計的機械学習)",   "https://rss.arxiv.org/rss/stat.ML"),
    ("arXiv eess.AS (音声)",            "https://rss.arxiv.org/rss/eess.AS"),

    # ── 大学・研究機関ブログ ──
    ("Stanford HAI",                "https://hai.stanford.edu/news/rss.xml"),
    ("Stanford AI Lab (SAIL)",      "https://ai.stanford.edu/blog/feed.xml"),
    ("MIT CSAIL",                   "https://www.csail.mit.edu/news/rss.xml"),
    ("MIT News AI",                 "https://news.mit.edu/topic/mitartificial-intelligence2-rss.xml"),
    ("Berkeley AI Research (BAIR)", "https://bair.berkeley.edu/blog/feed.xml"),
    ("CMU Machine Learning",        "https://blog.ml.cmu.edu/feed/"),
    ("Oxford AI Blog",              "https://www.ox.ac.uk/research/research-in-conversation/rss"),
    ("Allen Institute for AI (AI2)","https://blog.allenai.org/feed"),
    ("EleutherAI Blog",             "https://blog.eleuther.ai/rss/"),
    ("MIRI Blog",                   "https://intelligence.org/blog/feed/"),

    # ── 学術誌 / 論文サービス ──
    ("Nature AI",                   "https://www.nature.com/subjects/artificial-intelligence.rss"),
    ("Science (AAAS) AI",           "https://www.science.org/action/showFeed?type=searchTopic&taxonomyUri=/topic/ai-ml&feed=rss"),
    ("JMLR (Journal of ML Research)", "https://jmlr.org/jmlr.xml"),
    ("Semantic Scholar AI Feed",    "https://api.semanticscholar.org/feed/ai"),
    ("Connected Papers Blog",      "https://www.connectedpapers.com/blog/feed"),
    ("Hugging Face Daily Papers",   "https://huggingface.co/papers/rss"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # セキュリティ・倫理・ガバナンス・政策
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    ("NIST AI",                     "https://www.nist.gov/artificial-intelligence/rss.xml"),
    ("Center for AI Safety",        "https://www.safe.ai/blog/rss.xml"),
    ("Future of Life Institute",    "https://futureoflife.org/feed/"),
    ("Partnership on AI",           "https://partnershiponai.org/feed/"),
    ("AI Now Institute",            "https://ainowinstitute.org/feed"),
    ("EFF (Electronic Frontier Foundation)", "https://www.eff.org/rss/updates.xml"),
    ("Brookings AI",                "https://www.brookings.edu/topic/artificial-intelligence/feed/"),
    ("CSET Georgetown",             "https://cset.georgetown.edu/feed/"),
    ("OECD AI Policy Observatory",  "https://oecd.ai/en/feed"),
    ("UNESCO AI",                   "https://www.unesco.org/en/artificial-intelligence/rss"),
    ("World Economic Forum AI",     "https://www.weforum.org/topics/artificial-intelligence-and-robotics/feed"),
    ("UK AI Safety Institute",      "https://www.aisi.gov.uk/feed"),

    # ── サイバーセキュリティ x AI ──
    ("Krebs on Security",           "https://krebsonsecurity.com/feed/"),
    ("Schneier on Security",        "https://www.schneier.com/feed/atom/"),
    ("Dark Reading AI",             "https://www.darkreading.com/rss.xml"),
    ("The Hacker News",             "https://feeds.feedburner.com/TheHackersNews"),
    ("BleepingComputer",            "https://www.bleepingcomputer.com/feed/"),
    ("Naked Security (Sophos)",     "https://nakedsecurity.sophos.com/feed/"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # プロダクト・ツール系
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    ("OpenAI Cookbook (GitHub)",     "https://github.com/openai/openai-cookbook/releases.atom"),
    ("LlamaIndex Blog",             "https://www.llamaindex.ai/blog/rss.xml"),
    ("Pinecone Blog",               "https://www.pinecone.io/blog/rss.xml"),
    ("Weaviate Blog",               "https://weaviate.io/blog/feed.xml"),
    ("Chroma Blog",                 "https://www.trychroma.com/blog/rss.xml"),
    ("Modal Blog",                  "https://modal.com/blog/feed.xml"),
    ("Cursor Blog",                 "https://www.cursor.com/blog/rss.xml"),
    ("Replit Blog",                 "https://blog.replit.com/feed.xml"),
    ("Notion Blog",                 "https://www.notion.so/blog/feed"),
    ("Figma Blog",                  "https://www.figma.com/blog/feed/"),
    ("Linear Blog",                 "https://linear.app/blog/rss"),
    ("Deno Blog",                   "https://deno.com/blog/rss.xml"),
    ("Bun Blog",                    "https://bun.sh/blog/rss.xml"),
    ("Next.js Blog",                "https://nextjs.org/blog/rss.xml"),
    ("Astro Blog",                  "https://astro.build/rss.xml"),
    ("Tailwind CSS Blog",           "https://tailwindcss.com/feeds/feed.xml"),
    ("Docker Blog",                 "https://www.docker.com/blog/feed/"),
    ("Kubernetes Blog",             "https://kubernetes.io/feed.xml"),
    ("HashiCorp Blog",              "https://www.hashicorp.com/blog/feed.xml"),
    ("GitLab Blog",                 "https://about.gitlab.com/atom.xml"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 半導体・ハードウェア・インフラ
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    ("SemiAnalysis",                "https://www.semianalysis.com/feed"),
    ("Tom's Hardware",              "https://www.tomshardware.com/feeds/all"),
    ("AnandTech",                   "https://www.anandtech.com/rss/"),
    ("EE Times",                    "https://www.eetimes.com/feed/"),
    ("WikiChip Blog",               "https://fuse.wikichip.org/feed/"),
    ("Next Platform",               "https://www.nextplatform.com/feed/"),
    ("Serve The Home",              "https://www.servethehome.com/feed/"),
    ("PC Watch 半導体",              "https://pc.watch.impress.co.jp/data/rss/1.0/pcw/feed.rdf"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ロボティクス・自動運転・エッジAI
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    ("IEEE Spectrum Robotics",      "https://spectrum.ieee.org/feeds/topic/robotics.rss"),
    ("The Robot Report",            "https://www.therobotreport.com/feed/"),
    ("Robotics Business Review",    "https://www.roboticsbusinessreview.com/feed/"),
    ("ROS Discourse",               "https://discourse.ros.org/latest.rss"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ニュースレター・個人ブログ（影響力大）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    # ── Substack / Newsletter ──
    ("The Algorithmic Bridge",      "https://thealgorithmicbridge.substack.com/feed"),
    ("Import AI (Jack Clark)",      "https://importai.substack.com/feed"),
    ("AI Snake Oil",                "https://aisnakeoil.substack.com/feed"),
    ("Interconnects (Nathan Lambert)", "https://www.interconnects.ai/feed"),
    ("Ahead of AI (Sebastian Raschka)", "https://magazine.sebastianraschka.com/feed"),
    ("The Neuron",                  "https://www.theneurondaily.com/feed"),
    ("AI Supremacy",                "https://aisupremacy.substack.com/feed"),
    ("Latent Space",                "https://www.latent.space/feed"),
    ("Last Week in AI",             "https://lastweekin.ai/feed"),
    ("Davis Summarizes Papers",     "https://dblalock.substack.com/feed"),
    ("The Batch (Andrew Ng)",       "https://www.deeplearning.ai/the-batch/feed/"),
    ("Gary Marcus (The Road to AI We Can Trust)", "https://garymarcus.substack.com/feed"),
    ("Noahpinion (Noah Smith)",     "https://www.noahpinion.blog/feed"),
    ("Matt Shumer AI",              "https://mattshumer.substack.com/feed"),
    ("Swyx (Latent Space co-host)", "https://www.swyx.io/rss.xml"),
    ("Semi-Literate (Stefan Jansen)", "https://www.semi-literate.com/feed"),

    # ── 日本語個人・テック著名人 ──
    ("shi3z (清水亮) Blog",          "https://shi3z.hateblo.jp/rss"),
    ("matsumotory Blog",            "https://hb.matsumoto-r.jp/feed"),
    ("mizchi (mizchi's Blog)",       "https://mizchi.dev/feed.xml"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # GitHub Releases (主要AIプロジェクト)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    ("PyTorch Releases",            "https://github.com/pytorch/pytorch/releases.atom"),
    ("TensorFlow Releases",         "https://github.com/tensorflow/tensorflow/releases.atom"),
    ("Transformers (HF) Releases",  "https://github.com/huggingface/transformers/releases.atom"),
    ("LangChain Releases",          "https://github.com/langchain-ai/langchain/releases.atom"),
    ("LlamaIndex Releases",         "https://github.com/run-llama/llama_index/releases.atom"),
    ("vLLM Releases",               "https://github.com/vllm-project/vllm/releases.atom"),
    ("llama.cpp Releases",          "https://github.com/ggerganov/llama.cpp/releases.atom"),
    ("Ollama Releases",             "https://github.com/ollama/ollama/releases.atom"),
    ("OpenAI Python SDK Releases",  "https://github.com/openai/openai-python/releases.atom"),
    ("Anthropic Python SDK Releases","https://github.com/anthropics/anthropic-sdk-python/releases.atom"),
    ("Dify Releases",               "https://github.com/langgenius/dify/releases.atom"),
    ("Open WebUI Releases",         "https://github.com/open-webui/open-webui/releases.atom"),
    ("FastAPI Releases",            "https://github.com/tiangolo/fastapi/releases.atom"),
    ("Next.js Releases",            "https://github.com/vercel/next.js/releases.atom"),
    ("Stable Diffusion WebUI",      "https://github.com/AUTOMATIC1111/stable-diffusion-webui/releases.atom"),
    ("ComfyUI Releases",            "https://github.com/comfyanonymous/ComfyUI/releases.atom"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Reddit (RSS経由)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    ("r/MachineLearning",           "https://www.reddit.com/r/MachineLearning/top/.rss?t=day"),
    ("r/artificial",                "https://www.reddit.com/r/artificial/top/.rss?t=day"),
    ("r/LocalLLaMA",                "https://www.reddit.com/r/LocalLLaMA/top/.rss?t=day"),
    ("r/ChatGPT",                   "https://www.reddit.com/r/ChatGPT/top/.rss?t=day"),
    ("r/ClaudeAI",                  "https://www.reddit.com/r/ClaudeAI/top/.rss?t=day"),
    ("r/singularity",               "https://www.reddit.com/r/singularity/top/.rss?t=day"),
    ("r/StableDiffusion",           "https://www.reddit.com/r/StableDiffusion/top/.rss?t=day"),
    ("r/LangChain",                 "https://www.reddit.com/r/LangChain/top/.rss?t=day"),
    ("r/OpenAI",                    "https://www.reddit.com/r/OpenAI/top/.rss?t=day"),
    ("r/comfyui",                   "https://www.reddit.com/r/comfyui/top/.rss?t=day"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # YouTube (RSS経由)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    ("Two Minute Papers",           "https://www.youtube.com/feeds/videos.xml?channel_id=UCbfYPyITQ-7l4upoX8nvctg"),
    ("Yannic Kilcher",              "https://www.youtube.com/feeds/videos.xml?channel_id=UCZHmQk67mSJgfCCTn7xBfew"),
    ("AI Explained",                "https://www.youtube.com/feeds/videos.xml?channel_id=UCNJ1Ymd5yFuUPtn21xtRbbw"),
    ("Matt Wolfe",                  "https://www.youtube.com/feeds/videos.xml?channel_id=UCJMQhbGsRrpvqyVAKEdCcGA"),
    ("Fireship",                    "https://www.youtube.com/feeds/videos.xml?channel_id=UCsBjURrPoezykLs9EqgamOA"),
    ("3Blue1Brown",                 "https://www.youtube.com/feeds/videos.xml?channel_id=UCYO_jab_esuFRV4b17AJtAw"),
    ("Sentdex",                     "https://www.youtube.com/feeds/videos.xml?channel_id=UCfzlCWGWYyIQ0aLC5w48gBQ"),
    ("Corey Schafer",               "https://www.youtube.com/feeds/videos.xml?channel_id=UCCezIgC97PvUuR4_gbFUs5g"),
    ("NetworkChuck",                "https://www.youtube.com/feeds/videos.xml?channel_id=UC9-y-6csu5WGm29I7JiwpnA"),
    ("Computerphile",               "https://www.youtube.com/feeds/videos.xml?channel_id=UC9-y-6csu5WGm29I7JiwpnA"),
    ("TheAIGRID",                   "https://www.youtube.com/feeds/videos.xml?channel_id=UCJHnlmaSdrFGDJTvUb0I0Mw"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 画像・動画・マルチモーダルAI
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    ("Civitai Blog",                "https://civitai.com/feed"),
    ("Stable Diffusion Art",        "https://stable-diffusion-art.com/feed/"),
    ("Pika Blog",                   "https://pika.art/blog/rss.xml"),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 法務・規制・コンプライアンス（日本）
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    ("経済産業省 AI戦略",            "https://www.meti.go.jp/press/index_rss.xml"),
    ("総務省 情報通信",              "https://www.soumu.go.jp/main_content/rss.xml"),
    ("デジタル庁",                   "https://www.digital.go.jp/feed"),
    ("IPA (情報処理推進機構)",       "https://www.ipa.go.jp/feed/index.rdf"),
    ("JPCERT/CC",                   "https://www.jpcert.or.jp/rss/jpcert-all.rdf"),
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ヘルパー
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_feeds_by_keyword(keyword: str) -> list[tuple[str, str]]:
    """ソース名にキーワードを含むフィードを返す"""
    kw = keyword.lower()
    return [(name, url) for name, url in RSS_FEEDS if kw in name.lower()]


def feed_count() -> int:
    """登録フィード総数"""
    return len(RSS_FEEDS)


if __name__ == "__main__":
    print(f"Total feeds: {feed_count()}")
    # カテゴリ別のざっくり集計
    jp_feeds = [f for f in RSS_FEEDS if any(c > '\u3000' for c in f[0])]
    print(f"  Japanese feeds: {len(jp_feeds)}")
    print(f"  English feeds:  {feed_count() - len(jp_feeds)}")
