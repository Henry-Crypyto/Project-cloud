from collections import UserList
from email import message
from flask import Flask
import random 
import string
app = Flask(__name__)
from firebase import firebase
from flask import request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, PostbackEvent, TextSendMessage, ImagemapSendMessage, BaseSize, MessageImagemapAction, URIImagemapAction, ImagemapArea, TemplateSendMessage, ButtonsTemplate, DatetimePickerTemplateAction
from urllib.parse import parse_qsl
import datetime
import cv2
import sys  # opencv
from PIL import Image # Python Imaging Library
from pyzbar.pyzbar import decode # python zbarcode
line_bot_api = LineBotApi('MWdhAwjkGg9rWLi5d7w+LBv+pQ9o6fDgETMLjexvTRDUr9Aju+j7ibidk8BnXu9VcATEz7oXuhIdHDrQNwGpBp+FesASbbcRgdzIKF2QeiJgQKQ3o/s3zMX6vZlkmE+xtzYbbHai5g9BrXN0+3e2FwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('d03f66f4f4f5e6229b108acb97396a34')
url = 'https://henrydb1-69d3b-default-rtdb.asia-southeast1.firebasedatabase.app/'
fb = firebase.FirebaseApplication(url, None)
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent)
def handle_message(event):
   if event.message.type=='image':
        image_name = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(4))
        image_content = line_bot_api.get_message_content(event.message.id)
        image_name = image_name.upper()+'.jpg'
        path='./static/'+image_name
        with open(path, 'wb') as fd:
            for chunk in image_content.iter_content():
                fd.write(chunk)
        qrcodeDecode(event,path)
        
        
def qrcodeDecode(event,imgpath):
    try:
      image = cv2.imread(imgpath)
      gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
      blur = cv2.GaussianBlur(gray, (7,7), 0)
      thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,3)

      cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      cnts = cnts[0] if len(cnts) == 2 else cnts[1]
      cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
      for c in cnts:
          x,y,w,h = cv2.boundingRect(c)
          ROI = image[y:y+h, x:x+w]
          break

      cv2.imwrite('ROI.png', ROI)
      x = 70
      y = 500
# 裁切區域的長度與寬度
      w = 300
      h = 500

# 裁切圖片
    
      img = cv2.imread('ROI.png')
      crop_img = img[y:y+h, x:x+w]
      cv2.imwrite('QR.png', crop_img)
      data = decode(Image.open('QR.png'))  # QR code decoder
      str_data=str(data[0])
      data1=str_data.split(',')
      data2=str(data1)
      text1=data2[17:27]
      line_bot_api.reply_message(event.reply_token,TextSendMessage(text=text1))      
    
    except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))    
        
    


@handler.add(PostbackEvent)  #PostbackTemplateAction觸發此事件
def handle_postback(event):
    backdata = dict(parse_qsl(event.postback.data))  #取得data資料
    if backdata.get('action') == 'sell':
        sendData_sell(event, backdata)


def addCategory(event):
    try:
        mtext = event.message.text
        userText=mtext.split('@')
        fb.put('/Category',userText[2],'0')
        message='新增成功!!!'
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=message))
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))
#@紀錄@{分類}@{事件名稱}

def sendDatetime(event):  #日期時間
    try:
        
        mtext = event.message.text
        a=mtext
        userText=mtext.split('@')
        newEvent = [{'task': userText[3],'time':0}]
        tgPath='/Category/'+userText[2]
        for x in newEvent:
            fb.post(tgPath,x)  
        message = TemplateSendMessage(
            alt_text='日期時間範例',
            template=ButtonsTemplate(
                thumbnail_image_url='https://i.imgur.com/VxVB46z.jpg',
                title='日期時間示範',
                text='請選擇：',
                actions=[
                    DatetimePickerTemplateAction(
                        label="選取日期",
                        data="action=sell&mode=date",  #觸發postback事件
                        mode="date",  #選取日期
                        initial="2020-10-01",  #顯示初始日期
                        min="2020-10-01",  #最小日期
                        max="2021-12-31"  #最大日期
                    ),
                    DatetimePickerTemplateAction(
                        label="選取時間",
                        data="action=sell&mode=time",
                        mode="time",  #選取時間
                        initial="10:00",
                        min="00:00",
                        max="23:59"
                    ),
                    DatetimePickerTemplateAction(
                        label="選取日期時間",
                        data="action=sell&mode=datetime",
                        mode="datetime",  #選取日期時間
                        initial="2022-06-01T00:00",
                        min="2022-06-01T00:00",
                        max="2023-12-31T23:59"
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

def sendData_sell(event, backdata):  #Postback,顯示日期時間
    try:
        if backdata.get('mode') == 'date':
            dt = '日期為：' + event.postback.params.get('date')  #讀取日期
        elif backdata.get('mode') == 'time':
            dt = '時間為：' + event.postback.params.get('time')  #讀取時間
        elif backdata.get('mode') == 'datetime':
            dt = datetime.datetime.strptime(event.postback.params.get('datetime'), '%Y-%m-%dT%H:%M')  #讀取日期時間
            dt = dt.strftime('{d}%Y-%m-%d, {t}%H:%M').format(d='日期為：', t='時間為：')  #轉為字串
        message = TextSendMessage(
            text=dt
        )
    
        """
        mtext = event.message.text
        userText=mtext.split('-')
        print(userText)
        tgPath1='/Category/'+userText[2]
        taskKey = fb.get(tgPath1, None)
        for key in taskKey:
                 if taskKey[key]['task']==userText[3]:
                     myKey = str(key)
                     finalString=tgPath1+myKey
                     fb.put(finalString,"time",dt) 
        """
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！postback'))

def sendImgmap(event):  #圖片地圖
    try:
        image_url = 'https://i.imgur.com/Yz2yzve.jpg'  #圖片位址
        imgwidth = 1040  #原始圖片寛度一定要1040
        imgheight = 300
        message = ImagemapSendMessage(
            base_url=image_url,
            alt_text="圖片地圖範例",
            base_size=BaseSize(height=imgheight, width=imgwidth),  #圖片寬及高
            actions=[
                MessageImagemapAction(  #顯示文字訊息
                    text='你點選了紅色區塊！',
                    area=ImagemapArea(  #設定圖片範圍:左方1/4區域
                        x=0, 
                        y=0, 
                        width=imgwidth*0.25, 
                        height=imgheight  
                    )
                ),
                URIImagemapAction(  #開啟網頁
                    link_uri='http://www.e-happy.com.tw',
                    area=ImagemapArea(  #右方1/4區域(藍色1)
                        x=imgwidth*0.75, 
                        y=0, 
                        width=imgwidth*0.25, 
                        height=imgheight  
                    )
                ),
            ]
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

if __name__ == '__main__':
    app.run()
