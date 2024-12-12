import json
import subprocess
import shutil
from sys import prefix

import pymysql
import json


db = pymysql.connect(
    host="localhost",
    user="root",
    password="123456",
    database="my_huggingface_data",
)

def scan_git_repo(repo_path_or_url):
    try:
        # 调用 truffleHog 扫描 Git 仓库
        result = subprocess.run(['trufflehog','--json', '--entropy=True','--rules=rules.json',
                                 repo_path_or_url], capture_output=True, text=True, encoding='utf-8')
        try:
            # 逐行解析 JSON 对象
            json_objects = []
            for line in result.stdout.splitlines():
                try:
                    json_objects.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON on line: {line}")
                    continue  # 跳过无效的行

            # 将所有 JSON 对象合并到一个 JSON 对象中
            final_json_object = {
                "findings": json_objects  # 将解析得到的 JSON 对象作为数组放入字典中
            }

            # 打印最终的 JSON 对象
            final_json_object = json.dumps(final_json_object, indent=4)
            return final_json_object
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

    except Exception as e:
        print(f"Error scanning repository: {e}")
    return None

def store_final_in_database(trufflehog_py, space_id):
    # 创建数据库连接
    cursor = db.cursor()

    try:
        # 更新指定 ID 的 trufflehog_py 列
        sql = """
        UPDATE spaceinfo
        SET trufflehog_py = %s
        WHERE id = %s
        """
        cursor.execute(sql, (trufflehog_py, space_id))
        # 提交更改
        db.commit()
        print(f"{space_id} stored successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # 关闭连接
        cursor.close()


def fetch_ids_paginated(table_name, page_size, page_number):
    """
    按分页方式获取指定表的 ID 列。

    :param table_name: 表名
    :param page_size: 每页显示的记录数
    :param page_number: 当前页码（从 1 开始）
    :return: 当前页的 ID 列列表
    """
    cursor = db.cursor()

    try:
        # 计算偏移量
        offset = (page_number - 1) * page_size

        # 查询语句
        sql = f"""
        SELECT id
        FROM {table_name}
        LIMIT %s OFFSET %s
        """

        # 执行查询
        cursor.execute(sql, (page_size, offset))
        result = cursor.fetchall()

        # 提取 ID 列
        ids = [row[0] for row in result]
        return ids
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()



# 示例：分页获取 ID 列
table_name = 'spaceinfo'  # 替换为你的表名
page_size = 100  # 每页 10 条记录
page_number = 1  # 从第 1 页开始

while True:
    ids = fetch_ids_paginated(table_name, page_size, page_number)
    if not ids:  # 如果没有更多数据，终止
        break
    for id in ids:
        final_json = scan_git_repo(f'https://huggingface.co/spaces/{id}')
        if final_json:
            store_final_in_database(final_json, id)
    print(f"Page {page_number}: {ids}")
    page_number += 1
db.close()

#
# # 使用方法：传入 Git 仓库 URL 或本地仓库路径
# repo_url = 'https://huggingface.co/spaces/muhammad-uzair-raza/chatbot'
# final = scan_git_repo(repo_url)
#
#
# print(final)
#
#
# store_final_in_database(final, 'record_id_value')
#
