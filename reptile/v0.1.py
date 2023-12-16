from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By

# ����webdriver·��
webdriver_service = Service(EdgeChromiumDriverManager().install())

# ����webdriver����
driver = webdriver.Edge(service=webdriver_service)

# ������ҳ
driver.get('https://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&dyTabStr=MCwzLDEsMiw0LDYsNSw8LDcsOQ%3D%3D&word=%E4%BA%8C%E7%BB%B4%E7%A0%81')

# ִ��JavaScript����
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# �ȴ�ҳ�����
driver.implicitly_wait(10)

# ��ȡҳ��Դ����
content = driver.page_source

# �ر������
driver.quit()

