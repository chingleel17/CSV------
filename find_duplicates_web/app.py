from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import math
import io

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for upload'}), 400

    try:
        # 獲取用戶指定的標題行
        header_line = int(request.form.get('header_line',
                                           1)) - 1  # 將行號轉換為索引（從 0 開始）

        # 將檔案內容重新讀取為 DataFrame，指定標題行
        df = pd.read_csv(io.BytesIO(file.stream.read()),
                         encoding='utf-8-sig',
                         header=header_line)

        if df.empty:
            return jsonify({'error': 'CSV 文件內容為空，無法進行處理'}), 400

        # 將 DataFrame 中的 NaN 值替換為空字串，避免 JSON 序列化錯誤
        df = df.fillna('')

        # 清理欄位名稱，去除多餘的空格、換行符號和雙引號
        df.columns = df.columns.str.strip().str.replace('\n', '').str.replace(
            '\r', '').str.replace('"', '')

        # 移除所有空白的標題欄位
        df = df.loc[:, ~df.columns.str.match(r'^Unnamed(:?\s*\d+)?$')]
        df = df.loc[:, df.columns.str.strip() != '']

        # 移除最右側連續三行以上為空的欄位
        while df.columns[-1].strip() == '' or df.iloc[:, -1].isnull().all():
            df = df.iloc[:, :-1]

        # 更嚴格地清理資料
        # 移除所有欄位皆為空的行
        df = df.dropna(how='all')

        # 將空白字串視為空值
        df = df.replace(r'^\s*$', pd.NA, regex=True)

        # 移除所有行皆為空的欄位
        df = df.dropna(axis=1, how='all')

        # 移除僅包含空白字元的行
        df = df[~df.apply(lambda row: row.astype(str).str.strip().eq('').all(),
                          axis=1)]

        # 返回前 5 行預覽和欄位名稱，以及總筆數
        preview = df.head().to_dict(orient='records')
        columns = df.columns.tolist()
        total_rows = len(df)
        return jsonify({
            'preview':
            preview,
            'columns':
            columns,
            'total_rows':
            total_rows,
            'file_content':
            df.to_csv(index=False, encoding='utf-8-sig')
        })
    except Exception as e:
        return jsonify(
            {'error': f'Unexpected error during file upload: {str(e)}'}), 500


@app.route('/check_duplicates', methods=['POST'])
def check_duplicates():
    data = request.json
    content = data.get('file_content')
    columns = data.get('columns')
    check_categories = data.get('check_categories', False)

    if not content:
        return jsonify({'error': '檔案內容為空，請上傳有效的 CSV 文件'}), 400

    if not columns:
        return jsonify({'error': '未選擇檢查的欄位，請選擇至少一個欄位進行檢查'}), 400

    try:

        # 獲取用戶指定的標題行
        header_line = data.get('header_line', 1) - 1  # 將行號轉換為索引（從 0 開始）

        # 將檔案內，指定標題行重新讀取為 DDataFrame，指定標題行
        df = pd.read_csv(io.StringIO(content),
                         header=header_line,
                         encoding='utf-8-sig')

        if df.empty:
            return jsonify({'error': 'CSV 文件內容為空，無法進行檢查'}), 400

        # 清理資料
        df = df.replace(r'^\s*$', pd.NA, regex=True)  # 將空白字串視為空值
        df = df.dropna(how='all')  # 移除所有欄位皆為空的行
        df = df.dropna(axis=1, how='all')  # 移除所有行皆為空的欄位
        df = df[~df.apply(lambda row: row.astype(str).str.strip().eq('').all(),
                          axis=1)]  # 移除僅包含空白字元的行

        # 跳過內容為空白的欄位
        non_empty_rows = df.copy()
        for col in columns:
            # 若該欄位的值為空白、NaN 或空字串，則跳過該筆資料
            non_empty_rows = non_empty_rows[~(
                non_empty_rows[col].isna()
                | non_empty_rows[col].astype(str).str.strip().eq(''))]

        # 使用過濾後的資料檢查重複
        if check_categories:
            # 獲取下拉選單中選擇的類別欄位
            selected_category_column = data.get('selected_category_column',
                                                '正確類別(子)')

            if selected_category_column in df.columns:
                # 檢查類別是否重複
                duplicates = non_empty_rows[
                    non_empty_rows.duplicated(subset=columns, keep=False)
                    & ~non_empty_rows.duplicated(subset=columns +
                                                 [selected_category_column],
                                                 keep=False)]
            else:
                duplicates = non_empty_rows[non_empty_rows.duplicated(
                    subset=columns, keep=False)]
        else:
            # 檢查指定欄位的重複資料
            duplicates = non_empty_rows[non_empty_rows.duplicated(
                subset=columns, keep=False)]

        # 更嚴格地處理 NaN 值
        # 使用 replace 將所有 NaN 值替換為 None
        duplicates = duplicates.replace({
            np.nan: None,
            float('nan'): None,
            'NaN': None,
            'nan': None
        })

        if duplicates.empty:
            return jsonify({'message': '未找到重複資料', 'duplicates': []})

        # 確保在檢查重複資料時，保留所有相關資料
        duplicates = duplicates.reset_index(drop=True)  # 重置索引，避免因過濾導致的索引錯誤

        # 在返回前，將檢查結果的總數加入回應中
        total_duplicates = len(duplicates)
        duplicates_preview = duplicates.where(pd.notnull(duplicates),
                                              None).to_dict(orient='records')

        return jsonify({
            'message': f'找到 {total_duplicates} 筆重複資料',
            'duplicates': duplicates_preview,
            'total_duplicates': total_duplicates
        })

    except pd.errors.EmptyDataError:
        return jsonify({'error': 'CSV 文件內容為空或格式不正確，請檢查文件'}), 400
    except pd.errors.ParserError as e:
        return jsonify({'error': f'CSV 文件解析錯誤: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'檢查過程中發生未預期的錯誤: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
