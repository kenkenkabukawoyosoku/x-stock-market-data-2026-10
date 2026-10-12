# 予想抽出スキーマ v2（Prediction Extraction Schema）

検証可能な予想だけを構造化するための定義です。**v2（2026-10-13 採用）**。

- 機械検証用の定義: [`prediction.schema.json`](./prediction.schema.json)（JSON Schema 2020-12）
- 検証コマンド: `python3 scripts/validate_predictions.py predictions/raw/*.jsonl`
- 変更理由・詳しい背景: [`review/schema_v2_proposal.md`](../review/schema_v2_proposal.md)
- 判定ルール: [`review/evaluation_rules.md`](../review/evaluation_rules.md) ／ スコア: [`review/scoring.md`](../review/scoring.md)

v1 からの主な変更: `direction` に `avoid` を追加、`time_horizon` から `unspecified` を削除して `1d` / `this_week` / `6m` / `1y` / `target_only` を追加、`status` の `expired` を廃止して `flat` / `void` を追加、`current_price_at_post` を `stated_price_at_post` に改名、`confidence_note` を `strength` + `promo_flags` に置き換え。

---

## 1. 抽出条件（すべて満たすものだけ記録）

1. **銘柄が特定できる** … 個別株か ETF のティッカー／明確な社名。セクター名・指数名だけのものは記録しない（ETF に置き換えられる場合は `instrument_type: sector_etf` で可）。
2. **方向が明確** … 買い／売り／上昇期待／下落警戒／買わなくていい。「注目」「watch」だけは不可。目標株価が現値と違えば、その向きを方向とみなす。
3. **時間軸がある** … 次のどれか。
   - 期間が書かれている（`horizon_source: explicit`）
   - 文脈から期間が明確に読める（`inferred`。根拠を `horizon_raw_text` に入れる）
   - 目標株価はあるが期間がない → `time_horizon: target_only`, `horizon_source: default`
   - `avoid` で期間がない → `time_horizon: 1m`, `horizon_source: default`
   - 上のどれにも当たらない（方向だけで期間も目標もない long/short）→ **記録しない**
4. **作者自身の見解** … ニュース、アナリスト評価、他人の発言の転載・まとめは記録しない。
5. **事前の予想** … 「〜で利益が出た」などの事後報告は記録しない。

迷ったら記録せず、`predictions/rejected/` に理由つきで残す。

---

## 2. フィールド

| フィールド | 必須 | 値 | 説明 |
|---|---|---|---|
| `schema_version` | ✓ | `"2.0"` | |
| `id` | ✓ | `{post_id}-{ticker}-{direction}` | 例 `2109623475824632014-6617-long` |
| `post_id` | ✓ | 数字の文字列 | |
| `post_url` | ✓ | `https://x.com/{user}/status/{id}` | |
| `author` | ✓ | `@username` | |
| `posted_at` | ✓ | ISO8601 | |
| `collected_at` | ✓ | ISO8601 | Grok が投稿を取得した時刻 |
| `extracted_by` | | 文字列 | 例 `grok-automation/daily-jp@2026-10-13` |
| `backfill` | ✓ | bool | `collected_at − posted_at > 36時間` なら true |
| `source_type` | ✓ | `original \| quote \| reply \| thread` | thread = スレッドの2投稿目以降 |
| `thread_root_id` | | 文字列 \| null | |
| `ticker` | ✓ | `5803` / `285A` / `NVDA` | JP は4桁コード |
| `market` | ✓ | `JP \| US` | |
| `instrument_type` | ✓ | `stock \| etf \| sector_etf` | |
| `direction` | ✓ | `long \| short \| avoid \| neutral` | 「買わなくていい」「様子見」は `avoid`（short ではない） |
| `entry_condition` | | 文字列 \| null | 例 `close <= 60` |
| `target_price` | ✓ | 数値 \| null | `target_only` のときは必須 |
| `target_price_type` | | `point \| lower_bound \| upper_bound \| prior_high` | 「4桁」= lower_bound 1000 |
| `stop_price` | | 数値 \| null | |
| `stated_price_at_post` | ✓ | 数値 \| null | **投稿者が書いた**現在値。評価には使わない |
| `time_horizon` | ✓ | `1d \| this_week \| 1w \| 2w \| 1m \| 3m \| 6m \| 1y \| earnings \| target_only` | 「明日」=1d、「今週」=this_week |
| `horizon_source` | ✓ | `explicit \| inferred \| default` | |
| `horizon_raw_text` | | 文字列 \| null | 時間軸の根拠になった原文 |
| `post_ticker_count` | ✓ | 整数 ≥1 | 同じ投稿（スレッドならスレッド全体）の銘柄数 |
| `rank_in_post` | | 整数 \| null | ランキング形式の順位 |
| `raw_text` | ✓ | 文字列 | 予想部分の原文 |
| `strength` | | `strong \| normal \| weak` | |
| `promo_flags` | | 文字列の配列 | §3 |
| `reiterations` | | 整数 | 同じ予想の再投稿回数。再投稿は新規レコードにしない |
| `post_deleted_at` | | ISO8601 \| null | 削除されても評価は続ける |
| `status` | ✓ | `open \| hit \| miss \| flat \| void` | 抽出時は常に `open` |
| `evaluation` | | object \| null | **評価側だけが書く**。中身は `review/schema_v2_proposal.md` §2.3 |
| `notes` | | 文字列 | |

### 担当の分け方

- **収集・抽出側（Grok）が書く**: `status` / `evaluation` 以外のすべて。`status` は常に `"open"`、`evaluation` は `null`。
- **評価側が書く**: `status`, `evaluation`。

---

## 3. promo_flags の語彙

| 値 | 付ける条件 |
|---|---|
| `clickbait_phrase` | 「一度しか言いません」「一度だけ言っておく」「保存推奨」など勧誘系の定型文 |
| `implausible_target` | 期間内に届かない目標（日本株の値幅制限を超える1日目標、1週間で+50%超など） |
| `machine_translated_phrasing` | 「本週」など機械翻訳とみられる表記 |
| `wealth_claim` | 「100万→30億」など資産額の誇示 |
| `paid_group_invite` | LINE・有料グループ・DM への誘導 |

---

## 4. ファイルの置き場所

| パス | 内容 | 書く人 |
|---|---|---|
| `predictions/raw/YYYY-MM-DD.jsonl` | 抽出結果。1行1レコード、**追記のみ** | Grok |
| `predictions/rejected/YYYY-MM-DD.jsonl` | 記録しなかった候補と理由（`{"post_url", "ticker", "reason"}`） | Grok |
| `predictions/deletions.jsonl` | 削除を検知した投稿 `{"id", "post_deleted_at"}` | Grok |
| `predictions/evaluations/YYYY-MM-DD.jsonl` | 評価結果（`id` で紐付け） | 評価側 |
| `predictions/samples_2026-10-12.json` | 初期サンプル（v2 に移行済み） | — |

---

## 5. スコアリング

`review/scoring.md` を参照。要約: 超過リターンをボラティリティで割った z の加重平均を、件数で縮小した Skill Score が主指標。旧案（方向一致 +1 / 目標到達 +1 / 大外れ −0.5）は廃止。
