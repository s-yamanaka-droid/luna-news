# Now on AIr｜一目で分かるニュース図解

2026-10-13。SNSから来た人が「誰が、何を発表し、何が分かったか」を画像と見出しだけでつかみ、本文で原典と本誌の提案を区別できるようにする。

## 初回の適用：Anthropicの2026年9月の報告

[Anthropicの原典](https://www.anthropic.com/threat-intelligence-report-september-2026)

原典は、2025年12月〜2026年8月に妨害した活動を7領域で報告する。サイバー攻撃・監視・詐欺はそのうち3領域。これらはAnthropicが確認した事例であり、AI悪用全体の発生率ではない。企業内AIの接続権限をどう設計するかは本誌の実務提案として本文後半に置く。

| 場所 | 2秒で分かる情報 | 固有の画像 | 状態 |
|---|---|---|---|
| ホーム | 「AnthropicがAI悪用の事例を公開」「7領域」 | 報告書と3種の証拠を読む場面 | 実装済み |
| 記事本文 | 「サイバー攻撃・監視・詐欺」3例と短い説明 | 3つの場面を横並び／縦並びで描く図 | 実装済み |
| SNS共有 | 「AnthropicがAI悪用を報告」「7領域」 | サーバー・監視カメラ・不審なメッセージの静物 | 実装済み |

ホームの右側に並ぶ2記事も、最初の数語で内容が分かるよう見出しを直した。Googleの研究は「正しいツール操作から学習データを作る」、OpenAIの説明は「完了した仕事が重要」と主体を明示する。画像が情報を足さない場所では、短い見出しと要約だけを使う。

画像生成はCodex組み込み`imagegen`を使用。スタイルは明るい紙色、細い墨線、少量の深い赤。生成画像には正確な文字や数値を描かせず、見出し・カテゴリー・出所はHTMLで組む。図は事例を説明する模式表現であり、実際の報告書・被害者・製品画面を再現しない。

## 次の記事にも適用する編集ルール

1. 見出しに発表主体と変化を入れる。「AIに何を許す？」のような、対象も行動も分からない抽象的な問いを表紙にしない。
2. 図解は記事固有の事実を1件以上見せる。数字・対象・条件は原典で確認し、読めるHTML文字で示す。
3. 原典の事実と本誌の解釈・業務提案を近接しても見た目で区別する。
4. ホーム、本文、SNSで同じ画像を流用しない。画像が内容理解に寄与しない記事はテキストだけで見せる。
5. 390pxの実画面と1200×630の共有画像で、見出しと図の読みやすさを確認する。

## 今回の成果物と確認

- 生成元：`pipeline/newspaper.py`、`docs/news/2026-09-14/articles.json`
- 画像原本：`design/c12-threat-report-home.png`、`design/c12-threat-report-diagram-wide.png`、`design/c12-threat-report-diagram-mobile.png`、`design/c12-threat-report-social-art.png`
- 共有画像の文字組：`design/preview-c12-report-social-card.html`
- 実画面：`design/implemented-c12-home-desktop.png`、`design/implemented-c12-home-mobile.png`、`design/implemented-c12-diagram-desktop.png`、`design/implemented-c12-diagram-mobile.png`、`design/implemented-c12-report-social-card.png`
- 公開前検証：127号の再生成、14テスト成功、PCとスマートフォン390pxで横はみ出しなし、OG画像1200×630。公開・SNS配信・流入効果はそれぞれ別に確認する。
