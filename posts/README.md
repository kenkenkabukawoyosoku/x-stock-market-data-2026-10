# posts/ — X 投稿スナップショット（Grok が収集）

Grok が X から取得した投稿を、**判断を加えずにそのまま**保存する場所です。
予想の抽出・分類はしません（Claude が `predictions/raw/` に抽出します）。

## ファイル

- `posts/YYYY-MM-DD.jsonl` … 1行1投稿。日付は**収集を実行した日（JST）**。追記のみ。
- 定義: [`post.schema.json`](./post.schema.json)
- 検証: `python3 scripts/validate_posts.py posts/YYYY-MM-DD.jsonl`

## 何を保存するか（Grok の判断を入れない）

- `candidates/*_candidates.json` の `status: "active"` の全員について、前回の収集以降の投稿を**すべて**保存する。
  - 対象: 本人の通常投稿・本人のスレッド（自分へのリプライ）・引用投稿・他人へのリプライ
  - 対象外: 単純なリポスト（リツイート）
- 「予想に見えるか」で選別しない。株と関係ない投稿も入れてよい（抽出側で落とす）。
  選別しないことで、収集段階での後知恵（当たった投稿だけ拾う）を防ぐ。
- 本文は**全文**、編集された投稿は**最初のバージョン**を入れる（`edited: true`）。
- 画像・動画に銘柄名や目標株価が書かれている場合は、その内容を `media_note` に文字で書く。

## フィールド

| フィールド | 必須 | 説明 |
|---|---|---|
| `schema_version` | ✓ | `"1.0"` |
| `post_id` | ✓ | 投稿ID（数字の文字列） |
| `post_url` | ✓ | `https://x.com/{user}/status/{id}` |
| `author` | ✓ | `@username` |
| `posted_at` | ✓ | 投稿時刻（ISO8601） |
| `collected_at` | ✓ | 実際に取得した時刻（`posted_at` より後） |
| `collected_by` | ✓ | 例 `grok-automation/daily-jp` |
| `text` | ✓ | 本文の全文 |
| `post_type` | ✓ | `original \| reply \| quote \| thread` |
| `in_reply_to_id` | ✓ | リプライ先の投稿ID、なければ null |
| `thread_root_id` | ✓ | スレッドの最初の投稿ID、なければ null |
| `quoted_post_id` | ✓ | 引用元の投稿ID、なければ null |
| `quoted_text` | | 引用元の本文 |
| `edited` | ✓ | 編集されていたか |
| `media_note` | | 画像・動画の中の銘柄・数値の書き起こし |
| `link_urls` | | 本文中のリンク |
| `tickers_hint` | | 気づいた銘柄コード（参考。抽出には使わない） |
| `engagement` | | `{likes, reposts, replies, views}`（取得時点） |

## 例

```json
{"schema_version":"1.0","post_id":"2109623475824632014","post_url":"https://x.com/iddm_simple/status/2109623475824632014","author":"@iddm_simple","posted_at":"2026-10-12T12:33:26Z","collected_at":"2026-10-13T08:03:10+09:00","collected_by":"grok-automation/daily-jp","text":"本週も注目したい日本株\n6617 東光高岳：株価7560円 予想価格：8246円","post_type":"original","in_reply_to_id":null,"thread_root_id":null,"quoted_post_id":null,"quoted_text":null,"edited":false,"media_note":null,"link_urls":[],"tickers_hint":["6617"],"engagement":null}
```
