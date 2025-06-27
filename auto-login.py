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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': LOGIN_URL
    }
    
    try:
        # 获取登录页面
        response = session.get(LOGIN_URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 准备payload - 先检查实际表单字段
        payload = {
            "email": USERNAME,  # 可能需要改为username或其他字段
            "password": PASSWORD
        }
        
        # 添加所有隐藏字段
        for hidden in soup.find_all("input", type="hidden"):
            payload[hidden['name']] = hidden['value']
        
        # 添加Content-Type头
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        # 提交登录
        login_response = session.post(LOGIN_URL, 
                                    data=payload, 
                                    headers=headers,
                                    allow_redirects=True)
        
        # 调试输出
        print("Login response URL:", login_response.url)
        print("Status code:", login_response.status_code)
        
        # 检查登录成功条件可能需要调整
        if login_response.status_code == 200 and ("admin" in login_response.url.lower() or "Welcome" in login_response.text.lower()):
            message = "✅ **登录成功！**"
        else:
            message = f"❌ **登录可能失败！**\n状态码: {login_response.status_code}\nURL: {login_response.url}"
        
        print(message)
        send_telegram_message(message)
        
        # 尝试访问仪表板
        dashboard_response = session.get(DASHBOARD_URL, headers=headers)
        if dashboard_response.status_code == 200:
            print("✅ 成功访问仪表板")
        else:
            print(f"❌ 仪表板访问失败，状态码: {dashboard_response.status_code}")
    
    except Exception as e:
        error_msg = f"⚠️ **错误详情：**\n{str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        send_telegram_message(error_msg)

if __name__ == "__main__":
    login()
