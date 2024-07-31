import os
import csv
import time
import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 设置Chrome选项
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式，如果需要可注释掉
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# 创建存储目录
output_dir = 'Data'
os.makedirs(output_dir, exist_ok=True)

# 初始化存储变量
url_list = []
file_counter = 0

# 定义存储和加载Cookie的函数
def save_cookies(driver, path):
    with open(path, 'wb') as file:
        pickle.dump(driver.get_cookies(), file)

def load_cookies(driver, path):
    with open(path, 'rb') as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)

def save_to_csv(data, counter):
    filename = os.path.join(output_dir, f'urls_{counter}.csv')
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['URL'])
        for url in data:
            writer.writerow([url])
    print(f'Saved {len(data)} URLs to {filename}')

# 手动登录一次并保存Cookie
def login_and_save_cookies():
    driver.get("https://huggingface.co/login")
    time.sleep(30)  # 给予足够时间手动登录并完成二次验证
    save_cookies(driver, '../RawDataCollect/RawUrlDataCollect/cookies.pkl')

def fetch_urls(page_number):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式，如果需要可注释掉
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    try:
        # 加载Cookies并刷新页面
        driver.get("https://huggingface.co")
        load_cookies(driver, '../RawDataCollect/RawUrlDataCollect/cookies.pkl')
        driver.refresh()  # 刷新页面以应用Cookie

        if page_number == 0:
            url = "https://huggingface.co/models?sort=trending"
        else:
            url = f"https://huggingface.co/models?p={page_number}&sort=trending"

        # 打开目标URL
        driver.get(url)
        # 查找目标路径下的所有article元素
        path = "body > div > main > div > div > section.pt-8.border-gray-100.col-span-full.lg\\:col-span-6.xl\\:col-span-7.pb-12 > div.relative > div"
        section = driver.find_element(By.CSS_SELECTOR, path)
        articles = section.find_elements(By.TAG_NAME, 'article')

        # 提取并存储每个article元素的内容
        urls = [article.find_element(By.TAG_NAME, 'a').get_attribute('href') for article in articles]
        return urls
    except Exception as e:
        print(f"Error fetching page {page_number}: {e}")
        return []
    finally:
        driver.quit()

try:
    # 只在第一次运行时需要手动登录
    if not os.path.exists('../RawDataCollect/RawUrlDataCollect/cookies.pkl'):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        login_and_save_cookies()
        driver.quit()

    # 开始爬取数据
    page_numbers = range(8300, 15000)
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_urls, page_number): page_number for page_number in page_numbers}
        for future in as_completed(futures):
            urls = future.result()
            url_list.extend(urls)
            if len(url_list) >= 100:
                file_counter += 1
                save_to_csv(url_list[:100], file_counter)
                url_list = url_list[100:]

    # 保存剩余的URL
    if url_list:
        file_counter += 1
        save_to_csv(url_list, file_counter)

finally:
    print(f'Total pages processed: {len(page_numbers)}')
    # 保存错误的URL（如果有）
    error_file_path = 'ModelMarketDetailData/error_urls.csv'
    if error_urls:
        write_errors_to_csv(error_urls, error_file_path)
        print(f'The error URLs have been saved to {error_file_path}')
