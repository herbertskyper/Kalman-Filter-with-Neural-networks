from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By

# 设置webdriver路径
webdriver_service = Service(EdgeChromiumDriverManager().install())

# 创建webdriver对象
driver = webdriver.Edge(service=webdriver_service)

# 访问网页
driver.get('https://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&dyTabStr=MCwzLDEsMiw0LDYsNSw8LDcsOQ%3D%3D&word=%E4%BA%8C%E7%BB%B4%E7%A0%81')

# 执行JavaScript代码
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# 等待页面加载
driver.implicitly_wait(10)

# 获取页面源代码
content = driver.page_source

# 关闭浏览器
driver.quit()

