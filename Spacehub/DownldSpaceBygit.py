import os
import subprocess
import pymysql

os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'
os.environ['GIT_LFS_SKIP_SMUDGE'] = "1"
my_env = os.environ.copy()

try:
    conn = pymysql.connect(user="root", password="123456", host="192.168.196.11",
                           port=3306, database="my_huggingface_data")
except:
    exit(0)
mycursor = conn.cursor()
for i in range(0, 6000):
    a = f"select id from spaceinfo limit {i * 10},10"
    mycursor.execute(a)
    myresult = mycursor.fetchall()  # fechall获取所有数据
    for x in myresult:
        x = ''.join(x)
        print(x)
        # result = subprocess.run(
        #     ["", "GIT_LFS_SKIP_SMUDGE=1"], shell=True)
        subprocess.run(["git", "clone", "https://huggingface.co/spaces/ginipick/SORA-3D"],
                       env=my_env, shell=True, )
        exit(0)
