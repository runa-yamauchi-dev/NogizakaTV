# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 07:01:03 2026

@author: runa6
"""

import time
import datetime
import requests
import os
import paho.mqtt.client as mqtt


#HiveMQ Cloud
MQTT_HOST = "b9d63efc2f204cd88bb34208b8185d69.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USERNAME = "nogizaka46TV"
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

MQTT_TOPIC = "nogizaka/tv/channel"

#MQTTクライアント
client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

client.username_pw_set(
    MQTT_USERNAME,
    MQTT_PASSWORD
)

#TLS
client.tls_set()

#MQTT接続
def connect_mqtt():
    print("HiveMQ Cloudへ接続中...")

    client.connect(
        MQTT_HOST,
        MQTT_PORT
    )

    client.loop_start()

    print("MQTT Connected!")

#次の番組の保存場所
next_shows = {
    "koujichu":None,
    "star":None
    }

def update_next_shows():
    next_shows["koujichu"] = None
    next_shows["star"] = None

    shows = get_nogizaka_tv()#番組情報取得shows     
    reserved = load_reserved()#予約番組取得
    now = datetime.datetime.now()#今の時間
            
    for show in shows:#shows配列の中を1つずつ
        
        title = show["title"]
        
        #乃木坂工事中の場合"koujichu"がなければ予約しなくていいので飛ばすforから抜ける次のshowに
        if "乃木坂工事中" in title and "koujichu" not in reserved:
            continue
        #乃木坂スター誕生！SIXの場合"star"がなければ予約しなくていいので飛ばすforから抜ける次のshowに
        if "乃木坂スター誕生！SIX" in title and "star" not in reserved:
            continue
            
        date = show["date"]#日付
        time_str = show["start_time"]#開始時間
        
        hour, minute = map(int, time_str.split(":"))
        
        if hour >= 24:
            hour -= 24
            date = date + datetime.timedelta(days=1)
        
        start = datetime.datetime(
            date.year,
            date.month,
            date.day,
            hour,
            minute
        )

        if start <= now:
            continue

        if "乃木坂工事中" in title:
            if next_shows["koujichu"] is None or start < next_shows["koujichu"]["start"]:
                next_shows["koujichu"] = {
                    "title":title,
                    "start":start
                }
        
        if "乃木坂スター誕生！SIX" in title:
            if next_shows["star"] is None or start < next_shows["star"]["start"]:
                next_shows["star"] = {
                    "title":title,
                    "start":start
                    }
    return shows

from nogizaka_schedulescraper import get_nogizaka_tv#get_nogizaka_tv()を使えるようにしている

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

#通知機能(Discord)
def send_discord(message):
    
    data = {
        "content":message
        }
    
    requests.post(DISCORD_WEBHOOK, json=data)#Discordサーバーにメッセージ送信

#チャンネル変更
def send_channel(title):
    if "乃木坂工事中" in title:
        ch = 7
    
    elif "乃木坂スター誕生！SIX" in title:
        ch = 4

    else:
        return

    result = client.publish(
            MQTT_TOPIC,
            str(ch),
            qos=1
        )
    result.wait_for_publish()
    print("MQTT送信:", ch)

#予約読み込み
def load_reserved():
    
    reserved = []
    
    try:
        with open("reserved.txt", "r", encoding="utf-8") as f:#reserved.txt(r)を読み込むモードで開く
            for line in f:
                reserved.append(line.strip())#配列に入れるstrip()は改行をけす
    
    except:
        pass

    return reserved          
 
#番組スケジュール監視用関数   
def check_show():

    connect_mqtt()

    while True:
        
        shows = update_next_shows()#番組情報取得shows
        
        reserved = load_reserved()#予約番組取得
        
        now = datetime.datetime.now()#今の時間
               
        for show in shows:#shows配列の中を1つずつ
            
            title = show["title"]
            
            #乃木坂工事中の場合"koujichu"がなければ予約しなくていいので飛ばすforから抜ける次のshowに
            if "乃木坂工事中" in title and "koujichu" not in reserved:
                next_shows["koujichu"] = None
                continue
            #乃木坂スター誕生！SIXの場合"star"がなければ予約しなくていいので飛ばすforから抜ける次のshowに
            if "乃木坂スター誕生！SIX" in title and "star" not in reserved:
                next_shows["star"] = None
                continue
                
            date = show["date"]#日付
            time_str = show["start_time"]#開始時間
            
            hour, minute = map(int, time_str.split(":"))
            
            if hour >= 24:
                hour -= 24
                date = date + datetime.timedelta(days=1)
            
            start = datetime.datetime(
                date.year,
                date.month,
                date.day,
                hour,
                minute
                )
            
            notify_time = start - datetime.timedelta(minutes=5)
            
            print(notify_time)
            
            if notify_time >= now:
                if "乃木坂工事中" in title:
                    if next_shows["koujichu"] is None or start < next_shows["koujichu"]["start"]:
                        next_shows["koujichu"] = {
                            "title":title,
                            "start":start
                            }
                
                if "乃木坂スター誕生！SIX" in title:
                    if next_shows["star"] is None or start < next_shows["star"]["start"]:
                        next_shows["star"] = {
                            "title":title,
                            "start":start
                            }
                    
            if notify_time <= now <= start:#開始5分前での動作
                
                print("番組5分前:", show["title"])
                send_discord(f"もうすぐ{title}が始まります!")
                
                send_channel(show["title"])#番組にチャンネルを変える
                
                time.sleep(300)#5分何回も番組を変えないようにするため
                
        time.sleep(30)#30秒ごとにチェック
