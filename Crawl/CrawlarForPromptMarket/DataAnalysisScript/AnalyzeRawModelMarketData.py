import os
import json
import csv
import re
import os
import textwrap

import pandas as pd
import pickle
import time
from random import uniform

from matplotlib import pyplot as plt


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


def convert_num(text):
    if pd.isnull(text):
        return 0
    text = str(text)
    if 'k' in text:
        return float(text.replace('k', '')) * 1_000
    elif 'M' in text:
        return float(text.replace('M', '')) * 1_000_000
    else:
        return float(text)


# 模型类型数量前20的种类，对应的下载数量，喜爱数量
def top_20_model_type_analyze(data, pdf_file_path='./ResultFig/model_type_stats_top20.pdf'):
    # 模型类型的频率分布
    # 按model_type分组并统计数量，获取数量最多的前20个model_type
    top_20_model_types_by_count = data['model_type'].value_counts().nlargest(20).reset_index()
    top_20_model_types_by_count.columns = ['model_type', 'count']

    # 计算这些前20个model_type的总下载量和总点赞量
    top_20_model_types_stats = data[data['model_type'].isin(top_20_model_types_by_count['model_type'])].groupby(
        'model_type').agg(
        total_downloads=('download_num', 'sum'),
        total_likes=('like_num', 'sum')
    ).reset_index()

    # 将统计结果与模型类型数量合并
    top_20_model_types_stats = pd.merge(top_20_model_types_by_count, top_20_model_types_stats, on='model_type')

    # 显示结果
    print("按模型分布数量前20的model_type统计下载数量及点赞数量:")
    print(top_20_model_types_stats)

    plt.rcParams.update({'font.size': 14})

    # 可视化前20个模型类型的统计结果
    fig, ax1 = plt.subplots(figsize=(14, 10))
    plt.subplots_adjust(left=0.3)  # 增加左边距

    # 创建柱状图 - 模型数量
    ax1.barh(top_20_model_types_stats['model_type'], top_20_model_types_stats['count'], color='skyblue',
             label='Model Count')
    ax1.set_xlabel('Count')
    ax1.set_ylabel('Model Type')
    ax1.set_title('Top 20 Model Types by Count, Downloads, and Likes')

    # 创建次坐标轴 - 下载量和点赞量
    ax2 = ax1.twiny()
    ax2.plot(top_20_model_types_stats['total_downloads'], top_20_model_types_stats['model_type'], 'r--',
             label='Total Downloads')
    ax2.plot(top_20_model_types_stats['total_likes'], top_20_model_types_stats['model_type'], 'g--',
             label='Total Likes')
    ax2.set_xlabel('Total Downloads and Likes')

    # 添加图例
    fig.legend(loc="upper right", bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)

    # 保存图表为PDF文件
    plt.savefig(pdf_file_path)

    plt.show()


# 模型类型数量前20的下载量，对应的下载数量，喜爱数量
def top_20_download_Url(data, output_file_path='./ResultFig/top_20_urls.csv'):
    # 获取按下载量排序的前20个URL
    top_20_urls = data.nlargest(20, 'download_num')[['URL', 'download_num', 'like_num']]

    # 显示前20个URL
    print("按下载量排序的前20个URL:")
    print(top_20_urls)
    top_20_urls.to_csv(output_file_path, index=False)


def top_20_company_base_on_download_num(data, pdf_file_path_entry='./ResultFig/top_20_companies_entry_stats.pdf',
                                        pdf_file_path_model_type='./ResultFig/top_20_companies_model_types.pdf'):
    # 提取公司名（位于倒数第一个'//'和下一个'/'之间的部分）
    data['company'] = data['URL'].apply(lambda x: x.rstrip('/').split('/')[-2])

    # 统计每个公司总的下载量
    company_downloads = data.groupby('company')['download_num'].sum().reset_index()

    # 获取下载量最高的前20个公司
    top_20_companies = company_downloads.nlargest(20, 'download_num')

    # 统计这些公司的不同model_type数量
    company_model_types = data[data['company'].isin(top_20_companies['company'])].groupby('company')[
        'model_type'].nunique().reset_index()

    # 统计这些公司的总数据条目数
    company_data_counts = data[data['company'].isin(top_20_companies['company'])].groupby('company').size().reset_index(
        name='total_entries')

    # 合并三个统计结果
    top_20_companies_stats = pd.merge(top_20_companies, company_model_types, on='company')
    top_20_companies_stats = pd.merge(top_20_companies_stats, company_data_counts, on='company')
    top_20_companies_stats.columns = ['company', 'total_downloads', 'unique_model_types', 'total_entries']

    # 显示结果
    print("下载量最高的前20个公司及其不同模型类型数量和总数据条目数:")
    print(top_20_companies_stats)

    # 设置字体大小
    plt.rcParams.update({'font.size': 14})

    # 可视化结果
    fig, ax1 = plt.subplots(figsize=(14, 10))

    # 绘制下载量柱状图
    ax1.barh(top_20_companies_stats['company'], top_20_companies_stats['total_downloads'], color='skyblue',
             label='Total Downloads')
    ax1.set_xlabel('Total Downloads')
    ax1.set_ylabel('Company')
    ax1.set_title('Top 20 Companies by Total Downloads, Unique Model Types, and Total Entries')

    # 绘制次坐标轴 - 总数据条目数
    ax2 = ax1.twiny()
    ax2.plot(top_20_companies_stats['total_entries'], top_20_companies_stats['company'], 'g--', label='Total Entries')
    ax2.set_xlabel('Total Entries')

    # 添加图例
    fig.legend(loc="upper right", bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)

    # 保存图表为PDF文件
    plt.savefig(pdf_file_path_entry)
    plt.show()

    # 单独绘制不同模型类型数量的柱状图
    fig, ax3 = plt.subplots(figsize=(14, 10))
    ax3.barh(top_20_companies_stats['company'], top_20_companies_stats['unique_model_types'], color='orange', alpha=0.5,
             label='Unique Model Types')
    ax3.set_xlabel('Unique Model Types')
    ax3.set_ylabel('Company')
    ax3.set_title('Top 20 Companies by Unique Model Types')
    ax3.invert_yaxis()

    # 添加图例
    ax3.legend(loc="upper right")

    # 保存图表为PDF文件
    plt.savefig(pdf_file_path_model_type)
    plt.show()


# 示例路径
input_folder_path = 'RawData/ModelMarketRawUrlData'
data = read_and_concat_csvs(input_folder_path)

# 去重
data = data.drop_duplicates(subset='URL')

# 应用转换函数到download_num和like_num列
data['download_num'] = data['download_num'].apply(convert_num)
data['like_num'] = data['like_num'].apply(convert_num)

print(len(data))

# 模型类型排序
top_20_model_type_analyze(data)

# 下载量排序
top_20_download_Url(data)


# 下载量排序
top_20_company_base_on_download_num(data)
