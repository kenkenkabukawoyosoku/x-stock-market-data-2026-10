# Predictions Tracking

候補ユーザーの投稿から「検証可能な予想」を抽出し、後で精度を測るためのフォルダです。

## ファイル

| パス | 内容 | 書く人 |
|---|---|---|
| `schema.md` | 抽出ルールとフィールド定義（v2） | — |
| `prediction.schema.json` | 機械検証用 JSON Schema | — |
| `samples_2026-10-12.json` | 初期サンプル予想（v2 移行済み・未評価） | — |
| `raw/YYYY-MM-DD.jsonl` | 日次の抽出結果（追記のみ） | Grok |
| `rejected/YYYY-MM-DD.jsonl` | 記録しなかった候補と理由 | Grok |
| `deletions.jsonl` | 削除を検知した投稿（`{"id", "post_deleted_at"}`） | Grok |
| `evaluations/YYYY-MM-DD.jsonl` | 評価結果 | 評価側 |
| `archive_v1/` | v1 形式の旧出力（参照のみ） | — |

## 運用フロー

1. **収集** … 候補ユーザーの最新投稿を取得（Grok）
2. **抽出** … `schema.md` の条件を満たす予想だけを `raw/` に追記（Grok）
3. **検証** … `python3 scripts/validate_predictions.py predictions/raw/*.jsonl`
4. **評価** … 期間経過後に `review/evaluation_rules.md` で判定し `evaluations/` に記録
5. **集計** … `review/scoring.md` でユーザー別に集計

## 注意

- 投資助言ではありません（公開時の文言は `review/disclaimer.md`）
- サンプル数が少ない段階ではランキング化しない
- 曖昧な投稿は無理に抽出しない（`rejected/` に理由を残す）
