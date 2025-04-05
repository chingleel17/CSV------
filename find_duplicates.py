import pandas as pd
import os
import numpy as np

path = "C:/users/kere4/Downloads/{file_name}"


def find_duplicates(input_file, output_file, header_line=1):
    # 讀取CSV文件，確保正確處理中文編碼
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
    # 讀取CSV文件，確保正確處理中文編碼
    df = pd.read_csv(input_file, encoding='utf-8-sig')
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


if __name__ == "__main__":
    # input_file = "C:/users/kere4/Downloads/AI文本與測試-真實案例蒐集202503-2.csv"  # 輸入文件名
    input_file = "C:/users/kere4/Downloads/AI文本與測試-AI案例複審.csv"  # 輸入文件名
    #input_file = "D:/ching/文件資料/技術部共用/AI測試資料/AI文本與測試-真實案例蒐集202503.csv"  # 輸入文件名
    #input_file = "D:/ching/文件資料/技術部共用/AI測試資料/AI知識庫.csv"  # 輸入文件名
    #input_file = "output.csv"  # 輸出文件名
    #input_file = "D:/ching/文件資料/技術部共用/AI測試資料/分類資料庫-新.csv"  # 輸入文件名
    output_file = "duplicates.csv"  # 輸出文件名

    if not os.path.exists(input_file):
        print(f"錯誤：找不到輸入文件 {input_file}")
    else:
        duplicates = find_duplicates(input_file, output_file, header_line=1)

        # 更新原始文件
        #update_original_file(input_file, duplicates)
        #remove_duplicates(input_file, 'output.csv')
        # 查找重複但類別不同的記錄
        # duplicates_with_different_categories = find_duplicates_with_different_categories(
        #     input_file, "duplicates_with_different_categories.csv")
