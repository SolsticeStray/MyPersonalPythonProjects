import requests
from bs4 import BeautifulSoup

# 1. 吸尘（带伪装）：必须要告诉服务器“我是浏览器”，不是机器人
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
url = 'http://scp-wiki-cn.wikidot.com/scp-173'

try:
    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
        # 2. 消化
        soup = BeautifulSoup(response.text, 'html.parser')

        # 在 SCP Wiki 中，正文通常在 id="page-content" 里面
        content_div = soup.find('div', id='page-content')

        if content_div:
            print(f"--- 成功获取 {url} ---")

            # 3. 针对性拉取：Wiki 的格式比较自由，我们尝试抓取前几段文本
            # 这里模拟“人类阅读”，提取所有段落
            paragraphs = content_div.find_all('p')

            for p in paragraphs[:4]:  # 为了演示，只看前4段
                text = p.get_text().strip()
                if text:
                    print(text)
                    print("...")
        else:
            print("未找到正文内容，可能是网页结构变了。")
    else:
        print(f"访问失败，状态码: {response.status_code}")

except Exception as e:
    print(f"发生错误: {e}")