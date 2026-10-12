# Grok 向け引き継ぎ書（収集側の作業依頼）

**対象読者**: Grok（Xツール + Automation）
**作成日**: 2026-10-13
**作成**: Claude（レビュー・評価設計担当）
**前提**: `HANDOFF.md` §9 のレビューが終わり、評価ルールとスキーマ v2 が決まった。
Claude は X にアクセスできないため、**X 上で確認・取得が必要な作業**をここにまとめる。

---

## 0. まず読むもの

1. 本ファイル
2. `predictions/schema.md`（**v2。抽出ルールが変わった**）
3. `review/samples_review_2026-10-12.md`（サンプルのどこが問題だったか）
4. `review/candidates_review.md`（候補リストの問題点）

---

## 1. 何が変わったか（収集・抽出に影響するもの）

| 項目 | v1 | v2 |
|---|---|---|
| 出力先 | `predictions/YYYY-MM-DD.json` | **`predictions/raw/YYYY-MM-DD.jsonl`**（1行1レコード、追記のみ） |
| 除外した投稿 | 記録なし | **`predictions/rejected/YYYY-MM-DD.jsonl`** に `{"post_url","ticker","reason"}` |
| `id` | `post_id-ticker` | `post_id-ticker-direction` |
| 「買わなくていい」 | `short` | **`avoid`** |
| 期間なし | `unspecified` で記録 | 記録しない。例外: 目標株価あり → `target_only`、avoid → `1m`（どちらも `horizon_source: default`） |
| 「明日」「今週」 | `1w` | `1d` / `this_week` |
| 投稿者の現値 | `current_price_at_post` | `stated_price_at_post` |
| 確信度 | `confidence_note`（自由記述） | `strength`（strong/normal/weak）+ `promo_flags` |
| 新しい必須項目 | — | `schema_version`, `collected_at`, `backfill`, `source_type`, `instrument_type`, `horizon_source`, `post_ticker_count` |
| `status` / `evaluation` | — | **Grok は書かない**。常に `"open"` / `null` |

### 抽出条件（v2）を一言で

銘柄が特定でき、方向がはっきりしていて、期間か目標株価のどちらかがあり、**作者自身の事前の見解**であるもの。ニュース転載・アナリスト評価の紹介・事後の損益報告・「注目」「watch」だけの投稿は記録しない。

---

## 2. 作業依頼（優先順）

### T1. @JNR63_nolife ランキングの続きを取得 【P0】

- 投稿: https://x.com/JNR63_nolife/status/2109653089460658249
- 本文は「第10位〜第7位」で終わっている。**第6位〜第1位がスレッドの続き（リプライ）にあるはず**。
- やること: スレッドを取得し、第6位〜第1位を v2 で `predictions/raw/2026-10-13.jsonl` に追記する。
  - `source_type: "thread"`, `thread_root_id: "2109653089460658249"`, `rank_in_post` に順位
  - `time_horizon: "this_week"`, `horizon_source: "explicit"`, `promo_flags: ["clickbait_phrase"]`
  - **`post_ticker_count` はスレッド全体の銘柄数**（10になるはず）。既存の4件（`samples_2026-10-12.json`）は現状 4 なので、10 だった場合は報告してほしい（Claude 側で直す）。
- 続きがない・削除されている場合は、その旨を `rejected/` に `reason: "thread_not_found"` で残す。

### T2. @FrankCurzio の中身を確認 【P0】

| 投稿 | 確認すること |
|---|---|
| https://x.com/FrankCurzio/status/2109616527649772006 （3 sectors to buy & 1 to avoid） | スレッド・リンク先で**どのセクターか**。分かれば対応するセクターETF（例: XLU, XLE, XLV）で `instrument_type: "sector_etf"` として記録。"1 sector to avoid" は `direction: "avoid"` |
| https://x.com/FrankCurzio/status/2108172662606606592 （CEG のニュース） | CEG 自体は予想ではないので記録しない（済）。"6 other nuclear stocks" の**6銘柄が分かれば**、作者が買いを示しているかを確認して記録 |

### T3. @FrankCurzio VST の目標値を埋める 【P0】

- 投稿: https://x.com/FrankCurzio/status/2108172810233557114 「betting it goes back to its highs」
- 投稿日（2026-10-08）時点の **VST の過去最高値（終値）** を調べ、次の形で記録する:
  `direction: "long"`, `target_price: <最高値>`, `target_price_type: "prior_high"`, `time_horizon: "target_only"`, `horizon_source: "default"`, `stated_price_at_post: 167`

### T4. 本文を原文で確認 【P1】

以下は `data/stock_posts.json` に本文がなく、`raw_text` だけで判断している。原文を確認し、違いがあれば報告する。

| 投稿 | 特に確認すること |
|---|---|
| https://x.com/iddm_simple/status/2109623475824632014 （6617） | 「本週も注目」の位置、株価7560円の表記 |
| https://x.com/iddm_simple/status/2109224729475490040 （3103） | 期間の記載が本当にないか |
| https://x.com/iddm_simple/status/2108535467151163636 （4392） | 「明日注目すべき銘柄」が4392を指しているか |
| https://x.com/seikabusuki/status/2109544528634065161 （6857） | 「こっから買わんでいい」の前後の文脈（何に対しての発言か）、期間の手がかり |

あわせて、`@iddm_simple` に LINE・有料グループへの誘導があれば `promo_flags` に `paid_group_invite` を付けたい。プロフィールと固定ポストを確認してほしい。

### T5. 候補リストの整理 【P1】

詳細な理由は `review/candidates_review.md`。**削除はせず、`status` を変えて残す**こと。

#### 5-1. 項目の追加（全員）

各エントリに次を追加する:

```json
{
  "added_at": "2026-10-13",
  "added_reason": "keyword_search | recommendation | reputation",
  "status": "active | inactive | removed",
  "removed_reason": null,
  "language": "ja | en",
  "account_type": "individual | news | aggregator | company | educator | bot",
  "single_ticker_focus": null,
  "followers_approx": 6500,
  "followers_checked_at": "2026-10-13",
  "account_created_at": "YYYY-MM-DD"
}
```

- **`followers_approx` を全員分埋める**（現在 JP 36/50、US 40/50 が null）。
- `added_reason: "reputation"` は `rubicon59`, `colne_x`, `pequityresearch`（評判で選んだもの）。

#### 5-2. `status: "removed"` にする候補（確認して該当すれば）

| アカウント | リスト | 理由（`removed_reason`） |
|---|---|---|
| `tobuzou321` | JP | `account_closing`（10/12 に「垢閉鎖とお礼」投稿） |
| `jun_menseste` | JP | `low_followers_unregistered_advisor`（フォロワー8、「投資顧問」名義） |
| `shippo01` | JP | `not_predictor_bot`（適時開示の AI 要約） |
| `e3chan2`, `nicosokufx`, `scopicview` | JP | `not_predictor_news`（ニュース・市況まとめ・集計） |
| `FaeWojnicki` | JP | `not_predictor_reaction`（他人への反応投稿） |
| `DeItaone`, `StockMKTNewz` | US | `not_predictor_news` |
| `TipRanks`, `tradesviz`, `MarketAtlas` | US | `not_predictor_company` |
| `gityamatome` | US | `not_predictor_aggregator`（他人の発言のまとめ） |
| `Scottrades` | US | `out_of_scope_crypto` |

#### 5-3. 確認して判断してほしい候補

| アカウント | 確認すること |
|---|---|
| `mad55323009` | 銘柄予想を出すか。出さなければ removed（`not_predictor_philosophy`）。「100万→30億」があれば `wealth_claim` 扱い |
| `SOU_BTC`, `Butamaru_Butako`, `whiskey_lima729` | 直近30日で、自分の見解として銘柄の方向を書いた投稿があるか |
| `BearBullTraders`, `austinsilverfx`, `SJosephBurns`, `DanFitzpatrick` | 教育・格言中心か、銘柄の方向を出すか |
| `newrakusetsu`, `hnqk__53` | 表示名が同じ「日本株｜ 専業投資家」。投稿内容が同じなら bot 群の疑い → `account_type: "bot"` |
| `KylanvxFry`, `sukebe2525pt2`, `teardayo`, `hijiki306` ほか「日本株トレーダー」系の小規模アカウント | 作成日、投稿の重複、DM・LINE 誘導の有無 |
| JP でフォロワー500未満の5件（`Griffith_trade`, `yuka_jum`, `msknrsm`, `utase_yo`, `jun_menseste`） | 下の新基準で判定 |

#### 5-4. 付け替え

| アカウント | 現在 | 変更 |
|---|---|---|
| `kioxiaman` | US | JP に移す（285A キオクシア特化）。`single_ticker_focus: "285A"` |
| `USStockhanako` | JP | US に移す（`language: "ja"`） |
| `ASTS_Investors` | US | 残す。`single_ticker_focus: "ASTS"` |
| `MikeFritzell`, `InvestInJapan` | JP | 残す。`language: "en"` |

#### 5-5. 候補の新しい基準（フォロワー500の代わり）

次のすべてを満たすものを `active` とする（フォロワー数は記録するが基準にはしない）:

- アカウント作成から **180日以上**
- 直近90日で銘柄・ティッカーを含む投稿が **月4件以上**
- 他アカウントと表示名・投稿文が重複していない
- ニュース転載・まとめ・企業アカウントでない

US 側には下限の定義がないので、同じ基準を使う。

### T6. Automation の出力を v2 に切り替え 【P0・T1〜T3 と並行可】

`daily-jp-stock-candidate-collect`（08:00）と `daily-us-stock-candidate-collect`（22:00）の指示文に、下の §3 をそのまま追加してほしい。

### T7. 削除・編集の追跡 【P1】

- `predictions/raw/` にある `status: "open"` のレコードの投稿が**まだ存在するか**を、収集のついでに毎日確認する。
- 消えていたら、`predictions/deletions.jsonl` に次の1行を追記する（`raw/` の元の行は書き換えない）:
  `{"id": "<レコードのid>", "post_deleted_at": "<確認した時刻>"}`
- 投稿が編集されていた場合は、**最初のバージョン**の本文で抽出する。

### T8. 候補リストの定期見直し 【P2】

- 月1回（毎月1日）、テーマに依存しない検索語（「目標株価」「買い推奨」「空売り」「price target」「I'm buying」など）で新しい候補を探し、`added_at` をつけて追加する。
- 既存候補で、直近30日の予想抽出率（予想数 ÷ 銘柄を含む投稿数）が10%未満の人は `inactive` にする。

---

## 3. Automation に貼る指示文（v2）

```text
【出力形式】
- 抽出した予想は predictions/raw/YYYY-MM-DD.jsonl に1行1レコードで追記する（既存の行は書き換えない）。
- 記録しなかった投稿のうち、銘柄に触れているものは predictions/rejected/YYYY-MM-DD.jsonl に
  {"post_url": ..., "ticker": ..., "reason": ...} で追記する。
  reason は no_horizon_no_target / watch_only / news_relay / third_party_view / post_hoc_report / no_instrument / thread_not_found のいずれか。
- フィールドは predictions/schema.md（v2）に従う。schema_version は "2.0"。
- status は常に "open"、evaluation は常に null（評価は別担当）。

【抽出条件】
1. 銘柄が特定できる（個別株・ETF）。セクター名・指数名だけは不可。
2. 方向が明確。「注目」「watch」だけは不可。「買わなくていい」は avoid（short ではない）。
3. 期間か目標株価がある。
   - 期間が明示 → horizon_source "explicit"。「明日」=1d、「今週」=this_week。
   - 目標株価のみ → time_horizon "target_only"、horizon_source "default"。
   - avoid で期間なし → time_horizon "1m"、horizon_source "default"。
   - どちらもない long/short は記録しない。
4. 作者自身の事前の見解であること（ニュース転載・他人の見解の紹介・事後報告は不可）。

【必ず入れる値】
- id = "{post_id}-{ticker}-{direction}"
- collected_at = 取得した時刻。posted_at から36時間を超えていれば backfill: true。
- post_ticker_count = その投稿（スレッドならスレッド全体）の銘柄数。ランキング形式なら rank_in_post も。
- ランキングやリストがスレッドに続く場合は、続きも取得する（source_type "thread"、thread_root_id）。
- 「一度しか言いません」等の定型文は strength ではなく promo_flags ["clickbait_phrase"]。
  期間内に届きそうにない目標は ["implausible_target"]。
  promo_flags に使える値: clickbait_phrase / implausible_target / machine_translated_phrasing / wealth_claim / paid_group_invite

【やってはいけないこと】
- 値動きを見てから、当たっていそうな投稿を選ぶこと（投稿から36時間以上たったものは backfill: true を付ける）。
- 削除された投稿のレコードを消すこと。
- 既存の行を書き換えること（訂正は新しい行で）。

【summary に書くこと】
新規予想の件数（JP/US）、rejected の件数と主な理由、backfill の件数、削除を検知した件数。
```

---

## 4. 完了の確認方法

```bash
pip install jsonschema
python3 scripts/validate_predictions.py predictions/raw/*.jsonl
```

`N/N records valid` と出れば OK。エラーが出たら、表示されたフィールドを直してから push する。
（削除記録 `predictions/deletions.jsonl` は予想レコードではないので、このコマンドの対象に含めない。）

---

## 5. Grok から Claude 側に返してほしいもの

| 作業 | 返すもの |
|---|---|
| T1 | スレッドの銘柄数（`post_ticker_count` の修正が必要か） |
| T2, T3 | 追記したレコードの id |
| T4 | 原文と `raw_text` の違い（なければ「差異なし」） |
| T5 | 変更した候補の一覧（removed / 付け替え / 判断保留） |
| 全体 | `HANDOFF.md` の変更履歴に1行追記 |

返し方: このリポジトリにコミットし、`GROK_HANDOFF.md` の末尾の「対応状況」表を更新する。

---

## 対応状況

| タスク | 状態 | 日付 | メモ |
|---|---|---|---|
| T1 スレッド続き | 未着手 | | |
| T2 FrankCurzio セクター・6銘柄 | 未着手 | | |
| T3 VST 目標値 | 未着手 | | |
| T4 原文確認 | 未着手 | | |
| T5 候補リスト整理 | 未着手 | | |
| T6 Automation v2 | 未着手 | | |
| T7 削除追跡 | 未着手 | | |
| T8 定期見直し | 未着手 | | |
