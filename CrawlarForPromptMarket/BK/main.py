import os
import csv
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 设置Chrome选项
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# 初始化WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# 创建存储目录
output_dir = 'Data'
os.makedirs(output_dir, exist_ok=True)

# 初始化存储变量
url_list = []
file_counter = 0


def save_to_csv(data, counter):
    filename = os.path.join(output_dir, f'urls_{counter}.csv')
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['URL'])
        for url in data:
            writer.writerow([url])
    print(f'Saved {len(data)} URLs to {filename}')


try:
    # 23991
    for i in range(1500,23991):
        time.sleep(0.2)
        if (i+1) == 1:
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
        for article in articles:
            url_list.append(article.find_element(By.TAG_NAME, 'a').get_attribute('href'))

        # 每100个URL存为一个文件
        if (i+1) % 100 == 0:
            print(str(i) + ':' + str(file_counter))
            save_to_csv(url_list, int(i/100))
            url_list.clear()
            file_counter += 1
            time.sleep(1)


    # 保存剩余的URL
    if url_list:
        save_to_csv(url_list,int(i/100))

finally:
    print(i)
    # 关闭浏览器
    driver.quit()
