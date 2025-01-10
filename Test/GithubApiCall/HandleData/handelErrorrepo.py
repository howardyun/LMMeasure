import requests
import pandas as pd
from urllib.parse import urlparse

# 读取 CSV 文件
df = pd.read_csv('./Data/errors.csv')

# 初始化结果列表和错误列表
results = []
errors = []

# GitHub API URL 模板
api_url_template = "https://api.github.com/repos/{owner}/{repo}"

# 你的 GitHub API 令牌
github_token = 'your_github_token_here'

# 请求头，包含 Authorization 令牌
headers = {
    'Authorization': f'token {github_token}'
}

# 遍历每个 URL
for index, row in df.iterrows():
    url = row['Repository URL']
    error = row.get('Error', None)
    # 跳过错误字段中出现404的行
    if '404' in error:
        print(url)
        continue
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')

    if len(path_parts) < 2:
        errors.append({
            "URL": url,
            "Error": "Invalid URL"
        })
        continue

    owner, repo = path_parts[0], path_parts[1]

    # 构建 API URL
    api_url = api_url_template.format(owner=owner, repo=repo)

    # 调用 GitHub API 获取仓库信息
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        repo_info = response.json()
        results.append({
            "Repository Name": repo_info.get('name'),
            "Repository URL": repo_info.get('html_url'),
            "Description": repo_info.get('description'),
            "Programming Language": repo_info.get('language'),
            "Stars": repo_info.get('stargazers_count'),
            "Forks": repo_info.get('forks_count'),
            "Created At": repo_info.get('created_at')
        })
    else:
        errors.append({
            "URL": url,
            "Error": response.status_code
        })

# 将成功的结果写入新的 CSV 文件
output_df = pd.DataFrame(results)
output_df.to_csv('./Data/output_error.csv', index=False)

# 将错误的结果写入错误 CSV 文件
errors_df = pd.DataFrame(errors)
errors_df.to_csv('./Data/error_errors.csv', index=False)

print("信息已成功写入output_error.csv 和 error_errors.csv 文件")
