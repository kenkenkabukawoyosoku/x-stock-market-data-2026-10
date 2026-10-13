# Claude 向けメモ（このリポジトリ）

## 役割（2026-10-13 決定）

**Claude がメイン担当。** Grok は X 上の作業（投稿の取得、アカウント確認、削除確認、新候補の探索）だけを行う（`GROK_HANDOFF.md` §1）。
それ以外（予想の抽出、候補リストの編集、スキーマ・評価ルール、判定・集計、文書の更新、Grok の出力の検証）は Claude が行う。

## 定期実行（Routine）

- 名前: `x-stock 予想抽出（Claude 日次）`（`trig_014vgzTvzxQvEqqxjecQwJRK`）
- 毎日 **9:00 / 23:00 JST**（Grok の収集 08:00 / 22:00 の1時間後）。実行ごとに新しいセッションが起動し、下の手順 1〜7 を行って main に push する。
- 変更・停止は claude.ai の Routines 画面から。

## 毎回の作業手順

1. `main` の最新を取得し、**`CHANGELOG.md` を読む**。自分（Claude）の最後のエントリより新しい Grok のエントリと、「→ Claude」の申し送りを確認する。
2. Grok の新しい出力を検証する。
   - `python3 scripts/validate_posts.py posts/*.jsonl`
   - `python3 scripts/validate_x_facts.py candidates/x_facts/*.jsonl`（ファイルがあれば）
   - 問題があれば CHANGELOG に「→ Grok」で申し送る（Grok のファイルは直さない）。
3. **抽出**: まだ抽出していない `posts/YYYY-MM-DD.jsonl` の投稿をすべて判定し、`predictions/raw/YYYY-MM-DD.jsonl` と `predictions/rejected/YYYY-MM-DD.jsonl` に書く（日付は posts と同じ）。
   - ルールは `predictions/schema.md`。**抽出中に株価を調べない。**
   - 情報が足りない（画像の中身、スレッドの続きなど）ときは、その投稿を保留にして CHANGELOG で Grok に確認を頼む。
4. **候補リスト**: `candidates/x_facts/` の新しい行を `candidates/*_candidates.json` に反映する（`followers_approx`、`status`、`review_pending` など）。新候補の提案は採否を決めて追加する。
5. **削除**: `predictions/deletions.jsonl` の新しい行を、該当レコードの `post_deleted_at` に反映する（評価は続ける）。
6. 検証: `python3 scripts/validate_predictions.py predictions/raw/*.jsonl predictions/samples_2026-10-12.json`
7. **`CHANGELOG.md` の一番上にエントリを追加**し、作業したファイルと同じコミットで push する。

## 決まりごと

- Grok が書くファイル（`posts/`、`candidates/x_facts/`、`predictions/deletions.jsonl`）は書き換えない。
- `predictions/raw/` の訂正は評価前に限り、規則の適用ミス・事実誤りだけ。`notes` に `[日付 Claude] 変更内容` を書き、CHANGELOG に記録する。
- Grok に頼むことは `GROK_HANDOFF.md` §6 の表に ID（G1, G2, …）をつけて追加し、CHANGELOG でも申し送る。
