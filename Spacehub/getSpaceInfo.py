from envs.myenv.Lib.enum import verify
from huggingface_hub import HfApi, EvalResult
import mysql.connector
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
import json
import pymysql
import json
from huggingface_hub import HfApi

# 初始化 Hugging Face API
api = HfApi()

# 获取 Spaces 数据
spaces = api.list_spaces()

def safe_json_dump(data):
    try:
        return json.dumps(data)
    except (TypeError, ValueError) as e:
        # 如果 json.dumps 失败，使用 str() 转换为字符串
        return str(data)


# 数据库连接设置
db = pymysql.connect(
    host="localhost",
    user="root",
    password="123456",
    database="my_huggingface_data",
)

# 创建游标
cursor = db.cursor()

# 插入数据的 SQL 语句
insert_query = """
INSERT INTO SpaceInfo (
    id, author, sha, created_at, last_modified, private, gated, disabled, 
    host, subdomain, likes, tags, siblings, card_data, runtime, sdk, 
    models, datasets, trending_score
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
"""

# 模型列表（可以根据需要进行调整）
# 创建一个 HfApi 实例
api = HfApi()


spaces = api.list_spaces()

count = 0


# 遍历 spaces 数据并插入到数据库中
for space in spaces:
    try:
        # 提取字段信息
        id = space.id
        author = space.author
        sha = getattr(space, "sha", None)
        created_at = space.created_at
        last_modified = space.last_modified
        private = space.private
        gated = space.gated
        disabled = space.disabled
        host = getattr(space, "host", None)
        subdomain = getattr(space, "subdomain", None)
        likes = space.likes
        tags = safe_json_dump(space.tags)  # 转换为 JSON 字符串或普通字符串
        siblings = safe_json_dump(space.siblings)  # 转换为 JSON 字符串或普通字符串
        card_data = safe_json_dump(space.card_data)  # 转换为 JSON 字符串或普通字符串
        runtime = safe_json_dump(space.runtime)  # 转换为 JSON 字符串或普通字符串
        sdk = space.sdk
        models = safe_json_dump(space.models)  # 转换为 JSON 字符串或普通字符串
        datasets = safe_json_dump(space.datasets)  # 转换为 JSON 字符串或普通字符串
        trending_score = space.trending_score
        # 插入数据
        cursor.execute(insert_query, (
            id, author, sha, created_at, last_modified, private, gated, disabled,
            host, subdomain, likes, tags, siblings, card_data, runtime, sdk,
            models, datasets, trending_score
        ))
        db.commit()
        count += 1
        if count % 100 == 0:
            print(count)

    except Exception as e:
        print(f"Error inserting space {id}: {e}")


# 提交事务并关闭连接

cursor.close()
db.close()




