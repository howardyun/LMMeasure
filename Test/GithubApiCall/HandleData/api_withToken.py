import csv
import requests
import os


def get_repo_info(owner, repo, token=None):
    url = f'https://api.github.com/repos/{owner}/{repo}'
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'

    try:
        response = requests.get(url, headers=headers, timeout=10)  # 添加超时设置
    except requests.exceptions.Timeout:
        print(f"Error: Timeout while fetching data for {owner}/{repo}.")
        return None, "Timeout"
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None, str(e)

    if response.status_code == 200:
        data = response.json()
        repo_info = {
            'Repository Name': data['name'],
            'Repository URL': data['html_url'],
            'Description': data['description'],
            'Programming Language': data['language'],
            'Stars': data['stargazers_count'],
            'Forks': data['forks_count'],
            'Created At': data['created_at']
        }
        return repo_info, None
    else:
        error_message = f"Unable to fetch data for {owner}/{repo}. Status code: {response.status_code}, Response: {response.text}"
        print(f"Error: {error_message}")
        return None, error_message


def parse_repo_url(repo_url):
    parts = repo_url.split('/')
    if len(parts) >= 5:
        owner = parts[-2]
        repo = parts[-1]
        return owner, repo
    else:
        return None, None


def update_csv_with_repo_info(input_csv_path, output_csv_path, error_log_path, delete_log_path, token=None):
    updated_rows = []
    deleted_rows = []

    with open(input_csv_path, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['Search Query'] if 'Search Query' not in reader.fieldnames else reader.fieldnames

        with open(output_csv_path, mode='w', newline='', encoding='utf-8') as outfile, \
                open(error_log_path, mode='w', newline='', encoding='utf-8') as errorfile, \
                open(delete_log_path, mode='w', newline='', encoding='utf-8') as deletefile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            error_writer = csv.writer(errorfile)
            error_writer.writerow(['Repository URL', 'Error'])

            delete_writer = csv.DictWriter(deletefile, fieldnames=fieldnames)
            delete_writer.writeheader()

            for row in reader:
                repo_url = row['Repository URL']
                search_query = row['Search Query']
                owner, repo = parse_repo_url(repo_url)

                if owner and repo:
                    repo_info, error = get_repo_info(owner, repo, token)
                    if repo_info:
                        repo_info['Search Query'] = search_query
                        writer.writerow(repo_info)
                        updated_rows.append(row)
                    else:
                        print(f"Skipping {repo_url} due to API error.")
                        error_writer.writerow([repo_url, error])
                        if '404' in error:
                            delete_writer.writerow(row)
                            deleted_rows.append(row)
                else:
                    print(f"Invalid repository URL: {repo_url}")
                    error_writer.writerow([repo_url, 'Invalid URL'])

    # 将更新后的数据写回到新的 CSV 文件中
    with open(input_csv_path.replace('.csv', '_updated.csv'), mode='w', newline='', encoding='utf-8') as updatedfile:
        writer = csv.DictWriter(updatedfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in updated_rows:
            writer.writerow(row)

    # 将删除的数据写入一个新的 CSV 文件
    with open(input_csv_path.replace('.csv', '_deleted.csv'), mode='w', newline='', encoding='utf-8') as deletedfile:
        writer = csv.DictWriter(deletedfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in deleted_rows:
            writer.writerow(row)


if __name__ == "__main__":
    input_csv_path = './Data/merged.csv'
    output_csv_path = './Data/out.csv'
    error_log_path = './Data/errors.csv'
    delete_log_path = './Data/deleted.csv'
    token = "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"

    if token:
        print(f"Using token: {token[:4]}...{token[-4:]}")  # 显示令牌的前四位和后四位
    else:
        print("No token found. Please set the GITHUB_TOKEN environment variable.")

    update_csv_with_repo_info(input_csv_path, output_csv_path, error_log_path, delete_log_path, token)
