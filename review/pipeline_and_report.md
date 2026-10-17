# 評価パイプライン設計図と定期レポートのテンプレート（P2-7, P2-8）

---

## 1. パイプライン全体

```
[Grok 収集] ──► posts/YYYY-MM-DD_{jp|us}.jsonl（選別なし・回ごとの新しいファイル）
                       │
                       ▼
[Claude 抽出] ──► predictions/raw/YYYY-MM-DD.jsonl
                       │
                       ▼
              (1) validate  … predictions/prediction.schema.json で検証
                       │      NG → predictions/rejected/ に理由つきで退避
                       ▼
              (2) dedupe    … 同一作者×銘柄×方向で評価期間中 → reiterations++
                       ▼
              (3) prices    … 対象銘柄＋ベンチマークの日足を取得し prices/ にキャッシュ
                       ▼
              (4) evaluate  … evaluation_rules.md に従い t1 を過ぎたものを判定
                       │      → predictions/evaluations/YYYY-MM-DD.jsonl
                       ▼
              (5) score     … scoring.md に従いユーザー別に集計
                       │      → reports/scores_YYYY-MM-DD.csv
                       ▼
              (6) report    … 週次/月次 Markdown を生成 → reports/
```

| 段階 | 実行タイミング | 入力 | 出力 | 担当 |
|---|---|---|---|---|
| 収集 | 毎日 JP 08:00 / US 22:00 | X | `posts/` | Grok |
| 抽出 | 収集の後 | `posts/` | `raw/`, `rejected/` | Claude |
| validate / dedupe | 収集直後 | `raw/` | `raw/`（確定）, `rejected/` | 評価側 |
| prices | 毎日 JP 16:00 / US 07:00（JST） | 銘柄一覧 | `prices/` | 評価側 |
| evaluate | prices の直後 | `raw/`, `prices/` | `evaluations/` | 評価側 |
| score / report | 毎週土曜、毎月1日 | `evaluations/` | `reports/` | 評価側 |

### バックテストできるようにするための約束事

1. **入力は追記のみ、出力は再生成可能**: `raw/` と `prices/` を固定すれば、`evaluations/` 以降は何度作り直しても同じになる。
2. **ルールにバージョンをつける**: `evaluation_rules.md` の変更時は `rules_version` を上げ、評価結果に記録する。旧ルールと新ルールの結果を並べて比べられるようにする。
3. **時点をずらして再現できる**: `as_of` 日付を引数にとり、その日までに収集・確定していたデータだけで集計する（後から入った backfill を混ぜない）。
4. **乱数を使う処理（シミュレーション）はシード固定**。

### 最低限のテスト

- 東証の祝日（例: 2026-10-12 スポーツの日）をまたぐ予想でエントリー日がずれないか
- 株式分割をまたぐ予想で急落と誤判定しないか
- 目標到達日で打ち切ったとき、`r_ex` がその日の値になっているか
- 投稿削除済みのレコードが void にならず評価されるか
- 1投稿10銘柄の作者の n_eff が 1投稿1銘柄×10回の作者より小さくなるか

---

## 2. 週次レポート テンプレート

```markdown
# 週次レポート YYYY-MM-DD（対象: MM/DD〜MM/DD）

ルール: rules_version X.Y ／ データ時点: as_of YYYY-MM-DD

## 今週の収集
| 市場 | 新規予想 | 除外 | backfill | 収集ラグ中央値 |
|---|---|---|---|---|
| JP | | | | h |
| US | | | | h |

## 今週確定した予想
| 結果 | 件数 | 平均超過リターン |
|---|---|---|
| hit | | |
| miss | | |
| flat | | |
| void | | （理由の内訳） |

## 目立った事例（集計値のみ・推奨ではない）
- 誇大目標（implausible_target）: N件
- 削除された投稿: N件（うち評価期間中に削除: N件）

## データ品質
- スキーマ検証 NG: N件（主な理由）
- price_mismatch: N件

（注意書き: review/disclaimer.md の短縮版）
```

## 3. 月次レポート テンプレート

```markdown
# 月次レポート YYYY-MM

## 1. スコア上位（ランキング区分のみ）
| 順位 | アカウント | 区分 | n_eff | Skill（±SE） | 的中率（95%区間） | long比率 | 平均期間 |
|---|---|---|---|---|---|---|---|

※ 短期（〜1m）と中長期（3m〜）で別表にする。

## 2. 参考区分（順位なし、アルファベット順）
| アカウント | n_eff | Skill（±SE） | 的中率（95%区間） |
|---|---|---|---|

## 3. 全体の基準値
- 全予想の平均 Skill: 
- 常に long の場合の的中率（ベースライン）: 
- 実力ゼロを仮定したシミュレーションでの上位の的中率: 

## 4. 持続性チェック（四半期ごと）
前半の上位20%の、後半の平均 Skill: （0 との差の t 値）

## 5. キャリブレーション
| strength | 件数 | 的中率 |
|---|---|---|
| strong | | |
| normal | | |
| weak | | |

## 6. 候補リストの入れ替え
- 追加: 
- inactive 化: （理由）

（注意書き: review/disclaimer.md の全文版）
```
