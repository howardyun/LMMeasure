import os
import json
import gzip
import csv
import requests
from datetime import datetime, date, timedelta

StartDate = 2023
EndDate = 2024

model_name = large_language_models = [
    "diffusion",
    "mT5",
    "CodeGen",
    "CPM",
    "CodeGeeX",
    "Yi-",
    "Mistral",
    "Vicuna",
    "XGen",
    "Phi",
    "Qwen",
    "GPT",
    "Claude",
    "PaLM",
    "Falcon",
    "Gemini",
    "Llama",
    "Cohere Command",
    "Mixtral",
    "Stable LM",
    "ERNIE",
    "Jamba",
    "Inflection",
    "BERT",
    "Codex",
    "Gopher",
    "Turing-NLG",
    "MT-NLG",
    "Megatron-Turing NLG",
    "BLOOM",
    "T5",
    # "UL",
    "Jurassic",
    "Reformer",
    "CTRL",
    "XLM-R",
    "XLNet",
    "ALBERT",
    "Electra",
    "RoBERTa",
    "DistilBERT",
    "BioBERT",
    "ERNIE",
    "GShard",
    "Switch Transformer",
    "LaMDA",
    "M6",
    "ProphetNet",
    "GLM",
    "PanGu-Alpha",
    "DialoGPT",
    "Jukebox",
    "Turing-Bletchley",
    "ZeRO-Infinity",
    "Longformer",
    "Realformer",
    "Pegasus",
    "BigGAN",
    "DALL-E",
    "WuDao",
    "DeepSpeed",
    "GLIDE",
    "Retro",
    "Flamingo",
    "Gato",
    "Minerva",
    "VALL-E",
    "Cicero",
    "PALM",
    "OPT",
    "SPT",
    "NLLB",
    "Sparrow",
    "AlphaCode",
    "Switch-Transformers",
    "ChatGPT",
    "ZeRO",
    "Perceiver",
    "DeepSpeed",
    "ULMFiT",
    "Flaubert",
    "Megatron",
    "CTRL",
    "Alpa",
    "NeMo-Megatron",
    "PanGu-Alpha",
    "CogView",
    "Yuan 1.0",
    "Yuke 1.0",
    "ExaGPT",
    "Aether-GPT",
    "GPT"
]


def download_github_archive_data(search_queries, start_date, end_date, output_file):
    """
    下载GitHub Archive数据,并将包含指定搜索关键词的仓库信息保存到CSV文件中。

    参数:
    search_queries (list): 搜索关键词列表
    start_date (date): 数据下载的起始日期
    end_date (date): 数据下载的结束日期
    output_file (str): 输出CSV文件的名称

    Returns:
    None
    """
    # 定义CSV文件的列名
    fieldnames = ["Repository Name", "Repository URL", "Description", "Programming Language", "Stars", "Forks",
                  "Created At", "Search Query"]
    unique_repos = set()
    unique_repos_info = set()

    current_date = start_date
    while current_date <= end_date:
        for hour in range(0, 24):
            file_url = f"https://data.gharchive.org/{current_date.strftime('%Y-%m-%d')}-{hour}.json.gz"
            file_name = file_url.split("/")[-1]
            # 下载文件
            if not os.path.exists(file_name):
                print(f"Downloading {file_name}...")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                }
                try:
                    response = requests.get(file_url, headers=headers)
                    response.raise_for_status()
                    with open(file_name, 'wb') as f:
                        f.write(response.content)
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading {file_name}: {e}")
                    continue

            # 解压缩并解析JSON数据
            with gzip.open(file_name, "rb") as f:
                print(f"Processing {file_name}...")
                for line in f:
                    try:
                        event = json.loads(line)
                    except json.decoder.JSONDecodeError as e:
                        continue

                    # 检查事件类型是否为"PushEvent"
                    if event["type"] == "PushEvent":
                        # 检查事件的仓库名称是否包含任何搜索关键词
                        for search_query in search_queries:
                            if search_query.lower() in event["repo"]["name"].lower():
                                repo_name = event["repo"]["name"]
                                repo_url = f"https://github.com/{repo_name}"
                                if "commits" in event["payload"] and event["payload"]["commits"]:
                                    repo_description = event["payload"]["commits"][0]["message"]
                                    if "author" in event["payload"]["commits"][0] and "email" in \
                                            event["payload"]["commits"][0]["author"]:
                                        repo_language = \
                                            event["payload"]["commits"][0]["author"]["email"].split("@")[-1]
                                    else:
                                        repo_language = ""
                                else:
                                    repo_description = ""
                                    repo_language = ""
                                repo_stars = event["repo"].get("stargazers_count", 0)
                                repo_forks = event["repo"].get("forks_count", 0)
                                repo_created_at = datetime.strptime(event["created_at"],
                                                                    "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")

                                # 检查是否已经存在该仓库
                                if (repo_name, search_query) not in unique_repos:
                                    unique_repos_info.add((
                                        repo_name,
                                        repo_url,
                                        repo_description,
                                        repo_language,
                                        repo_stars,
                                        repo_forks,
                                        repo_created_at,
                                        search_query
                                    ))
                                    unique_repos.add((repo_name, search_query))
                                    # print(f"Added repository: {repo_name} (Search Query: {search_query})")

            # 删除当前文件
            os.remove(file_name)
            print(f"Deleted {file_name}")
        # 每3个月存储一次数据
        if current_date.month % 3 == 0:
            # 获取当前季度的起始和结束日期
            quarter_start = date(current_date.year, current_date.month - 2, 1)
            quarter_end = date(current_date.year, current_date.month, 1) - timedelta(days=1)
            output_filename = f"../Data/github_repos_{quarter_start.strftime('%Y-%m-%d')}_{quarter_end.strftime('%Y-%m-%d')}.csv"
            print(f"Saving data to {output_filename}")
            with open(output_filename, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in unique_repos_info:
                    writer.writerow({
                        "Repository Name": row[0],
                        "Repository URL": f"https://github.com/{row[0]}",
                        "Description": row[2],
                        "Programming Language": row[3],
                        "Stars": row[4],
                        "Forks": row[5],
                        "Created At": row[6],
                        "Search Query": row[7]
                    })
            unique_repos_info.clear()
        current_date += timedelta(days=1)

    if len(unique_repos) > 0:
        # 获取当前季度的起始和结束日期
        quarter_end = date(current_date.year, current_date.month, 1) - timedelta(days=1)
        output_filename = f"../Data/github_repos_last_{end_date.strftime('%Y-%m-%d')}.csv"
        print(f"Saving data to {output_filename}")
        with open(output_filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in unique_repos_info:
                writer.writerow({
                    "Repository Name": row[0],
                    "Repository URL": f"https://github.com/{row[0]}",
                    "Description": row[2],
                    "Programming Language": row[3],
                    "Stars": row[4],
                    "Forks": row[5],
                    "Created At": row[6],
                    "Search Query": row[7]
                })
        unique_repos_info.clear()

    print(
        f"Data saved to files for the date range {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")


# 示例用法
download_github_archive_data(
    search_queries=model_name,
    start_date=date(StartDate, 1, 1),
    end_date=date(EndDate, 6, 15),
    output_file="github_repos.csv"
)
