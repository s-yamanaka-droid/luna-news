# 2026-10-15号の編集結果と公開判断

## 結論

**今回は公開できる記事が0本。** 原典を照合して4本を採用候補にまとめ、本文図解（PC・mobile）とOGは4本分を作成した。ただし、トップ画像を作る唯一の許可経路 `~/Mark6-Work/agents/engine/codex_image.py` が物理Mark 6で動かない。依存する `~/.claude/skills/tekion-slide-generator-v5/scripts/codex_app_server_client.py` がこの端末に存在せず、4本とも `V5NotInstalledError` で停止した（Codex CLIのChatGPTログイン自体は確認済み）。

指示どおり、画像のない記事は号データに入れていない。`docs/` は変更していない（`docs/news/2026-10-15/`・`docs/articles/2026-10-15/`・候補版 `docs/index.html` は作業ツリーから外し、候補原稿は `reports/mark6-news-20261015/candidate-articles.json` に保存した）。10/14号には触れていない。

次回は、v5を正規の手順で配置した後に `reports/mark6-news-20261015/hero-generation-log.json` の4つのプロンプトでトップ画像を生成すれば、残りの作業は「画像の変換・配置 → render → 検査」だけになる。

## 採用候補（4本）と原典確認

確認日は2026-10-15。発表日と本誌の号日付は分けて `published_at`（原典の日付）に記録した。

| 順 | 記事 | 原典（一次） | 確認した事実・修正点 |
|---|---|---|---|
| 1 | Microsoft、AIエージェントの隔離環境「MXC」をWindows 11で一般提供 | Windows Developer Blog（2026-10-07、Logan Iyer署名） | 一般提供の発表日は**10月7日**（候補はPublickeyの掲載日10/15を日付にしていたため修正）。隔離4種（プロセス／セッション＝Win11のみ／WSL＝Win11のみ／MicroVM＝試験的）、ポリシー項目、3つの動作モード（強制・学習・観察、記録はWindowsのプロセスコンテナのみ）を原典の表で確認。**Claude Codeは「対応予定」**で、Publickeyの「対応を発表」は対応済みと誤読されやすいため区別した。Intune管理とEntraによる識別は「近く提供」で今回のGAに含まれない。 |
| 2 | 茨木市とNTT西日本、小中学校で校務AIを実証　国産LLMをオンプレミスで運用 | NTT西日本・茨木市のニュースリリース（2026-10-13） | 開始10月13日、期間は2027年3月31日まで（振り返りを含む）、市立の一部小中学校、tsuzumi 2最新モデル、権限に応じたアクセス制御とローカル運用、評価項目（時間・有用性・操作性・継続利用の意向）、役割分担を確認。「全国初」は**NTT西日本調べ（2026年9月時点）**と明記。対象校の数・効果の数値は原典に記載なし。 |
| 3 | Claude Codeのデスクトップアプリ、複数セッションの並行作業を改善 | gihyo.jp（2026-10-15）＋Claude Code公式ドキュメント（desktop-quickstart / desktop） | ClaudeDevsの案内日10月14日、最近使ったフォルダー・保存した「環境」・フォルダーごとのGit worktree・子セッションの報告・対応待ちの表示をgihyo.jpで確認。対象契約（Pro・Max・Team・Enterprise）、worktree、/btw、作業提案は公式ドキュメントで確認。**XのClaudeDevs投稿そのものは取得できず未確認**と本文に記載。gihyo.jpにある社員の発言はリンク先が別人の投稿だったため不採用。 |
| 4 | 続報：Gemini 4 Argonの安全対策　Googleが3層の防御と監視を公表 | Google公式ブログ（2026-10-13、候補URLのDeepMindからリダイレクト） | 10/14号のArgon記事にない新事実だけで構成し、前号の続報と明記：模擬サイバー攻撃12件すべて（前世代5件）、Frontier Safety Frameworkに基づく防御、3層の防御（入力の審査・activation probes・継続監視）、生物分野のジェイルブレイクで1%未満、近道・不正の試み2%、思考過程を罰した訓練で黙った近道が11.2%→36.4%。前号と重なるIPI 0.7%は使っていない。数値はすべて同社の公表値と明記。 |

原稿は `reports/mark6-news-20261015/reviewed-articles.json`。10/14号と同じ項目（`verified_at`・`article_kind`・`editorial_diagram` の wide/mobile/examples/note/source_url・`social_image`・`hero_image_credit`）を持つ。`hero_image_alt` は画像ができてから記入する（現在は空）。候補にあった `bizapp`・`likes` は10/14号の形式に合わせて外した。

## 不採用（4本）と理由

| 候補 | 理由 |
|---|---|
| 1 Anthropic Japan、導入企業10倍超 | 日経クロステックは有料記事で、読めたのは冒頭のみ。Anthropicの一次発表を探したが見つからなかった。「10倍」の母数・基準日・定義（企業数か売上か）が確認できない。 |
| 6 日立など5社、電力に合わせAI処理を移動 | 発表は**10月8日**（候補はITmediaの掲載日10/15を発表日扱い）。ITmediaは会員限定表示で、日立などの一次リリースは未照合。4本で十分な号になるため保留。 |
| 7 アンソロピック、四半期売上約2.7兆円と報道 | 非公開の投資家向け会合についてBusiness Insiderが報じたもの（初報はFT、有料で未確認）。会社はコメントを控え、売上が総額か純額か、黒字の定義も不明と同記事自身が書いている。報道と確認済み事実を分けても、読者が判断に使える確かな部分がほぼ残らないため不採用。 |
| 8 NTT東日本など5社、光ファイバで道路保全 | DXマガジン（転載的な要約）のみで、NTT東日本の一次リリースを未照合。原典本文でAIの関与がほぼ述べられておらず、AIニュースとしての根拠が弱い。 |

候補5（Argon安全性）は、前号にない新事実が複数あるため続報として採用した（上表）。

## 画像

### トップ画像（4本とも未作成）

`codex_image.generate_image(..., billing="subscription")` を4本で実行し、すべて `V5NotInstalledError` で失敗。APIキー・有料サービス・新しい認証・別の生成経路は使っていない。v5の配置（`~/.claude/skills/` への追加）は利用者の環境設定の変更にあたるため、今回は行っていない。プロンプト（Racco・むちむち猫・アザラシの各記事固有の場面、文字なし、3:2）と失敗の記録は `reports/mark6-news-20261015/hero-generation-log.json`。

### 本文図解とOG（4本分を作成、未配置）

10/14号のC13と同じく、HTMLで組んでPNGに書き出した（system ChromeとPlaywright）。数字・名称はHTMLの文字で原典どおりに組み、生成画像は使っていない。OGの右側は装飾画ではなく、記事の事実（MXCは原典のWebサイト更新の例、校務AIは評価項目、Claude Codeは子セッションの流れ、Argonは5→12件）を組んだ。12枚すべてで枠からのはみ出しがないことを確認した。

| 記事 | 役割 | ファイル（原本） | SHA-256 |
|---|---|---|---|
| MXC | PC図解 2172×724 | design/c14-mxc-diagram-wide.png | eb05a431c50bd52cf5ccc03685893c7b39337799aa319d8dea9a37e0d614ebae |
| MXC | mobile図解 1024×1536 | design/c14-mxc-diagram-mobile.png | 3f44e7502573c7d1ed9e36f46aa1bb9c1d9566a235257baf40af7a7f0933edd8 |
| MXC | OG 1200×630 | design/c14-mxc-social-card.png | ed010a82529b82766c279f1665babf7b31b10a744ccb5a6a425f4db3641c9570 |
| 茨木市 | PC図解 | design/c14-ibaraki-school-ai-diagram-wide.png | fe965872bf568da23e3f530b937abe5c858148f89e2f25b160bf038a16e3ea0d |
| 茨木市 | mobile図解 | design/c14-ibaraki-school-ai-diagram-mobile.png | 5ee633a33c969599d5d5cf998a542f0e24c30860d628caf393e8d9db3acb1f2f |
| 茨木市 | OG | design/c14-ibaraki-school-ai-social-card.png | 0c03c143aeebe629c92c8639665d74cef9400823f4a6acacaf867667b64e6757 |
| Claude Code | PC図解 | design/c14-claude-code-sessions-diagram-wide.png | aa54cceadb0925fc6bcf2f35379741c2af06a60f70c8d638bca6c8af490db47d |
| Claude Code | mobile図解 | design/c14-claude-code-sessions-diagram-mobile.png | 067790ca15ccfb36317903b64396178731fa528073b8f212b1c2b0223acca0d1 |
| Claude Code | OG | design/c14-claude-code-sessions-social-card.png | 486764ca50a3803d67f751a445a34efd3e151c446a908faefafb36e664d37d5c |
| Argon | PC図解 | design/c14-argon-safety-diagram-wide.png | 3644cc0c8a7c03c48c5d69ded12350408a62f170aebde6ec5f2208323e5e7a00 |
| Argon | mobile図解 | design/c14-argon-safety-diagram-mobile.png | b8dd402bde498817f7622155c40daa8d0bd6210bdc6e261ad797559ea0505711 |
| Argon | OG | design/c14-argon-safety-social-card.png | 2120215a64d71aae5bd215510a2fe67e723ec6d63d40f899a329b70f94a14306 |

元のHTML：`design/c14-*-diagram.html`（`?layout=wide` / `?layout=mobile`）、`design/preview-c14-*-social-card.html`。

公開時の配置先と、プレビューで変換したbytes（webpは `scripts/webp_convert.py` と同じ quality 82・method 6、OGはPNGをそのまま）：

| 配置先 | SHA-256 |
|---|---|
| /assets/illustrations/microsoft-mxc-ga-diagram-wide.webp | 0c51de026b52b351ae7a41b9511c926b575b783fefb357798957cd04092e1119 |
| /assets/illustrations/microsoft-mxc-ga-diagram-mobile.webp | 29ce45705f2b38b713a276026635e35e20b4f0b0e9d37b25faf8a28343861bd7 |
| /assets/og/microsoft-mxc-ga.png | ed010a82529b82766c279f1665babf7b31b10a744ccb5a6a425f4db3641c9570 |
| /assets/illustrations/ibaraki-school-ai-trial-diagram-wide.webp | c0dfbdaafcb26ef5da04d547a9a8de543692fb9acccbb405e35379f9cc7199eb |
| /assets/illustrations/ibaraki-school-ai-trial-diagram-mobile.webp | a75e4576033a16ef660144f0bab74405a7e674949c87c7ba0cea7e5b7d97b4c1 |
| /assets/og/ibaraki-school-ai-trial.png | 0c03c143aeebe629c92c8639665d74cef9400823f4a6acacaf867667b64e6757 |
| /assets/illustrations/claude-code-desktop-sessions-diagram-wide.webp | 5d668085d57e7c8cb8b34e0149b36c4a48cee37532702dfd65c88eb874707d33 |
| /assets/illustrations/claude-code-desktop-sessions-diagram-mobile.webp | 521977160549c629d64cd8d4ab3fc3e45bbef1b8ea50dd9a7f64498ed36c4d6c |
| /assets/og/claude-code-desktop-sessions.png | 486764ca50a3803d67f751a445a34efd3e151c446a908faefafb36e664d37d5c |
| /assets/illustrations/gemini-4-argon-safety-diagram-wide.webp | ac8e04cacf27f0411c4b194b811f9bb9b175e51469472943f5bd2a132c0d1089 |
| /assets/illustrations/gemini-4-argon-safety-diagram-mobile.webp | 63cbd0d9436b70537afdd1474fabb81dfa32fad6daaf2a8705b159a9fb83c7c2 |
| /assets/og/gemini-4-argon-safety.png | 2120215a64d71aae5bd215510a2fe67e723ec6d63d40f899a329b70f94a14306 |

## 検査結果

実際の作業ツリー（10/15号なし）：

- `bash scripts/daily.sh --render --date 2026-10-15`：全ページ再生成は成功。続く号検査は `articles:file_missing` で終了コード1（10/15号を入れていないため想定どおり）。再生成で変わったのは `docs/health.json` の確認日だけで、元に戻した。
- `python3 -m unittest discover -s tests -v`：53件成功。
- `git diff --check`：成功。
- `bash scripts/daily.sh --check --date 2026-10-15`：`ok:false`（`articles:file_missing`）。`--date 2026-10-14` は `ok:true`、articles_sha256 `c56f5430…cb53`。

作業場所の外の複製（scratch）に採用候補4本をトップ画像なしで入れたプレビュー：

- `issue_check`：エラーは4本のトップ画像の欠落だけ（PC図解・mobile図解・OGは画像の読込と重複の検査に合格）。
- `check_newspaper.py`：130ページ合格。
- 実ブラウザ（system Chrome、Playwright）：ホームと4記事を1440pxと390pxで確認。全10画面で横はみ出し0、壊れた画像0、コンソールエラー0、サイト内の失敗リクエスト0。390pxでは本文図解が `*-diagram-mobile.webp`、1440pxでは `*-diagram-wide.webp` を表示。各記事の `og:image` は記事ごとのOG（`/assets/og/<slug>.png`）。ホームのトップ見出し→記事1、右欄の1本目→記事2への移動を両方の幅で確認。結果は `reports/mark6-news-20261015/browser-check.json`。

スクリーンショット（トップ画像なしのプレビュー。公開版の見た目ではない）：`reports/mark6-news-20261015/preview-{home,story-1,story-2,story-3,story-4}-{1440,390}.png`

## 未検証・注意点

- トップ画像は4本とも未作成。プレビューのホームにはトップ画像の枠がない。
- ClaudeDevsのX投稿の本文と時刻、PublickeyとITmediaが引用した各社の一次情報のうち今回使っていないもの、FTの売上報道は確認していない。
- Argonの数値、MXCの対応状況は各社の公表内容で、本誌は実機や独自評価で検証していない。
- mobile図解（1024px幅の画像を390px画面で表示）は、MXCとArgonの小さい注記が読みにくい。同じ内容は図の下にHTMLの文字で表示されるが、デザインの確認が必要。
- OGと図解のデザインはC12/C13の紙色・墨線・深赤を継続した。この系統のキービジュアルが以前不評だった記録があるため、トップ画像を含めて最終判断は本人に委ねる。
- 公開・本番確認・既読登録・通知は行っていない。

## 公開に必要なファイル（トップ画像の生成後）

1. `docs/news/2026-10-15/articles.json`（`reviewed-articles.json` に `hero_image_alt` を記入したもの）
2. `docs/assets/illustrations/<slug>-racco.webp` ×4（新規生成）
3. `docs/assets/illustrations/<slug>-diagram-wide.webp` と `-diagram-mobile.webp` ×4本（上記原本から変換）
4. `docs/assets/og/<slug>.png` ×4
5. render後に再生成されるファイル：`docs/index.html`、`docs/news/2026-10-15/index.html`、`docs/articles/2026-10-15/story-1〜4/index.html`、`docs/feed.xml`、`docs/sitemap.xml`、`docs/news-sitemap.xml`、`docs/health.json`、ほか差分が出たページ（`git status` で個別に確認）

slugは `microsoft-mxc-ga`、`ibaraki-school-ai-trial`、`claude-code-desktop-sessions`、`gemini-4-argon-safety`。
