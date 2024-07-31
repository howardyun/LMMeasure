import os
import shutil

def remove_empty_folders(path):
    # 检查路径是否存在
    if not os.path.exists(path):
        print(f"Path {path} does not exist.")
        return

    # 遍历文件夹
    for root, dirs, files in os.walk(path, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            # 如果文件夹为空，删除它
            if not os.listdir(dir_path):
                print(f"Removing empty folder: {dir_path}")
                os.rmdir(dir_path)

# 使用示例
folder_path = '/Users/howardyun/Desktop/workspace/cloned_repos'
remove_empty_folders(folder_path)
