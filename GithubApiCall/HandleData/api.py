import csv
import requests
import os


def get_repo_info(owner, repo, token=None):
    url = f'https://api.github.com/repos/{owner}/{repo}'
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'

    response = requests.get(url, headers=headers)

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
        return repo_info
    else:
        print(f"Error: Unable to fetch data for {owner}/{repo}. Status code: {response.status_code}")
        return None


def parse_repo_url(repo_url):
    parts = repo_url.split('/')
    if len(parts) >= 5:
        owner = parts[-2]
        repo = parts[-1]
        return owner, repo
    else:
        return None, None


def update_csv_with_repo_info(input_csv_path, output_csv_path, token=None):
    with open(input_csv_path, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = ['Repository Name', 'Repository URL', 'Description', 'Programming Language', 'Stars', 'Forks',
                      'Created At']

        with open(output_csv_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                repo_url = row['Repository URL']
                owner, repo = parse_repo_url(repo_url)

                if owner and repo:
                    repo_info = get_repo_info(owner, repo, token)
                    if repo_info:
                        writer.writerow(repo_info)
                    else:
                        print(f"Skipping {repo_url} due to API error.")
                else:
                    print(f"Invalid repository URL: {repo_url}")


if __name__ == "__main__":
    input_csv_path = './Data/merged.csv'
    output_csv_path = './Data/out.csv'
    update_csv_with_repo_info(input_csv_path, output_csv_path)
