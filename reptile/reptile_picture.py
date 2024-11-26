#-*encoding:utf-8-*
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import os
import time

driver = webdriver.Chrome()#用selenium库打开谷歌浏览器
driver.maximize_window()
driver.get('https://cn.bing.com/images/search?q=%E4%BA%8C%E7%BB%B4%E7%A0%81&form=HDRSC2&first=1&cw=1177&ch=789')

img_dir = os.path.join(os.curdir, 'qrcodes')#qrcodes是文件夹名称
'''创建文件夹'''
if not os.path.isdir(img_dir):
    os.mkdir(img_dir)
    
num=1
for i in range(10):  # 滚动10次，你可以根据需要调整这个数字
    #img_list = driver.find_elements(By.CLASS_NAME,'mimg')
    img_list = driver.find_elements(By.XPATH,'//*[@class="img_cont hoff"]/img')
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    img_path = []
    for img in img_list:
        path = img.get_attribute('src')
        img_path.append(path)
        
    '''下载图片'''
    for path in img_path:
        img_name = 'qrcode' + str(num) + '.jpg'  # 图片名称
        if path is None:
            continue
        num+=1
        filepath = os.path.join(img_dir, img_name)
        print('Saving image to:', filepath)
        try:
            resp = requests.get(path)
            resp.raise_for_status()  # 如果状态码不是200，引发异常
        except requests.RequestException as e:
            print('Failed to download image:', e)
            continue  # 跳过这个路径，开始下一次迭代
        with open(filepath, 'wb') as f:
            for chunk in resp.iter_content(1024):  # 限速写入图片
                f.write(chunk)
        print('Image saved.')