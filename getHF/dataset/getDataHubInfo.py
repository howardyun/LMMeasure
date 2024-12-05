from huggingface_hub import HfApi, EvalResult
import mysql.connector
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
import json
from huggingface_hub import hf_hub_url




def check_for_dict(values):
    has_dict = False  # 标志是否存在 dict
    for i, value in enumerate(values):
        if isinstance(value, dict):  # 检查是否是 dict 类型
            has_dict = True
            print(f"Index {i}: Detected dict -> {value}")
    if not has_dict:
        print("No dict type found in values.")
    else:
        print("Found dict type in values. Please handle it before inserting into the database.")

def convert_to_json(data):
    """
    尝试将数据转换为 JSON，不行就直接转为字符串；
    如果是字典或列表中的字典，也直接转为字符串。
    """
    if isinstance(data, dict):
        # 将整个字典转换为字符串
        return str(data)
    elif isinstance(data, list):
        # 遍历列表，处理其中的每个元素
        return str(data)
    try:
        # 尝试将数据转换为 JSON
        return json.dumps(data, default=lambda o: o.__dict__)
    except (TypeError, ValueError):
        # 如果失败，则直接转换为字符串
        return str(data)


def connect_to_db():
    return MySQLdb.connect(
        host="localhost",        # MySQL 服务器地址
        user="root",    # MySQL 用户名
        password="123456", # MySQL 密码
        database="huggingface_data" # 数据库名
    )


# 获取 Hugging Face 模型信息并插入到数据库中
def insert_model_info_into_db(model_list,start):
    api = HfApi()

    try:
        # 连接到数据库
        db = connect_to_db()
        cursor = db.cursor()
        count = 0
        # 遍历模型列表，获取信息并插入数据库
        for model in model_list:
            count += 1
            if count <= start:
                continue

            try:
                model_id = model.id
                model_info = api.model_info(model_id)

                # 将模型信息转换为字典
                model_info_dict = model_info.__dict__

                # 创建插入语句
                insert_query = """
                INSERT INTO models (
                    modelId, author, sha, last_modified, created_at, private, gated,
                    disabled, downloads, downloads_all_time, likes, library_name, 
                    gguf, inference, tags, pipeline_tag, mask_token, trending_score,
                    card_data, widget_data, model_index, config, transformers_info, 
                    siblings, spaces, safetensors, security_repo_status, cardData, 
                    transformersInfo, _id
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s
                )
                """

                # 创建插入数据库的 values
                values = (
                    model_info_dict.get('id', None),
                    model_info_dict.get('author', None),
                    model_info_dict.get('sha', None),
                    model_info_dict.get('last_modified', None),
                    model_info_dict.get('created_at', None),
                    model_info_dict.get('private', False),
                    model_info_dict.get('gated', False),
                    model_info_dict.get('disabled', False),
                    model_info_dict.get('downloads', 0),
                    model_info_dict.get('downloads_all_time', 0),
                    model_info_dict.get('likes', 0),
                    model_info_dict.get('library_name', None),
                    convert_to_json(model_info_dict.get('gguf', False)),
                    model_info_dict.get('inference', False),
                    convert_to_json(model_info_dict.get('tags', None)),  # 转换列表为 JSON
                    model_info_dict.get('pipeline_tag', None),
                    model_info_dict.get('mask_token', None),
                    model_info_dict.get('trending_score', 0.0),
                    convert_to_json(model_info_dict.get('card_data', None)),  # 转换字典为 JSON
                    convert_to_json(model_info_dict.get('widget_data', None)),  # 转换字典为 JSON
                    model_info_dict.get('model_index', 0),
                    convert_to_json(model_info_dict.get('config', None)),  # 转换字典为 JSON
                    convert_to_json(model_info_dict.get('transformers_info', None)),  # 转换字典为 JSON
                    convert_to_json(model_info_dict.get('siblings', None)),  # 转换列表为 JSON
                    convert_to_json(model_info_dict.get('spaces', None)),  # 转换列表为 JSON
                    convert_to_json(model_info_dict.get('safetensors', False)),
                    model_info_dict.get('security_repo_status', None),
                    convert_to_json(model_info_dict.get('cardData', None)),  # 转换字典为 JSON
                    convert_to_json(model_info_dict.get('transformersInfo', None)),  # 转换字典为 JSON
                    model_info_dict.get('_id', None)
                )

                check_for_dict(values)

                # 执行插入操作
                cursor.execute(insert_query, values)

                # 提交事务
                db.commit()

                # 打印模型信息插入结果
                print(f"Inserted model: {model_id}")

            except Exception as e:
                print(f"Error inserting model {model_id}: {e}")

    except Exception as e:
        print(f"Database connection or query execution error: {e}")

    finally:
        # 确保关闭数据库连接
        if cursor:
            cursor.close()
        if db:
            db.close()
        print("Database connection closed.")


# 模型列表（可以根据需要进行调整）
# 创建一个 HfApi 实例
api = HfApi()

dataset_list = api.list_datasets()

dataset = api.dataset_info('HuggingFaceTB/smoltalk')


print(dataset.id)

files = api.list_repo_files('Qwen/QwQ-32B-Preview')

# 仓库名称
repo_name = "Qwen/QwQ-32B-Preview"

# 获取仓库下所有文件的信息
files = api.list_repo_files(repo_name)

# 打印每个文件的元数据
for file in files:
    file_url = hf_hub_url(repo_id=repo_name, filename=file)
    print(file_url)
    # 获取每个文件的元数据
    metadata = api.get_hf_file_metadata(url=file_url)
    # 打印文件和对应的元数据
    print(f"File: {file}")
    print(f"Metadata: {metadata}")

print(dataset)



# 获取模型仓库的元数据
#
# model_list = api.list_models()
#
# insert_model_info_into_db(model_list,400000)
