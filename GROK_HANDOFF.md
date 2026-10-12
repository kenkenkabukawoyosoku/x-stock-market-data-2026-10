# GROK_HANDOFF.md — 収集側引き継ぎ書（Grok専用）

**対象**: Grok（本会話・Automation・将来のGrokセッション）  
**作成日**: 2026-10-13  
**リポジトリ**: https://github.com/kenkenkabukawoyosoku/x-stock-market-data-2026-10  
**対になる文書**: [HANDOFF.md](./HANDOFF.md)（他AI向け・評価・レビュー）

---

## 1. Grokの役割（境界）

| やる | やらない |
|------|----------|
| X投稿の収集 | 的中率の最終判定（価格照合の設計は他AI） |
| 検証可能な予想の一次抽出 | 投資助言・「この人が最強」断定 |
| candidates / predictions の更新 | schemaの独断変更（変更時はHANDOFFと同期） |
| GitHubへの保存 | 他AI向け評価レポートの本書き |
| 日次Automationの維持 | |

**原則**: Grokに固有なのは主に **Xネイティブ収集 + 定期実行**。抽出ルールは `predictions/schema.md` に従う。

---

## 2. リポジトリと成果物

```
x-stock-market-data-2026-10/
├── GROK_HANDOFF.md          ← 本ファイル（収集手順）
├── HANDOFF.md               ← 他AI向け
├── README.md
├── candidates/
│   ├── jp_candidates.json
│   └── us_candidates.json
├── predictions/
│   ├── schema.md            ← 抽出の唯一の正
│   ├── samples_2026-10-12.json
│   ├── YYYY-MM-DD.json      ← 日次収集の出力先（推奨）
│   └── README.md
└── data/                    ← 初期スナップショット（参考）
```

**日次出力の推奨ファイル名**
- 日本株: `predictions/YYYY-MM-DD-jp.json` または同日1ファイルに `market` で分ける
- 米国株: `predictions/YYYY-MM-DD-us.json`
- 既存: `predictions/2026-10-13.json` など日付単位でも可

---

## 3. 自動化（稼働中）

| 名前 | task 概要 | 時刻（Asia/Tokyo） | 対象 |
|------|-----------|-------------------|------|
| `daily-jp-stock-candidate-collect` | 日本株候補全員の直近投稿収集→予想抽出 | **08:00** | `jp_candidates` 相当 |
| `daily-us-stock-candidate-collect` | 米国株候補全員の直近投稿収集→予想抽出 | **22:00** | `us_candidates` 相当 |

### Automationプロンプトの要点（再実行時も同じ）

1. `from:username` で候補全員（または実用上の優先サブセット）の直近24時間を収集  
2. **schema必須3条件**を満たす投稿だけ抽出  
   - 銘柄特定可能  
   - 方向が明確  
   - 時間軸が読み取れる  
3. JSON出力（下記）+ 短い summary  
4. 可能なら本リポジトリ `predictions/` に保存  
5. 投資助言ではない旨を守る  

### 出力JSON（日次）

```json
{
  "collected_at": "ISO8601",
  "market": "JP or US",
  "predictions": [
    {
      "post_id": "...",
      "author": "@...",
      "ticker": "...",
      "market": "JP or US",
      "direction": "long|short|neutral",
      "target_price": null,
      "time_horizon": "1w|2w|1m|3m|earnings|unspecified",
      "raw_text": "...",
      "status": "open"
    }
  ],
  "summary": "2-3文"
}
```

完全形フィールドは `predictions/schema.md` を優先（`id`, `post_url`, `posted_at`, `confidence_note` 等を付けられるなら付ける）。

---

## 4. 収集手順（手動・単発）

### 4.1 ツール
- `x_keyword_search` … `from:user` + キーワード、`mode: Latest`
- `x_semantic_search` … テーマ横断の補助
- `x_thread_fetch` … スレッド内の具体銘柄確認
- GitHub connected tools … `push_files` / `create_or_update_file`

### 4.2 日本株（例）
```
from:USERNAME (株 OR 銘柄 OR 買い OR 売り OR 予想 OR 目標)
```
`limit` は状況に応じて。候補が多い場合はアクティブな発信者を優先しつつ、リスト全員を可能な範囲で回す。

### 4.3 米国株（例）
```
from:USERNAME (stock OR buy OR sell OR "$TICKER" OR target OR bullish OR bearish)
```

### 4.4 抽出判定（短く）
- **採用**: 「6617 東光高岳 現7560 予想8246」「アドバンはこっから買わなくていい」「$VST 高値回帰」
- **不採用**: 「注目」「おもしろそう」「相場厳しい」（銘柄・方向・期間のいずれか欠ける）

### 4.5 保存
1. schemaに沿ってJSON化  
2. `predictions/` にコミット（message例: `Add JP predictions YYYY-MM-DD`）  
3. 必要なら README / HANDOFF の日付に触れない（収集ログは predictions 側）

---

## 5. 候補リストのメンテ

- 正本: `candidates/jp_candidates.json`, `candidates/us_candidates.json`
- フォロワー極端に少ない・スパム・同文連投のみのアカウントは載せない
- リスト変更時は **Automationプロンプト内の候補一覧も更新**すること（プロンプトにハードコードされている）
- 精度ランキングではない。検証用プール

---

## 6. 他AIとのインターフェース

| 渡すもの | 渡さない／任せること |
|----------|----------------------|
| 日次 `predictions/*.json` | hit/miss の最終定義の決定 |
| 生に近い `raw_text` と post_url | 価格APIの選定・本番バックテスト実装 |
| schema準拠の構造化データ | 候補バイアスの政策判断（提案は他AI） |

他AIは [HANDOFF.md](./HANDOFF.md) の P0（的中ルール・スコア式・サンプル品質）から入る想定。

---

## 7. 制約・品質

- 公開投稿のみ。投資助言に見える断定をしない  
- 無理な抽出をしない（0件なら0件と報告）  
- Xのレート・件数上限があるため「全員の全投稿」はベストエフォート  
- `status` は収集時点では原則 `open` のまま（評価は後工程）  
- schema変更は独断でしない。変更するなら `schema.md` + `HANDOFF.md` + 本ファイルを同じPR/コミットで更新  

---

## 8. トラブルシューティング

| 症状 | 対応 |
|------|------|
| Automationが空振り | 候補の投稿が少ない日→正常。ツールエラーなら手動で主要ユーザーのみ再実行 |
| 抽出が多すぎる/緩い | schemaの3条件を再確認。曖昧分を落とす |
| GitHub push失敗 | 接続・SHA・branch `main` を確認 |
| 候補が古い | candidates JSONを更新し、両Automationのpromptをupdate |

---

## 9. 変更履歴

| 日付 | 内容 |
|------|------|
| 2026-10-13 | 初版。JP 08:00 / US 22:00 の全員対象Automation、schema、candidates、日次predictions出力方針を固定。 |
