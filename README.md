# X Stock Market Data (Japan & US) – 2026-10-12

GrokでX（Twitter）から収集した**日米個別銘柄・株式市場**関連の投稿データセットです。  
他のAI（Claude, GPT, Gemini など）で分析・要約・センチメント分析・**予想精度のレビュー**に使うことを想定しています。

## 他のAI向け引き継ぎ

収集以外のレビュー・評価設計は **[HANDOFF.md](./HANDOFF.md)** を読んでください。  
Grok（収集担当）への作業依頼は **[GROK_HANDOFF.md](./GROK_HANDOFF.md)** にあります。

## データ概要

| カテゴリ | 件数 | 内容 |
|---------|------|------|
| `japanese_stocks` | 6 | 日本個別銘柄の推奨・分析・テクニカル |
| `us_stocks` | 6 | 米国個別銘柄・指数・アナリストコメント |
| `mixed_or_macro` | 2 | 日米横断・マクロ関連 |

**収集日時**: 2026-10-12 23:44 JST  
**ソース**: X 公開投稿（keyword / semantic search）

## ファイル構成

- `HANDOFF.md` … **他AI向け引き継ぎ書（収集以外のレビュー用）**
- `GROK_HANDOFF.md` … Grok 向け作業依頼（候補リスト整理・再取得・Automation の v2 対応）
- `data/stock_posts.json` … 構造化データ
- `data/stock_posts.jsonl` … 1行1投稿
- `candidates/` … 予想精度検証用の候補ユーザーリスト（JP/US 各約50人）
- `predictions/` … 抽出スキーマ（v2）・サンプル予想
- `review/` … 判定ルール・スコア設計・レビュー結果
- `scripts/validate_predictions.py` … 予想レコードのスキーマ検証
- `README.md` … このファイル

## 候補ユーザーリストについて

`candidates/` には定期的に銘柄・投資見解を発信しているアカウントの初期リストがあります。

- **精度ランキングではありません**（検証用候補）
- フォロワーが極端に少ないアカウントは除外
- 流れ: 投稿収集 → 予想抽出 → 事後検証 → スコアリング

## 自動化（収集）

| 対象 | 時刻（JST） |
|------|-------------|
| 日本株候補全員 | 毎日 08:00 |
| 米国株候補全員 | 毎日 22:00 |

## 注意

- 投資助言ではありません。公開投稿のスナップショットです。
- エンゲージメント数値は収集時点のものです。
- 商用利用や再配布時はXの利用規約を確認してください。

---
Collected by Grok · Repo: kenkenkabukawoyosoku/x-stock-market-data-2026-10
