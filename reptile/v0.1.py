#-*encoding:utf-8-*
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import requests
import os

#find / -name "msedgedriver" 2>/dev/null  查找msedgedriver路径
# 设置webdriver路径
driver_path = '/home/herbert/edgedriver/msedgedriver'

# 创建webdriver对象
driver = webdriver.Edge(executable_path=driver_path)

# 访问网页
driver.get('https://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&dyTabStr=MCwzLDEsMiw0LDYsNSw8LDcsOQ%3D%3D&word=%E4%BA%8C%E7%BB%B4%E7%A0%81')

# 执行JavaScript代码
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# 等待页面加载
driver.implicitly_wait(10)

# 获取页面源代码
content = driver.page_source

# 使用BeautifulSoup解析页面源代码
soup = BeautifulSoup(content, 'html.parser')

# 找到所有的二维码图片
img_tags = soup.find_all('img')

# 创建一个文件夹来保存二维码图片
if not os.path.exists('qrcodes'):
    os.makedirs('qrcodes')

# 下载所有的二维码图片
for i, img_tag in enumerate(img_tags):
    img_url = img_tag.get('src')
    response = requests.get(img_url)
    with open('qrcodes/qrcode{}.jpg'.format(i), 'wb') as f:
        f.write(response.content)

# 关闭浏览器
driver.quit()

