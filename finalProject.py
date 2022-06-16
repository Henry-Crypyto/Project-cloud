from pyzbar.pyzbar import decode  # python zbarcode
from PIL import Image  # Python Imaging Library 
import cv2
import pyimgur
import pandas as pd
import matplotlib.pyplot as plt
from linebot.models import MessageEvent, TextMessage, PostbackEvent, TextSendMessage, ImagemapSendMessage, BaseSize, MessageImagemapAction, URIImagemapAction, ImagemapArea, TemplateSendMessage, ButtonsTemplate, DatetimePickerTemplateAction
from linebot.exceptions import InvalidSignatureError
from linebot import LineBotApi, WebhookHandler
from flask import request, abort
from firebase import firebase
from flask import Flask
import speech_recognition as sr
from serpapi import GoogleSearch
from pydub import AudioSegment
import random
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os
import string
plt.switch_backend('agg')
app = Flask(__name__)
line_bot_api = LineBotApi(
    'MWdhAwjkGg9rWLi5d7w+LBv+pQ9o6fDgETMLjexvTRDUr9Aju+j7ibidk8BnXu9VcATEz7oXuhIdHDrQNwGpBp+FesASbbcRgdzIKF2QeiJgQKQ3o/s3zMX6vZlkmE+xtzYbbHai5g9BrXN0+3e2FwdB04t89/1O/w1cDnyilFU='
    )
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
        elif keywords[1] == '圓餅圖'  :
            totalPiechart(event)#@圓餅圖
        elif keywords[1] == 'help'  :
            commandHelp(event)
            

def commandHelp(event):
    try:
        rplyText='你好，這是您的私人小助手\n本機器人可以做三項功能\n1.幫您計帳\n2.幫您搜尋圖片\n3.幫您把語音訊息轉成文字\n相關指令格式如下:\n記帳相關:\n@新增種類\n@(分類)@(內容)@(價錢)\n@(分類))\n@圓餅圖\n搜尋圖片相關:\n@(照片).jpg\n'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=rplyText))
    except:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='發生錯誤！'))
        
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
            
        audioText = r.recognize_google(audio, language='zh-Hant')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=audioText))
    except:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='發生錯誤！'))


def qrcodeDecode(event):#{使用者傳圖片}
    try:
        image_name = ''.join(
            random.choice(string.ascii_letters + string.digits) for x in range(4)
            )
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
            blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 3
        )
        cnts = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            ROI = image[y:y+h, x:x+w]
            break
        
        x = 70
        y = 500
        w = 300
        h = 500
        cv2.imwrite('ROI.png', ROI)
        img = cv2.imread('ROI.png')
        crop_img = img[y:y+h, x:x+w]
        cv2.imwrite('QR.png', crop_img)
        decodeData = decode(Image.open('QR.png'))  # QR code decoder
        strData = str(decodeData[0])
        dataNum = strData.split(',')
        dataText = str(dataNum)
        reciptNum = dataText[17:27]
        if dataText[24:27] == '578':
            message = '恭喜中獎500元!!!\n'+reciptNum
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=message)
                )
        elif dataText[24:27] != '578':
            message1 = '沒中獎，下次再來~\n'+reciptNum
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=message1)
                )

    except:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='發生錯誤！'))


def googleSearch(event):#{搜尋資訊}.jpg

    try:
        get_message = event.message.text.rstrip()
        tempText=get_message.split('@')
        searchMessage=tempText[1]
        URL_list = []
        params = {
            "engine": "google",
            "tbm": "isch",
            "api_key": "24410c7313e732c1f2363dc9939a220d0f4d0d6dab53d0372ca2272b9f2802b9",
        }
        params['q'] = searchMessage
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
            
        rplyMessage = 'Add Complete!!'
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=rplyMessage)
        )
        #line_bot_api.reply_message(event.reply_token, [TextSendMessage(text= reply_text), TextSendMessage(text= reply_text1)])

    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))

def totalCaculate(event):#@交通
    mtext = event.message.text
    keywords = mtext.split('@')
    path = '/Category/'+keywords[1]
    try:
        expName=[]
        expPrice=[]
        expKey = fb.get(path, None)
        for keysss in expKey:
            expName.append(expKey.get(keysss).get('name')+str(expKey.get(keysss).get('price')))
        for keysss in expKey:
            expPrice.append(expKey.get(keysss).get('price'))
            
        list=","'\n'.join(expName)
        expSum = sum(expPrice)
        sumText='\n--------------------------\n你總共花費了:'+str(expSum)+'元'
        rplyText=list+sumText
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=rplyText))    
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
        
        
def totalPiechart(event):#@圓餅圖
    pathTraffic = '/Category/交通'
    pathFood = '/Category/美食'
    pathEntertain = '/Category/休閒'
    pathOther = '/Category/其他'
    try:
        nameTraffic=[]
        nameFood=[]
        nameEntertain=[]
        nameOthers=[]
        priceTraffic=[]
        priceFood=[]
        priceEntertain=[]
        priceOther=[]
        keyTraffic = fb.get(pathTraffic, None)
        for keysss in keyTraffic:
            nameTraffic.append(keyTraffic.get(keysss).get('name')+str(keyTraffic.get(keysss).get('price')))
        for keysss in keyTraffic:
            priceTraffic.append(keyTraffic.get(keysss).get('price'))
        sumTraffic = sum(priceTraffic)
        
        keyFood = fb.get(pathFood, None)
        for keysss in keyFood:
            nameFood.append(keyFood.get(keysss).get('name')+str(keyFood.get(keysss).get('price')))
        for keysss in keyFood:
            priceFood.append(keyFood.get(keysss).get('price'))
        sumFood = sum(priceFood)
        
        keyEntertain = fb.get(pathEntertain, None)
        for keysss in keyEntertain:
            nameEntertain.append(keyEntertain.get(keysss).get('name')+str(keyEntertain.get(keysss).get('price')))
        for keysss in keyEntertain:
            priceEntertain.append(keyEntertain.get(keysss).get('price'))
        sumEntertain = sum(priceEntertain)
        
        keyOther = fb.get(pathOther, None)
        for keysss in keyOther:
            nameOthers.append(keyOther.get(keysss).get('name')+str(keyOther.get(keysss).get('price')))
        for keysss in keyOther:
            priceOther.append(keyOther.get(keysss).get('price'))
        sumOther = sum(priceOther)
        
        
        spend1=int(sumTraffic)
        spend2=int(sumFood)
        spend3=int(sumEntertain)
        spend4=int(sumOther)
        price1=str(sumTraffic)
        price2=str(sumFood)
        price3=str(sumEntertain)
        price4=str(sumOther)
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
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='發生錯誤！QQQQ'))
                
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