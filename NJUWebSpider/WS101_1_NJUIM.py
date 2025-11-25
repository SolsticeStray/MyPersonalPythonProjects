# 注意：请先确保 curl_cffi 库是最新版本
# pip install --upgrade curl_cffi
# 如果最新版仍然不支持或移除 impersonate 后能工作，则使用此代码

from curl_cffi import requests
from bs4 import BeautifulSoup


def get_nju_im_news_with_curl_cffi():
    """
    使用 curl_cffi 库爬取南京大学信息管理学院网站内容。
    移除 impersonate 参数以兼容旧版本或使用默认 libcurl 行为。
    """
    url = "https://im.nju.edu.cn/"

    # 设置一个常见的浏览器 User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        print("正在使用 curl_cffi 连接 (无 impersonate)...")
        # 发送请求，不使用 impersonate 参数
        response = requests.get(url, headers=headers, timeout=10)

        # 检查 HTTP 状态码
        if response.status_code == 200:
            print(f"请求成功，状态码: {response.status_code}")

            # 获取页面内容
            content = response.content.decode('utf-8')  # 使用 .content 然后手动解码

            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(content, 'html.parser')

            print("--- 网页标题 ---")
            print(soup.title.string if soup.title else "无标题")
            print("\n--- 网页内容 ---")

            # --- 尝试查找知识库中提到的活动信息 ---
            print("\n--- 查找可能的活动信息 ---")
            # 搜索包含 "报告", "会议", "讲座", "学术", "活动", "评议人", "主持人" 等关键词的元素
            possible_elements = soup.find_all(string=lambda text: text and any(keyword in text for keyword in
                                                                               ["报告", "会议", "讲座", "学术", "活动",
                                                                                "评议人", "主持人", "时间", "地点"]))

            if possible_elements:
                found_content = set()  # 使用集合去重
                for element in possible_elements:
                    # 获取包含关键词的标签及其父级或同级标签的内容
                    parent = element.parent
                    if parent:
                        # 尝试获取更完整的信息，例如 <a> 标签的文本和链接
                        if parent.name == 'a':
                            link_text = parent.get_text(strip=True)
                            link_url = parent.get('href')
                            # 注意：curl_cffi.requests.Response 对象没有 requests.compat.urljoin 的直接等价物
                            # 我们可以使用 urllib.parse.urljoin
                            from urllib.parse import urljoin
                            full_url = urljoin(url, link_url)
                            info = f"链接文本: {link_text}\n完整链接: {full_url}\n"
                        else:
                            # 获取父标签的文本内容
                            info = parent.get_text(strip=True)

                        if info and info not in found_content:
                            print(info)
                            print("-" * 20)
                            found_content.add(info)
            else:
                print("未找到包含关键词的元素。")

        else:
            print(f"请求失败，状态码: {response.status_code}")

    except requests.RequestsError as e:
        # curl_cffi 的异常基类是 requests.RequestsError (注意是 curl_cffi.requests.RequestsError)
        print(f"curl_cffi 请求发生错误: {e}")
    except UnicodeDecodeError as e:
        print(f"内容解码错误: {e}")
    except Exception as e:
        # 捕获其他可能的异常
        print(f"发生未知错误: {e}")
        import traceback
        traceback.print_exc()  # 打印详细的错误堆栈信息


# 执行爬虫函数
if __name__ == "__main__":
    get_nju_im_news_with_curl_cffi()
