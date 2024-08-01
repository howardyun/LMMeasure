import os

def remove_empty_first_level_folders(path):
    # 检查路径是否存在
    if not os.path.exists(path):
        print(f"Path {path} does not exist.")
        return

    # 遍历第一级子文件夹
    for dir_name in os.listdir(path):
        dir_path = os.path.join(path, dir_name)
        # 确保是文件夹
        if os.path.isdir(dir_path):
            # 如果文件夹为空，删除它
            if not os.listdir(dir_path):
                print(f"Removing empty folder: {dir_path}")
                os.rmdir(dir_path)

# 使用示例
folder_path = '/Users/howardyun/Desktop/workspace/cloned_repos'
remove_empty_first_level_folders(folder_path)
