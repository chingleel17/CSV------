# CSV/Excel 資料清理與重複檢查工具

## 工具簡介
本工具是一套基於 FastAPI 與 pandas 的網頁應用，支援上傳 CSV 或 Excel 檔案，進行資料預覽、重複資料檢查、標點符號比對、分類正確率樞紐分析，並可將檢查結果或標註後的原始檔案匯出。

---

## 主要功能

1. **檔案上傳與預覽**
   - 支援 CSV、Excel（可選擇工作表）上傳。
   - 可自訂標題行。
   - 上傳後預覽前 5 筆資料與所有欄位。

2. **動態欄位選擇**
   - 可勾選任意欄位進行重複檢查或標點比對。
   - 可自訂顯示哪些欄位於檢查結果表格。

3. **重複資料檢查**
   - 多欄位組合檢查重複。
   - 可選擇分類欄位，檢查同資料但分類不同的情形。
   - 結果以表格顯示，可排序、可匯出。

4. **標點符號/格式檢查**
   - 任選兩欄比對標點符號，列出差異（多、少、缺漏）。
   - 結果以表格顯示，可排序、可匯出。

5. **樞紐分析**
   - 依子類別與分類正確欄位，計算正確/錯誤數量與正確率。
   - 結果以表格顯示，可排序、可匯出。

6. **匯出功能**
   - 可匯出檢查結果表格。
   - 可匯出標註後的原始檔案（自動於「修正後」欄位填 ai ）。

7. **介面特色**
   - 支援 loading 指示、表格排序、欄位顯示切換。
   - 支援 Docker 快速部署。

---

## 使用方式

### 1. 本地執行

1. 安裝 Python 3.8 以上。
2. 安裝相依套件：
   ```bash
   pip install -r requirements.txt
   ```
3. 啟動服務：
   ```bash
   python app.py
   ```
4. 瀏覽器開啟 http://127.0.0.1:5000

### 2. Docker 執行

1. 安裝 Docker。
2. 建立映像檔並啟動：
   ```bash
   docker build -t csv_checker .
   docker run -p 5000:5000 csv_checker
   ```
3. 瀏覽器開啟 http://127.0.0.1:5000

---

## 目錄結構

- `app.py`：主程式（FastAPI）
- `find_duplicates_web/templates/index.html`：前端頁面
- `find_duplicates_web/static/`：靜態資源
- `logger_services.py`：日誌
- `fill_category_ids.py`、`find_duplicates.py`：進階批次工具
- `storage/`：匯出結果、日誌

---

## API 端點簡述

- `POST /upload`：上傳檔案，回傳預覽、欄位、總筆數
- `POST /check_duplicates`：檢查重複資料
- `POST /generate_pivot`：產生樞紐分析表

---

## 注意事項
- 請確認上傳檔案格式正確（UTF-8 編碼最佳）。
- Excel 請選擇正確工作表。
- 若「修正後」欄位為空，匯出時會自動填入 ai。
- 匯出檔案為 UTF-8 編碼 CSV。

---

## 範例流程

1. 上傳 CSV 或 Excel 檔案，選擇標題行與（如為 Excel）工作表。
2. 預覽資料，勾選要檢查的欄位。
3. 點擊「檢查重複資料」或「檢查格式標點符號」。
4. 檢查結果可排序、切換顯示欄位、匯出。
5. 點擊「匯出更新檔案」可取得標註後的原始資料。
6. 使用樞紐分析工具可計算分類正確率。

---

## 相依套件
- fastapi
- pandas
- numpy
- jinja2
- uvicorn
- openpyxl
- colorlog

