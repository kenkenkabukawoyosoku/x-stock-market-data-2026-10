# predictions/deletions/ — 削除を検知した投稿（Grok）

Grok が、`predictions/raw/` の `status: "open"` のレコードの元投稿が消えていたときに、回ごとの新しいファイルを作ります（2026-10-17〜）。

- ファイル名: `YYYY-MM-DD_{jp|us}.jsonl`（削除を検知した回だけ。同じ名前があれば `_2` を付ける）
- 1行1件: `{"id": "<レコードの id>", "post_url": "...", "post_deleted_at": "<確認した時刻 ISO8601>"}`
- Claude が該当レコードの `post_deleted_at` に反映する（評価は続ける）。
