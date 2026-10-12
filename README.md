# X Stock Market Data (Japan & US) – 2026-10-12

GrokでX（Twitter）から収集した**日米個別銘柄・株式市場**関連の投稿データセットです。  
他のAI（Claude, GPT, Gemini など）で分析・要約・センチメント分析などに使うことを想定しています。

## データ概要

| カテゴリ | 件数 | 内容 |
|---------|------|------|
| `japanese_stocks` | 6 | 日本個別銘柄の推奨・分析・テクニカル |
| `us_stocks` | 6 | 米国個別銘柄・指数・アナリストコメント |
| `mixed_or_macro` | 2 | 日米横断・マクロ関連 |

**収集日時**: 2026-10-12 23:44 JST  
**ソース**: X 公開投稿（keyword / semantic search）

## ファイル構成

- `data/stock_posts.json` … 構造化データ（推奨）
- `data/stock_posts.jsonl` … 1行1投稿（LLMパイプライン向け）
- `README.md` … このファイル

## 各投稿のフィールド

```json
{
  "id": "投稿ID",
  "url": "投稿URL",
  "author": { "username", "name", "bio" },
  "created_at": "ISO8601",
  "text": "本文",
  "engagement": { "likes", "reposts", "replies", "views" },
  "tickers_mentioned": ["5803", "NVDA", ...],
  "theme": "短いテーマラベル"
}
```

## 他のAIでの使い方例

1. **センチメント分析**  
   「各投稿のポジティブ/ネガティブ度を0-10で採点し、銘柄別に集計して」

2. **銘柄抽出 & まとめ**  
   「言及されているティッカーを全てリストアップし、ポジティブ言及が多い順に並べて」

3. **テーマクラスタリング**  
   「AI半導体 / 高配当 / バリュー / テクニカル などのテーマで分類して」

4. **投資アイデア抽出**  
   「具体的な買い・売り判断や価格ターゲットが書かれている投稿だけ抽出して」

## 注意

- 投資助言ではありません。公開投稿のスナップショットです。
- エンゲージメント数値は収集時点のものです。
- 商用利用や再配布時はXの利用規約を確認してください。

---
Collected by Grok · Repo: kenkenkabukawoyosoku/x-stock-market-data-2026-10
