import os
import csv
import time
import pickle

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

# 初始化WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# 创建存储目录
output_dir = '../RawData/DataSetMarketRawUrlData'
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
        writer.writerow(['URL', ' dataset_type', 'dataset_volume', 'download_num', 'like_num'])
        for url, dataset_type, dataset_volume, download_num, like_num in data:
            writer.writerow([url, dataset_type, dataset_volume, download_num, like_num])
    print(f'Saved {len(data)} URLs to {filename}')


# 手动登录一次并保存Cookie
def login_and_save_cookies():
    driver.get("https://huggingface.co/login")
    time.sleep(30)  # 给予足够时间手动登录并完成二次验证
    save_cookies(driver, 'cookies.pkl')


try:
    # 只在第一次运行时需要手动登录
    if not os.path.exists('cookies.pkl'):
        login_and_save_cookies()
    else:
        driver.get("https://huggingface.co")
        load_cookies(driver, 'cookies.pkl')
        driver.refresh()  # 刷新页面以应用Cookie

    # 开始爬取数据
    # 6095
    for i in range(5300, 6095):
        # time.sleep(0.2)
        if (i + 1) == 1:
            url = "https://huggingface.co/datasets?sort=trending"
        else:
            url = f"https://huggingface.co/datasets?p={i}&sort=trending"
        # 打开目标URL
        driver.get(url)
        # 查找目标路径下的所有article元素
        path = "body > div > main > div > div > section.pt-8.border-gray-100.col-span-full.lg\\:col-span-6.xl\\:col-span-7.pb-12 > div.relative > div"
        section = driver.find_element(By.CSS_SELECTOR, path)
        articles = section.find_elements(By.TAG_NAME, 'article')

        # 提取并存储每个article元素的内容
        for article in articles:
            dataset_type = ''
            dataset_volume = ''
            download_num = ''
            like_num = ''
            try:
                divs = article.find_elements(By.TAG_NAME, 'div')
                if len(divs) > 0:
                    texts = divs[0].text
                    text = texts.replace("'", "").split('\n')
                    if len(text) == 4:
                        # if 'Updated' in text[3]:
                        #     model_type = text[1]
                        #     download_num = 'null'
                        #     like_num = 'null'
                        # else:
                        #     # 获取index3&5
                        #     model_type = 'null'
                        #     download_num = 'null'
                        #     like_num = text[3]
                        dataset_type = 'null'
                        dataset_volume = 'null'
                        download_num = 'null'
                        like_num = text[3]
                    elif len(text) == 6:
                        # 获取index3&5
                        if 'Updated' in text[3]:
                            dataset_type = 'null'
                            dataset_volume = text[5]
                            download_num = 'null'
                            like_num = 'null'
                        else:
                            dataset_type = 'null'
                            dataset_volume = 'null'
                            download_num = text[3]
                            like_num = text[5]
                    elif len(text) == 8:
                        # 获取索引1&5&7
                        dataset_type = text[1]
                        dataset_volume = 'null'
                        download_num = text[5]
                        like_num = text[7]
                    elif len(text) == 10:
                        # 获取索引1&5&8
                        dataset_type = text[1]
                        dataset_volume = text[5]
                        download_num = text[7]
                        like_num = text[9]
                    else:
                        dataset_type = 'null'
                        dataset_volume = 'null'
                        download_num = 'null'
                        like_num = 'null'
                else:
                    model_type = 'null'
                    download_num = 'null'
                    like_num = 'null'

            except Exception as e:
                text = f"Error: {e}"
            url_list.append(
                [article.find_element(By.TAG_NAME, 'a').get_attribute('href'), dataset_type, dataset_volume,
                 download_num, like_num])

        # 每100个URL存为一个文件
        if (i + 1) % 100 == 0:
            print(str(i) + ':' + str(file_counter))
            save_to_csv(url_list, int(i / 100))
            url_list.clear()
            file_counter += 1
            time.sleep(1)

    # 保存剩余的URL
    if url_list:
        save_to_csv(url_list, 'last')

finally:
    print(i)
    # 关闭浏览器
    driver.quit()
