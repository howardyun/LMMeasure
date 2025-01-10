import requests
import json
import csv

# 设置GitHub API的访问令牌
github_token = "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"

# 定义搜索关键词
search_query = "large language model"

# 设置每页的结果数量
per_page = 100

# 当前页码
page = 1

# 存储所有项目信息的列表
all_repos = []

# 循环获取所有页面的结果
while True:
    # 构建API请求URL
    url = f"https://api.github.com/search/repositories?q={search_query}&per_page={per_page}&page={page}"

    # 设置请求头
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 发送请求并获取响应
    response = requests.get(url, headers=headers)

    # 检查请求是否成功
    if response.status_code == 200:
        # 解析JSON响应数据
        data = response.json()

        # 将当前页面的结果添加到列表中
        all_repos.extend(data["items"])

        # 如果没有更多结果,退出循环
        if len(data["items"]) < per_page:
            break

        # 准备下一页的请求
        page += 1
    else:
        print(f"Error: {response.status_code} - {response.text}")
        break

# 定义CSV文件的列名
fieldnames = ["Repository Name", "Repository URL", "Description", "Programming Language", "Stars", "Forks"]

# 创建CSV文件并写入数据
with open("github_repos.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # 遍历所有项目信息并写入CSV文件
    for repo in all_repos:
        writer.writerow({
            "Repository Name": repo["name"],
            "Repository URL": repo["html_url"],
            "Description": repo["description"],
            "Programming Language": repo["language"],
            "Stars": repo["stargazers_count"],
            "Forks": repo["forks_count"]
        })

print("Data saved to github_repos.csv")