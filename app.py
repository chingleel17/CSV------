from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
import numpy as np
import io
from pydantic import BaseModel

app = FastAPI(title="Find Duplicates Web")
app.mount("/static",
          StaticFiles(directory="find_duplicates_web/static"),
          name="static")

templates = Jinja2Templates(directory="find_duplicates_web/templates")


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})


@app.post('/upload')
async def upload_file(file: UploadFile, header_line: int = Form(1)):
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content),
                         encoding='utf-8-sig',
                         header=header_line - 1)

        if df.empty:
            return JSONResponse(content={"error": "CSV 文件內容為空，無法進行處理"},
                                status_code=400)

        # 清理資料
        df = df.fillna('')
        df.columns = df.columns.str.strip().str.replace('\n', '').str.replace(
            '\r', '').str.replace('"', '')
        df = df.loc[:, ~df.columns.str.match(r'^Unnamed(:?\s*\d+)?$')]
        df = df.loc[:, df.columns.str.strip() != '']
        df = df.dropna(how='all')
        df = df.replace(r'^\s*$', pd.NA, regex=True)
        df = df.dropna(axis=1, how='all')
        df = df[~df.apply(lambda row: row.astype(str).str.strip().eq('').all(),
                          axis=1)]

        preview = df.head().to_dict(orient='records')
        columns = df.columns.tolist()
        total_rows = len(df)

        return {
            "preview": preview,
            "columns": columns,
            "total_rows": total_rows,
            "file_content": df.to_csv(index=False, encoding='utf-8-sig')
        }
    except Exception as e:
        return JSONResponse(content={
            "error":
            f"Unexpected error during file upload: {str(e)}"
        },
                            status_code=500)


class CheckDuplicatesRequest(BaseModel):
    file_content: str
    columns: list[str]
    check_categories: bool = False
    selected_category_column: str = None


class GeneratePivotRequest(BaseModel):
    file_content: str
    subcategory_column: str
    correct_column: str


@app.post('/check_duplicates')
async def check_duplicates(request: CheckDuplicatesRequest):
    try:
        df = pd.read_csv(io.StringIO(request.file_content),
                         encoding='utf-8-sig')

        if df.empty:
            return JSONResponse(content={"error": "CSV 文件內容為空，無法進行檢查"},
                                status_code=400)
        df = df.dropna(how='all')  # 移除所有欄位皆為空的行
        df = df[~df.apply(lambda row: row.astype(str).str.strip().eq('').all(),
                          axis=1)]  # 移除僅包含空白字元的行
        non_empty_rows = df.copy()
        for col in request.columns:
            # 若該欄位的值為空白、NaN 或空字串，則跳過該筆資料
            non_empty_rows = non_empty_rows[~(
                non_empty_rows[col].isna()
                | non_empty_rows[col].astype(str).str.strip().eq(''))]

        if request.check_categories and request.selected_category_column:
            if request.selected_category_column not in df.columns:
                return JSONResponse(content={
                    'error':
                    f'選擇的類別欄位 "{request.selected_category_column}" 不存在，請檢查輸入'
                },
                                    status_code=400)

            duplicates = non_empty_rows[
                non_empty_rows.duplicated(subset=request.columns, keep=False)
                &
                ~non_empty_rows.duplicated(subset=request.columns +
                                           [request.selected_category_column],
                                           keep=False)]
        else:
            # 檢查指定欄位的重複資料
            duplicates = non_empty_rows[non_empty_rows.duplicated(
                subset=request.columns, keep=False)]
            print(duplicates)

        # 更嚴格地處理 NaN 值
        # 使用 replace 將所有 NaN 值替換為 None
        duplicates = duplicates.replace({
            np.nan: None,
            float('nan'): None,
            'NaN': None,
            'nan': None
        })
        if duplicates.empty:
            return {"message": "未找到重複資料", "duplicates": []}
        # 確保在檢查重複資料時，保留所有相關資料
        duplicates = duplicates.reset_index(drop=True)  # 重置索引，避免因過濾導致的索引錯誤

        # 在返回前，將檢查結果的總數加入回應中
        total_duplicates = len(duplicates)
        duplicates_preview = duplicates.where(pd.notnull(duplicates),
                                              None).to_dict(orient='records')

        return {
            "message": f"找到 {len(duplicates)} 筆重複資料",
            "duplicates": duplicates.to_dict(orient='records')
        }
    except Exception as e:
        return JSONResponse(content={"error": f"檢查過程中發生錯誤: {str(e)}"},
                            status_code=500)


@app.post('/generate_pivot')
async def generate_pivot(request: GeneratePivotRequest):
    try:
        df = pd.read_csv(io.StringIO(request.file_content),
                         encoding='utf-8-sig')

        if df.empty:
            return JSONResponse(content={"error": "CSV 文件內容為空，無法進行處理"},
                                status_code=400)

        if request.subcategory_column not in df.columns or request.correct_column not in df.columns:
            return JSONResponse(content={
                "error":
                f"缺少必要欄位: {request.subcategory_column} 或 {request.correct_column}"
            },
                                status_code=400)

        pivot_table = df.pivot_table(index=request.subcategory_column,
                                     columns=request.correct_column,
                                     aggfunc='size',
                                     fill_value=0).reset_index()

        pivot_table['總計'] = pivot_table.get('正確', 0) + pivot_table.get('錯誤', 0)
        pivot_table['分類'] = (pivot_table.get('正確', 0) / pivot_table['總計'] *
                             100).round(2).astype(str) + '%'

        total_row = {
            request.subcategory_column:
            '總計',
            '正確':
            pivot_table.get('正確', 0).sum(),
            '錯誤':
            pivot_table.get('錯誤', 0).sum(),
            '總計':
            pivot_table['總計'].sum(),
            '分類': (pivot_table.get('正確', 0).sum() / pivot_table['總計'].sum() *
                   100).round(2).astype(str) + '%'
        }
        # 將子類別欄位進行排序（排除總計行）
        pivot_table = pivot_table.sort_values(
            by=[request.subcategory_column],
            key=lambda col: col.map(lambda x: ''
                                    if x == '總計' else x)  # 確保 "總計" 行在最後
        ).reset_index(drop=True)

        pivot_table = pd.concat(
            [pivot_table, pd.DataFrame([total_row])], ignore_index=True)
        # 調整輸出順序
        pivot_table = pivot_table[[
            request.subcategory_column, '正確', '錯誤', '總計', '分類'
        ]]

        # 將 NaN 值替換為 None，避免 JSON 序列化錯誤
        pivot_table = pivot_table.where(pd.notnull(pivot_table), None)

        return {
            "message": "樞紐分析完成",
            "pivot_table": pivot_table.to_dict(orient='records')
        }
    except Exception as e:
        return JSONResponse(content={"error": f"處理過程中發生錯誤: {str(e)}"},
                            status_code=500)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
