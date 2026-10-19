# Claude 向けメモ（このリポジトリ）

## 役割（2026-10-13 決定）

**Claude がメイン担当。** Grok は X 上の作業（投稿の取得、アカウント確認、削除確認、新候補の探索）だけを行う（`GROK_HANDOFF.md` §1）。
それ以外（予想の抽出、候補リストの編集、スキーマ・評価ルール、判定・集計、文書の更新、Grok の出力の検証）は Claude が行う。

## 定期実行（Routine）

- 名前: `x-stock 予想抽出（Claude 日次）`（`trig_01GTqAGehFfUsPo16yYhU9C6`）
- 毎日 **9:00 / 23:00 JST**（Grok の収集 08:00 / 22:00 の1時間後）に、専用セッション `session_014pbupgtMeK9BVmEQuBdoXB`（このリポジトリを push 権限つきで組み込み済み）を起こし、下の手順 1〜8 を行って main に push する。
- 毎回新しいセッションを起動する方式は、リポジトリへの push 権限が付かず 403 になるため使わない。
- 変更・停止は claude.ai の Routines 画面から。

## 毎回の作業手順

1. `main` の最新を取得し、**`CHANGELOG.md`（自分の前回までの記録）と、前回より後に増えた `logs/grok/*.md`（Grok の作業記録）を読む**。「→ Claude」の申し送りを確認する。
2. Grok の新しい出力を検証する。
   - `python3 scripts/check_grok_commits.py` … Grok のコミットが「新しいファイルの追加だけ」か（既存ファイルの変更・仮の文字列があれば問題として出る）。
     問題があれば、Grok が変更した既存ファイルは直前の版に戻し、CHANGELOG に記録して `GROK_HANDOFF.md` §6 で Grok に申し送る。
   - `python3 scripts/validate_posts.py posts/*.jsonl`
   - `python3 scripts/validate_x_facts.py candidates/x_facts/*.jsonl`
   - Grok の新しいファイル（`posts/`、`candidates/x_facts/`、`predictions/deletions/`、`logs/grok/`）は直さない。問題は §6 で申し送る。
3. **抽出**: まだ抽出していない投稿（`posts/*.jsonl` のうち、post_url が `predictions/raw/` にも `predictions/rejected/` にも出てこないもの）をすべて判定し、`predictions/raw/YYYY-MM-DD.jsonl` と `predictions/rejected/YYYY-MM-DD.jsonl` に書く（日付は posts のファイル名の日付。`posts/2026-10-18_jp.jsonl` なら 2026-10-18）。
   - 同じ `post_id` が複数の posts ファイルにあれば、ファイル名の順で後のもの（取り直し・訂正）を使う。
   - ルールは `predictions/schema.md`。**抽出中に株価を調べない。**
   - 情報が足りない（画像の中身、スレッドの続きなど）ときは、その投稿を保留にして `GROK_HANDOFF.md` §6 で Grok に確認を頼む。
4. **候補リスト**: `candidates/x_facts/` の新しいファイルを `candidates/*_candidates.json` に反映する（`followers_approx`、`status`、`review_pending` など）。新候補の提案は採否を決めて追加する。毎日の収集対象は `collect_daily: true` の人だけ（JP 8・US 6。2026-10-19〜）。入れ替えるときは、当たり外れではなく予想の書き方で選び、`collect_daily_reason` と CHANGELOG に理由を書く。
5. **削除**: `predictions/deletions/*.jsonl` の新しい行を、該当レコードの `post_deleted_at` に反映する（評価は続ける）。
6. 検証: `python3 scripts/validate_predictions.py predictions/raw/*.jsonl predictions/samples_2026-10-12.json`
7. `GROK_HANDOFF.md` §6 の表を更新する（Grok の記録にある「対応した §6 の依頼」を見て状態を変える。新しい依頼は G 番号をつけて追加）。
8. **`CHANGELOG.md` の一番上にエントリを追加**し、作業したファイルと同じコミットで push する。読んだ `logs/grok/` のファイル名もエントリに書く。

## 決まりごと

- Grok は新しいファイルを作るだけで、既存のファイルは変更しない（2026-10-17〜。`GROK_HANDOFF.md` §1）。Grok が作ったファイル（`posts/`、`candidates/x_facts/`、`predictions/deletions/`、`logs/grok/`）は Claude も書き換えない。
- `CHANGELOG.md` と `GROK_HANDOFF.md` §6 の表は Claude だけが書く。
- `predictions/raw/` の訂正は評価前に限り、規則の適用ミス・事実誤りだけ。`notes` に `[日付 Claude] 変更内容` を書き、CHANGELOG に記録する。
- Grok に頼むことは `GROK_HANDOFF.md` §6 の表に ID（G1, G2, …）をつけて追加する（Grok は CHANGELOG ではなく §6 の表を見る）。CHANGELOG にも書く。
