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
        df = pd.read_csv(io.BytesIO(content), encoding='utf-8-sig')

        # 將 DataFrame 中的 NaN 值替換為空字串，避免 JSON 序列化錯誤
        df = df.fillna('')

        # 返回前 5 行預覽和欄位名稱，以及總筆數
        preview = df.head().to_dict(orient='records')
        columns = df.columns.tolist()
        total_rows = len(df)
        return jsonify({'preview': preview, 'columns': columns, 'total_rows': total_rows, 'file_content': df.to_csv(index=False, encoding='utf-8-sig')})
    except Exception as e:
        return jsonify({'error': f'Unexpected error during file upload: {str(e)}'}), 500

@app.route('/check_duplicates', methods=['POST'])
def check_duplicates():
    data = request.json
    content = data.get('file_content')
    columns = data.get('columns')
    check_categories = data.get('check_categories', False)
    print(f"Received columns: {columns}")
    print(f"content: {content}")
    try:
        # 將檔案內容重新讀取為 DataFrame
        df = pd.read_csv(io.StringIO(content), encoding='utf-8-sig')
        df = df.fillna('')

        if check_categories:
            # 檢查類別是否重複
            duplicates = df[df.duplicated(subset=columns, keep=False)]
        else:
            # 檢查指定欄位的重複資料
            duplicates = df[df.duplicated(subset=columns, keep=False)]

        duplicates_preview = duplicates.to_dict(orient='records')
        return jsonify({'message': 'Duplicates found', 'duplicates': duplicates_preview})
    except Exception as e:
        return jsonify({'error': f'Unexpected error during duplicate check: {str(e)})'}), 500

if __name__ == '__main__':
    app.run(debug=True)
