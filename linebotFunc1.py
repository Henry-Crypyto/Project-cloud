from urllib.parse import uses_params
from flask import Flask
app = Flask(__name__)
from traceback import FrameSummary
from firebase import firebase
from flask import request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage,TextSendMessage, ImageSendMessage, StickerSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction
from firebase import firebase
dict

url = 'https://henrydb1-69d3b-default-rtdb.asia-southeast1.firebasedatabase.app/'

fb = firebase.FirebaseApplication(url, None)
line_bot_api = LineBotApi('MWdhAwjkGg9rWLi5d7w+LBv+pQ9o6fDgETMLjexvTRDUr9Aju+j7ibidk8BnXu9VcATEz7oXuhIdHDrQNwGpBp+FesASbbcRgdzIKF2QeiJgQKQ3o/s3zMX6vZlkmE+xtzYbbHai5g9BrXN0+3e2FwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('d03f66f4f4f5e6229b108acb97396a34')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    mtext = event.message.text
    keywords=mtext.split('@')
    users = fb.get('/user', None)
    admin = fb.get('/admin', None)
    username=[]
    userstat=[]
    adname=[]
    UserId = event.source.user_id
    profile = line_bot_api.get_profile(UserId)
    a=7
    for keysss in users:
            username.append(users.get(keysss).get('name'))
    for keysss in users:
            userstat.append(users.get(keysss).get('type'))  
 
    for keysss in admin:
        if admin[keysss]['name']==profile.display_name:
            print(profile.display_name)
            a=0
        elif a!=0:
            a=1
    print(a)        
    if keywords[1] == 'add' and a==0:
        try:
            new_users = [{'name': keywords[2],'type':2}]
            for data in new_users:			
                fb.post('/user', data)  
                
            message1='Add Complete!!'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=message1))
            print(a)
            #line_bot_api.reply_message(event.reply_token, [TextSendMessage(text= reply_text), TextSendMessage(text= reply_text1)])
            
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))
            
    if keywords[1] == 'rm' and a==0:
        try:
            for key in users:
                if users[key]['name']==keywords[2]:
                   fb.delete('/user',key)
                          
            message2='Delete Complete!!'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=message2))
            #line_bot_api.reply_message(event.reply_token, [TextSendMessage(text= reply_text), TextSendMessage(text= reply_text1)])
            
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))
    
    if keywords[1] == 'list' and a==0:
        try:
            alluser=","'\n'.join(username)
            message3=alluser
            print('我好帥')
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=message3))
            #line_bot_api.reply_message(event.reply_token, [TextSendMessage(text= reply_text), TextSendMessage(text= reply_text1)])
            
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))
            
    if keywords[1] == 'report' and a==0:
        try:
            unreply=[]
            for key in users:
                if users[key]['type']==2:
                    unreply.append(users[key]['name'])
                    
            unalluser=","'\n'.join(unreply)
            message4='這些人還沒有回覆喔:(\n'+unalluser        
                     
                          
            message2='Report Complete!!'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=message4))
            #line_bot_api.reply_message(event.reply_token, [TextSendMessage(text= reply_text), TextSendMessage(text= reply_text1)])
            
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))
    
    if keywords[1] == 'N':
        try:
            for key in users:
                 if users[key]['name']==keywords[2]:
                     mystring = str(key)
                     finalstring='/user/'+mystring
                     fb.put(finalstring,"type",0)
                    
                 
            message5='Reply Complete!!'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=message5))
            #line_bot_api.reply_message(event.reply_token, [TextSendMessage(text= reply_text), TextSendMessage(text= reply_text1)])
            
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))
    
    if keywords[1] == 'Y':
        try:
            for key in users:
                 if users[key]['name']==keywords[2]:
                     mystring = str(key)
                     finalstring='/user/'+mystring
                     fb.put(finalstring,"type",1)
                    
                 
            message6='Reply Complete!!'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=message6))
            #line_bot_api.reply_message(event.reply_token, [TextSendMessage(text= reply_text), TextSendMessage(text= reply_text1)])
            
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))
            
    if keywords[1] == 'addAdmin' and profile.display_name=='哭阿':
        try:
            new_users = [{'name': keywords[2],'type':2}]
            for data in new_users:			
                fb.post('/admin', data)  
                
            message9='Add Admin Complete!!'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=message9))
            
            #line_bot_api.reply_message(event.reply_token, [TextSendMessage(text= reply_text), TextSendMessage(text= reply_text1)])
            
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))
    """elif mtext == '@傳送圖片':
        try:
            message = ImageSendMessage(
                original_content_url = "https://i.imgur.com/4QfKuz1.png",
                preview_image_url = "https://i.imgur.com/4QfKuz1.png"
            )
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

    elif mtext == '@傳送貼圖':
        try:
            message = StickerSendMessage(  #貼圖兩個id需查表
                package_id='1',  
                sticker_id='2'
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

    elif mtext == '@多項傳送':
        try:
            message = [  #串列
                StickerSendMessage(  #傳送貼圖
                    package_id='1',  
                    sticker_id='2'
                ),
                TextSendMessage(  #傳送文字
                    text = "這是 Pizza 圖片！"
                ),
                ImageSendMessage(  #傳送圖片
                    original_content_url = "https://i.imgur.com/4QfKuz1.png",
                    preview_image_url = "https://i.imgur.com/4QfKuz1.png"
                )
            ]
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

    elif mtext == '@傳送位置':
        try:
            message = LocationSendMessage(
                title='101大樓',
                address='台北市信義路五段7號',
                latitude=25.034207,  #緯度
                longitude=121.564590  #經度
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

    if mtext == '@快速選單':
        try:
            message = TextSendMessage(
                text='請選擇最喜歡的程式語言',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="Python", text="Python")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="Java", text="Java")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="C#", text="C#")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="Basic", text="Basic")
                        ),
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))
"""
if __name__ == '__main__':
    app.run()
