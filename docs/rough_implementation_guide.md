# Never Skip Your Content: データソース自動リストアップ

以下は、ユーザーが指定したキーワード（アーティスト名、バンド名、研究領域など）に基づき、AI エージェントを用いて関連する公式サイト・SNS・RSS・API・ニュースメディア・学会サイトなどのデータソースを自動的に探索・リストアップする仕組みを Markdown 形式でまとめたものです。

---

## 1. 背景とゴール

* **背景**

  * ユーザーは「好きなアーティストのイベント情報」「ライブ先行チケット情報」「論文の新着情報」などを手動で探すのが手間。
  * 手間を省き、見逃したくないコンテンツを逃さずキャッチしたい。

* **暫定ゴール（First Step）**

  * ユーザーが指定したキーワードを AI エージェントに渡すと、その分野に関連性の高いデータソース（公式サイト・SNS・RSS・API・ニュースメディア・学会サイトなど）をリスト化して返す。
  * 出力形式は、テーブルまたは JSON 形式。

---

## 2. 全体アーキテクチャ

```
[ユーザー入力] → [AI エージェント Orchestrator]
  ↳ 検索クエリ生成 → 検索 API → URL一覧取得
  ↳ ページ解析 → メタ情報抽出
  ↳ LLM フィルタリング → ドメイン統合 → 出力
```

1. **ユーザー入力**: キーワード（例: アーティスト名、研究領域）
2. **検索クエリ生成**: LLM で「公式サイト」「ライブ情報」「RSS」などを含むクエリを自動生成
3. **検索 API**: SerpAPI/Bing 等で複数クエリを並列検索し URL を収集
4. **ページ解析**: Playwright/Selenium でメタ情報（title, description, RSSリンク等）を抽出
5. **LLM フィルタリング**: 各 URL を「公式サイト」「ライブ情報ページ」「RSS/API あり」等で判定・スコア化
6. **ドメイン統合**: 同一ドメイン内の複数ページをまとめ、フラグをマージ
7. **最終出力**: JSON もしくは Markdown テーブル形式でユーザーに返却

---

## 3. 各ステップ詳細

### 3.1 検索クエリ自動生成

* **プロンプト例**:

  ```text
  あなたはコンテンツソース発掘アシスタントです。キーワードに基づき、"公式サイト"、"ライブ情報"、"RSS"などを含む検索クエリを 5～8 個生成してください。
  キーワード例: "アーティスト: RADWIMPS"
  ```
* **出力例**:

  ```
  1. "RADWIMPS 公式サイト"
  2. "RADWIMPS ライブ 2025 情報"
  3. "RADWIMPS FANCLUB 先行チケット"
  4. "RADWIMPS RSS フィード"
  ```

### 3.2 検索結果取得 (SerpAPI)

```python
import requests
API_KEY = "YOUR_SERPAPI_KEY"
params = {"engine":"google","q":"RADWIMPS 公式サイト","api_key":API_KEY,"num":10}
response = requests.get("https://serpapi.com/search", params=params)
urls = [item["link"] for item in response.json()["organic_results"]]
```

### 3.3 ページ解析・メタ情報抽出

```javascript
// Playwright 例
title = await page.title()
rssLinks = await page.$$eval('link[type="application/rss+xml"]', els => els.map(e => e.href))
```

### 3.4 LLM によるフィルタリング

```json
[{
  "url":"https://radwimps.jp/",
  "title":"RADWIMPS Official Website",
  "rss_links":["/rss/news.xml"],
  "is_official":true,
  "contains_live_info":true,
  "rss_or_api":true
}, ...]
```

### 3.5 ドメイン統合

* 同一ドメインをキーに、複数ページのフラグをマージ
* 最終例:

  ```json
  [{
    "domain":"radwimps.jp",
    "source_name":"RADWIMPS 公式サイト",
    "features":["ライブ情報あり","RSSあり"]
  }, ...]
  ```

---

## 4. 利用技術スタック例

* **LLM**: OpenAI GPT-4, Azure/AWS LLM, Hugging Face Llama
* **エージェントフレームワーク**: LangChain, Auto-GPT
* **検索 API**: SerpAPI, Bing Search API
* **ブラウザ自動化**: Playwright, Puppeteer
* **HTML パーサー**: BeautifulSoup, lxml, Cheerio
* **バックエンド**: Python + FastAPI / TypeScript + NestJS
* **DB**: PostgreSQL, MongoDB
* **ベクトル検索**: FAISS, Pinecone
* **通知**: AWS SES, Firebase Cloud Messaging
* **CI/CD**: GitHub Actions

---

## 5. 実装ステップ (PoC → API → ダッシュボード)

1. CLI スクリプトで一連パイプラインを実装
2. FastAPI で `/api/v1/sources` エンドポイント化
3. React/Vue ダッシュボードで入力→結果表示 UI を構築
4. ユーザーフィードバックループで精度向上

---

## 6. 注意点・リスク

* **検索 API コスト**: キャッシュ・頻度制御で抑制
* **スクレイピング規約**: robots.txt, リクエスト間隔遵守
* **LLM 誤判定**: スコア閾値調整、HITL の導入
* **プライバシー**: メタ情報のみ扱い、利用規約遵守

---

*以上が「データソース自動リストアップ」機能を Markdown にまとめた内容です。必要に応じて調整してください。*
