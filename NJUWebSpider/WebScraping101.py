import requests
from bs4 import BeautifulSoup

# 1. 吸尘：访问网站
url = 'http://quotes.toscrape.com/'
response = requests.get(url)

# 2. 消化：把获取的 HTML 变成可解析对象
soup = BeautifulSoup(response.text, 'html.parser')

# 3. 解析与拉取：找到每一个名言卡片
quotes = soup.find_all('div', class_='quote')

print("--- 开始收集 ---")
for quote in quotes:
    # 提取名言内容
    text = quote.find('span', class_='text').text
    # 提取作者
    author = quote.find('small', class_='author').text

    print(f"名言: {text}")
    print(f"作者: {author}")
    print("-" * 20)