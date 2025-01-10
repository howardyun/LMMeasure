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
# chrome_options.add_argument("--headless")  # 无头模式，如果需要可注释掉
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# 使用 ChromeDriverManager 自动下载并配置指定版本的 ChromeDriver


# 初始化WebDriver
driver = webdriver.Chrome( options=chrome_options)

output_dir = 'RepoData/'
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
            writer.writerow(url)
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
    start_page = 700
    # 开始爬取数据
    driver.get(f"https://huggingface.co/spaces?p={start_page}&sort=trending")

    for i in range(700, 9351):
        # 查找目标路径下的所有article元素
        css_selector = "body > div > main > div.SVELTE_HYDRATER.contents > div > div > div.pb-12 > div.grid.grid-cols-1.gap-x-4.gap-y-6.md\:grid-cols-3.xl\:grid-cols-4"
        section = driver.find_element(By.CSS_SELECTOR, css_selector)
        articles = section.find_elements(By.TAG_NAME, 'article')

        # 提取并存储每个article元素的内容
        for article in articles:
            url_list.append([article.find_element(By.TAG_NAME, 'a').get_attribute('href')])

        # 每100个URL存为一个文件
        if (i + 1) % 100 == 0:
            print(str(i) + ':' + str(file_counter))
            save_to_csv(url_list, int(i / 100))
            url_list.clear()
            file_counter += 1
            time.sleep(1)

        # 点击“下一页”按钮
        try:
            next_button = driver.find_element(By.XPATH, '//a[contains(@class, "next") and contains(text(), "Next")]')
            next_button.click()
            time.sleep(2)  # 给予足够时间加载新页面
        except Exception as e:
            print(f"An error occurred while clicking next button: {e}")
            break

    # 保存剩余的URL
    if url_list:
        save_to_csv(url_list, 'last')

finally:
    print(i)
    # 关闭浏览器
    driver.quit()

# import shutil
#
# # 指定要删除的文件夹路径
# folder_path = r"C:\Users\YSX\.wdm\drivers\chromedriver"
#
# # 删除文件夹及其所有内容
# try:
#     shutil.rmtree(folder_path)
#     print(f"Folder {folder_path} has been deleted.")
# except FileNotFoundError:
#     print(f"Folder {folder_path} does not exist.")
# except PermissionError:
#     print(f"Permission denied: could not delete {folder_path}.")
# except Exception as e:
#     print(f"An error occurred: {e}")

