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
output_dir = '../RawData/ModelMarketRawUrlData'
os.makedirs(output_dir, exist_ok=True)

# 初始化存储变量
file_counter = 0


# 定义存储和加载Cookie的函数
def save_cookies(driver, path):
    with open(path, 'wb') as file:
        pickle.dump(driver.get_cookies(), file)


def load_cookies(driver, cookies):
    driver.delete_all_cookies()
    for cookie in cookies:
        driver.add_cookie(cookie)


def add_cookies_to_webdriver(driver, cookies):
    driver.delete_all_cookies()
    for cookie in cookies:
        driver.add_cookie(cookie)


def save_to_csv(data, counter):
    filename = os.path.join(output_dir, f'urls_{counter}.csv')
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['URL', 'model_type', 'download_num', 'like_num'])
        for url, model_type, download_num, like_num in data:
            writer.writerow([url, model_type, download_num, like_num])
    print(f'Saved {len(data)} URLs to {filename}')


# 手动登录一次并保存Cookie
def login_and_save_cookies(driver):
    driver.get("https://huggingface.co/login")
    time.sleep(30)  # 给予足够时间手动登录并完成二次验证
    save_cookies(driver, 'cookies.pkl')


# 单个页面的爬取函数
def fetch_page(i, cookies):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        load_cookies(driver, cookies)
        driver.refresh()  # 刷新页面以应用Cookie

        time.sleep(0.2)
        if (i + 1) == 1:
            url = "https://huggingface.co/models?sort=trending"
        else:
            url = f"https://huggingface.co/models?p={i}&sort=trending"

        # 打开目标URL
        driver.get(url)
        # 查找目标路径下的所有article元素
        path = "body > div > main > div > div > section.pt-8.border-gray-100.col-span-full.lg\\:col-span-6.xl\\:col-span-7.pb-12 > div.relative > div"
        section = driver.find_element(By.CSS_SELECTOR, path)
        articles = section.find_elements(By.TAG_NAME, 'article')

        # 提取并存储每个article元素的内容
        page_data = []
        for article in articles:
            model_type = ''
            download_num = ''
            like_num = ''
            try:
                divs = article.find_elements(By.TAG_NAME, 'div')
                if len(divs) > 0:
                    texts = divs[0].text
                    text = texts.replace("'", "").split('\n')
                    if len(text) == 4:
                        if 'Updated' in text[3]:
                            model_type = text[1]
                            download_num = 'null'
                            like_num = 'null'
                        else:
                            model_type = 'null'
                            download_num = 'null'
                            like_num = text[3]
                    elif len(text) == 6:
                        if 'Updated' in text[3]:
                            model_type = text[1]
                            download_num = 'null'
                            like_num = text[5]
                        else:
                            model_type = 'null'
                            download_num = text[3]
                            like_num = text[5]
                    elif len(text) == 8:
                        model_type = text[1]
                        download_num = text[5]
                        like_num = text[7]
                    elif len(text) == 9:
                        model_type = text[1]
                        download_num = text[5]
                        like_num = text[8]
                    else:
                        model_type = 'null'
                        download_num = 'null'
                        like_num = 'null'
                else:
                    model_type = 'null'
                    download_num = 'null'
                    like_num = 'null'
            except Exception as e:
                text = f"Error: {e}"
            page_data.append(
                [article.find_element(By.TAG_NAME, 'a').get_attribute('href'), model_type, download_num, like_num])

        return page_data
    except Exception as e:
        print(f"Error fetching page {i}: {e}")
        return []
    finally:
        driver.quit()


def load_cookies_from_pkl(file_path):
    with open(file_path, 'rb') as file:
        cookies = pickle.load(file)
    return cookies


# 主函数
def main():
    try:
        # 只在第一次运行时需要手动登录
        if not os.path.exists('cookies.pkl'):
            login_and_save_cookies(
                webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options))
        cookies = load_cookies_from_pkl('cookies.pkl')
        # 开始爬取数据
        url_list = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(fetch_page, i, cookies) for i in range(0, 10)]
            for future in as_completed(futures):
                url_list.extend(future.result())

        # 保存数据
        global file_counter
        save_to_csv(url_list, file_counter)

    finally:
        print("Done")


if __name__ == "__main__":
    main()
