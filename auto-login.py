import requests
from bs4 import BeautifulSoup
from os import getenv

# 登录页面和登录提交的URL
LOGIN_URL = "https://searcade.userveria.com/login/"
DASHBOARD_URL = "https://searcade.com/en/"

# 用户凭证（通过变量管理）
USERNAME = getenv('USERNAME')  # 通过环境变量获取
PASSWORD = getenv('PASSWORD')

if not USERNAME or not PASSWORD:
    raise ValueError("⚠️ 环境变量 USERNAME 和 PASSWORD 必须设置！")

# Telegram 发送消息函数
def send_telegram_message(message):
    bot_token = getenv('TELEGRAM_BOT_TOKEN')  # 通过环境变量获取 Bot Token
    chat_id = getenv('TELEGRAM_CHAT_ID')      # 通过环境变量获取 Chat ID
    if not bot_token or not chat_id:
        print("⚠️ TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID 未设置，无法发送消息。")
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()

# 创建一个会话对象来维护Cookies
session = requests.Session()

def login():
    payload = {
        "email": USERNAME,  # 用户名/邮箱
        "password": PASSWORD  # 密码
    }
    try:
        # 获取登录页面并解析隐藏字段 (如有必要)
        response = session.get(LOGIN_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取隐藏字段(如果有，比如csrf_token)
        hidden_inputs = soup.find_all("input", type="hidden")
        for hidden in hidden_inputs:
            payload[hidden['name']] = hidden['value']

        # 提交登录表单
        login_response = session.post(LOGIN_URL, data=payload)
        login_response.raise_for_status()

        # 检查是否成功登录
        if "admin" in login_response.url or "Welcome" in login_response.text:
            message = "✅ **登录成功！**\n已成功登录 searcade 仪表板。"
        else:
            message = "❌ **登录失败！**\n请检查 searcade 用户名和密码是否正确。"
        print(message)
        
        # 发送Telegram消息
        send_telegram_message(message)

        # 访问受保护页面 (如用户仪表板)
        dashboard_response = session.get(DASHBOARD_URL)
        if dashboard_response.status_code == 200:
            dashboard_message = "✅ **成功访问仪表板！**"
            print(dashboard_message)
            send_telegram_message(dashboard_message)
        else:
            dashboard_message = "❌ **访问仪表板失败！**"
            print(dashboard_message)
            send_telegram_message(dashboard_message)
    
    except requests.exceptions.RequestException as e:
        error_message = f"⚠️ **请求发生错误：**\n{e}"
        print(error_message)
        send_telegram_message(error_message)

if __name__ == "__main__":
    login()
