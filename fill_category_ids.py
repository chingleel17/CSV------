import pandas as pd

# 主類別與細項分類對應表
category_map = {
    "帳號相關": {
        "帳密查詢或遺失": "1-1",
        "帳號轉移": "1-2",
        "帳號註銷": "1-3",
        "帳號綁定或解綁": "1-4",
        "帳號封鎖或解鎖": "1-5",
        "其他帳號相關": "1-6",
        "查詢帳密": "1-1",
        "帳號凍結或解凍": "1-5",
    },
    "儲值相關": {
        "儲值掉單": "2-1",
        "無法儲值": "2-2",
        "申請退款": "2-3",
        "如何儲值": "2-4",
        "其他儲值相關": "2-5",
    },
    "活動相關": {
        "序號或活動內容": "3-1",
        "獎勵沒拿到": "3-2",
        "其他活動相關": "3-3",
    },
    "遊戲內容": {
        "玩法說明": "4-1",
        "數值設定": "4-2",
    },
    "回報BUG": {
        "遊戲BUG": "5-1",
    },
    "物品消失": {
        "貨幣消失": "6-1",
        "道具消失": "6-2",
    },
    "盜用及詐騙": {
        "盜用與詐騙": "7-1",
        "詐騙": "7-1",
    },
    "建議": {
        "建議": "8-1",
    },
    "外掛及檢舉": {
        "非法程式": "9-1",
        "洗頻辱罵": "9-2",
        "其他違規": "9-3",
    },
    "更新進度": {
        "改版進度": "10-1",
    },
    "連線相關": {
        "延遲閃退": "11-1",
        "無法登入": "11-2",
    },
    "安裝及下載": {
        "安裝下載問題": "12-1",
        "下載問題": "12-1",
    },
    "稱讚聊天": {
        "稱讚與聊天": "13-1",
        "聊天": "13-1",
    },
    "其他": {
        "意義不明": "14-1",
        "廣告": "14-2",
        "其他": "14-3",
    },
    "無法分類": {
        "無法分類": "",
    },
    "抱怨": {
        "抱怨": "",
    }
}


def fill_category_ids(input_csv, output_csv):
    df = pd.read_csv(input_csv, encoding='utf-8-sig')
    df.columns = df.columns.str.strip().str.replace('\n',
                                                    '').str.replace('\r', '')

    def get_ids(row):
        main = str(row.get('問題類型', '')).strip()
        sub = str(row.get('細項分類', '')).strip()
        for main_cat, sub_map in category_map.items():
            if main == main_cat and sub in sub_map:
                code = sub_map[sub]
                if '-' in code:
                    main_id, sub_id = code.split('-')
                    return pd.Series([main_id, sub_id])
                elif code:
                    return pd.Series([code, ''])
        return pd.Series(['', ''])

    df[['主類別編號', '子類別編號']] = df.apply(get_ids, axis=1)
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"已補齊主類別編號與子類別編號，儲存於：{output_csv}")


# 範例用法：
fill_category_ids('D:\\下載\\AI文本與測試-AI資料庫.csv', 'storage\\id替換.csv')
