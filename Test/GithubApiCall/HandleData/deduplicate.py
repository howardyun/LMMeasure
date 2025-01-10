import os
import pandas as pd

def merge_and_deduplicate_csv(folder_path):
    all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]
    combined_csv = pd.concat([pd.read_csv(f) for f in all_files], ignore_index=True)
    
    # 去重
    deduplicated_csv = combined_csv.drop_duplicates(subset=['Repository Name', 'Repository URL'])
    
    return deduplicated_csv

def save_csv(dataframe, output_path):
    dataframe.to_csv(output_path, index=False)

if __name__ == "__main__":
    folder_path = './Test'
    output_path = './Test/merged.csv'
    
    deduplicated_csv = merge_and_deduplicate_csv(folder_path)
    save_csv(deduplicated_csv, output_path)
