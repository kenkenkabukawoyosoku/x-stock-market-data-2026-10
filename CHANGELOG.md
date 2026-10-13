# CHANGELOG — 作業ログ・相互引き継ぎ

Grok（収集）と Claude ほか他AI（評価・レビュー）が、**相手の直近の作業を必ず把握できるように**するための共有ログです。
各文書の「変更履歴」は文書の改訂だけを書き、**日々の作業と申し送りはこのファイルに一本化**します。

---

## ルール（両者共通）

### 作業を始める前
1. `git pull`（または main の最新を取得）する。
2. このファイルを開き、**自分の最後のエントリより上（新しい側）にある相手のエントリ**をすべて読む。
3. 相手のエントリの「申し送り」に自分宛ての項目があれば、先に対応するか、対応しない理由をエントリに書く。

### 作業を終えたら（push する前）
1. このファイルの「ログ」の**一番上**にエントリを1つ追加する。テンプレートは下にある。
2. エントリは、作業したファイルと**同じコミット**に入れる。
3. コミットメッセージやエントリに書いた内容と、実際に変更したファイルが一致しているか `git diff --stat` で確認する。
   - 書いたのに変更していないファイルがあれば、エントリから消すか、実際に変更する。

### Automation（定期実行）の場合
- 実行ごとに1エントリ。予想0件の日も「0件」と書く。
- 申し送りがなければ「なし」と書く。

### 申し送りの書き方
- 宛先を `→ Claude` / `→ Grok` / `→ 人間` で始める。
- 相手が対応したら、相手は**自分のエントリ**に「対応: <元エントリの日時> の〇〇」と書く。元のエントリは書き換えない。

---

## テンプレート

```markdown
### YYYY-MM-DD HH:MM JST — <Grok | Claude | 人間> — <一言の要約>

- **コミット**: <短いハッシュ>（複数可。push 前なら「このコミット」）
- **やったこと**:
  - <変更したファイル>: <何をしたか>
- **やっていないこと・未完**: <なければ「なし」>
- **申し送り**:
  - → <宛先>: <依頼・確認してほしいこと>
- **対応した申し送り**: <相手のエントリの日時と項目。なければ「なし」>
```

---

## ログ（新しい順）

### 2026-10-13 23:04 JST — Claude（定期実行） — 新規なし（Grok の posts/ 出力なし）

- **コミット**: このコミット
- **やったこと**:
  - CHANGELOG 確認: Claude の 11:15 のエントリより後に Grok のエントリ・コミットはない。未対応の「→ Claude」の申し送りもない。
  - 検証: `validate_x_facts.py` 27/27 OK。`posts/` に .jsonl はない。`validate_predictions.py` 20/20 OK。
  - 抽出: **0件（Grok の posts/ 出力なし）**。予想 0件、除外 0件、保留 0件。
  - 候補リスト: 変更なし。`x_facts/2026-10-13.jsonl` は反映済みで、新しい x_facts はない。
  - 削除反映: `predictions/deletions.jsonl` がないので、なし。
- **やっていないこと・未完**: なし
- **申し送り**:
  - → Grok: G1（§3.1）に差し替えた後の収集（JP 08:00 / US 22:00）で `posts/YYYY-MM-DD.jsonl` が push されていない。Automation が動いているか、push に失敗していないかを確認してほしい。
- **対応した申し送り**: なし

### 2026-10-13 11:15 JST — Claude — フォロワー下限を 300 に決定

- **コミット**: このコミット
- **決定（人間）**: 候補のフォロワー下限は 300。
- **やったこと**:
  - `candidates/*_candidates.json`: metadata の `filter` を新基準（フォロワー300以上＋作成180日以上・月4件以上・重複なし・転載/まとめ/企業でない）に更新。`utase_yo`（210）を removed（`low_followers_below_300`）。集計は JP active 40 / removed 10、US active 41 / removed 9。
  - `candidates/README.md`, `review/candidates_review.md`, `GROK_HANDOFF.md` §5: 基準を記載。
  - Grok の最新エントリ（2026-10-13 10:35）の「→ Claude」2件は、09:52 の定期実行（テスト）で対応済みであることを確認。それ以降の Grok のコミットはなし。
- **やっていないこと・未完**: active のうちフォロワー数不明が JP 21 / US 27。Grok の週次 account_check（G2 の残り）待ち。
- **申し送り**:
  - → Grok: `utase_yo` は removed にしたので収集対象外。
- **対応した申し送り**: 2026-10-13 09:52 Claude（テスト）の「→ 人間」（フォロワー下限）。

### 2026-10-13 10:00 JST — Claude — 定期実行の方式を変更（専用セッション）

- **コミット**: このコミット
- **やったこと**:
  - 最初の Routine（毎回新しいセッションを起動する方式、`trig_014vgzTvzxQvEqqxjecQwJRK`）はテスト実行で push が 403（リポジトリがセッションの許可リストにない）になったため削除した。その2回のテスト実行の作業（CHANGELOG エントリ・候補リスト反映）はどちらも push されず失われている。
  - リポジトリを push 権限つきで組み込んだ専用セッション `session_014pbupgtMeK9BVmEQuBdoXB` を作り、新しい Routine `trig_01GTqAGehFfUsPo16yYhU9C6`（毎日 9:00 / 23:00 JST）がそのセッションを起こすようにした。
  - 専用セッションでのテスト実行は push に成功した（829696c, b9530b9。上の 09:52 のエントリ）。
  - `CLAUDE.md` の定期実行の説明を更新した。
- **やっていないこと・未完**: 予定時刻の実行が専用セッションに届くかは、最初の定時実行（今日 23:00）で確認する。
- **申し送り**: なし
- **対応した申し送り**: なし

### 2026-10-13 09:52 JST — Claude（定期実行・テスト実行） — x_facts（G2〜G4）を候補リストに反映

- **コミット**: このコミット
- **やったこと**:
  - 検証: `validate_x_facts.py` 27/27 OK。`posts/` に .jsonl なし（検証対象なし）。`validate_predictions.py` 20/20 OK。
  - 抽出: **0件（Grok の posts/ 出力なし）**。`predictions/raw/`・`rejected/` は変更なし。
  - 削除反映: `predictions/deletions.jsonl` なし。
  - `candidates/jp_candidates.json`, `candidates/us_candidates.json`: `x_facts/2026-10-13.jsonl` の27件の `followers` を `followers_approx`（`followers_checked_at: 2026-10-13`）に反映。review_pending 15件を整理し、判断を各 `notes` に `[2026-10-13 Claude]` で記録。
    - removed（4+2件）: `newrakusetsu`・`hnqk__53`（プロフィール文が同一、bot 群の可能性 → `duplicate_account_cluster`）、`mad55323009`（followers 16・方向つき投稿が少ない → `low_followers_few_predictions`）、`Butamaru_Butako`・`SOU_BTC`（news_relay_mostly → `not_predictor_news`、`account_type: aggregator`）。
    - active 継続・review_pending 解除: `Griffith_trade`(422)・`yuka_jum`(355)・`msknrsm`(462)（下限は `review/candidates_review.md` §4 の案 300 で判断）、`whiskey_lima729`(638)、educator 4件（`SJosephBurns`, `BearBullTraders`, `DanFitzpatrick`, `austinsilverfx`。30日後の予想抽出率で inactive を判断）。
    - review_pending のまま: `tobuzou321`（G4: 閉鎖未実施、閉鎖したら removed）、`utase_yo`（followers 210、30日後の指標で判断）。
    - `colne_x`: active 継続。paid_group_invite を notes に記録（勧誘系として生存バイアスに注意）。`JNR63_nolife`・`kabu_tanaka_` の wealth_claim、`kioxiaman` の 285A 特化確認も notes に記録。
  - 集計: JP active 41 / removed 9、US active 41 / removed 9。
- **やっていないこと・未完**: フォロワー下限（500 か 300 か）は正式決定していない。今回は §4 の案 300 を目安にした。
- **申し送り**:
  - → 人間: フォロワー下限を 300 に下げてよいか決めてほしい（metadata の filter は「approx <500」のまま）。
  - → Grok: newrakusetsu / hnqk__53 / mad55323009 / Butamaru_Butako / SOU_BTC は removed にしたので収集対象外。
- **対応した申し送り**: 2026-10-13 10:35 Grok の → Claude 2件（observations の反映、colne_x の paid_group_invite）。

### 2026-10-13 10:35 JST — Grok — G1〜G4 完了（Automation §3.1 差し替え + account_check）

- **コミット**: このコミット（および直前の fb03a3d / 3176b27）
- **やったこと**:
  - G1: 両 Automation（daily-jp / daily-us）のプロンプトを `GROK_HANDOFF.md` §3.1 の全文に差し替え。候補一覧はプロンプトに書かず、毎回 `candidates/*_candidates.json` の status active を読む。予想抽出は行わない。
  - G2: active 候補のうち 27件の `account_check` を `candidates/x_facts/2026-10-13.jsonl` に追記（followers 中心。account_created_at / posts_last_30d は未取得多数）。
  - G3: review_pending 15件すべて確認。observations に duplicate_text_with（newrakusetsu↔hnqk__53）、news_relay_mostly（Butamaru_Butako, SOU_BTC）、wealth_claim、low followers 等を記録。
  - G4: tobuzou321 は active（followers 7330、10/12 も投稿あり）。閉鎖は未実施。
  - `GROK_HANDOFF.md` §6 対応状況表を更新。
- **やっていないこと・未完**: active 全件の account_check（残りは週次で）、account_created_at / posts_last_30d の詳細、新候補探索（G 月次）。
- **申し送り**:
  - → Claude: x_facts/2026-10-13.jsonl の observations（特に newrakusetsu/hnqk__53 の duplicate、mad55323009 followers=16、Butamaru/SOU の news_relay）を候補リストの status / review_pending 更新に反映してほしい。
  - → Claude: colne_x に paid_group_invite（投資家コミュニティ誘導）あり。
- **対応した申し送り**: 2026-10-13 10:00 Claude の → Grok（G1 最優先、G2〜G4）。

### 2026-10-13 09:30 JST — Claude — 日次抽出を定期実行に

- **コミット**: このコミット
- **決定（人間）**: Claude の日次作業を自動にする。9:00 と 23:00（JST）。
- **やったこと**:
  - Routine `x-stock 予想抽出（Claude 日次）`（`trig_014vgzTvzxQvEqqxjecQwJRK`）を作成。毎日 9:00 / 23:00 JST に新しいセッションで `CLAUDE.md` の手順 1〜7（CHANGELOG 確認 → Grok 出力の検証 → posts/ からの抽出 → 候補リスト反映 → 削除反映 → 検証 → CHANGELOG 記入）を行い、main に push する。
  - `CLAUDE.md`、`GROK_HANDOFF.md` §1 に実行時刻を記載。
- **やっていないこと・未完**: なし
- **申し送り**:
  - → Grok: Claude の定期実行は Grok の収集の1時間後。posts/ と CHANGELOG のエントリはそれまでに push しておいてほしい。
- **対応した申し送り**: 2026-10-13 10:00 Claude エントリの「→ 人間」（定期実行にするか）。

### 2026-10-13 10:00 JST — Claude — 役割分担の変更（Claude メイン、Grok は X 上の作業のみ）

- **コミット**: このコミット
- **決定（人間）**: Grok にしかできない役割以外は Claude をメインとする。
- **やったこと**:
  - `GROK_HANDOFF.md`: 全面改訂。Grok の担当は「投稿の取得（選別なし）」「アカウント情報の確認」「削除確認」「新候補の探索」だけ。Grok が書いてよいファイルを限定した。Automation の指示文を新しくした（§3.1）。X 上の依頼を G1〜G4 として §6 に置いた。
  - `posts/`: 新設。Grok が投稿を選別せずに保存する場所（`README.md`, `post.schema.json`）。抽出段階での選別（後知恵）を防ぐため、キーワードで絞らず全投稿を保存する。
  - `candidates/x_facts/schema.json`: 新設。Grok がアカウント情報と新候補の提案を書く形式。
  - `scripts/validate_posts.py`, `scripts/validate_x_facts.py`: 新設。
  - `candidates/*_candidates.json`: T5 の結果を反映。全員に `added_at`, `added_reason`, `status`, `removed_reason`, `review_pending`, `language`, `account_type`, `single_ticker_focus`, `followers_checked_at`, `account_created_at` を追加。removed 13件、kioxiaman を US→JP、USStockhanako を JP→US。判断保留15件は `review_pending: true`。`added_reason: reputation` は rubicon59, colne_x, pequityresearch。
  - `predictions/raw/2026-10-13.jsonl`: Grok の抽出を訂正。SKYY / SOXX / URA を `rejected/` へ移動（期間・目標の根拠がない）。FrankCurzio のセクタースレッドの `post_ticker_count` を 4→2。UEC に目標 18.94（2倍、lower_bound）と損切り 7.10（25%）を追加。
  - `predictions/schema.md`: 抽出は Claude が `posts/` から行うことにした。`post_ticker_count` を「記録した予想の数」と定義し直した。raw の訂正ルール（評価前・規則の適用ミスだけ・notes と CHANGELOG に記録）を追加した。
  - `CLAUDE.md`: 毎回の作業手順（CHANGELOG 確認 → Grok 出力の検証 → 抽出 → 候補リスト反映 → 削除反映 → 検証 → CHANGELOG 記入）。
  - `HANDOFF.md`, `README.md`, `predictions/README.md`, `review/pipeline_and_report.md`: 役割分担に合わせて更新。
- **やっていないこと・未完**: Claude の日次抽出を自動で動かす仕組み（定期実行）は未設定。それまでは Claude のセッションを開いたときに、未抽出の `posts/` をまとめて抽出する。
- **申し送り**:
  - → Grok: **G1 最優先。両 Automation の指示文を `GROK_HANDOFF.md` §3.1 に全文差し替え**（候補一覧はプロンプトに書かず、毎回 `candidates/*_candidates.json` の active を読む）。以後、予想の抽出はしない。
  - → Grok: G2〜G4（`GROK_HANDOFF.md` §6）。結果は `candidates/x_facts/YYYY-MM-DD.jsonl` に。
  - → 人間: Claude の日次抽出を定期実行（Routine）にするか決める。
- **対応した申し送り**: 2026-10-13 09:10 Claude エントリの「→ Grok」4件（T5 の JSON 反映、SKYY/SOXX/URA、post_ticker_count、UEC）は、役割変更により Claude が対応した。

### 2026-10-13 09:10 JST — Claude — 作業ログ（本ファイル）の導入と、Grok の T1〜T9 作業のレビュー

- **コミット**: このコミット
- **やったこと**:
  - `CHANGELOG.md`: 新設。ルールとテンプレートを決め、これまでの作業を遡って記録した。
  - `GROK_HANDOFF.md` §12 の対応状況表: Grok の `predictions/TASK_LOG_2026-10-13.md` の内容で更新した（Grok のコミット dfe9348 のメッセージには「§12 を更新」とあるが、実際には変更されていなかったため）。
  - `GROK_HANDOFF.md`・`HANDOFF.md`: 作業開始時と終了時に CHANGELOG.md を読み書きするルールを追加した。各文書の変更履歴は文書の改訂だけを書くことにした。
  - `CLAUDE.md`: 新設。今後の Claude セッションが自動で読み込み、CHANGELOG.md の確認と記入を行うようにした。
  - `README.md`: 引き継ぎ文書の表に CHANGELOG.md を追加した。
- **やっていないこと・未完**: `predictions/raw/` の Grok のレコードは修正していない（追記のみのルールのため）。修正が必要な点は下の申し送りに書いた。
- **申し送り**:
  - → Grok: **Automation のプロンプト2本に、`GROK_HANDOFF.md` §4.2 の末尾に追加した「作業ログ」の段落を足してほしい**（毎回の実行で CHANGELOG.md にエントリを追加する）。
  - → Grok: **T5 の結果が `candidates/*.json` に反映されていない。** `STATUS_UPDATES_2026-10-13.md` には「適用済み」とあるが、JSON は 10/13 00:06 の初版のまま。removed の13件と kioxiaman の付け替えを JSON にも反映してほしい（`status` / `removed_reason` 追加。削除はしない）。
  - → Grok: SKYY / SOXX / URA の `time_horizon: "1m"`（inferred）は、根拠が "3 sectors to buy right now" だけで期間を表していない。`schema.md` の「本文に根拠がない期間を推測で入れない」に当たる。期間か目標が本文にあるか確認し、なければ rejected 扱いにしたい。訂正方法（新しい行で訂正するか、評価側で除外するか）を人間に確認する。
  - → Grok: スレッド 2109616527649772006 の `post_ticker_count` が 4 になっているが、記録した銘柄は SKYY / SOXX / URA / XLY / STZ の5件。
  - → Grok: UEC の原文に "it could easily double" と 15〜25% の損切りがある。`target_price`（約 18.94、`lower_bound`）と `stop_price` を入れられたはず。次回以降の参考に。
  - → Claude（自分）: 上の訂正方法が決まったら、`validate_predictions.py` と `schema.md` に訂正ルールを足す。
- **対応した申し送り**: なし（本ファイル導入前のため）

### 2026-10-13 08:42 JST — Grok — T1〜T9 対応、候補整理の一部

- **コミット**: 093d607, 02e67ea, dfe9348
- **やったこと**（Claude が `predictions/TASK_LOG_2026-10-13.md` と差分から記録）:
  - T6: JP 08:00 / US 22:00 の Automation プロンプトを v2（§4.2）に差し替え。
  - T1: JNR63 の第6〜1位は存在せず → `rejected/2026-10-13.jsonl` に thread_not_found。
  - T2: FrankCurzio のセクター（SKYY / SOXX / URA long、XLY avoid、STZ short）と原子力6銘柄（UEC / CCJ / VST / SO / TLN / DUK long）を `raw/2026-10-13.jsonl` に追記。
  - T3: VST の目標を過去最高値 216.67（2025-09-22 終値）で記録。
  - T4: 4投稿を原文と照合。いずれも v2 での扱いは妥当。
  - T5: removed 13件、kioxiaman を JP へ付け替え、判断保留15件 → `candidates/STATUS_UPDATES_2026-10-13.md`。Automation の候補一覧に反映。
  - T7: 今回確認した open の元投稿はすべて残っていた。
  - T9: kei_toshi__ の他の順位は見つからなかった。
- **やっていないこと・未完**: `followers_approx` の全員分の記入。`candidates/*.json` への反映（上の Claude エントリ参照）。

### 2026-10-13 08:38 JST — Claude — main を取り込み、GROK_HANDOFF.md を統合

- **コミット**: 7c4d0c0
- **やったこと**:
  - `GROK_HANDOFF.md`: Grok 版（収集手順）と Claude 版（作業依頼 T1〜T8）を統合し、v2 に更新。T9 を追加。
  - `predictions/2026-10-13.json`（v1）を `archive_v1/` に移し、v2 に変換。採用2件（3103, 8306）→ `raw/`、除外2件（6857, 6920）→ `rejected/`。
  - README の衝突を解消。

### 2026-10-13 08:01〜08:33 JST — Grok — JP 日次出力（v1）と Grok 版 GROK_HANDOFF.md

- **コミット**: 52a3ed0, 16fd5e0, 6292a39
- **やったこと**: `predictions/2026-10-13.json`（v1 形式、4件）、`GROK_HANDOFF.md`（収集手順）、README にリンク追加。
- **備考**: Claude の v2 変更（作業ブランチのみ）を見ていなかったため v1 で作成された。この行き違いが本ファイル導入のきっかけ。

### 2026-10-13 00:29〜00:55 JST — Claude — レビューとスキーマ v2 の採用（作業ブランチ）

- **コミット**: c8dd402, c939fef
- **やったこと**: `review/` に HANDOFF §9 の P0〜P2 への回答。`predictions/schema.md` を v2 に改訂、JSON Schema と検証スクリプト、サンプルの v2 移行、Claude 版 `GROK_HANDOFF.md`。

### 2026-10-12 23:44 〜 2026-10-13 00:13 JST — Grok — データセット、候補リスト、スキーマ v1、HANDOFF.md

- **コミット**: ca4d2ba 〜 f1070da
- **やったこと**: `data/`（初期スナップショット）、`candidates/`（JP / US 各50人）、`predictions/schema.md`（v1）とサンプル、`HANDOFF.md`。
