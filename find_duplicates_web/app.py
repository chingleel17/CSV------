from flask import Flask, request, jsonify, render_template
import pandas as pd
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
        # 確保檔案物件可讀取
        content = file.stream.read()
        if not content:
            return jsonify({'error': 'Uploaded file is empty'}), 400

        try:
            df = pd.read_csv(io.BytesIO(content), encoding='utf-8-sig')
        except pd.errors.EmptyDataError:
            return jsonify({'error': 'CSV 文件內容為空或格式不正確，請檢查文件'}), 400
        except pd.errors.ParserError as e:
            return jsonify({'error': f'CSV 文件解析錯誤: {str(e)}'}), 400

        if df.empty:
            return jsonify({'error': 'CSV 文件內容為空，無法進行處理'}), 400

        # 將 DataFrame 中的 NaN 值替換為空字串，避免 JSON 序列化錯誤
        df = df.fillna('')

        # 清理欄位名稱，去除多餘的空格、換行符號和雙引號
        df.columns = df.columns.str.strip().str.replace('\n', '').str.replace('\r', '').str.replace('"', '')

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
        # 將檔案內容重新讀取為 DataFrame
        df = pd.read_csv(io.StringIO(content), encoding='utf-8-sig')

        if df.empty:
            return jsonify({'error': 'CSV 文件內容為空，無法進行檢查'}), 400

        df = df.fillna('')

        if check_categories:
            # 獲取下拉選單中選擇的類別欄位
            selected_category_column = data.get('selected_category_column', '正確類別(子)')

            # 檢查類別是否重複
            duplicates = df[df.duplicated(subset=['玩家問題'], keep=False)
                            & ~df.duplicated(subset=['玩家問題', selected_category_column], keep=False)]
        else:
            # 檢查指定欄位的重複資料
            duplicates = df[df.duplicated(subset=columns, keep=False)]

        if duplicates.empty:
            return jsonify({'message': '未找到重複資料', 'duplicates': []})

        duplicates_preview = duplicates.to_dict(orient='records')
        return jsonify({'message': '找到重複資料', 'duplicates': duplicates_preview})
    except pd.errors.EmptyDataError:
        return jsonify({'error': 'CSV 文件內容為空或格式不正確，請檢查文件'}), 400
    except pd.errors.ParserError as e:
        return jsonify({'error': f'CSV 文件解析錯誤: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'檢查過程中發生未預期的錯誤: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
