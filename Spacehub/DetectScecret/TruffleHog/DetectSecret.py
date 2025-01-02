import subprocess
import detect_secrets
def scan_file(file_path):
    try:
        # 调用 detect-secrets 命令来扫描单个文件
        result = subprocess.run(['detect-secrets', '--scan', file_path], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Secrets found in {file_path}:")
            print(result.stdout)
        else:
            print(f"No secrets found in {file_path}.")
    except Exception as e:
        print(f"Error scanning file: {e}")

# 使用方法
scan_file('../../bk/app.py')
