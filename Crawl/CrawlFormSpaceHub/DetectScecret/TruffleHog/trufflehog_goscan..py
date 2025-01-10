import os
import time


import pymysql
import subprocess
import json
import csv

#os.environ['http_proxy'] = 'http://127.0.0.1:7890'
#os.environ['https_proxy'] = 'http://127.0.0.1:7890'
#huggingface_hub.login("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")


try:
    conn = pymysql.connect(user="root", password="root", host="127.0.0.1",
                           port=3306, database="huggingface")
except:
    print("wrong")
    exit(0)
mycursor = conn.cursor()
csv.field_size_limit(500 * 1024 * 1024)
with open(r"D:\huggingface\spaceinfo\spaceinfo.csv", 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    i = 0
    sum=0
    for _ in range(214820):  #590+，正序读取从8954开始
        next(reader)
    for row in reader:
        x = ''.join(row[0])
        print(f"{x}, {i}")
        print(f"sum:{sum}")
        sum = sum + 1
        if not os.path.exists("//NX/nx_共享文件/our_space_data/" + x.replace("/", "_") + "/"):
            conn.commit()
            time.sleep(10)
            print("不存在")
            print(f"sum:{sum}")
            continue
        result = subprocess.run(
            ["trufflehog", "filesystem", "//NX/nx_共享文件/our_space_data/" + x.replace("/", "_") + "/",
             "--results=verified,unknown", "--json"], stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, shell=True)
        json_strings = result.stdout.split('\n')
        json_objects = [json.loads(js) for js in json_strings if js.strip()]
        # json_objects = json_objects[2:]
        if json_objects[-1]["verified_secrets"] == 0 and json_objects[-1]["unverified_secrets"] == 0:
            merged_json = {"findings": []}
            b = "insert into space(id,trufflehog_go) values(%s,%s)"
            mycursor.execute(b, (x, json.dumps(merged_json, indent=2)))
        else:
            merged_json = {"findings": json_objects}
            b = "insert into space(id,trufflehog_go) values(%s,%s)"
            mycursor.execute(b, (x, json.dumps(merged_json, indent=2)))
        i = i + 1

        if i % 20 == 0:
            i = 0
            conn.commit()
            time.sleep(2)
conn.close()
