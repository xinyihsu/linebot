from flask import Flask, request

# 載入 json 標準函式庫，處理回傳的資料格式
import json

# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage # 載入 TextSendMessage 模組

import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True) # 取得收到的訊息內容
    try:
        json_data = json.loads(body) # json 格式化訊息內容
        access_token = 'NxqekyyN/zUuo4Hb58Oe1vYuKyjdwZHhZjCdYEK63xwUkiwyH870S9SojkV3jlfwZ9/5tGwxmcWWo4MOK5yq8HSukIoulR7bEjq9SwlQiyEBHFJhnUJYayerQyRn/36Cum5JMhQ2RYKsMi0g6Un1tAdB04t89/1O/w1cDnyilFU=' #LINE Channel secret
        secret = 'af04e583fbe221a7d24459f9f8903087' #LINE Channel access token
        line_bot_api = LineBotApi(access_token) # 確認 token 是否正確
        handler = WebhookHandler(secret) # 確認 secret 是否正確
        signature = request.headers['X-Line-Signature'] # 加入回傳的 headers
        handler.handle(body, signature) # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken'] # 取得回傳訊息的 Token
        type = json_data['events'][0]['message']['type'] # 取得 LINE 收到的訊息類型

        if type=='text':
            msg = json_data['events'][0]['message']['text'] # 取得 LINE 收到的文字訊息
            if (msg == '?'): reply = menu()
            elif (msg == '台積電'): reply = getStock('2330')
            elif (msg.isdigit()): reply = getStock(msg)
            elif (msg == '日圓' or msg == '日幣' or msg == '日元' or msg == '日'): reply = getMoney('JPY')
            else: reply = getMoney(msg.upper())
        else:
            reply = '你傳的不是文字呦～\n輸入股號查詢股價\n或輸入英文幣別查詢匯率'
        print(reply)

        line_bot_api.reply_message(tk, TextSendMessage(reply)) # 回傳訊息
    except:
        print(body) # 如果發生錯誤，印出收到的內容
    return 'OK'

def getStock(num):
    url = 'https://tw.stock.yahoo.com/quote/' + num # Yahoo 股市網址
    try:
        web = requests.get(url) # 取得網頁內容
        soup = BeautifulSoup(web.text, "html.parser") # 轉換內容
        title = soup.select('h1')[1] # 找到 h1 的內容
        price = soup.select(r'.Fz\(32px\)')[0] # 找到第一個 class 為 Fz(32px) 的內容
        change = soup.select(r'.Fz\(20px\)')[0] # 找到第一個 class 為 Fz(20px) 的內容
    except:
        return(f'找不到 {num}\n\n輸入股號查詢股價\n或輸入英文幣別查詢匯率')
    
    state = '' # 漲或跌的狀態
    try:
        # 如果 main-0-QuoteHeader-Proxy id 的 div 裡有 C($c-trend-down) 的 class
        # 表示狀態為下跌
        if soup.select('#main-0-QuoteHeader-Proxy')[0].select('.C($c-trend-down)')[0]:
            state = '-'
    except:
        try:
            # 如果 main-0-QuoteHeader-Proxy id 的 div 裡有 C($c-trend-up) 的 class
            # 表示狀態為上漲
            if soup.select('#main-0-QuoteHeader-Proxy')[0].select('.C($c-trend-up)')[0]:
                state = '+'
        except:
            # 如果都沒有包含，表示平盤
            state = '-'

    return(f'{title.get_text()} : {price.get_text()} ( {state}{change.get_text()} )') # 印出結果

def getMoney(type):
    url = 'https://www.esunbank.com/zh-tw/personal/deposit/rate/forex/foreign-exchange-rates'
    web = requests.get(url) # 取得網頁內容
    soup = BeautifulSoup(web.text, "html.parser") # 轉換內容

    try:
        price = soup.find(class_=type).select('.SellDecreaseRate')[0]
        return(f'{type} : {price.get_text()}')
    except:
        return(f'找不到 {type}\n\n輸入股號查詢股價\n或輸入英文幣別查詢匯率')

def menu():
    return('輸入股號查詢股價\n或輸入英文幣別查詢匯率')

if __name__ == "__main__":
    app.run()