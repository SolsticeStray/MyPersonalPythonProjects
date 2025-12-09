import requests
from bs4 import BeautifulSoup

# 1. 准备工作：设置 URL 和 伪装头 (Wiki 对没有 User-Agent 的请求很敏感)
url = "https://zh.wikipedia.org/wiki/PewDiePie与T-Series之争"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print(f"正在访问: {url} ...")
response = requests.get(url, headers=headers)

if response.status_code == 200:
    # 2. 消化：解析 HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # --- 模块 A: 抓取标题和简介 (文本) ---
    print("\n=== 📝 页面简介 ===")
    title = soup.find('h1', id='firstHeading').text
    print(f"标题: {title}")

    # 维基百科的正文通常在 mw-content-text -> mw-parser-output 下
    # 我们抓取前两段文字
    content_div = soup.find('div', class_='mw-parser-output')
    paragraphs = content_div.find_all('p', recursive=False)  # recursive=False 避免抓到表格里的 p

    for i, p in enumerate(paragraphs[:2]):
        text = p.get_text().strip()
        if text:
            print(f"段落 {i + 1}: {text[:100]}...")  # 只显示前100个字

    # --- 模块 B: 抓取侧边栏图片 (图片) ---
    print("\n=== 🖼️ 关键图片 ===")
    # 维基百科的侧边栏通常是 class="infobox"
    infobox = soup.find('table', class_='infobox')
    if infobox:
        img_tag = infobox.find('img')
        if img_tag:
            # 维基百科的图片链接通常是 //upload.wikimedia... 开头，缺少 https:
            src = img_tag.get('src')
            if src.startswith('//'):
                src = 'https:' + src
            print(f"发现主图链接: {src}")
            print("(你可以复制这个链接在浏览器打开，或者用代码下载它)")
        else:
            print("Infobox 中未找到图片")

    # --- 模块 C: 抓取统计表格 (表格) ---
    print("\n=== 📊 战况统计表格 ===")
    # 维基百科的标准表格 class 是 "wikitable"
    # 我们尝试找包含“时间”和“次数”的那个表格
    tables = soup.find_all('table', class_='wikitable')

    target_table = None
    for t in tables:
        # 简单的判断：如果表头包含 "日期" 或 "时间"，可能就是我们要找的
        if "日期" in t.text or "時間" in t.text:
            target_table = t
            break

    if target_table:
        # 遍历表格的行 (tr)
        rows = target_table.find_all('tr')
        print(f"找到表格，共 {len(rows)} 行，显示前 5 行数据：")

        for row in rows[:5]:  # 只演示前5行
            # 提取每一行中的单元格 (th 或 td)
            cols = row.find_all(['th', 'td'])
            # 使用列表推导式清洗数据：去除换行符
            cols_text = [ele.text.strip() for ele in cols]
            print(cols_text)
    else:
        print("未找到目标统计表格")

else:
    print("访问失败，请检查网络或 URL")