# 本文件被用于通过model market市场的url收集每个网页对应的详细的收集
import os
import json
import csv
import pandas as pd
import pickle
import time
from random import uniform

from bs4 import Tag, BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor, as_completed

# Path to the folder containing CSV files
input_folder_path = 'Data/'
output_folder_path = 'ModelMarketDetailData/'
error_file_path = 'ModelMarketDetailData/error_urls.csv'
cookie_file_path = 'cookies.pkl'  # Path to your cookies pkl file


# Function to read URLs from a CSV file
def read_urls_from_csv(file_path):
    urls = pd.read_csv(file_path)['URL'].to_list()
    return urls


# Function to extract the content preserving the hierarchy in a dictionary
def extract_content(tag):
    content = {}
    current_key = None
    for child in tag.children:
        if isinstance(child, Tag):
            text = child.get_text(strip=True)
            if text:
                if child.name in ['h1', 'h2', 'h3']:
                    current_key = text
                    content[current_key] = []
                elif child.name in ['p', 'span', 'div'] and current_key:
                    content[current_key].append(text)
                elif child.name == 'ul' and current_key:
                    ul_content = extract_ul_content(child)
                    if ul_content:
                        content[current_key].append(ul_content)
    return content


# Function to extract content from ul tags
def extract_ul_content(tag):
    ul_content = {}
    items = tag.find_all('li')
    for i, item in enumerate(items, 1):
        text = item.get_text(strip=True)
        if text:
            ul_content[f'li_{i}'] = text
    return ul_content


# Function to write error URLs to a CSV file
def write_errors_to_csv(errors, file_path):
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['URL'])
        for error in errors:
            writer.writerow([error])


# Load cookies from a pkl file
def load_cookies_from_pkl(file_path):
    with open(file_path, 'rb') as file:
        cookies = pickle.load(file)
    return cookies


# Function to add cookies to WebDriver
def add_cookies_to_webdriver(driver, cookies):
    driver.delete_all_cookies()
    for cookie in cookies:
        driver.add_cookie(cookie)


# Function to fetch and process a single URL
def fetch_and_process_url(url, cookies):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get(url)
        add_cookies_to_webdriver(driver, cookies)
        driver.refresh()

        # Add a delay after loading the page
        time.sleep(uniform(2, 5) / 10)  # Random delay between 2 to 5 seconds

        # Get the page source after loading
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find the target div with class 'model-card-content'
        target_div = soup.find('div', class_='model-card-content')
        if target_div:
            # Extract data from the target div
            extracted_content = extract_content(target_div)
            return url, extracted_content
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return url, None
    finally:
        driver.quit()

        # Add a delay after closing the WebDriver
        time.sleep(uniform(1, 3) / 10)  # Random delay between 1 to 3 seconds


# List to store error URLs
error_urls = []

# Load cookies from the pkl file
cookies = load_cookies_from_pkl(cookie_file_path)

# Iterate through all CSV files in the folder
for file_name in os.listdir(input_folder_path):
    if file_name.endswith('.csv'):
        csv_file_path = os.path.join(input_folder_path, file_name)
        # Read URLs from the CSV file
        urls = read_urls_from_csv(csv_file_path)
        # Dictionary to store extracted content for the current file
        file_content = {}

        # Use ThreadPoolExecutor to process URLs in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_and_process_url, url, cookies) for url in urls]
            for future in as_completed(futures):
                url, content = future.result()
                if content is not None:
                    file_content[url] = content
                else:
                    error_urls.append(url)

        # Define the JSON file name based on the CSV file name
        json_file_name = os.path.join(output_folder_path, file_name.replace('.csv', '.json'))
        # Save the file_content dictionary to a JSON file
        with open(json_file_name, 'w', encoding='utf-8') as f:
            json.dump(file_content, f, ensure_ascii=False, indent=4)
        # Print the path to the saved JSON file
        print(f'The extracted content has been saved to {json_file_name}')

# Save the error URLs to a CSV file
write_errors_to_csv(error_urls, error_file_path)
# Print the path to the saved error CSV file
print(f'The error URLs have been saved to {error_file_path}')
