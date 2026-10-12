# Claude 向けメモ（このリポジトリ）

- 役割: 評価・レビュー担当。X の収集は Grok が担当（`GROK_HANDOFF.md`）。
- **作業を始める前に `CHANGELOG.md` を読む。** 自分（Claude）の最後のエントリより新しい Grok のエントリと、`→ Claude` の申し送りを確認する。
- **作業を終えたら、push 前に `CHANGELOG.md` の「ログ」の一番上にエントリを追加する**（同じコミットで）。ルールとテンプレートは同ファイル冒頭。
- 予想レコードの定義は `predictions/schema.md`（v2）。変更後は `python3 scripts/validate_predictions.py predictions/raw/*.jsonl predictions/samples_2026-10-12.json` で検証する。
- `predictions/raw/` は Grok の追記専用。直接書き換えず、問題は CHANGELOG の申し送りで伝える。
