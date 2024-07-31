import os
import subprocess
import time
import pandas as pd
from git import Repo
from concurrent.futures import ThreadPoolExecutor, as_completed


def extract_segment(url):
    # 使用rsplit分割字符串，最多分割两次
    parts = url.rsplit('/', 2)
    if len(parts) >= 2:
        return parts[-2] + '_' + parts[-1]
    return None


def clone_repo(repo_url, clone_dir, failed_repos):
    """
    克隆Git仓库到指定目录
    """
    if os.path.exists(clone_dir):
        # print(f"Directory {clone_dir} already exists. Skipping clone.")
        return
    os.makedirs(clone_dir, exist_ok=True)
    try:
        Repo.clone_from(repo_url, clone_dir)
        print(f"Cloned {repo_url} into {clone_dir}")
    except Exception as e:
        print(f"Failed to clone {repo_url}: {e}")
        failed_repos.append({'repo_url': repo_url, 'error': str(e)})


def scan_code_with_bandit(code_dir, report_file):
    """
    使用Bandit扫描代码，并将结果保存到报告文件
    """
    command = f"bandit -r {code_dir} -f json -o {report_file}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Bandit scan completed successfully. Report saved to {report_file}")
    else:
        print(f"Bandit scan failed: {result.stderr}")


def scan_code_with_sonar(code_dir, project_key, project_name, sonar_host, sonar_token):
    """
    使用SonarScanner扫描代码
    """
    command = (
        f"sonar-scanner "
        f"-Dsonar.projectKey={project_key} "
        f"-Dsonar.projectName={project_name} "
        f"-Dsonar.sources={code_dir} "
        f"-Dsonar.host.url={sonar_host} "
        f"-Dsonar.login={sonar_token}"
    )
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"SonarScanner scan completed successfully for {project_name}")
    else:
        print(f"SonarScanner scan failed for {project_name}: {result.stderr}")


def process_repo(repo_url, base_dir, sonar_host, sonar_token, failed_repos):
    repo_name = extract_segment(repo_url)
    clone_dir = os.path.join(base_dir, repo_name)
    bandit_report_file = os.path.join(base_dir, f"{repo_name}_bandit_report.json")

    clone_repo(repo_url, clone_dir, failed_repos)
    # scan_code_with_bandit(clone_dir, bandit_report_file)

    # project_key = f"project_{repo_name}"
    # project_name = f"{repo_name}"
    # scan_code_with_sonar(clone_dir, project_key, project_name, sonar_host, sonar_token)


def main(repo_urls, base_dir, sonar_host, sonar_token, failed_repos):
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(process_repo, repo_url, base_dir, sonar_host, sonar_token, failed_repos)
            for repo_url in repo_urls
        ]
        for idx, future in enumerate(as_completed(futures)):
            try:
                future.result()
                if idx % 20 == 0:
                    print(f"{idx} repositories processed.")
                    time.sleep(1)
            except Exception as e:
                print(f"An error occurred: {e}")


if __name__ == "__main__":
    # 替换为你的Git仓库链接
    failed_repos = []
    for i in range(0, 3):
        print(f"Processing file number {i}")
        repo_urls = pd.read_csv(f'../RepoData/urls_{i}.csv')['URL'].to_list()

        base_dir = "/Users/howardyun/Desktop/workspace/cloned_repos"

        # 替换为你的SonarQube服务器配置
        sonar_host = "http://localhost:9000"
        sonar_token = "your_sonar_token"

        main(repo_urls, base_dir, sonar_host, sonar_token, failed_repos)

    # 保存失败的仓库信息到CSV文件
    if failed_repos:
        failed_repos_df = pd.DataFrame(failed_repos)
        failed_repos_df.to_csv('failed_repos.csv', index=False)
        print("Failed repos saved to failed_repos.csv")
