from cv2 import findEssentialMat
from pyzbar.pyzbar import decode  # python zbarcode
from PIL import Image  # Python Imaging Library 
import cv2
import pyimgur
import pandas as pd
import matplotlib.pyplot as plt
from urllib.parse import parse_qsl
from linebot.models import MessageEvent, TextMessage, PostbackEvent, TextSendMessage, ImagemapSendMessage, BaseSize, MessageImagemapAction, URIImagemapAction, ImagemapArea, TemplateSendMessage, ButtonsTemplate, DatetimePickerTemplateAction
from linebot.exceptions import InvalidSignatureError
from linebot import LineBotApi, WebhookHandler
from flask import request, abort
from firebase import firebase
from collections import UserList
from email import message
from flask import Flask
import speech_recognition as sr
from serpapi import GoogleSearch
from pydub import AudioSegment
import random
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import re
import os
import string
app = Flask(__name__)
line_bot_api = LineBotApi(
    'MWdhAwjkGg9rWLi5d7w+LBv+pQ9o6fDgETMLjexvTRDUr9Aju+j7ibidk8BnXu9VcATEz7oXuhIdHDrQNwGpBp+FesASbbcRgdzIKF2QeiJgQKQ3o/s3zMX6vZlkmE+xtzYbbHai5g9BrXN0+3e2FwdB04t89/1O/w1cDnyilFU=')
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
    if event.message.type == 'image':
        qrcodeDecode(event)#{使用者傳圖片}
    elif event.message.type == 'audio':
        audioTotext(event)#{使用者傳音訊}
    elif event.message.type == 'text':
        rplyText = event.message.text
        keywords = rplyText.split('@')
        if rplyText[-4:] == '.jpg':#{搜尋資訊}.jpg
            googleSearch(event)
        elif keywords[1] == '新增種類':
            addCategory(event)#@新增種類
        elif rplyText[0] == '@' and len(rplyText)>5:
            addExpenses(event)#@交通@火車@140
        elif rplyText[0] == '@' and len(rplyText)==3:
            totalCaculate(event)#@交通
        elif keywords[1] == '圓餅圖' and len(rplyText)==4 :
            totalPiechart(event)#@圓餅圖
            


def audioTotext(event):#{使用者傳音訊}
    try:
        audio_content = line_bot_api.get_message_content(event.message.id)
        path = './static/sound.m4a'
        with open(path, 'wb') as fd:
            for chunk in audio_content.iter_content():
                fd.write(chunk)
        r = sr.Recognizer()
        AudioSegment.converter = 'C:\\Users\\hjins\\anaconda3\\envs\\line_env\\Lib\\site-packages\\ffmpeg\\bin\\ffmpeg.exe'
        sound = AudioSegment.from_file_using_temporary_files(path)
        path = os.path.splitext(path)[0]+'.wav'
        sound.export(path, format="wav")
        with sr.AudioFile(path) as source:
            audio = r.record(source)
        text12 = r.recognize_google(audio, language='zh-Hant')
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=text12))
    except:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='發生錯誤！'))


def qrcodeDecode(event):#{使用者傳圖片}
    try:
        image_name = ''.join(random.choice(
            string.ascii_letters + string.digits) for x in range(4))
        image_content = line_bot_api.get_message_content(event.message.id)
        image_name = image_name.upper()+'.jpg'
        path = './static/'+image_name
        with open(path, 'wb') as fd:
            for chunk in image_content.iter_content():
                fd.write(chunk)
        image = cv2.imread(path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        thresh = cv2.adaptiveThreshold(
            blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 3)

        cnts = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            ROI = image[y:y+h, x:x+w]
            break

        cv2.imwrite('ROI.png', ROI)
        x = 70
        y = 500
        w = 300
        h = 500
        img = cv2.imread('ROI.png')
        crop_img = img[y:y+h, x:x+w]
        cv2.imwrite('QR.png', crop_img)
        data = decode(Image.open('QR.png'))  # QR code decoder
        str_data = str(data[0])
        data1 = str_data.split(',')
        data2 = str(data1)
        text1 = data2[17:27]
        if data2[24:27] == '578':
            message = '恭喜中獎500元!!!\n'+text1
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=message))
        elif data2[24:27] != '578':
            message1 = '沒中獎，下次再來~\n'+text1
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=message1))

    except:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='發生錯誤！'))


def googleSearch(event):#{搜尋資訊}.jpg

    try:
        get_message = event.message.text.rstrip()
        URL_list = []
        params = {
            "engine": "google",
            "tbm": "isch",
            "api_key": "24410c7313e732c1f2363dc9939a220d0f4d0d6dab53d0372ca2272b9f2802b9",
        }
        params['q'] = get_message
        client = GoogleSearch(params)
        data = client.get_dict()
        imgs = data['images_results']
        x = 0
        for img in imgs:
            if x < 7:
                URL_list.append(img['original'])
                x += 1
        url = random.choice(URL_list)
        message = ImageSendMessage(
            original_content_url=url, preview_image_url=url
        )
        print(message)
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))



def addExpenses(event):# @交通@火車@140
    mtext = event.message.text
    keywords = mtext.split('@')
    try:
        price = int(keywords[3])
        new_users = [{'name': keywords[2], 'price':price}]
        path = '/Category/'+keywords[1]
        for data in new_users:
            fb.post(path, data)
        message1 = 'Add Complete!!'
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=message1))
        #line_bot_api.reply_message(event.reply_token, [TextSendMessage(text= reply_text), TextSendMessage(text= reply_text1)])

    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))

def totalCaculate(event):#@交通
    mtext = event.message.text
    keywords = mtext.split('@')
    path = '/Category/'+keywords[1]
    try:
        expensesName=[]
        expensesPrice=[]
        expensesKey = fb.get(path, None)
        for keysss in expensesKey:
            expensesName.append(expensesKey.get(keysss).get('name')+str(expensesKey.get(keysss).get('price')))
        for keysss in expensesKey:
            expensesPrice.append(expensesKey.get(keysss).get('price'))
        list=","'\n'.join(expensesName)
        expensesSum = sum(expensesPrice)
        sumText='\n--------------------------\n你總共花費了:'+str(expensesSum)+'元'
        finalText=list+sumText
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=finalText))    
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
        
        
def totalPiechart(event):#@圓餅圖
    mtext = event.message.text
    keywords = mtext.split('@')
    path1 = '/Category/交通'
    path2 = '/Category/美食'
    path3 = '/Category/休閒'
    path4 = '/Category/其他'
    try:
        expensesName1=[]
        expensesName2=[]
        expensesName3=[]
        expensesName4=[]
        expensesPrice1=[]
        expensesPrice2=[]
        expensesPrice3=[]
        expensesPrice4=[]
        expensesKey1 = fb.get(path1, None)
        for keysss in expensesKey1:
            expensesName1.append(expensesKey1.get(keysss).get('name')+str(expensesKey1.get(keysss).get('price')))
        for keysss in expensesKey1:
            expensesPrice1.append(expensesKey1.get(keysss).get('price'))
        expensesSum1 = sum(expensesPrice1)
        
        expensesKey2 = fb.get(path2, None)
        for keysss in expensesKey2:
            expensesName2.append(expensesKey2.get(keysss).get('name')+str(expensesKey2.get(keysss).get('price')))
        for keysss in expensesKey2:
            expensesPrice2.append(expensesKey2.get(keysss).get('price'))
        expensesSum2 = sum(expensesPrice2)
        
        expensesKey3 = fb.get(path3, None)
        for keysss in expensesKey3:
            expensesName3.append(expensesKey3.get(keysss).get('name')+str(expensesKey3.get(keysss).get('price')))
        for keysss in expensesKey3:
            expensesPrice3.append(expensesKey3.get(keysss).get('price'))
        expensesSum3 = sum(expensesPrice3)
        
        expensesKey4 = fb.get(path4, None)
        for keysss in expensesKey4:
            expensesName4.append(expensesKey4.get(keysss).get('name')+str(expensesKey4.get(keysss).get('price')))
        for keysss in expensesKey4:
            expensesPrice4.append(expensesKey4.get(keysss).get('price'))
        expensesSum4 = sum(expensesPrice4)
        
        
        spend1=int(expensesSum1)
        spend2=int(expensesSum2)
        spend3=int(expensesSum3)
        spend4=int(expensesSum4)
        price1=str(expensesSum1)
        price2=str(expensesSum2)
        price3=str(expensesSum3)
        price4=str(expensesSum4)
        total=spend1+spend2+spend3+spend4
        totalText=str(total)
        df = pd.DataFrame([['traffic:'+price1, spend1], ['food:'+price2, spend2],['entertainment:'+price3, spend3],['others:'+price4, spend4],],columns=['Category', 'price'])
        plt.pie(df['price'], labels=df['Category'], autopct='%1.2f%%')
        plt.title('Expenses:'+totalText)
        plt.savefig('Piechart.jpg')
        
        CLIENT_ID = "64c8666d44b0d79"
        PATH = "Piechart.jpg" #A Filepath to an image on your computer"
        title = "Uploaded with PyImgur"

        im = pyimgur.Imgur(CLIENT_ID)
        uploaded_image = im.upload_image(PATH, title=title)
        url=uploaded_image.link
        message = ImageSendMessage(
            original_content_url=url, preview_image_url=url
        )
        line_bot_api.reply_message(event.reply_token, message)  
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！QQQQ'))
                
def addCategory(event):
    try:
        mtext = event.message.text
        userText = mtext.split('@')
        fb.put('/Category', userText[2], '0')
        message = '新增成功!!!'
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=message))
    except:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='發生錯誤！'))


if __name__ == '__main__':
    app.run()


"""
@handler.add(PostbackEvent)  #PostbackTemplateAction觸發此事件
def handle_postback(event):
    backdata = dict(parse_qsl(event.postback.data))  #取得data資料
    if backdata.get('action') == 'sell':
        sendData_sell(event, backdata)



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
        """
