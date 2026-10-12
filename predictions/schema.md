# 予想抽出スキーマ（Prediction Extraction Schema）

検証可能な予想だけを構造化するための定義です。

## 抽出条件（必須）

以下を**すべて満たす**投稿だけを「検証可能な予想」として記録する：

1. **銘柄が特定できる**（ティッカー or 明確な社名）
2. **方向が明確**（買い / 売り / 上昇期待 / 下落警戒 など）
3. **時間軸が読み取れる**（今週 / 1ヶ月 / 決算まで / 目標価格到達 など）

曖昧な「注目」「上がりそう」だけの投稿は除外。

## JSONフィールド

```json
{
  "id": "一意ID（post_id + ticker）",
  "post_id": "X投稿ID",
  "post_url": "https://x.com/...",
  "author": "@username",
  "posted_at": "ISO8601",
  "ticker": "5803 or NVDA",
  "market": "JP or US",
  "direction": "long | short | neutral",
  "target_price": null or number,
  "current_price_at_post": null or number,
  "time_horizon": "1w | 2w | 1m | 3m | earnings | unspecified",
  "raw_text": "元の予想部分テキスト",
  "confidence_note": "投稿の強さ（一度しか言わない、目標株価など）",
  "status": "open | hit | miss | expired",
  "evaluated_at": null,
  "actual_move_pct": null,
  "notes": ""
}
```

## スコアリング案（後で適用）

- 方向一致: +1
- 目標価格到達（期間内）: +1
- 大きく外れた場合: 0 or -0.5
- サンプル数が少ない人は「参考」扱い
