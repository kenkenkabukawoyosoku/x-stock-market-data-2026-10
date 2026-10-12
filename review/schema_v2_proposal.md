# スキーマ改訂案 v2（P1-5）

> **採用済み（2026-10-13）**。最新の定義は [`predictions/schema.md`](../predictions/schema.md)。採用時に「期間なしの avoid は既定 1m」「promo_flags は語彙を固定」を追加した。

対象: `predictions/schema.md`（v1）。機械検証用の定義は [`predictions/prediction.schema.json`](../predictions/prediction.schema.json)（JSON Schema 2020-12）。
適用する場合は HANDOFF §12 のとおり、`predictions/schema.md` と HANDOFF.md を先に更新すること。

---

## 1. 抽出条件の改訂

| v1 | v2 |
|---|---|
| 1. 銘柄が特定できる | 同じ。**個別株・ETF のみ**。セクター名だけ・指数名だけは対象外（ETF に置き換えられる場合のみ可） |
| 2. 方向が明確 | 同じ。ただし「注目」「watch」だけは不可（v1と同じ）。**目標株価が現値と異なれば方向ありとみなす** |
| 3. 時間軸が読み取れる | **「明示」か「目標株価あり」のどちらか。** 目標株価だけで期間がない場合は `target_only`（63営業日で打ち切り）。どちらもない場合は記録しない |
| — | 4. **作者自身の見解であること**（ニュース・アナリスト評価・他人の発言の転載は除外） |
| — | 5. **事前の予想であること**（「〜で利益が出た」のような事後報告は除外） |

---

## 2. フィールドの変更一覧

### 2.1 追加

| フィールド | 型 | 理由 |
|---|---|---|
| `schema_version` | `"2.0"` | 混在したときに読み分けるため |
| `collected_at` | ISO8601 | 収集ラグの計測、後知恵の防止 |
| `extracted_by` | string | 抽出したモデル・プロンプトのバージョン |
| `backfill` | bool | 投稿から36時間超で収集したもの |
| `source_type` | `original \| quote \| reply \| thread` | 転載との区別、スレッドの取りこぼし確認 |
| `thread_root_id` | string \| null | ランキング形式の続き投稿を紐付ける |
| `instrument_type` | `stock \| etf \| sector_etf` | SECTOR のような評価不能な値をなくす |
| `entry_condition` | string \| null | 「60円以下なら買い」など条件付き予想 |
| `target_price_type` | `point \| lower_bound \| upper_bound \| prior_high` | 「4桁」「高値回帰」を表せるように |
| `stop_price` | number \| null | 損切りラインが書かれている場合 |
| `horizon_source` | `explicit \| inferred \| default` | 推測で埋めた時間軸を区別（重みに使う） |
| `horizon_raw_text` | string \| null | 時間軸の根拠となった原文 |
| `post_ticker_count` | int | 1投稿あたりの銘柄数（重み 1/n） |
| `rank_in_post` | int \| null | ランキング形式の順位 |
| `strength` | `strong \| normal \| weak` | v1 の `confidence_note` を集計できる形に |
| `promo_flags` | string[] | `clickbait_phrase`, `implausible_target`, `machine_translated_phrasing` など |
| `reiterations` | int | 同じ予想の再投稿回数（新規レコードにしない） |
| `post_deleted_at` | ISO8601 \| null | 削除されても評価は続ける |
| `evaluation` | object \| null | 評価結果をまとめる（§2.3） |

### 2.2 変更

| v1 | v2 | 理由 |
|---|---|---|
| `direction: long \| short \| neutral` | `long \| short \| avoid \| neutral` | 「買わなくていい」は short ではない |
| `time_horizon: 1w \| 2w \| 1m \| 3m \| earnings \| unspecified` | `1d \| this_week \| 1w \| 2w \| 1m \| 3m \| 6m \| 1y \| earnings \| target_only` | 「明日」「今週」「長期」を表せない。`unspecified` は記録しない |
| `current_price_at_post` | `stated_price_at_post` | 投稿者が書いた値であることを明確に。実際のエントリー価格は `evaluation.entry_price` |
| `status: open \| hit \| miss \| expired` | `open \| hit \| miss \| flat \| void` | `expired` の意味が曖昧（`evaluation_rules.md` §4） |
| `id: post_id-ticker` | `post_id-ticker-direction` | 1投稿で同じ銘柄の long と short（例: ペアトレード）を区別 |

### 2.3 `evaluation` オブジェクト（評価時に埋める）

```json
{
  "evaluated_at": "2026-10-16T16:00:00+09:00",
  "entry_date": "2026-10-13",
  "entry_price": 7480,
  "exit_date": "2026-10-16",
  "exit_price": 7920,
  "price_mismatch": false,
  "benchmark": "1306.T",
  "return_pct": 5.88,
  "benchmark_return_pct": 1.10,
  "excess_return_pct": 4.78,
  "sigma_h_pct": 6.2,
  "z_score": 0.77,
  "theta_pct": 1.55,
  "target_reached": false,
  "target_reached_at": null,
  "target_touched_intraday": true,
  "progress": 0.57,
  "max_favorable_pct": 7.1,
  "max_adverse_pct": -1.8,
  "void_reason": null,
  "corporate_action": null,
  "price_source": "yfinance",
  "price_snapshot": "prices/2026-10-16.parquet"
}
```

v1 の `evaluated_at` / `actual_move_pct` はこのオブジェクトに移す（`actual_move_pct` は絶対リターンか超過リターンか曖昧だったため、両方を別の名前で持つ）。

### 2.4 削除

| フィールド | 理由 |
|---|---|
| `confidence_note`（自由記述） | `strength` + `promo_flags` に置き換え。自由記述は `notes` へ |

---

## 3. ファイル運用

- 1日1ファイル `predictions/YYYY-MM-DD.json` は、**評価で status を書き換えるとき差分が追いにくい**。次を推奨:
  - `predictions/raw/YYYY-MM-DD.jsonl` … 抽出結果（追記のみ、書き換えない）
  - `predictions/evaluations/YYYY-MM-DD.jsonl` … 評価結果（`id` で紐付け）
- 抽出（Grok）と評価（別プロセス）が同じファイルを書き換えないようにすると、責任範囲（HANDOFF §2）とも一致する。
- 追記前に `predictions/prediction.schema.json` で検証し、通らないレコードは `predictions/rejected/` に理由つきで退避する。
