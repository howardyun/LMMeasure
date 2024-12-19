import os
import subprocess
import pymysql

os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'
os.environ['GIT_LFS_SKIP_SMUDGE'] = "1"
my_env = os.environ.copy()

try:
    conn = pymysql.connect(user="root", password="123456", host="127.0.0.1",
                           port=3306, database="my_huggingface_data")
except:
    exit(0)


def fetch_ids_paginated(table_name, page_size, page_number):
    """
    按分页方式获取指定表的 ID 列。

    :param table_name: 表名
    :param page_size: 每页显示的记录数
    :param page_number: 当前页码（从 1 开始）
    :return: 当前页的 ID 列列表
    """
    cursor = conn.cursor()

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

# 270- 400
# 401- 600

table_name = 'spaceinfo'  # 替换为你的表名
page_size = 100  # 每页 10 条记录
page_number = 601  # 从第 1页 开始

while True:
    if page_number == 801:
        break
    ids = fetch_ids_paginated(table_name, page_size, page_number)
    if not ids:  # 如果没有更多数据，终止
        break
    for id in ids:
        id=''.join(id)
        print(id)
        subprocess.run(["git", "clone", "https://huggingface.co/spaces/" + id,
                        "D:/共享文件/our_space_data_600_800/" + id.replace("/", "_")],
                       env=my_env, shell=True,)
    print(f"page{page_number},finish")
    page_number += 1
conn.close()

