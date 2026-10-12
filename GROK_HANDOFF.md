# GROK_HANDOFF.md — 収集側引き継ぎ書（Grok専用）

**対象**: Grok（本会話・Automation・将来のGrokセッション）
**作成日**: 2026-10-13（Grok 版と Claude 版を同日に統合）
**リポジトリ**: https://github.com/kenkenkabukawoyosoku/x-stock-market-data-2026-10
**対になる文書**: [HANDOFF.md](./HANDOFF.md)（他AI向け・評価・レビュー）

> **作業を始める前に必ず [CHANGELOG.md](./CHANGELOG.md) の新しいエントリを読み、終わったらエントリを追加すること**（Claude との相互引き継ぎ。ルールは CHANGELOG.md 冒頭）。
>
> **最初に §3 を読むこと。** 2026-10-13 に抽出ルールと出力形式が v2 に変わった。
> 08:00 の JP Automation 出力（v1 形式）は Claude が v2 に変換済み（§3.3）。**次回の実行から Automation の指示文を §4.2 に差し替える**必要がある。

---

## 1. Grokの役割（境界）

| やる | やらない |
|------|----------|
| X投稿の収集 | 的中の判定（`status` / `evaluation` は書かない。常に `"open"` / `null`） |
| 検証可能な予想の一次抽出 | 投資助言・「この人が最強」断定 |
| candidates / predictions の更新 | schemaの独断変更（変更時は HANDOFF と同期） |
| GitHubへの保存 | 他AI向け評価レポートの本書き |
| 日次Automationの維持 | 価格APIの選定・バックテスト実装 |

**原則**: Grokに固有なのは **Xネイティブ収集 + 定期実行**。抽出ルールは `predictions/schema.md`（v2）が唯一の正。

---

## 2. リポジトリと成果物

```
x-stock-market-data-2026-10/
├── CHANGELOG.md             ← ★作業ログ・相互引き継ぎ（毎回読む・書く）
├── GROK_HANDOFF.md          ← 本ファイル（収集手順・作業依頼）
├── HANDOFF.md               ← 他AI向け
├── README.md
├── candidates/
│   ├── jp_candidates.json
│   └── us_candidates.json
├── predictions/
│   ├── schema.md            ← 抽出の唯一の正（v2）
│   ├── prediction.schema.json ← 機械検証用
│   ├── raw/YYYY-MM-DD.jsonl ← ★日次収集の出力先（1行1予想・追記のみ）
│   ├── rejected/YYYY-MM-DD.jsonl ← 記録しなかった投稿と理由
│   ├── deletions.jsonl      ← 削除を検知した投稿
│   ├── evaluations/         ← 評価側が書く（Grokは触らない）
│   ├── archive_v1/          ← v1 形式の旧出力（参照のみ）
│   └── samples_2026-10-12.json
├── review/                  ← 判定ルール・スコア設計（他AI）
├── scripts/validate_predictions.py
└── data/                    ← 初期スナップショット（参考）
```

**日次出力のファイル名**: JP と US は同じ `predictions/raw/YYYY-MM-DD.jsonl` に追記する（各行に `market` があるので分けなくてよい）。
日付は **収集を実行した日（JST）**。

---

## 3. 2026-10-13 に変わったこと（v1 → v2）

### 3.1 変更点

| 項目 | v1 | v2 |
|---|---|---|
| 出力先 | `predictions/YYYY-MM-DD.json`（日ごとの JSON オブジェクト） | **`predictions/raw/YYYY-MM-DD.jsonl`**（1行1レコード、追記のみ） |
| 除外した投稿 | 記録なし | **`predictions/rejected/YYYY-MM-DD.jsonl`** に `{"post_url","ticker","reason"}` |
| summary | JSON 内の `summary` | Automation の返答（会話）に書く。ファイルには入れない |
| `id` | 任意 | **`{post_id}-{ticker}-{direction}`（必須）** |
| `post_url`, `posted_at` | 任意 | **必須** |
| 「買わなくていい」 | `short` | **`avoid`** |
| 期間なし | `unspecified` で記録 | **記録しない**。例外: 目標株価あり → `target_only`、avoid → `1m`（どちらも `horizon_source: "default"`） |
| 「明日」「今週」「長期」 | `1w` / `3m` など | `1d` / `this_week` / `1y`（期間は**本文に根拠があるものだけ**） |
| 投稿者の現値 | `current_price_at_post` | `stated_price_at_post` |
| 確信度 | `confidence_note`（自由記述） | `strength`（strong/normal/weak）+ `promo_flags` |
| 新しい必須項目 | — | `schema_version`, `collected_at`, `backfill`, `source_type`, `instrument_type`, `horizon_source`, `post_ticker_count` |

### 3.2 抽出条件を一言で

銘柄が特定でき、方向がはっきりしていて、**期間か目標株価のどちらか**があり、**作者自身の事前の見解**であるもの。
ニュース転載・アナリスト評価の紹介・事後の損益報告・「注目」「watch」だけの投稿は記録しない。

### 3.3 2026-10-13 08:00 の JP 出力の変換結果

v1 の `predictions/2026-10-13.json`（4件）は `predictions/archive_v1/` に移し、v2 に変換した。

| 投稿 | v1 | v2 での扱い | 理由 |
|---|---|---|---|
| @tomorotenn 3103 | long / unspecified / 目標1895 | **採用** `target_only`, strength weak | 目標株価があるので期間なしでも可 |
| @SERIKURA 6857 | long / earnings | **除外**（`rejected/`） | 本文の「ASML、TSMCの材料」は他社の話で、当該銘柄の決算までという根拠ではない。期間も目標もない |
| @SERIKURA 6920 | long / earnings | **除外** | 同上 |
| @kei_toshi__ 8306 | long / 3m | **採用** `1y`（inferred） | 本文は「長期的にみたら」。3m の根拠はない |

`posted_at` は v1 出力になかったため、投稿 ID（Snowflake）から算出した。**v2 では `posted_at` を必ず投稿から取得して入れること。**

---

## 4. 自動化（稼働中）

| 名前 | task 概要 | 時刻（Asia/Tokyo） | 対象 |
|------|-----------|-------------------|------|
| `daily-jp-stock-candidate-collect` | 日本株候補全員の直近投稿収集→予想抽出 | **08:00** | `jp_candidates` の `status: active` |
| `daily-us-stock-candidate-collect` | 米国株候補全員の直近投稿収集→予想抽出 | **22:00** | `us_candidates` の `status: active` |

### 4.1 Automation の流れ

0. `CHANGELOG.md` の Claude からの申し送り（`→ Grok`）を確認する
1. `from:username` で候補全員（または実用上の優先サブセット）の直近24時間を収集
2. スレッド・ランキング形式は続きも取得（`x_thread_fetch`）
3. §4.2 の条件で抽出し、`predictions/raw/YYYY-MM-DD.jsonl` に追記、除外分を `rejected/` に追記
4. 前日までの `status: open` の投稿が消えていないか確認し、消えていれば `deletions.jsonl` に追記
5. `CHANGELOG.md` の一番上にエントリを追加する（同じコミットで）
6. 会話に summary を返す
7. 投資助言ではない旨を守る

### 4.2 Automation に貼る指示文（v2・両 Automation 共通）

**現在のプロンプトの「出力JSON」「schema必須3条件」の部分をこれに差し替える。** 候補一覧（プロンプトにハードコードされている部分）はそのまま残す。

```text
【出力形式】
- 抽出した予想は predictions/raw/YYYY-MM-DD.jsonl（YYYY-MM-DD は実行日 JST）に1行1レコードで追記する。既存の行は書き換えない。
- 記録しなかった投稿のうち、銘柄に触れているものは predictions/rejected/YYYY-MM-DD.jsonl に
  {"post_url": ..., "ticker": ..., "reason": ...} で追記する。
  reason は no_horizon_no_target / watch_only / news_relay / third_party_view / post_hoc_report / no_instrument / thread_not_found のいずれか。
- フィールドは predictions/schema.md（v2）に従う。schema_version は "2.0"。
- status は常に "open"、evaluation は常に null（評価は別担当）。
- summary はファイルに入れず、返答に書く。

【抽出条件】
1. 銘柄が特定できる（個別株・ETF）。セクター名・指数名だけは不可。
2. 方向が明確。「注目」「watch」だけは不可。「買わなくていい」は avoid（short ではない）。
3. 期間か目標株価がある。
   - 期間が明示 → horizon_source "explicit"。「明日」=1d、「今週」=this_week。
   - 文脈から期間が明確 → horizon_source "inferred"、根拠の原文を horizon_raw_text に。「長期」=1y。
   - 目標株価のみ → time_horizon "target_only"、horizon_source "default"。
   - avoid で期間なし → time_horizon "1m"、horizon_source "default"。
   - どれもない long/short は記録しない（rejected に no_horizon_no_target）。
   - 本文に根拠のない期間を推測で入れない。
4. 作者自身の事前の見解であること（ニュース転載・他人の見解の紹介・事後報告は不可）。

【必ず入れる値】
- id = "{post_id}-{ticker}-{direction}"
- post_url, posted_at（投稿の時刻）, collected_at（取得した時刻。posted_at より後）
- backfill = collected_at − posted_at が36時間を超えていれば true
- source_type = original / quote / reply / thread
- post_ticker_count = その投稿（スレッドならスレッド全体）の銘柄数。ランキング形式なら rank_in_post も。
- 「一度しか言いません」等の定型文は strength ではなく promo_flags ["clickbait_phrase"]。
  期間内に届きそうにない目標は ["implausible_target"]。
  promo_flags に使える値: clickbait_phrase / implausible_target / machine_translated_phrasing / wealth_claim / paid_group_invite

【やってはいけないこと】
- 値動きを見てから、当たっていそうな投稿を選ぶこと（36時間以上前の投稿は backfill: true）。
- 削除された投稿のレコードを消すこと。
- 既存の行を書き換えること（訂正は新しい行で）。

【作業ログ（CHANGELOG.md）】
- 実行の最初に CHANGELOG.md を読み、Claude からの申し送り（「→ Grok」で始まる行）で未対応のものを確認する。
  対応できるものは対応し、できないものは理由を書く。
- 実行の最後に、CHANGELOG.md の「ログ（新しい順）」の一番上に、冒頭のテンプレートでエントリを1つ追加する。
  予想0件でも書く。予想を追記したファイルと同じコミットに入れる。
- エントリに書いたファイルが実際に変更されているか確認してからコミットする。

【返答の summary に書くこと】
新規予想の件数（JP/US）、rejected の件数と主な理由、backfill の件数、削除を検知した件数、気になった傾向（2〜3文）。
```

### 4.3 1行の例

```json
{"schema_version":"2.0","id":"2109623475824632014-6617-long","post_id":"2109623475824632014","post_url":"https://x.com/iddm_simple/status/2109623475824632014","author":"@iddm_simple","posted_at":"2026-10-12T12:33:26Z","collected_at":"2026-10-13T00:07:00+09:00","backfill":false,"source_type":"original","thread_root_id":null,"ticker":"6617","market":"JP","instrument_type":"stock","direction":"long","entry_condition":null,"target_price":8246,"target_price_type":"point","stop_price":null,"stated_price_at_post":7560,"time_horizon":"this_week","horizon_source":"explicit","horizon_raw_text":"本週も注目","post_ticker_count":1,"rank_in_post":null,"raw_text":"6617 東光高岳：株価7560円 予想価格：8246円","strength":"normal","promo_flags":["machine_translated_phrasing"],"reiterations":0,"post_deleted_at":null,"status":"open","evaluation":null,"notes":""}
```

---

## 5. 収集手順（手動・単発）

### 5.1 ツール
- `x_keyword_search` … `from:user` + キーワード、`mode: Latest`
- `x_semantic_search` … テーマ横断の補助
- `x_thread_fetch` … スレッド内の具体銘柄確認（**ランキング形式は必ず続きまで**）
- GitHub connected tools … `push_files` / `create_or_update_file`

### 5.2 日本株（例）
```
from:USERNAME (株 OR 銘柄 OR 買い OR 売り OR 予想 OR 目標)
```
`limit` は状況に応じて。候補が多い場合はアクティブな発信者を優先しつつ、リスト全員を可能な範囲で回す。

### 5.3 米国株（例）
```
from:USERNAME (stock OR buy OR sell OR "$TICKER" OR target OR bullish OR bearish)
```

### 5.4 抽出判定の例（v2）

| 投稿 | 判定 |
|---|---|
| 「6617 東光高岳 現7560 予想8246」+「本週」 | 採用: long, this_week, 目標8246 |
| 「3103 ユニチカ 現1454 予想1863」（期間なし） | 採用: long, target_only |
| 「アドバンはこっから買わなくていい」 | 採用: **avoid**, 1m（default） |
| 「$VST 高値回帰に賭ける」 | 採用: long, target_only, target_price_type prior_high（**過去最高値の数値を入れる**） |
| 「明日注目すべき銘柄 4392 現860 予想1248」 | 採用: long, 1d, promo_flags implausible_target |
| 「今買うべき日本株 AGC 4,900円前後」（期間・目標なし） | 除外: no_horizon_no_target |
| 「注目」「おもしろそう」「相場厳しい」 | 除外 |
| 「Google が CEG と契約」などニュースの紹介 | 除外: news_relay |
| 「Goldman が強気に転換」 | 除外: third_party_view |

### 5.5 保存
1. v2 で JSONL 化し、`predictions/raw/` に追記
2. 可能なら検証: `python3 scripts/validate_predictions.py predictions/raw/YYYY-MM-DD.jsonl`
3. コミット（message例: `Add JP predictions YYYY-MM-DD`）
4. README / HANDOFF の日付には触れない（収集ログは predictions 側）

---

## 6. 候補リストのメンテ

- 正本: `candidates/jp_candidates.json`, `candidates/us_candidates.json`
- 精度ランキングではない。検証用プール
- リスト変更時は **Automationプロンプト内の候補一覧も更新**すること（プロンプトにハードコードされている）
- **削除はしない**。外すときは `status: "removed"` と `removed_reason` を付けて残す
- 評価は**候補に追加した日（`added_at`）より後の投稿だけ**を数えるので、`added_at` は必ず入れる
- 選定基準・整理の具体的な作業は §7 T5

---

## 7. 作業依頼（Claude から・優先順）

X 上の確認・取得が必要で、Claude にはできない作業。終わったら §12 の表を更新する。

### T1. @JNR63_nolife ランキングの続きを取得 【P0】

- 投稿: https://x.com/JNR63_nolife/status/2109653089460658249
- 本文は「第10位〜第7位」で終わっている。**第6位〜第1位がスレッドの続きにあるはず**。
- 第6位〜第1位を v2 で `predictions/raw/` に追記する。
  - `source_type: "thread"`, `thread_root_id: "2109653089460658249"`, `rank_in_post` に順位
  - `time_horizon: "this_week"`, `horizon_source: "explicit"`, `promo_flags: ["clickbait_phrase"]`
  - **`post_ticker_count` はスレッド全体の銘柄数**（10になるはず）。既存の4件（`samples_2026-10-12.json`）は 4 なので、10 だった場合は §12 に書く（Claude 側で直す）。
- 続きがない・削除されている場合は `rejected/` に `reason: "thread_not_found"`。

### T2. @FrankCurzio の中身を確認 【P0】

| 投稿 | 確認すること |
|---|---|
| https://x.com/FrankCurzio/status/2109616527649772006 （3 sectors to buy & 1 to avoid） | **どのセクターか**。分かれば対応するセクターETF（例: XLU, XLE, XLV）で `instrument_type: "sector_etf"`。"1 sector to avoid" は `direction: "avoid"` |
| https://x.com/FrankCurzio/status/2108172662606606592 （CEG のニュース） | CEG 自体は予想ではない（除外済み）。"6 other nuclear stocks" の**6銘柄が分かれば**、作者が買いを示しているか確認して記録 |

### T3. @FrankCurzio VST の目標値を埋める 【P0】

- 投稿: https://x.com/FrankCurzio/status/2108172810233557114 「betting it goes back to its highs」
- 2026-10-08 時点の **VST の過去最高値（終値）** を調べ、次の形で記録:
  `direction: "long"`, `target_price: <最高値>`, `target_price_type: "prior_high"`, `time_horizon: "target_only"`, `horizon_source: "default"`, `stated_price_at_post: 167`

### T4. 本文を原文で確認 【P1】

`data/stock_posts.json` に本文がなく、`raw_text` だけで判断している投稿。原文と違いがあれば §12 に書く。

| 投稿 | 特に確認すること |
|---|---|
| https://x.com/iddm_simple/status/2109623475824632014 （6617） | 「本週も注目」の位置、株価7560円の表記 |
| https://x.com/iddm_simple/status/2109224729475490040 （3103） | 期間の記載が本当にないか |
| https://x.com/iddm_simple/status/2108535467151163636 （4392） | 「明日注目すべき銘柄」が4392を指しているか |
| https://x.com/seikabusuki/status/2109544528634065161 （6857） | 「こっから買わんでいい」の前後の文脈、期間の手がかり |

あわせて `@iddm_simple` のプロフィール・固定ポストに LINE・有料グループへの誘導があるか確認（あれば `paid_group_invite`）。

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

### T6. Automation の指示文を v2 に差し替え 【P0・最優先】

`daily-jp-stock-candidate-collect` と `daily-us-stock-candidate-collect` の両方を §4.2 に差し替える。**次の US 22:00 実行より前に**行うこと。

### T7. 削除・編集の追跡 【P1】

- `predictions/raw/` の `status: "open"` のレコードの投稿が**まだ存在するか**を、収集のついでに毎日確認する。
- 消えていたら `predictions/deletions.jsonl` に `{"id": "<レコードのid>", "post_deleted_at": "<確認した時刻>"}` を追記する（`raw/` の元の行は書き換えない）。
- 投稿が編集されていた場合は、**最初のバージョン**の本文で抽出する。

### T8. 候補リストの定期見直し 【P2】

- 月1回（毎月1日）、テーマに依存しない検索語（「目標株価」「買い推奨」「空売り」「price target」「I'm buying」など）で新しい候補を探し、`added_at` をつけて追加する。
- 直近30日の予想抽出率（予想数 ÷ 銘柄を含む投稿数）が10%未満の候補は `inactive` にする。

### T9. @kei_toshi__ ランキングの他の順位 【P1】

- 投稿: https://x.com/kei_toshi__/status/2109781166144557335 は「下げたら強気で集めたい銘柄 **第4位** 三菱UFJ」。
- 第1〜3位・第5位以降が別投稿・スレッドにあれば v2 で追記し、`post_ticker_count` を報告する。

---

## 8. 他AIとのインターフェース

| Grok が渡すもの | 他AIに任せること |
|----------|----------------------|
| `predictions/raw/*.jsonl`（v2） | hit/miss の判定（`review/evaluation_rules.md`） |
| `rejected/`, `deletions.jsonl` | スコア計算・ランキング（`review/scoring.md`） |
| 生に近い `raw_text` と `post_url` | 価格APIの選定・バックテスト実装 |
| 候補リストの更新 | 候補バイアスの分析（`review/candidates_review.md`） |

---

## 9. 制約・品質

- 公開投稿のみ。投資助言に見える断定をしない
- 無理な抽出をしない（0件なら0件と報告）
- Xのレート・件数上限があるため「全員の全投稿」はベストエフォート
- `status` は常に `open`、`evaluation` は常に `null`（評価は後工程）
- 値動きを見てから投稿を選ばない（後知恵の防止）
- 作業の前後に `CHANGELOG.md` を読み・書く（コミットメッセージだけで済ませない）
- schema変更は独断でしない。変更するなら `schema.md` + `prediction.schema.json` + `HANDOFF.md` + 本ファイルを同じコミットで更新

---

## 10. 確認方法

```bash
pip install jsonschema
python3 scripts/validate_predictions.py predictions/raw/*.jsonl
```

`N/N records valid` と出れば OK。エラーが出たら、表示されたフィールドを直してから push する。
（`deletions.jsonl` と `rejected/` は予想レコードではないので対象に含めない。）

---

## 11. トラブルシューティング

| 症状 | 対応 |
|------|------|
| Automationが空振り | 候補の投稿が少ない日→正常。ツールエラーなら手動で主要ユーザーのみ再実行 |
| 抽出が多すぎる/緩い | §3.2・§5.4 を再確認。曖昧分は rejected へ |
| 期間を書きたくなるが本文に根拠がない | 推測で入れない。目標株価があれば target_only、なければ除外 |
| 検証で `collected_at is before posted_at` | collected_at に実行開始の名目時刻ではなく、実際に取得した時刻を入れる |
| 検証で `id should be ...` | id を `{post_id}-{ticker}-{direction}` にする |
| GitHub push失敗 | 接続・SHA・branch `main` を確認 |
| 候補が古い | candidates JSONを更新し、両Automationのpromptをupdate |

---

## 12. Claude への返却と対応状況

| 作業 | 返すもの |
|---|---|
| T1, T9 | スレッドの銘柄数（`post_ticker_count` の修正が必要か） |
| T2, T3 | 追記したレコードの id |
| T4 | 原文と `raw_text` の違い（なければ「差異なし」） |
| T5 | 変更した候補の一覧（removed / 付け替え / 判断保留） |
| 全体 | `HANDOFF.md` の変更履歴に1行追記 |

| タスク | 状態 | 日付 | メモ |
|---|---|---|---|
| T1 JNR63 スレッド続き | 完了（続きなし） | 2026-10-13 | rejected に thread_not_found。銘柄数は4のまま |
| T2 FrankCurzio セクター・6銘柄 | 完了・要確認 | 2026-10-13 | 11件追記。SKYY/SOXX/URA の期間根拠と post_ticker_count を CHANGELOG で確認依頼 |
| T3 VST 目標値 | 完了 | 2026-10-13 | 216.67（2025-09-22 終値） |
| T4 原文確認 | 完了 | 2026-10-13 | 差異なし（`predictions/TASK_LOG_2026-10-13.md`） |
| T5 候補リスト整理 | 一部 | 2026-10-13 | 方針は `candidates/STATUS_UPDATES_2026-10-13.md`。**candidates/*.json は未反映**、followers 未記入 |
| T6 Automation v2 | 完了 | 2026-10-13 | 作業ログ（CHANGELOG）の段落の追加が残り |
| T7 削除追跡 | 継続中 | 2026-10-13 | 初回確認では削除なし |
| T8 定期見直し | 未着手 | | 11/1 から |
| T9 kei_toshi ランキング | 完了（他順位なし） | 2026-10-13 | |

---

## 13. 変更履歴

この表は本文書の改訂だけを書く。日々の作業は [CHANGELOG.md](./CHANGELOG.md)。

| 日付 | 内容 |
|------|------|
| 2026-10-13 | 初版（Grok）。JP 08:00 / US 22:00 の全員対象Automation、schema、candidates、日次predictions出力方針を固定。 |
| 2026-10-13 | Claude 版（作業依頼 T1〜T8）と統合。抽出ルール・出力形式を v2 に更新（出力先 `predictions/raw/*.jsonl`）。08:00 JP 出力を v2 に変換し旧ファイルは `archive_v1/` へ。T9 を追加。 |
| 2026-10-13 | CHANGELOG.md による相互引き継ぎのルールを追加（冒頭、§4.1、§4.2、§9）。§12 を Grok の作業結果で更新（Claude）。 |
