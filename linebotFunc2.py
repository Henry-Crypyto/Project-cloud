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
    username=[]
    userstat=[]
    for keysss in users:
            username.append(users.get(keysss).get('name'))
    for keysss in users:
            userstat.append(users.get(keysss).get('type'))        
    UserId = event.source.user_id
    profile = line_bot_api.get_profile(UserId)
    print(profile)
    