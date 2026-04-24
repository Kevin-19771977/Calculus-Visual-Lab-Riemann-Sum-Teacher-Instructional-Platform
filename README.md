# 微積分視覺實驗室｜黎曼和教學平台

這是 Streamlit 版的黎曼和教學平台組合包。

## 內容
- `app.py`：主程式
- `requirements.txt`：需要安裝的套件
- `README.md`：使用說明

## 執行方式
1. 先安裝套件
   ```bash
   pip install -r requirements.txt
   ```
2. 啟動程式
   ```bash
   streamlit run app.py
   ```

## 功能摘要
- 左端點法、右端點法、中點法、隨機取點法
- 支援較友善的函數輸入，例如 `x^2`、`2x`、`3(x+1)`、`|x|`
- 支援 `ln(x)`、`log10(x)`、`log2(x)`
- 四種方法比較與誤差分析
- 區間 `a`、`b` 左右並排顯示

## 注意事項
- 若使用 `ln(x)`、`log10(x)`、`log2(x)`，請設定區間滿足 `x > 0`
- 若使用 `sqrt(x)`，請注意根號內需合法
