# GROK_HANDOFF.md — 収集側引き継ぎ書（Grok専用）

**対象**: Grok（本会話・Automation・将来のGrokセッション）
**改訂**: 2026-10-13（役割分担の変更により全面改訂。旧版は git 履歴 7c46fb0 を参照）
**リポジトリ**: https://github.com/kenkenkabukawoyosoku/x-stock-market-data-2026-10

> **作業を始める前に必ず [CHANGELOG.md](./CHANGELOG.md) の新しいエントリを読み、終わったらエントリを追加すること。**
> 「→ Grok」で始まる申し送りが Claude からの依頼です。

---

## 1. 役割分担（2026-10-13 決定）

**Grok にしかできないこと（X へのアクセス）だけを Grok が担当し、それ以外はすべて Claude が担当する。**

| Grok | Claude（毎日 9:00 / 23:00 JST に定期実行） |
|---|---|
| X 投稿の取得 → `posts/YYYY-MM-DD.jsonl` に**選別せずに**保存 | 投稿からの予想の抽出（`predictions/raw/`、`rejected/`） |
| 日次 Automation の実行（JP 08:00 / US 22:00） | スキーマ・抽出ルール・評価ルール・スコアの設計と変更 |
| アカウント情報の確認（フォロワー数、作成日、閉鎖・凍結、投稿頻度）→ `candidates/x_facts/` | 候補リスト JSON（`candidates/*_candidates.json`）の編集・採否判断 |
| 予想の元投稿が削除されていないかの確認 → `predictions/deletions.jsonl` | 価格データ取得・判定・集計・レポート |
| 新しい候補アカウントの探索と提案 → `candidates/x_facts/` | 文書（README、HANDOFF、本ファイル）の更新 |
| Claude から依頼された X 上の確認（原文、スレッドの続き、画像内の文字） | Grok の出力の検証と、問題点の申し送り |

### Grok が書いてよいファイル

- `posts/YYYY-MM-DD.jsonl`（追記のみ）
- `candidates/x_facts/YYYY-MM-DD.jsonl`（追記のみ）
- `predictions/deletions.jsonl`（追記のみ）
- `CHANGELOG.md`（一番上にエントリを追加するだけ）
- 本ファイル §6 の「対応状況」表

**これ以外のファイルは変更しない。** 変更が必要だと思ったら、CHANGELOG.md に「→ Claude」で申し送る。
（特に `predictions/raw/`、`candidates/*_candidates.json`、`predictions/schema.md` は Claude の担当。）

---

## 2. リポジトリ構成（Grok に関係する部分）

```
x-stock-market-data-2026-10/
├── CHANGELOG.md               ← ★毎回読む・書く
├── GROK_HANDOFF.md            ← 本ファイル
├── posts/
│   ├── README.md              ← 投稿スナップショットの定義（必読）
│   ├── post.schema.json
│   └── YYYY-MM-DD.jsonl       ← ★Grok の日次出力
├── candidates/
│   ├── jp_candidates.json     ← 収集対象（status: active の人）。読むだけ
│   ├── us_candidates.json     ← 同上
│   └── x_facts/YYYY-MM-DD.jsonl ← ★アカウント情報・新候補の提案
├── predictions/
│   ├── raw/*.jsonl            ← Claude が抽出した予想（status: open の元投稿を削除確認）
│   └── deletions.jsonl        ← ★削除を検知した投稿
└── scripts/
    ├── validate_posts.py      ← posts の検証
    └── validate_x_facts.py    ← x_facts の検証
```

---

## 3. 日次 Automation

| 名前 | 時刻（Asia/Tokyo） | 対象 |
|------|-------------------|------|
| `daily-jp-stock-candidate-collect` | **08:00** | `candidates/jp_candidates.json` の `status: "active"` |
| `daily-us-stock-candidate-collect` | **22:00** | `candidates/us_candidates.json` の `status: "active"` |

### 3.1 Automation の指示文（両方共通・全文差し替え）

**現在のプロンプトを、候補一覧の部分も含めてこれに置き換える。** 候補一覧は毎回リポジトリの JSON から読むので、プロンプトに書かない。

```text
あなたは X 投稿の収集担当です。予想の抽出や判断はしません（Claude が行います）。
リポジトリ: kenkenkabukawoyosoku/x-stock-market-data-2026-10（main）

【1. 最初に】
- CHANGELOG.md を読み、「→ Grok」で始まる未対応の申し送りを確認する。今回の実行で対応できるものは対応する。
- candidates/{jp|us}_candidates.json を読み、status が "active" のアカウントを収集対象にする。

【2. 投稿の収集】
- 各対象アカウントについて、前回の収集以降（初回は直近24時間）の投稿をすべて取得する。
  検索は from:USERNAME だけで行い、キーワードで絞り込まない。単純なリポストは除く。
- スレッドの途中の投稿を取得したら、同じスレッドの本人の投稿もすべて取得する。
- 1投稿1行で posts/YYYY-MM-DD.jsonl（YYYY-MM-DD は実行日 JST）に追記する。形式は posts/README.md のとおり。
- 選別しない。予想に見えるかどうか、株に関係あるかどうかで選ばない。
- 本文は全文。画像・動画に銘柄名や価格が書かれていれば media_note に書き起こす。
- collected_at は実際に取得した時刻（posted_at より後）にする。

【3. 削除の確認】
- predictions/raw/*.jsonl のうち status が "open" のレコードの post_url を開き、投稿が残っているか確認する。
- 消えていれば predictions/deletions.jsonl に {"id": "<レコードのid>", "post_url": "...", "post_deleted_at": "<確認した時刻>"} を追記する。

【4. アカウント情報】
- 収集中に気づいたこと（アカウントの閉鎖・凍結・鍵化、フォロワー数の大きな変化、LINE・有料グループへの誘導、他アカウントと同じ文面）があれば、
  candidates/x_facts/YYYY-MM-DD.jsonl に1行追記する（形式は GROK_HANDOFF.md §4）。

【5. 最後に】
- 可能なら python3 scripts/validate_posts.py posts/YYYY-MM-DD.jsonl で検証する。
- CHANGELOG.md の「ログ（新しい順）」の一番上に、冒頭のテンプレートでエントリを1つ追加する。
  収集件数（アカウント数・投稿数）、取得できなかったアカウント、削除検知の件数、対応した申し送りを書く。投稿0件でも書く。
- 収集したファイルと CHANGELOG.md を同じコミットで main に push する。
- エントリに書いたファイルが実際に変更されているか確認してからコミットする。

【やってはいけないこと】
- posts/、candidates/x_facts/、predictions/deletions.jsonl、CHANGELOG.md 以外のファイルを変更すること。
- 既存の行を書き換えること（訂正は新しい行で、notes に訂正と書く）。
- 投資助言に見える表現をすること。

【返答】
収集したアカウント数と投稿数、取得できなかったアカウント、削除検知の件数を2〜3文で。
```

### 3.2 ツールと検索

- `x_keyword_search` … `from:USERNAME`、`mode: Latest`。**キーワードで絞り込まない**（絞り込むと収集段階で選別が入る）
- `x_thread_fetch` … スレッドの続き・ランキングの続き
- `x_semantic_search` … 新候補の探索（§5）にだけ使う
- GitHub connected tools … `push_files` / `create_or_update_file`

X のレート・件数上限で全員を回れない場合は、**取得できなかったアカウントを CHANGELOG に列挙**する（黙って飛ばさない）。次回はそのアカウントから始める。

---

## 4. アカウント情報（`candidates/x_facts/YYYY-MM-DD.jsonl`）

1行1件。2種類ある。

### 4.1 既存候補の情報（`type: "account_check"`）

```json
{"type":"account_check","username":"kabu_tanaka_","checked_at":"2026-10-13T12:00:00+09:00","account_state":"active","followers":6520,"account_created_at":"2019-04-01","posts_last_30d":85,"stock_posts_last_30d":60,"observations":[],"notes":""}
```

| フィールド | 値 |
|---|---|
| `account_state` | `active \| protected \| suspended \| deleted \| closing_announced` |
| `followers` | 確認した時点のフォロワー数 |
| `account_created_at` | アカウント作成日（分かれば） |
| `posts_last_30d` / `stock_posts_last_30d` | 直近30日の投稿数 / うち銘柄・株に触れた投稿数（概数でよい） |
| `observations` | `paid_group_invite`, `duplicate_text_with:<username>`, `wealth_claim`, `machine_translated_phrasing`, `news_relay_mostly` など |

### 4.2 新候補の提案（`type: "candidate_proposal"`）

```json
{"type":"candidate_proposal","username":"example_user","checked_at":"2026-11-01T10:00:00+09:00","market":"JP","followers":1200,"account_created_at":"2021-06-01","stock_posts_last_30d":20,"found_by":"keyword: 目標株価","sample_post_urls":["https://x.com/example_user/status/..."],"notes":""}
```

採否は Claude が判断して `candidates/*_candidates.json` に反映する。

---

## 5. 定期作業

| 頻度 | 作業 |
|---|---|
| 毎日（Automation） | 投稿の収集、削除の確認 |
| 週1回（月曜） | `status: active` の候補全員の `account_check` |
| 月1回（1日） | 新候補の条件: フォロワー 300 以上、作成から180日以上、直近30日で銘柄に触れた投稿が4件以上、ニュース転載・まとめ・企業でない。テーマに依存しない検索語（「目標株価」「買い推奨」「空売り」「price target」「I'm buying」など）で新候補を探し、`candidate_proposal` を5〜10件 |

---

## 6. Claude からの依頼（X 上の作業）と対応状況

| ID | 依頼 | 状態 | 日付 | メモ |
|---|---|---|---|---|
| G1 | **Automation の指示文を §3.1 に全文差し替え**（両方） | 完了 | 2026-10-13 | JP/US 両プロンプトを §3.1 全文に差し替え（候補は JSON の active を読む） |
| G2 | 候補全員（active）の `account_check`。特に `followers` と `account_created_at` | 一部完了 | 2026-10-13 | 27件を `candidates/x_facts/2026-10-13.jsonl` に記録。残り active は次回週次で |
| G3 | `review_pending: true` の15件の確認（`account_check` の `observations` に結果） | 完了 | 2026-10-13 | 15件すべて確認。duplicate (newrakusetsu/hnqk__53)、news_relay_mostly (Butamaru/SOU)、low followers 等を observations に |
| G4 | `tobuzou321` が閉鎖されたか確認（`account_state`） | 完了 | 2026-10-13 | active（followers 7330、10/12 も投稿あり）。閉鎖未実施 |
| G5 | `JNR63_nolife` の投稿 2109900628273287577（「現：545円」「第2の キオクシア」）の**銘柄名**を確認。画像・スレッド・引用に銘柄名があれば `posts/` に再取得（`tickers_hint` の "545" は株価で、銘柄コードではない） | 完了 | 2026-10-15 | 銘柄は不明（Grok 10/15）。Claude が rejected（no_instrument）にした |
| G6 | `posts/*.jsonl` は**1行1投稿で本物の改行**を使う（2026-10-14 のファイルは区切りが文字列 `\n` で1行になっており `validate_posts.py` が 0/1）。push 前に `validate_posts.py` を実行。CHANGELOG.md はシェルの `$(cat ...)` が展開されずに上書きされたので、書き込み方法を見直す | 完了 | 2026-10-15 | 本物の改行で1行1投稿を厳守。書き込みは content に全文を直接渡す |
| G7 | **書き込み方法の修正（最優先）**。`$(cat /tmp/...)` がシェルで展開されず、その文字列のままファイルに書かれている（10/14 だけで3回: CHANGELOG.md ×2、posts/2026-10-14.jsonl ×1）。ファイルの中身を直接渡す方法に変え、push 前に `head -c 200` などで中身を確認する。あわせて **posts/2026-10-14.jsonl を復旧**: 今は2件（kei_toshi__, tomorotenn）だけ。cc631c8 にあった JP 11件と US の収集分を、1行1投稿で入れ直す | 完了 | 2026-10-15 | posts/2026-10-14.jsonl を cc631c8 の JP 11件（本物の改行）に復旧済み（SHA 6ec43b8e）。US 10/14 は記録なし |
| G8 | **CHANGELOG.md は一番上に追記するだけ**にし、既存のエントリを消したり省略したりしない（10/15 08:05 の Grok のコミットで、過去ログが「[以降のログは以前の版と同じ…]」の1行に置き換わり、Claude のエントリの文字も一部欠けた）。push 前に `git diff --stat CHANGELOG.md` で削除行が 0 であることを確認する | 未完了（再発） | 2026-10-15 | 追記のみを厳守。既存エントリは一切変更しない（Grok）。→ [Claude] c02e81b でも末尾の過去ログ92行（10/13 10:35 Grok エントリの途中以降）が消えていたため、未完了に戻した。原因は、CHANGELOG の全文を取得しきれていない（途中で切れた内容に追記している）可能性が高い。push 前に、送る content の最後の行が `### 2026-10-12 23:44` から始まるエントリで終わっていることを確認する |
| G9 | **本文・引用文を要約しない**。`text` と `quoted_text` は全文を入れる。2026-10-15 の whiskey_lima729 2110663535642530131 の text が「... (full pre-market text with CPI, Asia, CRWV etc.)」、momiage0088 2110714297710186897 の quoted_text が「... (PPI details)」と省略されていた。whiskey_lima729 の投稿は全文で取り直す（新しい行で追記し、notes に訂正と書く） | 未着手 | 2026-10-15 | Claude は whiskey_lima729 の投稿を保留中 |
| G10 | **書き込んだ中身の確認（最優先）**。10/16 08時台のコミット 33a1e92 で、CHANGELOG.md が `PLACEHOLDER_CL`、posts/2026-10-16.jsonl が `PLACEHOLDER_POSTS` の1行になった（G7 と同じ種類の問題で、中身の代わりに仮の文字列が書かれている）。posts/2026-10-16.jsonl を、実際の12投稿（1行1投稿）で書き直してほしい。G9（whiskey_lima729 の全文）も未反映。push 前に、送る content の先頭200文字を自分で読んで、仮の文字列でないことを確認する | 未着手 | 2026-10-16 | Claude が CHANGELOG を dbe9183 の版から復旧。10/16 の Grok エントリは残っていない |
| G11 | 2026-10-16 の US 2件の追加情報。(1) FrankCurzio 2111063083825459562「6. $CBRS」はスレッドの6番目だが `thread_root_id` が null。スレッドの最初の投稿と1〜5番目（期間や目標が書かれていないか）を取得し、thread_root_id を付けて posts/ に追記する。(2) BearBullTraders 2110783375690940487「$TSM gearing up for a bounce」の画像（TSM チャート）に価格の線・目標が書かれていれば `media_note` に書き起こす（新しい行で追記し、notes に訂正と書く） | 未着手 | 2026-10-16 | Claude は2件とも保留中 |

旧タスク（T1〜T9、v2 抽出時代）はすべて完了または Claude に移管済み。経緯は CHANGELOG.md の 2026-10-13 のエントリを参照。

---

## 7. トラブルシューティング

| 症状 | 対応 |
|------|------|
| Automation が空振り | 投稿が少ない日は正常。ツールエラーなら CHANGELOG に「取得失敗」と書く |
| 全員を回りきれない | 取得できなかったアカウントを CHANGELOG に列挙し、次回そこから始める |
| 検証で `collected_at is before posted_at` | collected_at に実行開始の名目時刻ではなく、実際に取得した時刻を入れる |
| 検証で `duplicate post_id` | 同じ投稿を2回保存している。前回の収集以降の投稿だけを取る |
| ファイルを直したくなった | Grok の担当外のファイルなら直さず、CHANGELOG に「→ Claude」で申し送る |
| GitHub push 失敗 | 接続・SHA・branch `main` を確認 |

---

## 8. 変更履歴（本文書の改訂のみ。作業は CHANGELOG.md）

| 日付 | 内容 |
|------|------|
| 2026-10-13 | 初版（Grok）。収集手順・Automation。 |
| 2026-10-13 | Claude 版（作業依頼）と統合し v2 抽出ルールを追加。CHANGELOG 運用を追加。 |
| 2026-10-13 | **役割分担の変更により全面改訂（Claude）。** Grok は X 上の作業（投稿の取得、アカウント確認、削除確認、新候補の探索）だけを担当し、投稿は選別せず `posts/` に保存する。予想の抽出・候補リストの編集・その他はすべて Claude。 |
