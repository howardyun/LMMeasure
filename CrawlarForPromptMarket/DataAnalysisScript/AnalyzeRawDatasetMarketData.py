import os
import json
import csv
import re
import os
import pandas as pd
import pickle
import time
from random import uniform

# key的排序函数
def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(_nsre, s)]


# 合并文件夹下的csv
def read_and_concat_csvs(input_folder_path):
    file_names = sorted(os.listdir(input_folder_path), key=natural_sort_key)
    # 初始化一个空的 DataFrame 列表
    df_list = []
    # 遍历目录中的所有文件
    for filename in file_names:
        if filename.endswith(".csv"):
            # 读取 CSV 文件并添加到列表中
            df = pd.read_csv(os.path.join(input_folder_path, filename))
            df_list.append(df)

    # 使用 pd.concat 合并所有 DataFrame
    combined_df = pd.concat(df_list, ignore_index=True)
    return combined_df


def process_and_split_raw_concat_urls(concat_df, output_folder_path):
    """
    读取CSV文件，提取URL中倒数第二个斜杠后的内容作为唯一键，
    统计不同键有多少对应的URL，并将不同键对应的URL分别存为不同的DataFrame并保存到指定目录。

    :param concat_df: 输入的连接好的df结构
    :param output_folder_path: 输出目录路径
    """

    # 提取URL中倒数第二个斜杠中的内容作为key
    concat_df['key'] = concat_df['URL'].apply(lambda x: x.rstrip('/').split('/')[-2])

    # 统计不同key对应的URL数量
    key_counts = concat_df['key'].value_counts()

    # 打印统计结果
    print(key_counts)

    # 创建一个字典，用于存储不同key对应的DataFrame
    key_to_df = {key: concat_df[concat_df['key'] == key] for key in concat_df['key'].unique()}

    # 创建输出目录（如果不存在）
    os.makedirs(output_folder_path, exist_ok=True)

    # 保存每个DataFrame到不同的CSV文件中
    for key, key_df in key_to_df.items():
        output_file_path = os.path.join(output_folder_path, f'{key}.csv')
        key_df.to_csv(output_file_path, index=False)
        print(f'Saved {key} DataFrame to {output_file_path}')

    print("All key DataFrames have been saved to separate CSV files.")



input_folder_path = '../Data/'
output_folder_path = '../SplitData/'
# error_file_path = 'ModelMarketDetailData/error_urls.csv'
process_and_split_raw_concat_urls(read_and_concat_csvs(input_folder_path), output_folder_path)