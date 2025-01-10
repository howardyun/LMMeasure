from huggingface_hub import HfApi, EvalResult
import mysql.connector
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
import json
from huggingface_hub import HfApi

from huggingface_hub import login

# Log in to Hugging Face
login(token="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")



# 初始化HfApi对象
api = HfApi()

# 获取模型的提交历史
model_name = "google/cxr-foundation"  # 你需要替换为具体的模型名称
commits = api.list_repo_commits(model_name)


print(commits)

# 打印所有的提交信息
for commit in commits:
    print(commit)
    # commits.
    # print(f"Date: {commit.date}")
    # print(f"Author: {commit.author}")
    # print(f"Message: {commit.message}")
    # print("-" * 40)
