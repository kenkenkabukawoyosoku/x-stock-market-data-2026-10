# X Stock Market Data (Japan & US) – 2026-10-12

GrokでX（Twitter）から収集した**日米個別銘柄・株式市場**関連の投稿データセットです。  
他のAI（Claude, GPT, Gemini など）で分析・要約・センチメント分析・**予想精度のレビュー**に使うことを想定しています。

## 引き継ぎ文書

| ファイル | 対象 |
|----------|------|
| **[GROK_HANDOFF.md](./GROK_HANDOFF.md)** | Grok（X 上の作業：投稿収集・アカウント確認・削除確認） |
| **[CLAUDE.md](./CLAUDE.md)** | Claude（メイン：抽出・候補リスト・評価・文書） |
| **[HANDOFF.md](./HANDOFF.md)** | 他のAI（評価設計・レビュー） |
| **[CHANGELOG.md](./CHANGELOG.md)** | Claude の作業ログと申し送り（Claude だけが書く） |
| [logs/grok/](./logs/grok/) | Grok の作業記録（回ごとの新しいファイル） |

## データ概要

| カテゴリ | 件数 | 内容 |
|---------|------|------|
| `japanese_stocks` | 6 | 日本個別銘柄の推奨・分析・テクニカル |
| `us_stocks` | 6 | 米国個別銘柄・指数・アナリストコメント |
| `mixed_or_macro` | 2 | 日米横断・マクロ関連 |

**収集日時**: 2026-10-12 23:44 JST  
**ソース**: X 公開投稿（keyword / semantic search）

## ファイル構成

- `GROK_HANDOFF.md` … **Grok向け収集手順と作業依頼**
- `CLAUDE.md` … Claude向け作業手順
- `posts/` … Grok が収集した投稿スナップショット（選別なし）
- `HANDOFF.md` … 他AI向け評価・レビュー
- `data/` … 初期スナップショット
- `candidates/` … 候補ユーザー（JP/US 各約50人）
- `predictions/` … 抽出スキーマ（v2）・日次予想（`raw/`）
- `review/` … 判定ルール・スコア設計・レビュー結果
- `scripts/validate_*.py` … 予想・投稿・アカウント情報のスキーマ検証
- `README.md` … このファイル

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
