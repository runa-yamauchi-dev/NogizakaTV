# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 04:47:09 2026

@author: runa6
"""

from flask import Flask, request#pythonでWebサーバーを作る,スマホからpythonのデータ取得
import auto_scheduler
from flask import render_template_string
import paho.mqtt.client as mqtt
import os

app = Flask(__name__)#Flaskアプリを作る

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

#トップページURL
@app.route("/")
def home():
    
    koujichu = auto_scheduler.next_shows["koujichu"]
    star = auto_scheduler.next_shows["star"]
    
    if koujichu:
        koujichu_title = koujichu["title"]
        koujichu_time = koujichu["start"]
    else:
        koujichu_title = None
        koujichu_time = None
    
    if star:
        star_title = star["title"]
        star_time = star["start"]
    else:
        star_title = None
        star_time = None
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    
    body{
        font-family: Arial;
        background:linear-gradient(135deg,#c8b6ff,#ffd6f6);
        text-align:center;
        }
    
    h1{
       color:#7a3db8;
       font-size:30px;
       }
    
    h2{
       font-size:20px;
       margin-top:0;
       }
    
    .section{
        margin:20px auto;
        padding:20px;
        width:90%;
        max-width:420px;
        background:rgba(255,255,255,0.25);
        backdrop-filter:blur(10px);
        border-radius:18px;
        border:1px solid rgba(255,255,255,0.3);
        box-shadow:0 8px 20px rgba(0,0,0,0.1);
        }
    
    button{
        font-size:15px;
        padding:15px;
        border:none;
        border-radius:15px;
        background:#9370db;
        color:white;
        box-shadow:0 5px 10px rgba(0,0,0,0.25);
        }
    
    button:active{
        transform:scale(0.95);
        }
    
    .remote{
        display:grid;
        grid-template-columns:repeat(3,90px);
        justify-content:center;
        gap:30px;
        margin-top:15px;
        }
    
    .power button{
        background:#ff6347;
        width:90px;
        }
    
    .reserve button{
        background:#ff77c8;
        width:110px;
        }
    
    label{
        font-size:15px;    
        }
    
    </style>
    </head>
    
    <body>
    
    <h1>Nogizaka TV Controller</h1>
    
    <div class="section power">
    <h2>電源</h2>
    <button onclick="setChannel(0)">⏻</button>
    </div>
    
    <div class="section">
    <h2>チャンネル</h2>
    
    <div class="remote">
    <button onclick="setChannel(1)">1ch</button>
    <button onclick="setChannel(2)">2ch</button>
    <button onclick="setChannel(4)">4ch</button>
    <button onclick="setChannel(5)">5ch</button>
    <button onclick="setChannel(6)">6ch</button>
    <button onclick="setChannel(7)">7ch</button>
    <button onclick="setChannel(8)">8ch</button>
    </div> 
    </div>
    
    <div class="section reserve">
    <h2>番組予約</h2>
    
    <label>
    <input type="checkbox" id="koujichu">
    乃木坂工事中
    </label>
    
    <br><br>
    
    <label>
    <input type="checkbox" id="star">
    乃木坂スター誕生！SIX
    </label>
    
    <br><br>
    
    <button onclick="reserveShow()">予約</button>
    
    </div>
    
    <div class="section nextshow">
    <h2>次の予約番組</h2>

    <div id="next-show-list">
    
    {% if koujichu_title %}
    <p>
    {{koujichu_title}}<br>
    {{koujichu_time}}
    </p>
    {% endif %}
    
    {% if star_title %}
    <p>
    {{star_title}}<br>
    {{star_time}}
    </p>
    {% endif %}
    </div>

    </div>
    
    <script>
    
    function setChannel(ch){
        fetch("/ch" + ch)
        .then(response => response.json())
        .then(data => {
            console.log("channel changed");
            });
        }
    
    function reserveShow(){
        let shows = []
        
        if(document.getElementById("koujichu").checked){
                shows.push("koujichu")
                }
        
        if(document.getElementById("star").checked){
                shows.push("star")
                }
        
        fetch("/reserve",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
                },
            body:JSON.stringify({shows:shows})
            })
        .then(response => response.json())
        .then(data => {
            console.log("予約完了");
            
            setTimeout(()=>{
                location.reload()
                },1000)
            
            setTimeout(()=>{
                location.reload()
                },1000)
            
            })
        }
    
    function updateNextShows(){
        fetch("/next_shows")
        .then(response => response.json())
        .then(data => {
            let html = "";

            if(data.koujichu){
                html += `
                    <p>
                    ${data.koujichu.title}<br>
                    ${data.koujichu.time}
                    </p>
                `;
            }

            if(data.star){
                html += `
                    <p>
                    ${data.star.title}<br>
                    ${data.star.time}
                    </p>
                `;
            }

            document.getElementById("next-show-list").innerHTML = html;
        });
    }

    setInterval(updateNextShows, 30000);
    
    </script>
    
    </body>
    </html>
    """,
    koujichu_title=koujichu_title,
    koujichu_time=koujichu_time,
    star_title=star_title,
    star_time=star_time
    )

@app.route("/ch<int:ch>")
def set_channel(ch):
    result = client.publish(
        MQTT_TOPIC,
        str(ch),
        qos=1
    )
    result.wait_for_publish()
    print("MQTT送信:", ch)
    return {"status":"ok"}

@app.route("/reserve", methods=["POST"])#/reserve(フォームに入力された情報を送信する先)にPOST(送信方法の種類)がきたら実行
def reserve():
    
    data = request.json
    shows = data["shows"]
    
    print("予約番組:",shows)
    
    with open("reserved.txt", "w", encoding="utf-8") as f:#reserved.txt(w)を書き込むモードで開く
        for s in shows:
            f.write(s+"\n")

    auto_scheduler.update_next_shows()
    
    return {"status":"ok"}

@app.route("/next_shows")
def get_next_shows():
    koujichu = auto_scheduler.next_shows["koujichu"]
    star = auto_scheduler.next_shows["star"]

    result = {
        "koujichu": None,
        "star": None
    }

    if koujichu:
        result["koujichu"] = {
            "title": koujichu["title"],
            "time": koujichu["start"].strftime("%m/%d %H:%M")
        }

    if star:
        result["star"] = {
            "title": star["title"],
            "time": star["start"].strftime("%m/%d %H:%M")
        }

    return result

def run_server():
    connect_mqtt()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)#pcをサーバーとして起動