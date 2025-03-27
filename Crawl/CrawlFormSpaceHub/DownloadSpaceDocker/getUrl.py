from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# 设置浏览器驱动
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 打开目标网页
url1 = 'https://huggingface.co/spaces/krrishD/facebook_bart-large-cnn?docker=true'
url = 'https://huggingface.co/spaces/akhaliq/AnimeGANv2?docker=true'
# url1 = 'https://huggingface.co/spaces/krrishD/facebook_bart-large-cnn?docker=true'
# url1 = 'https://huggingface.co/spaces/krrishD/facebook_bart-large-cnn?docker=true'

driver.get(url)

# 等待页面加载完成
driver.implicitly_wait(2)  # 等待最多 10 秒钟，直到页面加载

# 使用 XPath 和 contains() 函数匹配包含 "docker run -it" 的元素
floatbox_content = driver.find_element(By.XPATH, "//*[contains(text(), 'docker run -it')]").text


# 打印浮框内容
print(floatbox_content)

# 关闭浏览器
driver.quit()