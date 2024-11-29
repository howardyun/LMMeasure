import MySQLdb
import mysql.connector

# Step 1: 数据库连接信息
def connect_to_db():
    return MySQLdb.connect(
        host="localhost",        # MySQL 服务器地址
        user="root",    # MySQL 用户名
        password="123456", # MySQL 密码
        database="huggingface_data" # 数据库名
    )

def get_value_counts(connect_to_db, table_name, column_name):
    """
    获取指定表中某列不同值及其出现次数。

    参数:
        db_config (dict): 数据库连接信息，包括 host, user, password, database。
        table_name (str): 数据库表名。
        column_name (str): 需要统计的列名。

    返回:
        list: 包含元组的列表，每个元组包含 (值, 出现次数)。
    """
    try:
        # Step 1: 连接到数据库
        db =connect_to_db
        cursor = db.cursor()

        # Step 2: 构建 SQL 查询
        query = f"""
        SELECT {column_name}, COUNT(*) AS value_count
        FROM {table_name}
        GROUP BY {column_name}
        ORDER BY value_count DESC;
        """

        # Step 3: 执行查询
        cursor.execute(query)
        results = cursor.fetchall()  # 获取结果

        # Step 4: 输出结果
        print(f"不同值及其出现次数 for '{column_name}' in '{table_name}':")
        for value, count in results:
            print(f"值: {value}, 数量: {count}")

        return results

    except mysql.connector.Error as e:
        print(f"数据库错误: {e}")
        return None
    finally:
        # 确保关闭数据库连接
        if cursor:
            cursor.close()
        if db:
            db.close()
        print("Database connection closed.")




# 示例调用
if __name__ == "__main__":
    column_names = ['gated','disabled','library_name','pipeline_tag','mask_token','trending_score','security_repo_status']
    table_name = "models"  # 写入想要查询表名
    # column_name = "gated"  # 写入想要查询列名
    for column_name in column_names:
        # 调用函数
        result = get_value_counts(connect_to_db(), table_name, column_name)

