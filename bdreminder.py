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

from person import Person  # from檔名 import類名 
from bubble_generator import BubbleGenerator  
from user_states import UserState

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
    mongo_client.admin.command('ping')
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
bubble_generator = BubbleGenerator('temp_data/BDbubble.json', 'temp_data/starbubble.json')
user_states = {}
zodiac_signs = ["水瓶", "雙魚", "牡羊", "金牛", "雙子", "巨蟹", "獅子", "處女", "天秤", "天蠍", "射手", "魔羯"]

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    # 收到指令時,先抓出送指令的人的id,然後去看她之間有沒有送過其他指令
    # 如果沒送過指令,就先把id保存起來,連同指令一起保存
    user_id = event.source.user_id
    # 根據user_id,找出對應的 current_function, current_status, people_list, current_name, current_person
    # 如果找不到對應的資料,那就為新的user_id新增一筆資料
    if user_id not in user_states:
        user_states[user_id] = UserState(user_id) #實例化
    
    user = user_states[user_id] #user=user_states這個字典裡key為user_id的value

    text = event.message.text
    current_status = user.current_status
    current_function = user.current_function
    current_name = user.current_name
    current_person = user.current_person
    people_list = user.people_list


    print(f"current_function:{user.current_function}, current_status:{user.current_status}, text: {text}")
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
            user.current_function=''
            user.current_status=''
        else:
            msg=TextMessage(text=f"壽星名字叫做  {name}  ,\n接著請輸入壽星生日,例如:1990/01/01(出生年可省略) ")
            user.current_person=Person(name)
            user.current_name = name
            user.current_status = 'create birthday'
    elif current_function == "A" and current_status == 'create birthday':   
        birthday = text
        result={}
        result = user.current_person.setBirthday(birthday)
        print(f'result: {result}')
        if result['success_msg'] != None:
            r = result['success_msg'] 
            user.current_status=''
            people_list[current_name]=user.current_person.birthday
            with open("temp_data/birthday_data.json", "w", encoding='utf-8') as f:
                json.dump(people_list,f, indent=4,ensure_ascii=False)

        else:
            r = result['error_msg']
            print(people_list)


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
            user.current_status =''
            user.current_function=''
        else:
            r = f"找不到姓名為 {name} 的壽星,請重新輸入【B】刪除正確的壽星名字"
            user.current_function=''
            user.current_status=''

        msg=TextMessage(text=r)
        
   
    elif current_function == "D" and current_status == 'select month':
        if text.isdigit():  # 檢查輸入是否為數字
            month = int(text)
            if 1 <= month <= 12:
                with open('temp_data/birthday_data.json', encoding='utf-8') as f:
                    birthday_data = json.load(f)
                bubble_data = bubble_generator.generate_month_bubble(month, birthday_data)
                msg = FlexMessage(contents=FlexContainer.from_dict(bubble_data), altText='bdbubble')
            
            else:
                msg = TextMessage(text="沒有正確輸入數字1到12,請重新輸入【D】查詢")
        else:
            msg = TextMessage(text="沒有正確輸入數字1到12,請重新輸入【D】查詢")
        
        user.current_function=''
        user.current_status=''

    
    elif current_function == "E" and current_status == 'select star':
        star = text

        if star not in zodiac_signs:
            msg = TextMessage(text="無效的星座，請重新輸入【E】來查找")
            user.current_function = ''
            user.current_status = ''
        else:
            with open('temp_data/birthday_data.json', encoding='utf-8') as f:
                birthday_data = json.load(f)
            star_bubble = bubble_generator.generate_star_bubble(star, birthday_data)
            msg = FlexMessage(contents=FlexContainer.from_dict(star_bubble), altText='starbubble')
            user.current_function = ''
            user.current_status = ''

    elif current_function == "F" and current_status == 'select people':
        people = text
        found = False  # 添加一个变量来标记是否找到匹配的人名
        for name, birthday in people_list.items():
            if name == people:
                msg = TextMessage(text=f"{name}的生日是：{birthday['month']}/{birthday['day']}")
                found = True  # 找到匹配的人名
                break  # 找到后退出循环

        if not found:  # 如果没有找到匹配的人名
            msg = TextMessage(text="找不到該壽星,請重新輸入【F】查詢")

        user.current_function = ''
        user.current_status = ''

    elif text == "A":
        msg = TextMessage(text="請輸入壽星的姓名")
        user.current_function = 'A'
        user.current_status = 'create name'

    elif text == "B":
        msg = TextMessage(text="請輸入欲刪除的壽星姓名")
        user.current_function = "B"
        user.current_status = 'delete name'

    elif text == "C":
        msg = TextMessage(text="還在施工中喔!去其他地方玩")
        user.current_function = ''
        user.current_status = ''

    elif text == "D":
        msg = TextMessage(text="請輸入要查詢的月份,例如12")
        user.current_function = "D"
        user.current_status = 'select month'

    elif text == "E":
        items = [QuickReplyItem(action=MessageAction(label=sign, text=sign)) for sign in zodiac_signs]
        quick_reply = QuickReply(items=items)
        msg = TextMessage(text="請選擇星座：", quick_reply=quick_reply)
        user.current_function = 'E'
        user.current_status = 'select star'

    elif text == "F" :
        msg=TextMessage(text="請輸入要查詢的壽星姓名")
        user.current_function="F"
        user.current_status='select people'

        
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


@handler.add(FollowEvent)
def handle_message(event): 
    userid=event.source.user_id
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        profile=line_bot_api.get_profile(userid) 

        #user_states[userid] = UserState(userid)
        #user_states[userid].setUserProfile(profile)

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