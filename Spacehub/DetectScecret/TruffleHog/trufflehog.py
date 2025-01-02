import subprocess
import shutil
shutil.rmtree(path)


def scan_git_repo(repo_path_or_url):
    try:
        # 调用 truffleHog 扫描 Git 仓库
        result = subprocess.run(['trufflehog', '--regex', '--entropy=True',
                                 repo_path_or_url], capture_output=True, text=True, encoding='utf-8')

        # 如果有泄露的敏感信息
        if result.returncode == 0:
            print(f"Secrets found in repository {repo_path_or_url}:")
            print(result.stdout)
        else:
            print(f"No secrets found in repository {repo_path_or_url}.")
    except Exception as e:
        print(f"Error scanning repository: {e}")

# 使用方法：传入 Git 仓库 URL 或本地仓库路径
repo_url = 'https://huggingface.co/spaces/muhammad-uzair-raza/chatbot'
scan_git_repo(repo_url)



# import psutil
#
# def find_and_kill_process_using_file(file_path):
#     for proc in psutil.process_iter(['pid', 'name', 'open_files']):
#         for file in proc.info['open_files'] or []:
#             if file_path in file.path:
#                 print(f"Process {proc.info['name']} (PID {proc.info['pid']}) is using the file")
#                 proc.terminate()  # 结束该进程
#                 return True
#     return False
#
# file_path = "C:\\Users\\SHAOXU~1\\AppData\\Local\\Temp\\tmpguhsjp7j"
# if find_and_kill_process_using_file(file_path):
#     print(f"Successfully terminated process using {file_path}")
# else:
#     print(f"No process found using {file_path}")
