from google.cloud import firestore
from time import strftime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from linebot import LineBotApi, WebhookParser
import json
import re
import requests
from datetime import datetime
from flask import Flask, request, abort
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage,
    ImageMessage,
    LocationMessage,
    FlexMessage,
    FlexContainer,
    QuickReply,
    QuickReplyItem,
    MessageAction,
    CameraAction,
    PostbackAction,
    URIAction,
    CameraRollAction,
    DatetimePickerAction
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    PostbackEvent,
    FollowEvent,
    UnfollowEvent

)
from linebot.models import (
    MessageEvent,
)

app = Flask(__name__)

with open('key/bdreminder.json') as f:
    env =json.load(f)
    
configuration = Configuration(access_token=env[ 'CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(env[ 'CHANNEL_SECRET' ])

#mongodb init 初始化mongodb
uri = "mongodb+srv://x94x94:lai261026@x94x94.fohhjet.mongodb.net/?retryWrites=true&w=majority&appName=x94x94"
# Create a new client and connect to the server
mongo_client = MongoClient(uri, server_api=ServerApi('1'))    
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e) 
db= mongo_client['bdreminder']
dbusers = db['users']

firestore_client= firestore.Client.from_service_account_json('key/classtest_cloud_key.json')
users = firestore_client.collection('x94x94')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

class Person:
    def __init__(self, name):
        self.name = name
        self.birthday = None

    def show(self):
        print(f"{self.name} {self.birthday}")
    
    def setBirthday(self, birthday_parts_text):
        birthday_parts = birthday_parts_text.split('/')
        year, month, day = 0, 0, 0

        # 判斷邏輯
        if len(birthday_parts) == 3:
            year, month, day = map(int, birthday_parts)
        elif len(birthday_parts) == 2:
            month, day = map(int, birthday_parts)
        else:
            return {'success_msg': None, 'error_msg': "輸入格式不正確，請重新輸入，例如: 1990/01/01"}
   
        # 1. 檢查年
        if year != 0 and (2024 < year or year < 1900):
            return {'success_msg': None, 'error_msg': "輸入格式不正確，請重新輸入，例如: 1990/01/01"}
        # 2. 檢查月
        if not (1 <= month <= 12):
            return {'success_msg': None, 'error_msg': "輸入格式不正確，請重新輸入，例如: 1990/01/01"}
        # 3. 檢查日
        if month in [1, 3, 5, 7, 8, 10, 12]:
            if not (1 <= day <= 31):
                return {'success_msg': None, 'error_msg': "輸入格式不正確，請重新輸入，例如: 1990/01/01"}
        elif month in [4, 6, 9, 11]:
            if not (1 <= day <= 30):
                return {'success_msg': None, 'error_msg': "輸入格式不正確，請重新輸入，例如: 1990/01/01"}
        elif month == 2:
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):  # 閏年
                if not (1 <= day <= 29):
                    return {'success_msg': None, 'error_msg': "輸入格式不正確，請重新輸入，例如: 1990/01/01"}
            else:
                if not (1 <= day <= 28):
                    return {'success_msg': None, 'error_msg': "輸入格式不正確，請重新輸入，例如: 1990/01/01"}


        if year != 0:
            self.birthday = {"year": str(year), "month": str(month), "day": str(day)}
        else:
            self.birthday = {"year": "0", "month": str(month), "day": str(day)}

        if year != 0:
            return {'success_msg': f"壽星名字叫做 {self.name}，生日是 {year:04d}/{month:02d}/{day:02d} 已記錄完成"}
        else:
            return {'success_msg': f"壽星名字叫做 {self.name}，生日是 {month:02d}/{day:02d} 已記錄完成"}

current_person=None
people_list = {}
current_function = ''
current_status = ''
current_name = ''
welcome_msg = """您好!
我是 Birthday Reminder
請手動輸入指令代碼
【A】建立生日
【B】刪除生日
【C】提醒生日
【D】每月壽星
【E】星座一覽
【F】查詢生日
"""

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    text = event.message.text
    global current_function
    global current_status
    global people_list
    global current_name
    global current_person
    global msg
    print(f"current_function:{current_function}, current_status:{current_status}, text: {text}")
    msg = ''
    r = ''
    # 檢查檔案是否存在，如果不存在就創建一個空的 JSON 檔案
    if not os.path.isfile("temp_data/birthday_data.json"):
        with open("temp_data/birthday_data.json", "w", encoding='utf-8') as f:
            json.dump({}, f,ensure_ascii=False)
    else:
        with open("temp_data/birthday_data.json","r+", encoding='utf-8') as f:  # 讀取
            people_list = json.load(f)        
              
    if text=="嗨":
        msg=TextMessage(text=welcome_msg)
    elif current_function == "A" and current_status == 'create name':
        name = text

        if name in people_list:
            msg=TextMessage(text="壽星名字已存在,請重新輸入【A】另外命名,或輸入【B】刪除先前重複的壽星資料後再新增")
            current_function = ''
            current_status = ''
        else:
            msg=TextMessage(text=f"壽星名字叫做  {name}  ,\n接著請輸入壽星生日,例如:1990/01/01(出生年可省略) ")
            current_person=Person(name)
            current_name = name
            current_status = 'create birthday'
    elif current_function == "A" and current_status == 'create birthday':   
        result={}
        result = current_person.setBirthday(text)
        print(f'result: {result}')
        if (result['success_msg'] != None):
            r = result['success_msg'] 
            current_status = ''
            people_list[current_name]=current_person.birthday
            with open("temp_data/birthday_data.json", "w", encoding='utf-8') as f:
                json.dump(people_list,f, indent=4,ensure_ascii=False)

        else:
            r = result['error_msg']
            print(people_list)
            if current_name in people_list:
                current_function = ''
                current_status = ''

        msg=TextMessage(text=r)

    elif current_function == "B" and current_status == 'delete name':
        name = text
        
        if name in people_list:
            del people_list[name]
            with open("temp_data/birthday_data.json", "r", encoding='utf-8') as f:
                birthday_data = json.load(f)
            if name in birthday_data:
                del birthday_data[name]
                with open("temp_data/birthday_data.json", "w", encoding='utf-8') as f:
                    json.dump(birthday_data, f,ensure_ascii=False)
            r = f"已刪除壽星 {name} 的生日"
            current_status = ''
            current_function = ''
        else:
            r = f"找不到姓名為 {name} 的壽星,請重新輸入【B】刪除正確的壽星名字"
            current_function = ''
            current_status = ''

        msg=TextMessage(text=r)
        
   
    elif current_function == "D" and current_status == 'select month':
        if text.isdigit():  # 檢查輸入是否為數字
            month = int(text)
            if 1 <= month <= 12:
                with open('temp_data/birthday_data.json', encoding='utf-8') as f:
                    birthday_data = json.load(f)
                bubble_data = generate_month_bubble(month, birthday_data)
                msg = FlexMessage(contents=FlexContainer.from_dict(bubble_data), altText='bdbubble')
            
            else:
                msg = TextMessage(text="沒有正確輸入數字1到12,請重新輸入【D】查詢")
        else:
            msg = TextMessage(text="沒有正確輸入數字1到12,請重新輸入【D】查詢")
        
        current_function = ''
        current_status = ''

    
    elif current_function == "E" and current_status == 'select star':
        star = text
        valid_star_signs = ["水瓶", "雙魚", "牡羊", "金牛", "雙子", "巨蟹", "獅子", "處女", "天秤", "天蠍", "射手", "魔羯"]

        if star not in valid_star_signs:
            msg=TextMessage(text="無效的星座，請重新輸入【E】來查找")
            current_function = ''
            current_status = ''
        else:
            with open('temp_data/birthday_data.json', encoding='utf-8') as f:
                birthday_data = json.load(f)
            star_bubble = generate_star_bubble(star, birthday_data)
            msg = FlexMessage(contents=FlexContainer.from_dict(star_bubble), altText='starbubble')
            current_function = ''
            current_status = ''
            
    
    elif current_function == "F" and current_status == 'select people':
        people = text  
        found = False  # 添加一个变量来标记是否找到匹配的人名
        for name, birthday in people_list.items():
            if name == people:
                msg=TextMessage(text=f"{name}的生日是：{birthday['month']}/{birthday['day']}")
                found = True  # 找到匹配的人名
                break  # 找到后退出循环
        
        if not found:  # 如果没有找到匹配的人名
            msg=TextMessage(text="找不到該壽星,請重新輸入【F】查詢")
            
        current_function = ''
        current_status = ''
        
    elif text=="A":
        msg=TextMessage(text="請輸入壽星的姓名")
        current_function = "A"
        current_status = 'create name'
            
    elif text == "B" :
        msg=TextMessage(text="請輸入欲刪除的壽星姓名")
        current_function = "B"
        current_status = 'delete name'

    elif text == "C" :
        msg=TextMessage(text="還在施工中喔!去其他地方玩")
        current_function = ""
        current_status = ''

    elif text == "D" :
        msg=TextMessage(text="請輸入要查詢的月份,例如12")
        current_function = "D"
        current_status = 'select month'

    elif text == "E" :
        items=[QuickReplyItem(action=MessageAction(label='水瓶',text='水瓶')),
               QuickReplyItem(action=MessageAction(label='雙魚',text='雙魚')),
               QuickReplyItem(action=MessageAction(label='牡羊',text='牡羊')),
               QuickReplyItem(action=MessageAction(label='金牛',text='金牛')),
               QuickReplyItem(action=MessageAction(label='雙子',text='雙子')),
               QuickReplyItem(action=MessageAction(label='巨蟹',text='巨蟹')),
               QuickReplyItem(action=MessageAction(label='獅子',text='獅子')),
               QuickReplyItem(action=MessageAction(label='處女',text='處女')),
               QuickReplyItem(action=MessageAction(label='天秤',text='天秤')),
               QuickReplyItem(action=MessageAction(label='天蠍',text='天蠍')),
               QuickReplyItem(action=MessageAction(label='射手',text='射手')),
               QuickReplyItem(action=MessageAction(label='魔羯',text='魔羯'))]
        quick_reply=QuickReply(items=items)
        msg=TextMessage(text="請選擇星座：", quick_reply=quick_reply)
        current_function = "E"
        current_status = 'select star'

    elif text == "F" :
        msg=TextMessage(text="請輸入要查詢的壽星姓名")
        current_function = "F"
        current_status = 'select people'

        
    else:
        msg=TextMessage(text="我不知道你在說什麼,請重新輸入指令")
        


    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[msg]
            )
        )

def generate_month_bubble(month, birthday_data):
    with open('temp_data/BDbubble.json', encoding='utf-8') as f:
        b = json.load(f)

    # 每个月的天数列表，注意2月天数为28，未考虑闰年
    days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    # 修改 Bubble 模板中的標題和日期範圍
    b['body']['contents'][0]['text'] = f"{month}月壽星"
    b['body']['contents'][1]['text'] = f"{month}/1-{month}/{days_in_month[month-1]}"
     # 清空原有的壽星列表
    b['body']['contents'][3]['contents'] = []

    # 筛选并排序指定月份的生日数据 
    #如果要在列表推导式中使用 if ，需要一个表达式来决定每个迭代项如何出现在结果列表中 
    #(name, info) 是每次迭代时添加到列表中的表达式  明确你想从迭代中获取什么，并需要在 for 关键字之前放置
    month_people = [(name, info) for name, info in birthday_data.items() if info['month'] == str(month)]
    
    if not month_people:
        # 如果当月没有寿星，则在Bubble中显示相应信息
        b['body']['contents'][3]['contents'].append({"type": "text", "text": f"這個月沒有人生日", "align": "center"})
    else:
        # 替换 Bubble 模板中的人名和生日
        sorted_month_people = sorted(month_people, key=lambda x: int(x[1]['day']))
        for name, info in sorted_month_people:
            name_text = {"type": "text", "text": name, "size": "lg", "color": "#555555", "flex": 0}
            birthday_text = {"type": "text", "text": f"{info['month']}/{info['day']}", "size": "lg", "color": "#111111", "align": "end"}
            b['body']['contents'][3]['contents'].append(
                {"type": "box", "layout": "horizontal", "contents": [name_text, birthday_text]}
            )

    return b


def generate_star_bubble(star, birthday_data):
    # 加载 starbubble.json 模板
    with open('temp_data/starbubble.json', encoding='utf-8') as f:
        star_bubble = json.load(f)    
    
    # 获取星座对应的日期范围
    star_date_range = get_star_date_range(star)
    
    # 修改 Bubble 模板中的标题和日期范围
    star_bubble['body']['contents'][0]['text'] = f"{star}座"
    star_bubble['body']['contents'][1]['text'] = star_date_range
    
    # 清空原有的生日列表
    star_bubble['body']['contents'][3]['contents'] = []
    
     # 在 birthday_data 中查找指定星座的生日数据
    people_list = {}
    for name, info in birthday_data.items():
        month = int(info['month'])
        day = int(info['day'])
        star_sign = get_star_sign(month, day)
        if star_sign == star:
            birthday = f"{info['month']}/{info['day']}"
            people_list[name] = birthday
    
    # 如果有生日数据，则将其添加到 Bubble 模板中
    if people_list:
        for name, birthday in people_list.items():
            name_text = {"type": "text", "text": name, "size": "lg", "color": "#555555", "flex": 0}
            birthday_text = {"type": "text", "text": birthday, "size": "lg", "color": "#111111", "align": "end"}
            star_bubble['body']['contents'][3]['contents'].append(
                {"type": "box", "layout": "horizontal", "contents": [name_text, birthday_text]}
            )
    else:
        # 如果没有生日数据，则显示提示信息
        star_bubble['body']['contents'][3]['contents'].append(
            {"type": "text", "text": f"此星座沒有人生日", "align": "center"}
        )
    
    return star_bubble

def get_star_sign(month, day): #根据日期返回星座名称
    if (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "水瓶"
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "雙魚"
    elif (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "牡羊"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "金牛"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 21):
        return "雙子"
    elif (month == 6 and day >= 22) or (month == 7 and day <= 22):
        return "巨蟹"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "獅子"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "處女"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "天秤"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "天蠍"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "射手"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "魔羯"
    else:
        return None

def get_star_date_range(star): #根據星座返回星座的日期范围
    star_date_ranges = {
        "水瓶": "1/20-2/18",
        "雙魚": "2/19-3/20",
        "牡羊": "3/21-4/19",
        "金牛": "4/20-5/20",
        "雙子": "5/21-6/21",
        "巨蟹": "6/22-7/22",
        "獅子": "7/23-8/22",
        "處女": "8/23-9/22",
        "天秤": "9/23-10/22",
        "天蠍": "10/23-11/21",
        "射手": "11/22-12/21",
        "魔羯": "12/22-1/19"
    }
    return star_date_ranges.get(star, "未知星座")


@handler.add(FollowEvent)
def handle_message(event): 
    userid=event.source.user_id
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        profile=line_bot_api.get_profile(userid) 

        #insert into mongodb
        u=dict(profile)
        u['_id']=userid
        u['follow']=strftime('%Y/%m/%d-%H:%M:%S')
        u['unfollow']= None
        
         #insert into mongo
        try:
            dbusers.insert_one(u) 
        except Exception as e:
           print(e)
            
        #insert into firestore
        if users.document(u['user_id']).get().exists: #如果用戶已存在
            users.document(u['user_id']).update(u) #就更新其全部資訊
        else:
            users.add(document_data=u, document_id=u['user_id']) #如果不存在就add
        
        print(f"New user: {profile.display_name}, ID: {userid}")
        welcome=f'Hello!{profile.display_name} ,你的 ID 是 {userid},歡迎使用 Birthday Reminder!'
        #print(profile.picture_url)
        line_bot_api.reply_message_with_http_info(                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=welcome)]
             ) 
         )
        

if __name__ == "__main__":
    app.run()