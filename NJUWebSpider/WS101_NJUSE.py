# 注意：请先确保 curl_cffi 和 PyMySQL 库是最新版本
# pip install --upgrade curl_cffi PyMySQL

from curl_cffi import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin
import time
from datetime import datetime
import pymysql  # 导入 PyMySQL 库

# --- MySQL 数据库配置 ---
# 请根据您的实际安装情况修改以下信息
DB_CONFIG = {
    'host': 'localhost',  # MySQL 服务器地址，通常为 localhost
    'port': 3306,  # MySQL 默认端口
    'user': 'crawler',  # MySQL 用户名，这里使用 root (不推荐在生产环境用 root)
    'password': 'NovB@666',  # 您安装 MySQL 时设置的 root 密码
    'database': 'crawler_db',  # 您刚才创建的数据库名称
    'charset': 'utf8mb4'  # 推荐使用 utf8mb4 以支持更广泛的字符，包括 emoji
}


def save_activities_to_mysql(activities):
    """
    将活动信息列表保存到 MySQL 数据库。

    :param activities: 包含活动信息字典的列表
    """
    connection = None
    cursor = None
    try:
        # 连接到 MySQL 数据库
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 正在连接到 MySQL 数据库...")
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # SQL 插入语句
        insert_sql = """
        INSERT INTO activities (text_content, link_url) 
        VALUES (%s, %s)
        """

        inserted_count = 0
        for activity in activities:
            # 防止 SQL 注入，使用参数化查询
            cursor.execute(insert_sql, (activity['text'], activity['link']))
            inserted_count += 1

        # 提交事务，确保数据被写入数据库
        connection.commit()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] --- 成功向数据库插入 {inserted_count} 条活动信息 ---")

    except pymysql.MySQLError as e:
        # 捕获 MySQL 相关错误
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] MySQL 错误: {e}")
        if connection:
            connection.rollback()  # 发生错误时回滚事务
    except Exception as e:
        # 捕获其他可能的异常
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 保存到数据库时发生未知错误: {e}")
        if connection:
            connection.rollback()  # 发生错误时回滚事务
    finally:
        # 确保游标和连接被关闭，释放资源
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 数据库连接已关闭。")


def get_nju_im_news_with_curl_cffi_and_save():
    """
    使用 curl_cffi 库爬取南京大学信息管理学院网站内容，
    提取活动信息，并保存到 MySQL 数据库。
    """
    url = "https://im.nju.edu.cn/"

    # 设置一个常见的浏览器 User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 正在使用 curl_cffi 连接 (无 impersonate)...")
        # 发送请求，不使用 impersonate 参数
        response = requests.get(url, headers=headers, timeout=10)

        # 检查 HTTP 状态码
        if response.status_code == 200:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 请求成功，状态码: {response.status_code}")

            # 获取页面内容
            content = response.content.decode('utf-8')  # 使用 .content 然后手动解码

            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(content, 'html.parser')

            print("--- 网页标题 ---")
            print(soup.title.string if soup.title else "无标题")

            # --- 尝试查找知识库中提到的活动信息 ---
            print("\n--- 查找可能的活动信息 ---")
            # 搜索包含 "报告", "会议", "讲座", "学术", "活动", "评议人", "主持人", "时间", "地点" 等关键词的元素
            possible_elements = soup.find_all(string=lambda text: text and any(keyword in text for keyword in
                                                                               ["报告", "会议", "讲座", "学术", "活动",
                                                                                "评议人", "主持人", "时间", "地点"]))

            activities = []  # 用于存储找到的活动信息字典
            if possible_elements:
                found_content = set()  # 使用集合去重，基于 text 字段
                for element in possible_elements:
                    # 获取包含关键词的标签及其父级或同级标签的内容
                    parent = element.parent
                    if parent:
                        activity_info = {
                            "text": "",  # 存储提取到的文本信息
                            "link": ""  # 存储相关链接（如果有）
                        }
                        # 尝试获取更完整的信息，例如 <a> 标签的文本和链接
                        if parent.name == 'a':
                            link_text = parent.get_text(strip=True)
                            link_url = parent.get('href')
                            full_url = urljoin(url, link_url)
                            activity_info["text"] = link_text
                            activity_info["link"] = full_url
                        else:
                            # 获取父标签的文本内容
                            activity_info["text"] = parent.get_text(strip=True)
                            # 如果父标签本身不是链接，尝试在父标签内查找链接
                            link_tag = parent.find('a')
                            if link_tag:
                                link_url = link_tag.get('href')
                                full_url = urljoin(url, link_url)
                                activity_info["link"] = full_url

                        text_key = activity_info["text"]
                        if text_key and text_key not in found_content:
                            print(activity_info["text"])
                            if activity_info["link"]:
                                print(f"链接: {activity_info['link']}")
                            print("-" * 20)
                            activities.append(activity_info)  # 将信息字典添加到列表中
                            found_content.add(text_key)

                if activities:
                    # 调用新函数，将数据保存到 MySQL
                    save_activities_to_mysql(activities)
                else:
                    print("\n--- 未找到任何活动信息，数据库未更新。 ---")

            else:
                print("未找到包含关键词的元素。")
                print("\n--- 未找到任何活动信息，数据库未更新。 ---")

        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 请求失败，状态码: {response.status_code}")

    except requests.RequestsError as e:
        # curl_cffi 的异常基类是 requests.RequestsError (注意是 curl_cffi.requests.RequestsError)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] curl_cffi 请求发生错误: {e}")
    except UnicodeDecodeError as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 内容解码错误: {e}")
    except Exception as e:
        # 捕获其他可能的异常
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 发生未知错误: {e}")
        import traceback
        traceback.print_exc()  # 打印详细的错误堆栈信息


def run_scheduler(frequency_minutes):
    """
    定时运行爬虫函数。

    :param frequency_minutes: 爬取间隔，单位为分钟
    """
    frequency_seconds = frequency_minutes * 60
    print(f"--- 爬虫已启动，将每隔 {frequency_minutes} 分钟运行一次。 ---")
    print(f"--- 首次运行将在 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 开始。 ---")
    print("--- 按 Ctrl+C 停止程序。 ---")
    try:
        while True:
            get_nju_im_news_with_curl_cffi_and_save()
            print(f"--- 等待 {frequency_minutes} 分钟后再次运行... ---")
            time.sleep(frequency_seconds)
    except KeyboardInterrupt:
        print("\n--- 程序已被用户中断。 ---")


# --- 配置爬取频率 ---
# 例如，设置为每 30 分钟爬取一次
SCHEDULING_FREQUENCY_MINUTES = 30  # 修改这个数字来改变爬取间隔

# --- 重要：请务必修改 DB_CONFIG 中的 'password' 为您的 MySQL root 密码 ---
# 例如: 'password': 'MyNewPass123'

# 执行定时爬虫
if __name__ == "__main__":
    # 在启动前先检查配置
    if DB_CONFIG['password'] == 'your_password':
        print("错误: 请先修改 DB_CONFIG 中的 'password' 为您的 MySQL 实际密码！")
        exit(1)
    run_scheduler(SCHEDULING_FREQUENCY_MINUTES)