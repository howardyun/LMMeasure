# import os
# import subprocess
# import json
#
#
# def scan_python_files_in_repo(repo_path):
#     # Run bandit on the repository with the confidence and severity level set to low to capture all issues
#     result = subprocess.run(
#         ['bandit', '-r', repo_path, '-f', 'json'],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True
#     )
#
#     try:
#         # Parse the JSON result
#         return json.loads(result.stdout)
#     except json.JSONDecodeError:
#         # If there's an error, return the stderr message
#         return {"error": result.stderr}
#
#
# def scan_all_repos_in_directory(directory):
#     all_results = {}
#     i = 0
#     for item in os.listdir(directory):
#         i = i + 1
#         if i == 10:
#             break
#         item_path = os.path.join(directory, item)
#
#         # Check if the item is a directory (assuming it's a git repository)
#         if os.path.isdir(item_path):
#             if os.path.exists(os.path.join(item_path, '.git')):
#                 print(f"Scanning repository: {item}")
#                 scan_result = scan_python_files_in_repo(item_path)
#                 all_results[item] = scan_result
#             else:
#                 print(f"Skipping {item}, not a git repository.")
#         else:
#             print(f"Skipping {item}, not a directory.")
#
#     return all_results
#
#
# def save_results_to_json(results, output_file):
#     with open(output_file, 'w') as f:
#         json.dump(results, f, indent=4)
#
#
# # Specify the directory containing the GitHub repositories
# repos_directory = "/Users/howardyun/Desktop/workspace/cloned_repos"
#
# # Specify the path to save the JSON file
# output_file = "result/security_reports.json"
#
# # Scan all repositories and get the results
# results = scan_all_repos_in_directory(repos_directory)
#
# # Save the detailed results to a JSON file, preserving all bandit output by repository
# save_results_to_json(results, output_file)
#
# print(f"Detailed results have been saved to {output_file}")

import os
import subprocess
import json


def scan_python_files_in_repo(repo_path):
    # Run bandit on the repository with the confidence and severity level set to low to capture all issues
    result = subprocess.run(
        ['bandit', '-r', repo_path, '-f', 'json'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        # Parse the JSON result
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        # If there's an error, return the stderr message
        return {"error": result.stderr}


def scan_all_repos_in_directory(directory, save_interval=100):
    all_results = {}
    repo_count = 0
    batch_number = 1

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)

        # Check if the item is a directory (assuming it's a git repository)
        if os.path.isdir(item_path):
            if os.path.exists(os.path.join(item_path, '.git')):
                print(f"Scanning repository: {item}")
                scan_result = scan_python_files_in_repo(item_path)
                all_results[item] = scan_result
                repo_count += 1

                # Save the results every 'save_interval' repositories
                if repo_count % save_interval == 0:
                    output_file = f"result/security_reports_batch_{batch_number}.json"
                    save_results_to_json(all_results, output_file)
                    print(f"Batch {batch_number} saved to {output_file}")
                    all_results = {}  # Clear the results for the next batch
                    batch_number += 1

            else:
                print(f"Skipping {item}, not a git repository.")
        else:
            print(f"Skipping {item}, not a directory.")

    # Save any remaining results after the loop
    if all_results:
        output_file = f"result/security_reports_batch_{batch_number}.json"
        save_results_to_json(all_results, output_file)
        print(f"Final batch {batch_number} saved to {output_file}")

    return all_results


def save_results_to_json(results, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)


# Specify the directory containing the GitHub repositories
repos_directory = "/Users/howardyun/Desktop/workspace/cloned_repos"

# Scan all repositories and get the results
results = scan_all_repos_in_directory(repos_directory)

print("Scanning completed.")

