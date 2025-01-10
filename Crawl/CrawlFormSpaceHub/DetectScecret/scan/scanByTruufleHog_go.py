import os
import subprocess
import json
import csv


def scan_with_trufflehog(folder_path):
    """
    使用 TruffleHog 扫描指定文件夹中的代码仓库
    :param folder_path: 要扫描的文件夹路径
    :return: 仓库名称和扫描结果 (JSON 格式字符串)，如果没有结果返回 None
    """
    try:
        # 执行 TruffleHog 扫描
        result = subprocess.run(
            [
                "trufflehog", "filesystem",
                folder_path,
                "--results=verified,unknown", "--json"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True
        )

        # 分割结果输出为 JSON 字符串列表
        json_strings = result.stdout.split('\n')
        # 转换为 JSON 对象列表
        json_objects = [json.loads(js) for js in json_strings if js.strip()]

        # 检查最后一个 JSON 对象中的 verified_secrets 和 unverified_secrets
        if json_objects[-1]["verified_secrets"] == 0 and json_objects[-1]["unverified_secrets"] == 0:
            print(f"没有发现敏感信息: {folder_path}")
            merged_json = {"findings": []}
            return merged_json  # 返回空表示没有结果
        else:
            print(f"发现敏感信息: {folder_path}")
            merged_json = {"findings": json_objects}
            return os.path.basename(folder_path), json.dumps(merged_json, indent=2)

    except Exception as e:
        print(f"扫描时发生错误: {e}")
        return None


def save_to_csv(data, output_csv_path):
    """
    将扫描结果保存到 CSV 文件
    :param data: 扫描结果列表，每项为 (仓库名称, 扫描结果 JSON 字符串)
    :param output_csv_path: 保存的 CSV 文件路径
    """
    # 写入 CSV 文件
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)
        # 写入表头
        csv_writer.writerow(["Repository Name", "Scan Results"])
        # 写入每一行数据
        csv_writer.writerows(data)
    print(f"结果已保存到 CSV 文件: {output_csv_path}")


def process_folder(folder_path, output_dir):
    """
    处理一个大文件夹，扫描其下的所有子文件夹，并保存扫描结果
    :param folder_path: 要处理的大文件夹路径
    :param output_dir: 保存结果的根目录
    """
    print(f"正在处理大文件夹: {folder_path}")
    scan_results = []  # 用于存储当前大文件夹的所有扫描结果

    # 遍历大文件夹中的每个子文件夹
    for subfolder in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, subfolder)
        if os.path.isdir(subfolder_path):  # 确保是子文件夹
            result = scan_with_trufflehog(subfolder_path)
            if result:  # 如果有扫描结果
                # 将子文件夹名称（仓库名称）和扫描结果保存到列表
                repository_name, scan_result = result
                scan_results.append([repository_name.replace("_", "/"), scan_result])

    # 如果有扫描结果，保存到 CSV
    if scan_results:
        folder_name = os.path.basename(folder_path)
        output_csv_path = os.path.join(output_dir, f"{folder_name}_scan_results.csv")
        save_to_csv(scan_results, output_csv_path)
    else:
        print(f"没有在 {folder_path} 中找到任何敏感信息。")


def process_root_directory(root_dir, output_dir):
    """
    处理根目录中的所有大文件夹
    :param root_dir: 根目录路径
    :param output_dir: 保存结果的根目录
    """
    os.makedirs(output_dir, exist_ok=True)  # 如果目录不存在，则创建

    # 遍历根目录中的所有大文件夹
    for folder in os.listdir(root_dir):
        folder_path = os.path.join(root_dir, folder)
        if os.path.isdir(folder_path):  # 确保是文件夹
            process_folder(folder_path, output_dir)


def process_single_folder(folder_path, output_dir):
    """
    单独处理一个大文件夹（例如新添加的月份文件夹）
    :param folder_path: 要处理的大文件夹路径
    :param output_dir: 保存结果的根目录
    """
    print(f"正在处理单独文件夹: {folder_path}")
    scan_results = []  # 用于存储扫描结果

    # 遍历该文件夹中的每个子文件夹（假设子文件夹是代码仓库）
    for subfolder in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, subfolder)
        if os.path.isdir(subfolder_path):  # 确保是子文件夹
            result = scan_with_trufflehog(subfolder_path)
            if result:  # 如果有扫描结果
                # 将子文件夹名称（仓库名称）和扫描结果保存到列表
                repository_name, scan_result = result
                scan_results.append([repository_name.replace("_", "/"), scan_result])

    # 如果有扫描结果，保存到 CSV
    if scan_results:
        folder_name = os.path.basename(folder_path)
        output_csv_path = os.path.join(output_dir, f"{folder_name}_scan_results.csv")
        save_to_csv(scan_results, output_csv_path)
    else:
        print(f"没有在 {folder_path} 中找到任何敏感信息。")





if __name__ == "__main__":
    # 定义根目录和输出结果根目录
    # root_dir = "E:/download_space"
    trufflehog_output_dir = "E:/download_space/trufflehog_scan_results"
    #
    # # 调用根目录处理函数
    # process_root_directory(root_dir, trufflehog_output_dir)

    # 示例：扫描一个新添加的文件夹（例如 "E:/download_space/2024-12"）
    new_folder_path = "E:/download_space/2024-12"
    process_single_folder(new_folder_path, trufflehog_output_dir)
