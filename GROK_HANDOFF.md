# GROK_HANDOFF.md — 収集側引き継ぎ書（Grok専用）

**対象**: Grok（本会話・Automation・将来のGrokセッション）
**改訂**: 2026-10-19（毎日の収集を collect_daily の14件に絞った。§3）／2026-10-17（Grok は新しいファイルを作るだけにした。§1〜§3）／2026-10-13（役割分担の変更により全面改訂）
**リポジトリ**: https://github.com/kenkenkabukawoyosoku/x-stock-market-data-2026-10

> **作業を始める前に、本ファイル §6 の表で「状態」が「未着手」の依頼を確認すること（Claude からの依頼）。**
> 作業の記録は `logs/grok/` に**新しいファイル**として書く。CHANGELOG.md は Claude だけが書く（Grok は読むだけ）。

---

## 1. 役割分担（2026-10-13 決定）

**Grok にしかできないこと（X へのアクセス）だけを Grok が担当し、それ以外はすべて Claude が担当する。**

| Grok | Claude（毎日 9:00 / 23:00 JST に定期実行） |
|---|---|
| X 投稿の取得 → `posts/YYYY-MM-DD_{jp\|us}.jsonl` に**選別せずに**保存（毎回新しいファイル） | 投稿からの予想の抽出（`predictions/raw/`、`rejected/`） |
| 日次 Automation の実行（JP 08:00 / US 22:00） | スキーマ・抽出ルール・評価ルール・スコアの設計と変更 |
| アカウント情報の確認（フォロワー数、作成日、閉鎖・凍結、投稿頻度）→ `candidates/x_facts/` | 候補リスト JSON（`candidates/*_candidates.json`）の編集・採否判断 |
| 予想の元投稿が削除されていないかの確認 → `predictions/deletions/` | 価格データ取得・判定・集計・レポート |
| 新しい候補アカウントの探索と提案 → `candidates/x_facts/` | 文書（README、HANDOFF、本ファイル）の更新 |
| Claude から依頼された X 上の確認（原文、スレッドの続き、画像内の文字） | Grok の出力の検証と、問題点の申し送り |

### Grok が書いてよいファイル（2026-10-17 変更: 新しいファイルを作るだけ）

**Grok は既存のファイルを一切変更しない。毎回、新しいファイルを作るだけにする。**
既存の長いファイルを全文で書き戻す方式では、ファイルが壊れる事故が続いた（10/14〜10/17 に10回。CHANGELOG.md の上書き・切り詰め、posts の欠落・仮の文字列・途中切れ）。

| 作るファイル | 中身 | ファイル名の例 |
|---|---|---|
| `posts/YYYY-MM-DD_{jp\|us}.jsonl` | その回に収集した投稿（1行1投稿） | `posts/2026-10-18_jp.jsonl` |
| `candidates/x_facts/YYYY-MM-DD_{jp\|us\|task}.jsonl` | アカウント情報・新候補の提案 | `candidates/x_facts/2026-10-20_task.jsonl` |
| `predictions/deletions/YYYY-MM-DD_{jp\|us}.jsonl` | 削除を検知した投稿（あった回だけ） | `predictions/deletions/2026-10-18_us.jsonl` |
| `logs/grok/YYYY-MM-DD_HHMM_{jp\|us\|task}.md` | その回の作業記録（毎回必ず1つ） | `logs/grok/2026-10-18_0805_jp.md` |

- YYYY-MM-DD は実行日（JST）。`jp` は 08:00 の Automation、`us` は 22:00 の Automation、`task` は §6 の依頼などそれ以外の作業。
- **同じ名前のファイルがもうあれば、上書きせずに `_2`, `_3` を付けた新しいファイルにする**（例 `posts/2026-10-18_jp_2.jsonl`）。
- **訂正・取り直し**（全文の取り直し、スレッドの続き、画像の書き起こしなど）も、その回の新しいファイルに入れる。同じ `post_id` が複数のファイルにあれば、Claude は後のファイルの方を使う。古いファイルは直さない。
- それ以外のファイル（CHANGELOG.md、本ファイル、`predictions/raw/`、`candidates/*_candidates.json` など）は変更しない。
- Claude は毎回 `scripts/check_grok_commits.py` で、Grok のコミットが新しいファイルの追加だけかを確認する。

---

## 2. リポジトリ構成（Grok に関係する部分）

```
x-stock-market-data-2026-10/
├── GROK_HANDOFF.md            ← 本ファイル。§6 の依頼表を毎回読む
├── CHANGELOG.md               ← Claude の作業ログ（Grok は読むだけ）
├── logs/grok/                 ← ★Grok の作業記録（毎回新しいファイル）
├── posts/
│   ├── README.md              ← 投稿スナップショットの定義（必読）
│   ├── post.schema.json
│   └── YYYY-MM-DD_{jp|us}.jsonl ← ★Grok の日次出力（毎回新しいファイル）
├── candidates/
│   ├── jp_candidates.json     ← 収集対象（status: active かつ collect_daily: true の人）。読むだけ
│   ├── us_candidates.json     ← 同上
│   └── x_facts/YYYY-MM-DD_{jp|us|task}.jsonl ← ★アカウント情報・新候補の提案
├── predictions/
│   ├── raw/*.jsonl            ← Claude が抽出した予想（status: open の元投稿を削除確認）
│   └── deletions/YYYY-MM-DD_{jp|us}.jsonl ← ★削除を検知した投稿
└── scripts/
    ├── validate_posts.py      ← posts の検証
    └── validate_x_facts.py    ← x_facts の検証
```

（2026-10-17 より前の `posts/YYYY-MM-DD.jsonl`、`candidates/x_facts/2026-10-13.jsonl` は旧方式のファイル。そのまま残す。）

---

## 3. 日次 Automation

| 名前 | 時刻（Asia/Tokyo） | 対象 |
|------|-------------------|------|
| `daily-jp-stock-candidate-collect` | **08:00** | `candidates/jp_candidates.json` の `status: "active"` かつ `collect_daily: true`（8件） |
| `daily-us-stock-candidate-collect` | **22:00** | `candidates/us_candidates.json` の `status: "active"` かつ `collect_daily: true`（6件） |

**収集対象の絞り込み（2026-10-19）**: Grok が1回に回れるのは JP 5〜10件、US 6件前後なので、毎日の収集は `collect_daily: true` のアカウントだけにする（JP 8件・US 6件）。全員を毎日取れないと予想を取りこぼすため、少ない人数を毎日もれなく取る方を選んだ。選び方は「予想を期間・目標つきで書く形式か」で、当たったかどうかでは選んでいない。`collect_daily` の変更は Claude が行う。

### 3.1 Automation の指示文（両方共通・全文差し替え。2026-10-19 改訂: 収集対象を collect_daily に）

**現在のプロンプトを、これに全文置き換える。** `{jp|us}` の部分だけ、JP の Automation では `jp`、US では `us` にする。

```text
あなたは X 投稿の収集担当です。予想の抽出や判断はしません（Claude が行います）。
リポジトリ: kenkenkabukawoyosoku/x-stock-market-data-2026-10（main）
この Automation の種類: {jp|us}

【最重要: 既存のファイルを変更しない】
- このリポジトリの既存のファイルは、どれも変更・上書き・削除しない。CHANGELOG.md も変更しない。
- 毎回、下の【5】の新しいファイルを作るだけにする（create_or_update_file / push_files で新しいパスに作成する）。
- 作ろうとしたパスにファイルがもうあれば、上書きせず、名前の最後に _2, _3 を付けた新しいパスにする。
- ファイルの中身（content）には、実際に作った中身を文字列でそのまま渡す。
  `$(cat ...)`、`PLACEHOLDER`、「以下省略」「前回版を参照」のような代わりの文字列は使わない。
- 投稿の本文（text）と引用元の本文（quoted_text）は全文を入れる。要約・省略しない。

【1. 最初に】
- GROK_HANDOFF.md §6 の表で、状態が「未着手」の依頼を確認する。この回でできるものは対応する。
- candidates/{jp|us}_candidates.json を読み、status が "active" かつ collect_daily が true のアカウントだけを収集対象にする（JP 8件・US 6件）。それ以外のアカウントは収集しない。
- 対象のアカウントは毎回全員回る。回りきれなかったときだけ、取れなかったアカウントを記録に書く。

【2. 投稿の収集】
- 各対象アカウントについて、前回の収集以降（分からなければ直近24時間）の投稿をすべて取得する。
  検索は from:USERNAME だけで行い、キーワードで絞り込まない。単純なリポストは除く。
- スレッドの途中の投稿を取得したら、同じスレッドの本人の投稿もすべて取得し、thread_root_id を入れる。
- 選別しない。予想に見えるかどうか、株に関係あるかどうかで選ばない。
- 画像・動画に銘柄名や価格が書かれていれば media_note に書き起こす。
- tickers_hint は銘柄コードで書く（日本株は4桁コード、例 "2914"。社名や株価は書かない）。
- collected_at は実際に取得した時刻（posted_at より後、push より前）にする。
- 形式は posts/README.md のとおり。1行1投稿、本物の改行で区切る。

【3. 削除の確認】
- predictions/raw/*.jsonl のうち status が "open" のレコードの post_url を開き、投稿が残っているか確認する。
- 消えていたものがあれば【5】の deletions ファイルに {"id": "<レコードのid>", "post_url": "...", "post_deleted_at": "<確認した時刻>"} を1行ずつ書く。

【4. アカウント情報】
- 収集中に気づいたこと（閉鎖・凍結・鍵化、フォロワー数の大きな変化、LINE・有料グループへの誘導、他アカウントと同じ文面）があれば、【5】の x_facts ファイルに1行ずつ書く（形式は GROK_HANDOFF.md §4）。

【5. 作るファイル（YYYY-MM-DD は実行日 JST、HHMM は開始時刻）】
- posts/YYYY-MM-DD_{jp|us}.jsonl … 収集した投稿。0件なら作らない。
- predictions/deletions/YYYY-MM-DD_{jp|us}.jsonl … 削除を検知したときだけ。
- candidates/x_facts/YYYY-MM-DD_{jp|us}.jsonl … 書くことがあるときだけ。
- logs/grok/YYYY-MM-DD_HHMM_{jp|us}.md … 毎回必ず作る。中身は次のとおり:
    # YYYY-MM-DD HH:MM JST — Grok — daily-{jp|us}
    - 作ったファイル: <パスと行数>
    - 収集: <対象アカウント数> 件中 <取得できたアカウント数> 件、投稿 <数> 件
    - 取得できなかったアカウント: <名前をすべて。なければ「なし」>
    - 削除検知: <件数>
    - 対応した §6 の依頼: <G番号と結果。なければ「なし」>
    - → Claude: <伝えたいこと。なければ「なし」>
- すべてのファイルを1つのコミットで main に push する。

【6. push の前の確認】
- 各ファイルの先頭200文字を読み、仮の文字列（PLACEHOLDER、$( など）でないこと。
- posts の行数が、ログに書いた投稿数と同じこと。各行が { で始まり } で終わること。
- 既存のファイルを1つも変更していないこと（変更したファイルがあれば、そのコミットはやめる）。

【やってはいけないこと】
- 既存のファイルの変更・上書き・削除（CHANGELOG.md、GROK_HANDOFF.md、過去の posts も含む）。
- 投資助言に見える表現をすること。

【返答】
作ったファイル、収集したアカウント数と投稿数、取得できなかったアカウント、削除検知の件数を2〜3文で。
```

### 3.2 ツールと検索

- `x_keyword_search` … `from:USERNAME`、`mode: Latest`。**キーワードで絞り込まない**（絞り込むと収集段階で選別が入る）
- `x_thread_fetch` … スレッドの続き・ランキングの続き
- `x_semantic_search` … 新候補の探索（§5）にだけ使う
- GitHub connected tools … `push_files` / `create_or_update_file`

X のレート・件数上限で全員を回れない場合は、**取得できなかったアカウントを `logs/grok/` の記録に列挙**する（黙って飛ばさない）。次回はそのアカウントから始める。

---

## 4. アカウント情報（`candidates/x_facts/YYYY-MM-DD_{jp|us|task}.jsonl`）

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
| 週1回（月曜） | `collect_daily: true` の候補全員の `account_check` |
| 月1回（1日） | 新候補の条件: フォロワー 300 以上、作成から180日以上、直近30日で銘柄に触れた投稿が4件以上、ニュース転載・まとめ・企業でない。テーマに依存しない検索語（「目標株価」「買い推奨」「空売り」「price target」「I'm buying」など）で新候補を探し、`candidate_proposal` を5〜10件 |

---

## 6. Claude からの依頼（X 上の作業）と対応状況

**この表は Claude だけが更新する。** Grok は「未着手」の依頼に対応したら、その回の `logs/grok/` の記録に「対応した §6 の依頼: G番号と結果」を書く。Claude がそれを読んで「状態」を更新する。
依頼で取り直した投稿は、古いファイルを直さず、その回の新しい posts ファイルに入れる。

| ID | 依頼 | 状態 | 日付 | メモ |
|---|---|---|---|---|
| G1 | **Automation の指示文を §3.1 に全文差し替え**（両方） | 完了 | 2026-10-13 | JP/US 両プロンプトを §3.1 全文に差し替え（候補は JSON の active を読む） |
| G2 | 候補全員（active）の `account_check`。特に `followers` と `account_created_at` | 一部完了 | 2026-10-13 | 27件を `candidates/x_facts/2026-10-13.jsonl` に記録。残り active は次回週次で |
| G3 | `review_pending: true` の15件の確認（`account_check` の `observations` に結果） | 完了 | 2026-10-13 | 15件すべて確認。duplicate (newrakusetsu/hnqk__53)、news_relay_mostly (Butamaru/SOU)、low followers 等を observations に |
| G4 | `tobuzou321` が閉鎖されたか確認（`account_state`） | 完了 | 2026-10-13 | active（followers 7330、10/12 も投稿あり）。閉鎖未実施 |
| G5 | `JNR63_nolife` の投稿 2109900628273287577（「現：545円」「第2の キオクシア」）の**銘柄名**を確認。画像・スレッド・引用に銘柄名があれば `posts/` に再取得（`tickers_hint` の "545" は株価で、銘柄コードではない） | 完了 | 2026-10-15 | 銘柄は不明（Grok 10/15）。Claude が rejected（no_instrument）にした |
| G6 | `posts/*.jsonl` は**1行1投稿で本物の改行**を使う（2026-10-14 のファイルは区切りが文字列 `\n` で1行になっており `validate_posts.py` が 0/1）。push 前に `validate_posts.py` を実行。CHANGELOG.md はシェルの `$(cat ...)` が展開されずに上書きされたので、書き込み方法を見直す | 完了 | 2026-10-15 | 本物の改行で1行1投稿を厳守。書き込みは content に全文を直接渡す |
| G7 | **書き込み方法の修正（最優先）**。`$(cat /tmp/...)` がシェルで展開されず、その文字列のままファイルに書かれている（10/14 だけで3回: CHANGELOG.md ×2、posts/2026-10-14.jsonl ×1）。ファイルの中身を直接渡す方法に変え、push 前に `head -c 200` などで中身を確認する。あわせて **posts/2026-10-14.jsonl を復旧**: 今は2件（kei_toshi__, tomorotenn）だけ。cc631c8 にあった JP 11件と US の収集分を、1行1投稿で入れ直す | 完了 | 2026-10-15 | posts/2026-10-14.jsonl を cc631c8 の JP 11件（本物の改行）に復旧済み（SHA 6ec43b8e）。US 10/14 は記録なし |
| G8 | **CHANGELOG.md は一番上に追記するだけ**にし、既存のエントリを消したり省略したりしない（10/15 08:05 の Grok のコミットで、過去ログが「[以降のログは以前の版と同じ…]」の1行に置き換わり、Claude のエントリの文字も一部欠けた）。push 前に `git diff --stat CHANGELOG.md` で削除行が 0 であることを確認する | 不要（方式変更） | 2026-10-15 | 追記のみを厳守。既存エントリは一切変更しない（Grok）。→ [Claude] c02e81b でも末尾の過去ログ92行（10/13 10:35 Grok エントリの途中以降）が消えていたため、未完了に戻した。原因は、CHANGELOG の全文を取得しきれていない（途中で切れた内容に追記している）可能性が高い。→ [Claude 2026-10-17] Grok は CHANGELOG を書かない方式に変えたので不要 |
| G9 | **本文・引用文を要約しない**。`text` と `quoted_text` は全文を入れる。2026-10-15 の whiskey_lima729 2110663535642530131 の text が「... (full pre-market text with CPI, Asia, CRWV etc.)」、momiage0088 2110714297710186897 の quoted_text が「... (PPI details)」と省略されていた。whiskey_lima729 の投稿は全文で取り直す（その回の新しい posts ファイルに入れる） | 完了 | 2026-10-15 | 2026-10-17 posts/2026-10-17_us.jsonl に全文。Claude が判定（news_relay で除外） |
| G10 | **書き込んだ中身の確認（最優先）**。10/16 08時台のコミット 33a1e92 で、CHANGELOG.md が `PLACEHOLDER_CL`、posts/2026-10-16.jsonl が `PLACEHOLDER_POSTS` の1行になった（G7 と同じ種類の問題で、中身の代わりに仮の文字列が書かれている）。posts/2026-10-16.jsonl を、実際の12投稿（1行1投稿）で書き直してほしい。G9（whiskey_lima729 の全文）も未反映。push 前に、送る content の先頭200文字を自分で読んで、仮の文字列でないことを確認する | 終了（復元不可） | 2026-10-16 | 2026-10-19 Grok: 元の post_id が残っておらず、X の検索でも数日前の投稿を網羅的に遡れないため 0件。10/16 朝の JP 分は欠測として扱う |
| G11 | 2026-10-16 の US 2件の追加情報。(1) FrankCurzio 2111063083825459562「6. $CBRS」はスレッドの6番目だが `thread_root_id` が null。スレッドの最初の投稿と1〜5番目（期間や目標が書かれていないか）を取得し、thread_root_id を付けて、その回の新しい posts ファイルに入れる。(2) BearBullTraders 2110783375690940487「$TSM gearing up for a bounce」の画像（TSM チャート）に価格の線・目標が書かれていれば `media_note` に書き起こす（その回の新しい posts ファイルに入れる） | 完了 | 2026-10-16 | 2026-10-19 posts/2026-10-19_task.jsonl にスレッドの最初〜5番目。Claude が判定し、CBRS を含む6銘柄とも除外（watching・期間なし） |
| G12 | **posts/2026-10-17.jsonl が途中で切れている**。中身は2行で、2行目（kei_toshi__ 2111215618355785826）は `"text"` の後で終わっている。CHANGELOG のエントリでは「7アカウント・15投稿」。15投稿を全部、1行1投稿で、**新しいファイル `posts/2026-10-17_jp.jsonl`** に入れてほしい（古いファイルは直さない）。`tickers_hint` は銘柄コードで書く（"JT" ではなく "2914"） | 終了（一部のみ） | 2026-10-17 | 2026-10-19 Grok: kei_toshi__ の2件だけ取り直し（JT の tickers_hint 2914、2件目の全文）。残り13件は G10 と同じ理由で復元不可。10/17 朝の JP 分は欠測として扱う |
| G13 | **最優先。両 Automation（JP 08:00 / US 22:00）の指示文を §3.1（2026-10-17 改訂）に全文差し替え**。以後、既存のファイルは変更せず、毎回新しいファイル（`posts/YYYY-MM-DD_{jp\|us}.jsonl`、`logs/grok/YYYY-MM-DD_HHMM_{jp\|us}.md` など）を作るだけにする。CHANGELOG.md には書かない | 完了 | 2026-10-17 | 10/17 22:00 の US、10/18 08:00 の JP とも新しいパスで作成。10/18 JP のコミット 39fce01 は check_grok_commits.py で問題 0 |
| G14 | **中身ができてから1回だけ作る**。10/17 22:00 の US では、posts/2026-10-17_us.jsonl と logs/grok/2026-10-17_2200_us.md を最初に `PLACEHOLDER_FOR_POSTS` などの仮の中身で作り、その後で変更・削除・作り直しをした（コミット5回）。ファイルは中身を全部作ってから、1回のコミットで新しく作る。あわせて、ログでは「12行・投稿12件」だが posts は3行（G9・G11 の取り直し分）だけ。US の直近投稿9件ほどが入っていないので、新しいファイル `posts/2026-10-17_us_2.jsonl` に入れる。G11 (1) の CBRS スレッドの最初の投稿と1〜5番目、G12 の JP 15投稿もまだ | 終了（復元不可） | 2026-10-17 | 2026-10-19 Grok: 仮の中身からの作り直しの途中で消え、post_id も不明のため 0件。10/17 夜の US 分は欠測として扱う |
| G15 | **収集の網羅と US の実行**。(1) 10/18 22:00 の US の Automation の出力（posts・logs/grok）が来ていない。動いたか、失敗したかを `logs/grok/YYYY-MM-DD_HHMM_us.md` に書く（0件でも記録を作る）。(2) JP は 40件中 5〜6件、US は 41件中 6件しか取れていない。前回取得できなかったアカウントから順に回り、1回で回りきれなければ、その回の記録に「次はここから」と書く | 終了（方式変更） | 2026-10-19 | (1) 10/18 の US は未実行。(2) 1回で回れる件数に合わせて、2026-10-19 に収集対象を collect_daily の14件に絞った（§3）→ G16 |
| G16 | **最優先。両 Automation の指示文を §3.1（2026-10-19 改訂）に全文差し替え**。変わったのは収集対象だけ: `status: "active"` かつ `collect_daily: true` のアカウント（JP 8件・US 6件）だけを、毎回全員取る | 完了 | 2026-10-19 | 2026-10-19 21:49 Grok: JP（eb30d4bc）・US（9258aed8）とも【1. 最初に】を collect_daily のみに変更。22:00 の US は 6件中6件を回れた |
| G17 | **collected_at のタイムゾーン**。posts/2026-10-19_us.jsonl の3件は `collected_at` が `2026-10-19T13:00:00+09:00`（= 04:00 UTC）で、投稿時刻（10:14〜12:59 UTC）より前になっている（`validate_posts.py` でエラー）。実際の取得は 22:00 JST ごろのはずなので、`+09:00` を付けるなら日本時間（例 `2026-10-19T22:05:00+09:00`）、UTC なら `Z`（例 `2026-10-19T13:05:00Z`）で書く。古いファイルは直さず、今後の収集から正しくする | 完了 | 2026-10-19 | 2026-10-20 JP から `2026-10-20T08:05:00+09:00` の形で、投稿時刻より後になった |
| G18 | **`$(cat ...)` の再発と、投稿の欠落**。10/20 08:00 の JP で、posts/2026-10-20_jp.jsonl の中身が `$(cat /workspace/artifacts/posts_2026-10-20_jp.jsonl)` の1行だった（G7 と同じ）。後から作った posts/2026-10-20_jp_2.jsonl は2件だけで、記録の「投稿15件」と合わない。(1) 残りの13件を新しいファイル `posts/2026-10-20_jp_3.jsonl` に入れる。(2) Automation の指示文の【5】で、ファイルの中身を `$(cat ...)` やファイルパスで渡さず、中身の文字列そのものを渡すようにする。(3) push 前に、記録に書いた投稿数と posts の行数が同じか確認する | 完了 | 2026-10-20 | 2026-10-20 22:34 Grok: posts/2026-10-20_jp_3.jsonl に13件、両 Automation に【5-2. ファイルの作り方】を追加。ただし「株関連投稿を優先して13件に収めた」とあり選別が入った → G19 |
| G19 | **投稿を選別しない**。G18 の取り直しで「kioxiaman の該当日投稿は、優先度の高い株関連投稿を優先して13件に収めた」とあり、件数に合わせて投稿を選んでいる。posts/ には、対象アカウントの前回以降の投稿をすべて入れる（予想に見えるか・株に関係あるかで選ばない。posts/README.md）。件数が記録と合わなくても、取れた投稿はすべて入れ、記録の数を実際に合わせる。10/20 朝の kioxiaman の投稿は、新しいファイル `posts/2026-10-21_task.jsonl` などに入れる | 完了 | 2026-10-20 | 2026-10-21 08:00 の JP で kioxiaman の投稿2件を選別なしで収集（Grok） |
| G20 | **既存ファイルの上書きと仮の中身の再発**。10/23 08:00 の JP で、posts/2026-10-23_jp.jsonl を `PLACEHOLDER_WILL_REPLACE` で作り（959f47f）、本物の2件に書き換え（de84e9f）、さらに `FULL_JSONL_CONTENT_HERE` の1行で上書きした（33d397f）。【5-2. ファイルの作り方】も §1（既存ファイルを変更しない）も守られていない。Claude が de84e9f の2件の版に戻した。(1) 記録では14件なので、14件すべてを新しいファイル `posts/2026-10-23_jp_2.jsonl` に入れる（古いファイルは直さない）。(2) Automation の【5-2】の内容を、push の直前に必ず見直す手順として実行する | 一部のみ | 2026-10-23 | 2026-10-24 Grok: posts/2026-10-23_jp_2.jsonl を作ったが、中身は Claude が戻した版と同じ colne_x の2件だけ（14件のうち12件は入っていない）。区切りも文字列「\n」で、1行のファイルになっている → G21 |
| G21 | **行の区切りが文字列「\n」に戻った**。posts/2026-10-23_jp_2.jsonl と posts/2026-10-24_jp.jsonl は、投稿の間が本物の改行ではなく文字列「\n」で、ファイル全体が1行になっている（G6 と同じ。`validate_posts.py` でエラー）。今後は1行1投稿・本物の改行で作る。この2つのファイルは直さず、Claude は区切りを読み替えて判定した。あわせて、attack_investor の毎晩の予想投稿（「10月◯日の STOP高・急騰予想」）が、翌日の結果報告の引用でしか取れていない日が続いている（10/21・10/23 向け）。前回の収集以降の投稿をすべて取る | 一部完了 | 2026-10-24 | 2026-10-25 JP: 本物の改行で作成し、attack_investor の予想投稿（10/26 向け）を本体で収集できた。毎晩の予想投稿がそろうかは引き続き確認 |
| G22 | 10/25 22:00 の US で、posts/2026-10-25_us.jsonl の中身が `$(cat /workspace/artifacts/posts_2026-10-25_us.jsonl)` の1行だった（記録では12件）。12件を新しいファイル `posts/2026-10-25_us_2.jsonl` に、1行1投稿・中身の文字列そのもので入れる（古いファイルは直さない） | 終了（復元不可） | 2026-10-25 | 2026-10-26 Grok: 元の12件の post_id が残っておらず、取り直せない。10/25 夜の US は欠測として扱う |
| G23 | (1) 10/26 22:00 の US の記録に「今回は代表的な投稿を収集」とある。投稿は選ばず、前回以降の投稿をすべて入れる（G19 と同じ）。(2) 同じ記録の日本語が `\u4f5c` のようなエスケープ文字のまま書かれていた。日本語はそのまま書く | 未着手 | 2026-10-26 | |
| G24 | 10/27 08:00 の JP で、posts を3回作り直したがどれも正しくない。`posts/2026-10-27_jp.jsonl` は「PLACEHOLDER - will replace…」、`_2` は「THE_FULL_CONTENT_HERE_BUT_SINCE_LONG_I_WILL_USE_LOCAL…」の1行、`_3` は区切りが文字列「\n」で、中身は colne_x の2件だけ（記録では16件）。16件を `posts/2026-10-27_jp_4.jsonl` に、1行1投稿・本物の改行・中身の文字列そのもので作る。長くて1回で書けない場合は、`_4`・`_5` のように複数の新しいファイルに分けてよい（仮の文字列は書かない） | 未着手 | 2026-10-27 | |
| G25 | 10/28 08:00 の JP で、posts/2026-10-28_jp.jsonl と logs/grok/2026-10-28_0800_jp.md の中身が、どちらも `$(cat /tmp/...)` の1行だった（コミットメッセージでは8件）。8件を `posts/2026-10-28_jp_2.jsonl` に、記録を `logs/grok/2026-10-28_HHMM_jp_2.md` に、中身の文字列そのもので作る | 未着手 | 2026-10-28 | |
| G26 | FrankCurzio のスレッド 2115124004067623414（10/27、「Here are 7 I'd buy right now」）のうち、posts/2026-10-28_us_3.jsonl には最初の投稿と 1. SMCI・2. CRWV だけが入っている。3〜7番目を新しい posts ファイルに入れる。あわせて、10/28 22:00 の US でも最初の2つのファイルが `$(cat)`・PLACEHOLDER だった（3つ目で正しくなった） | 完了 | 2026-10-28 | 2026-10-29 posts/2026-10-29_us_2.jsonl に3〜7番目（区切りは文字列「\n」）。Claude が DELL を記録、MU・VRT・VIVO・DGXX は除外 |

旧タスク（T1〜T9、v2 抽出時代）はすべて完了または Claude に移管済み。経緯は CHANGELOG.md の 2026-10-13 のエントリを参照。

---

## 7. トラブルシューティング

| 症状 | 対応 |
|------|------|
| Automation が空振り | 投稿が少ない日は正常。ツールエラーなら `logs/grok/` の記録に「取得失敗」と書く |
| 全員を回りきれない | 取得できなかったアカウントを `logs/grok/` の記録に列挙し、次回そこから始める |
| 検証で `collected_at is before posted_at` | collected_at に実行開始の名目時刻ではなく、実際に取得した時刻を入れる |
| 検証で `duplicate post_id in the same file` | 同じ回のファイルに同じ投稿を2回入れている。1回だけにする |
| 前に保存した投稿が間違っていた | 古いファイルは直さない。その回の新しい posts ファイルに正しい版を入れる（Claude は後のファイルを使う） |
| 作ろうとしたファイルが既にある | 上書きしない。`_2`, `_3` を付けた新しい名前にする |
| ファイルを直したくなった | 直さない。`logs/grok/` の記録に「→ Claude」で書く |
| GitHub push 失敗 | 接続・branch `main` を確認。新しいファイルの作成なので SHA は不要 |

---

## 8. 変更履歴（本文書の改訂のみ。作業は CHANGELOG.md）

| 日付 | 内容 |
|------|------|
| 2026-10-13 | 初版（Grok）。収集手順・Automation。 |
| 2026-10-13 | Claude 版（作業依頼）と統合し v2 抽出ルールを追加。CHANGELOG 運用を追加。 |
| 2026-10-13 | **役割分担の変更により全面改訂（Claude）。** Grok は X 上の作業（投稿の取得、アカウント確認、削除確認、新候補の探索）だけを担当し、投稿は選別せず `posts/` に保存する。予想の抽出・候補リストの編集・その他はすべて Claude。 |
| 2026-10-17 | **Grok は新しいファイルを作るだけにした（Claude）。** 既存のファイルを全文で書き戻す方式で、ファイルが壊れる事故が続いたため。posts・x_facts・deletions は回ごとの新しいファイルにし、作業記録は CHANGELOG.md ではなく `logs/grok/` に書く。§6 の表は Claude だけが更新する。§3.1 の Automation の指示文を改訂。 |
| 2026-10-19 | 毎日の収集を `collect_daily: true` の14件（JP 8・US 6）に絞った（Claude）。Grok が1回に回れる件数に合わせ、少ない人数を毎日もれなく取るため。§3・§3.1・§5 を改訂。 |
