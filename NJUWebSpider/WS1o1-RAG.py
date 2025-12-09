import os
from typing import List, Dict
import pymysql
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI # 使用 OpenAI 封装，但指向 DeepSeek
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# --- MySQL 数据库配置 ---
# 请根据您的实际安装情况修改以下信息
DB_CONFIG = {
    'host': 'localhost',        # MySQL 服务器地址，本地用 localhost
    'port': 3306,              # MySQL 默认端口
    'user': 'root',            # MySQL 用户名
    'password': 'Sunxiaochuan258', # 您的 MySQL 密码
    'database': 'nju_crawler_db', # 您创建的数据库名称
    'charset': 'utf8mb4'       # 推荐使用 utf8mb4 以支持更广泛的字符
}

# --- DeepSeek LLM 配置 ---
# 请根据您的 DeepSeek 账户信息进行配置
DEEPSEEK_API_KEY = "sk-4911c93f3cc146bba9b4869cb46290c2" # 替换为您的 DeepSeek API Key
DEEPSEEK_API_BASE = "https://api.deepseek.com" # 替换为 DeepSeek 提供的 API Base URL
DEEPSEEK_MODEL_NAME = "deepseek-chat" # 替换为您要使用的具体模型名称

# 实例化 ChatOpenAI，但指向 DeepSeek API
llm = ChatOpenAI(
    model=DEEPSEEK_MODEL_NAME,
    temperature=0, # 设置温度
    openai_api_key=DEEPSEEK_API_KEY, # 使用 DeepSeek API Key
    openai_api_base=DEEPSEEK_API_BASE, # 使用 DeepSeek API Base URL
    # openai_proxy="your_proxy_url_here", # 如果需要代理，请取消注释并填入
)

@tool
def get_latest_activities(limit: int = 5) -> List[Dict]:
    """
    Fetches the latest activities from the MySQL database.
    Returns a list of dictionaries containing activity information.
    """
    connection = None
    cursor = None
    try:
        # 连接到 MySQL 数据库
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(pymysql.cursors.DictCursor) # 使用 DictCursor 获取字典格式结果

        # SQL 查询语句，获取最新的 limit 条记录
        select_sql = """
        SELECT text_content, link_url, crawled_time
        FROM activities
        ORDER BY crawled_time DESC
        LIMIT %s
        """

        cursor.execute(select_sql, (limit,))
        results = cursor.fetchall()

        # 将结果转换为列表
        activities_list = [dict(row) for row in results]
        print(f"[DEBUG] Retrieved {len(activities_list)} activities from DB.")
        return activities_list

    except pymysql.MySQLError as e:
        print(f"[ERROR] MySQL error in get_latest_activities: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] General error in get_latest_activities: {e}")
        return []
    finally:
        # 确保游标和连接被关闭
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@tool
def search_activities_by_keyword(keyword: str) -> List[Dict]:
    """
    Searches for activities in the MySQL database containing a specific keyword in the text_content.
    Returns a list of dictionaries containing matching activity information.
    """
    connection = None
    cursor = None
    try:
        # 连接到 MySQL 数据库
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(pymysql.cursors.DictCursor) # 使用 DictCursor 获取字典格式结果

        # SQL 查询语句，按关键词搜索
        select_sql = """
        SELECT text_content, link_url, crawled_time
        FROM activities
        WHERE text_content LIKE %s
        ORDER BY crawled_time DESC
        LIMIT 10 -- 限制搜索结果数量
        """

        search_pattern = f"%{keyword}%"
        cursor.execute(select_sql, (search_pattern,))
        results = cursor.fetchall()

        # 将结果转换为列表
        activities_list = [dict(row) for row in results]
        print(f"[DEBUG] Found {len(activities_list)} activities matching keyword '{keyword}' from DB.")
        return activities_list

    except pymysql.MySQLError as e:
        print(f"[ERROR] MySQL error in search_activities_by_keyword: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] General error in search_activities_by_keyword: {e}")
        return []
    finally:
        # 确保游标和连接被关闭
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# --- LangChain Agent 配置 ---
tools = [get_latest_activities, search_activities_by_keyword]

# 定义提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能助手，可以查询南京大学信息管理学院的最新活动信息。"
               "请根据用户的问题，调用相应的工具从数据库中获取信息，并生成简洁、准确的回答。"
               "如果用户问及未来活动，请告知信息来源于已爬取的数据，可能不是最新的未来安排，建议访问官网确认。"
               "请优先返回活动的文本摘要和链接。"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"), # Agent 的思考过程占位符
])

# 创建 LangChain Agent
agent = create_tool_calling_agent(llm, tools, prompt)

# 创建 Agent 执行器
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True) # verbose=True 可以看到 agent 的思考过程

def query_activities(question: str):
    """
    Query the activities database using the LangChain agent.
    """
    print(f"\n--- 用户提问: {question} ---")
    try:
        # 执行查询
        response = agent_executor.invoke({"input": question})
        print(f"\n--- AI 回答: ---\n{response['output']}\n")
    except Exception as e:
        print(f"[ERROR] 执行查询时发生错误: {e}")

# --- 主程序 ---
if __name__ == "__main__":
    # 检查数据库配置
    if DB_CONFIG['password'] == 'your_password':
        print("错误: 请先修改 DB_CONFIG 中的 'password' 为您的 MySQL 实际密码！")
        exit(1)

    # 检查 DeepSeek API Key
    if DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
        print("错误: 请先修改 DEEPSEEK_API_KEY 为您的实际 DeepSeek API Key！")
        exit(1)

    print("--- 南京大学信息管理学院活动 RAG 查询系统 (DeepSeek) 已启动 ---")
    print("--- 输入 'quit' 退出 ---\n")

    while True:
        user_input = input("请输入您的问题 (例如: '最近有哪些学术报告会？', '搜索 AI 相关的活动'): ")
        if user_input.lower() == 'quit':
            print("再见！")
            break
        query_activities(user_input)
