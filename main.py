import os
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone

# 1. 設定要隨機抽選的股票清單 (以台股為例，Yahoo Finance 的代號通常加上 .TW)
STOCK_LIST = ['2330.TW', '2317.TW', '2454.TW', '2308.TW', '2881.TW']

def get_stock_price(ticker):
    # 使用 Yahoo Finance 美國站的資料，因為其 HTML 結構較為穩定
    url = f"https://finance.yahoo.com/quote/{ticker}"
    
    # 必須加入 User-Agent 偽裝成瀏覽器，否則會被 Yahoo 阻擋
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Yahoo Finance 目前將股價放在 <fin-streamer> 標籤中
        price_element = soup.find('fin-streamer', {'data-symbol': ticker, 'data-field': 'regularMarketPrice'})
        
        if price_element:
            return price_element.text
        else:
            return "無法解析股價"
    except Exception as e:
        return f"爬取失敗: {e}"

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    requests.post(url, data=payload)

if __name__ == "__main__":
    # 2. 從環境變數讀取 Telegram 資訊 (稍後會設定在 GitHub Secrets)
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("請先設定 TELEGRAM_TOKEN 與 TELEGRAM_CHAT_ID 環境變數")
        exit(1)

    # 3. 隨機選擇一檔股票並爬取
    target_stock = random.choice(STOCK_LIST)
    price = get_stock_price(target_stock)
    
    # 4. 取得當前台灣時間 (UTC+8)
    tz_taipei = timezone(timedelta(hours=8))
    current_time = datetime.now(tz_taipei).strftime('%Y-%m-%d %H:%M:%S')

    # 5. 組合訊息內容
    msg = f"📈 **股市定時播報**\n" \
          f"🕒 時間: {current_time}\n" \
          f"🎯 股票: `{target_stock}`\n" \
          f"💰 價格: **{price}**"
    
    print("準備發送訊息：\n", msg)

    # 6. 發送到 Telegram
    send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, msg)
