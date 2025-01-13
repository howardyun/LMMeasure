from huggingface_hub import HfApi
from datetime import datetime, timezone
import os
import json

def initialize_output_dir(output_dir):
    """创建存储目录。"""
    os.makedirs(output_dir, exist_ok=True)

def preload_existing_datasets(output_dir):
    """预加载已有的数据集数据到缓存中。"""
    monthly_datasets = {}
    for file_name in os.listdir(output_dir):
        if file_name.endswith(".json"):
            month_key = file_name.replace(".json", "")
            file_path = os.path.join(output_dir, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                monthly_datasets[month_key] = json.load(f)
    return monthly_datasets

def save_datasets_to_files(monthly_datasets, output_dir):
    """保存每个类别的数据到文件。"""
    for month_key, dataset_ids in monthly_datasets.items():
        file_path = os.path.join(output_dir, f"{month_key}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(dataset_ids, f, ensure_ascii=False, indent=4)
        print(f"已保存 {month_key} 的数据集到文件: {file_path}")

def process_datasets(datasets, monthly_datasets, start_date, end_date):
    """处理数据集列表，将其分类到每个月份或未知分类。"""
    count = 0
    for dataset in datasets:
        created_at = dataset.created_at  # 直接是 offset-aware datetime 对象
        if created_at:
            # 提取年-月字符串作为文件名的一部分，例如 "2024-01"
            month_key = created_at.strftime("%Y-%m")
        else:
            # 对于没有 created_at 的数据集，归入 "unknown" 类别
            month_key = "unknown"

        if month_key not in monthly_datasets:
            monthly_datasets[month_key] = []  # 初始化该类别的列表

        # 如果数据集 ID 不在该类别列表中，才添加
        if dataset.id not in monthly_datasets[month_key]:
            monthly_datasets[month_key].append(dataset.id)

        count += 1
        if count % 1000 == 0:
            print(f"已处理 {count} 个数据集")

def main(api_token, output_dir, start_date, end_date):
    """主函数，负责调用 API 并保存数据集数据。"""
    # 初始化 API
    api = HfApi(token=api_token)

    # 初始化存储目录
    initialize_output_dir(output_dir)

    # 预加载已有数据
    monthly_datasets = preload_existing_datasets(output_dir)

    # 调用 API 获取数据集数据
    print("正在调用 Hugging Face API 获取数据集列表...")
    datasets = api.list_datasets(full=False)

    # 处理数据集数据
    process_datasets(datasets, monthly_datasets, start_date, end_date)

    # 保存到文件
    save_datasets_to_files(monthly_datasets, output_dir)

    print(f"所有数据集文件已更新到目录: {output_dir}")

# 调用主函数
def run():
    API_TOKEN = "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"
    OUTPUT_DIR = "monthly_dataset_files"
    START_DATE = datetime(2022, 2, 1, tzinfo=timezone.utc)
    END_DATE = datetime(2024, 12, 31, tzinfo=timezone.utc)

    main(API_TOKEN, OUTPUT_DIR, START_DATE, END_DATE)

if __name__ == "__main__":
    run()
