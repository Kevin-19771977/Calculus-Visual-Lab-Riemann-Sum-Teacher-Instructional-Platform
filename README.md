# FTC Streamlit Research UI Package

## 專案名稱
Interactive Visualization Tool for the First Fundamental Theorem of Calculus

## 內容
這是一個以 **微積分第一基本定理** 為主題的 Streamlit 網頁教學平台原型，重點功能包括：

- 原函數 `f(x)` 圖形顯示
- 從固定起點 `a` 到目前位置 `x` 的累積面積
- 累積函數 `A(x)=∫_a^x f(t)dt`
- 差商近似 `[A(x+Δx)-A(x)] / Δx`
- 與 `f(x)` 的即時比較
- 預設函數按鈕版介面
- 教學平台風格首頁與數學式展示
- 教學引導頁與使用說明頁

---

## 本機執行方式

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Streamlit Community Cloud 部署方式

1. 將本資料夾上傳到 GitHub
2. 登入 Streamlit Community Cloud
3. 選擇你的 GitHub repository
4. Main file path 填入：

```bash
app.py
```

5. 按下 Deploy

---

## 建議資料夾結構

```text
FTC_Streamlit_Research_UI_Package/
├─ app.py
├─ requirements.txt
├─ README.md
├─ .gitignore
└─ .streamlit/
   └─ config.toml
```

---

## 後續可升級方向

- 學生作答區
- 前測／後測頁面
- 問卷頁
- CSV 存檔
- 教師查看結果頁
- 圖片匯出與紀錄下載
