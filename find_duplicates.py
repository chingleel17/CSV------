import pandas as pd
import os
import numpy as np  # 修正錯誤
import re

path = "C:/users/kere4/Downloads/{file_name}"


def find_duplicates(input_file, output_file, header_line=1):
    # 讀取CSV文件，確保正確處理中文編碼
    header_line = int(header_line) - 1  # 將行號轉換為索引（從 0 開始）
    df = pd.read_csv(input_file, encoding='utf-8-sig', header=header_line)
    # 清理欄位名稱，去除多餘的空格和換行符號
    df.columns = df.columns.str.strip().str.replace('\n',
                                                    '').str.replace('\r', '')
    # 按 Q 和遊戲名稱分組，找出重複的記錄
    # duplicates = df[df.duplicated(subset=['Q', '遊戲名稱'], keep=False)]
    duplicates = df[df.duplicated(subset=['玩家問題', '遊戲名稱'], keep=False)]

    print(f"總共找到 {len(duplicates)} 條重複記錄")
    if len(duplicates) > 0:
        output_file = path.format(file_name=output_file)
        # 將這些記錄保存到新的CSV文件
        duplicates.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"重複記錄已保存到: {output_file}")

    return duplicates


def find_duplicates_with_different_categories(input_file,
                                              output_file,
                                              header_line=1):

    header_line = int(header_line) - 1  # 將行號轉換為索引（從 0 開始）
    # 讀取CSV文件，確保正確處理中文編碼
    df = pd.read_csv(input_file, encoding='utf-8-sig', header=header_line)
    # 清理欄位名稱，去除多餘的空格和換行符號
    df.columns = df.columns.str.strip().str.replace('\n',
                                                    '').str.replace('\r', '')

    # 排除細項分類為空的記錄s
    #df = df[df['細項分類'].notna() & (df['細項分類'] != '')]
    df = df[df['正確類別(子)'].notna() & (df['正確類別(子)'] != '')]
    # 按案件編號分組，找出重複的記錄
    #duplicates = df[df.duplicated(subset=['Q'], keep=False) & ~df.duplicated(subset=['Q', '細項分類'], keep=False)]
    duplicates = df[df.duplicated(subset=['玩家問題'], keep=False)
                    & ~df.duplicated(subset=['玩家問題', '正確類別(子)'], keep=False)]
    print(f"總共找到 {len(duplicates)} 條重複但類別不同的記錄")

    if len(duplicates) > 0:
        output_file = path.format(file_name=output_file)
        # 將這些記錄保存到新的CSV文件
        duplicates.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"重複記錄已保存到: {output_file}")
    else:
        print("沒有重複的紀錄")
    return duplicates


def update_original_file(input_file, duplicates, header_line=1):
    # 讀取原始文件

    header_line = int(header_line) - 1  # 將行號轉換為索引（從 0 開始）
    df = pd.read_csv(input_file, encoding='utf-8-sig', header=header_line)
    # 清理欄位名稱，去除多餘的空格和換行符號
    df.columns = df.columns.str.strip().str.replace('\n',
                                                    '').str.replace('\r', '')

    # 更新原始文件中的數據
    for index, row in duplicates.iterrows():
        df.loc[(df['玩家問題'] == row['玩家問題']) & (df['正確類別(子)'] != row['正確類別(子)']),
               '正確類別(子)'] = row['正確類別(子)']

    # 將更新後的數據寫回原始文件
    df.to_csv(input_file, index=False, encoding='utf-8-sig')

    print(f"原始文件 {input_file} 已更新。")


def remove_duplicates(input_file, output_file, header_line=1):
    # 讀取CSV文件，確保正確處理中文編碼
    header_line = int(header_line) - 1  # 將行號轉換為索引（從 0 開始）
    df = pd.read_csv(input_file, encoding='utf-8-sig', header=header_line)
    # 清理欄位名稱，去除多餘的空格和換行符號
    df.columns = df.columns.str.strip().str.replace('\n',
                                                    '').str.replace('\r', '')

    # 將細項分類為空的值替換為 np.nan，便於排序
    df['細項分類'] = df['細項分類'].replace('', np.nan)

    # 按 Q 和遊戲名稱分組，並按細項分類是否為空進行排序
    # 保留細項分類不為空的第一條記錄
    df_unique = df.sort_values('細項分類', na_position='last') \
                 .drop_duplicates(subset=['Q', '遊戲名稱'], keep='first') \
                 .copy()

    # 將 NaN 值重新替換回空字符串
    df_unique['細項分類'] = df_unique['細項分類'].fillna('')

    # 重新排序並更新流水號
    df_unique = df_unique.sort_index()
    df_unique.loc[:, '流水號'] = range(1, len(df_unique) + 1)

    # 判斷是否有重複資料被刪除
    if len(df) > len(df_unique):
        output_file = path.format(file_name=output_file)
        # 將不重複的記錄保存到新的CSV文件
        df_unique.to_csv(output_file, index=False, encoding='utf-8-sig')

        print(f"不重複的記錄已保存到: {output_file}")
        print(f"原始記錄數: {len(df)}")
        print(f"處理後記錄數: {len(df_unique)}")
        print(f"刪除的重複記錄數: {len(df) - len(df_unique)}")
    else:
        print("沒有重複的記錄，無需保存到新文件。")


def remove_illegal_characters(df):
    # 定義一個函式來移除非法字元
    def clean_cell(value):
        if isinstance(value, str):
            # 移除非法字元
            return re.sub(r'[\x00-\x1F\x7F-\x9F]', '', value)
        return value

    # 對整個 DataFrame 的每個元素應用清理函式
    return df.applymap(clean_cell)


def normalize_text(df, columns):
    """
    定義一個函式來標準化指定欄位的文字內容，移除多餘的空格和換行符號。
    """
    for col in columns:
        df[col] = df[col].apply(lambda x: re.sub(r'\s+', '', x)
                                if isinstance(x, str) else x)
    return df


def find_differences(file_a, file_b, output_file):
    # 讀取兩個 CSV 檔案
    df_a = pd.read_csv(file_a, nrows=2600)  # 只讀取前 2600 筆資料
    df_b = pd.read_csv(file_b, nrows=2600)  # 只讀取前 2600 筆資料

    # 將欄位名稱對應
    df_a.rename(columns={'資料來源id': '編號', 'A': '客服答覆'}, inplace=True)

    # 檢查是否存在指定欄位，若存在則標準化文字內容
    # 移除 A 檔案中 A 或 客服答覆 為空白的資料
    if 'A' in df_a.columns:
        df_a = normalize_text(df_a, ['A'])
        df_a = df_a[~(df_a['A'].isna()
                      | df_a['A'].astype(str).str.strip().eq(''))]
    if '客服答覆' in df_a.columns:
        df_a = normalize_text(df_a, ['客服答覆'])
        df_a = df_a[~(df_a['客服答覆'].isna()
                      | df_a['客服答覆'].astype(str).str.strip().eq(''))]
    # 移除 B 檔案中 A 或 客服答覆 為空白的資料
    if 'A' in df_b.columns:
        df_b = normalize_text(df_b, ['A'])
        df_b = df_b[~(df_b['A'].isna()
                      | df_b['A'].astype(str).str.strip().eq(''))]
    if '客服答覆' in df_b.columns:
        df_b = normalize_text(df_b, ['客服答覆'])
        df_b = df_b[~(df_b['客服答覆'].isna()
                      | df_b['客服答覆'].astype(str).str.strip().eq(''))]

    # 確保合併的欄位型別一致
    df_a['編號'] = df_a['編號'].astype(str)
    df_b['編號'] = df_b['編號'].astype(str)

    # 找出 A 檔案有但 B 檔案沒有的編號
    a_not_in_b = df_a[~df_a['編號'].isin(df_b['編號'])][['編號', '流水號']]
    a_not_in_b['來源'] = 'A 檔案'

    # 找出 B 檔案有但 A 檔案沒有的編號
    b_not_in_a = df_b[~df_b['編號'].isin(df_a['編號'])][['編號', '流水號']]
    b_not_in_a['來源'] = 'B 檔案'

    # 比對相同編號但玩家問題不同的記錄
    merged = pd.merge(df_a, df_b, on='編號', suffixes=('_A', '_B'))
    different_q = merged[merged['客服答覆_A'] != merged['客服答覆_B']][[
        '編號', '流水號_A', '流水號_B', '客服答覆_A', '客服答覆_B'
    ]]

    # 合併結果
    differences = pd.concat([a_not_in_b, b_not_in_a], ignore_index=True)

    # 將不同玩家問題的記錄加入結果
    different_q['來源'] = '玩家問題不同'
    differences = pd.concat([differences, different_q], ignore_index=True)

    # 清理非法字元
    differences = remove_illegal_characters(differences)

    # 將結果輸出到檔案
    differences.to_excel(output_file, index=False)
    print(f"差異結果已保存到: {output_file}")


if __name__ == "__main__":
    # input_file = "C:/users/kere4/Downloads/AI文本與測試-真實案例蒐集202503-2.csv"  # 輸入文件名
    # input_file = "C:/users/kere4/Downloads/AI文本與測試-AI案例複審.csv"  # 輸入文件名
    #input_file = "D:/ching/文件資料/技術部共用/AI測試資料/AI文本與測試-真實案例蒐集202503.csv"  # 輸入文件名
    input_file = "D:/ching/文件資料/技術部共用/AI測試資料/AI知識庫.csv"  # 輸入文件名
    #input_file = "output.csv"  # 輸出文件名
    #input_file = "D:/ching/文件資料/技術部共用/AI測試資料/分類資料庫-新.csv"  # 輸入文件名
    output_file = "duplicates.csv"  # 輸出文件名
    a_file = "D:/下載/AI文本與測試-AI資料庫.csv"  # 輸入文件名
    b_file = "D:/下載/AI文本與測試-AI案例複審.csv"  # 輸入文件名
    if not os.path.exists(input_file):
        print(f"錯誤：找不到輸入文件 {input_file}")
    else:
        # duplicates = find_duplicates(input_file, output_file, header_line=1)

        # 更新原始文件
        #update_original_file(input_file, duplicates)
        # remove_duplicates(input_file, 'output.csv')
        # 查找重複但類別不同的記錄
        # duplicates_with_different_categories = find_duplicates_with_different_categories(
        #     input_file, "duplicates_with_different_categories.csv")
        find_differences(a_file, b_file, 'storage/differences_output.xlsx')
