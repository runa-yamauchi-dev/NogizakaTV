#include <WiFi.h>
#include <WebServer.h>
#include <IRremoteESP8266.h>
#include <IRsend.h>

#include <WiFiClientSecure.h>
#include <PubSubClient.h>

//Wi-Fi
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

//HiveMQ Cloud
const char* mqtt_server = "YOUR_MQTT_SERVER";
const char* mqtt_username = "YOUR_MQTT_USERNAME";
const char* mqtt_password = "YOUR_MQTT_PASSWORD";
const int mqtt_port = 8883;

//MQTT
WiFiClientSecure espClient;
PubSubClient mqttClient(espClient);

//赤外線
const uint16_t IR_LED = 4;
IRsend irsend(IR_LED);//赤外線送信装置irsendを作る

//WebServer
WebServer server(80);//Webサーバー作成

//チャンネル処理
void sendChannel(int ch) {
  if (ch == 0) {
    irsend.sendNEC(YOUR_IR_CODE, 32);
    Serial.println("IR: POWER");
  }

  else if (ch == 1){
    irsend.sendNEC(YOUR_IR_CODE, 32);
    Serial.println("IR: CH1");
  }

  else if (ch == 2){
    irsend.sendNEC(YOUR_IR_CODE, 32);
    Serial.println("IR: CH2");
  } 

  else if (ch == 4){
    irsend.sendNEC(YOUR_IR_CODE, 32);
    Serial.println("IR: CH4");
  }

  else if (ch == 5){
    irsend.sendNEC(YOUR_IR_CODE, 32);
    Serial.println("IR: CH5");
  }

  else if (ch == 6){
    irsend.sendNEC(YOUR_IR_CODE, 32);
    Serial.println("IR: CH6");
  }

  else if (ch == 7){
    irsend.sendNEC(YOUR_IR_CODE, 32);
    Serial.println("IR: CH7");
  }

  else if (ch == 8){
    irsend.sendNEC(YOUR_IR_CODE, 32);
    Serial.println("IR: CH8");
  }
}

//MQTTメッセージ受信
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("MQTT受信: ");

  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);

  int ch = message.toInt();
  sendChannel(ch);
}

//MQTT接続
void connectMQTT() {
  while (!mqttClient.connected()) {
    Serial.println("HiveMQ Cloudへ接続中...");
    String clientId = "ESP32-TV-";
    clientId += String((uint32_t)ESP.getEfuseMac(), HEX);

    if (mqttClient.connect(
          clientId.c_str(),
          mqtt_username,
          mqtt_password
       )) {
        Serial.println("MQTT Connected!");
        mqttClient.subscribe("nogizaka/tv/channel");
        Serial.println("Subscribe: nogizaka/tv/channel");
       } else {
        Serial.print("MQTT接続失敗 state=");
        Serial.println(mqttClient.state());
        delay(5000);
       }
  }
}

//WebServer
void handleRoot() {//トップページ
  String html = "<h1>TV Remote</h1>";//タイトル
  html += "<a href=\"/ch0\"><button>power</button></a>";//電源
  html += "<a href=\"/ch1\"><button>1ch</button></a>";//1chボタン(ボタンを押すと/ch1というURLにアクセス)
  html += "<a href=\"/ch2\"><button>2ch</button></a>";
  html += "<a href=\"/ch4\"><button>4ch</button></a>";
  html += "<a href=\"/ch5\"><button>5ch</button></a>";
  html += "<a href=\"/ch6\"><button>6ch</button></a>";
  html += "<a href=\"/ch7\"><button>7ch</button></a>";
  html += "<a href=\"/ch8\"><button>8ch</button></a>";

  server.send(200, "text/html", html);//スマホにHTMLページを送る
}

void ch0() {//電源押されたときの処理
  irsend.sendNEC(YOUR_IR_CODE, 32);
  server.send(200, "text/html", "CH0 sent");//スマホにCH0 sentと表示
}

void ch1() {//1ch押されたときの処理
  irsend.sendNEC(YOUR_IR_CODE, 32);
  server.send(200, "text/html", "CH1 sent");//スマホにCH1 sentと表示
}

void ch2() {//2ch押されたときの処理
  irsend.sendNEC(YOUR_IR_CODE, 32);
  server.send(200, "text/html", "CH2 sent");//スマホにCH2 sentと表示
}

void ch4() {//4ch押されたときの処理
  irsend.sendNEC(YOUR_IR_CODE, 32);
  server.send(200, "text/html", "CH4 sent");//スマホにCH4 sentと表示
}

void ch5() {//5ch押されたときの処理
  irsend.sendNEC(YOUR_IR_CODE, 32);
  server.send(200, "text/html", "CH5 sent");//スマホにCH5 sentと表示
}

void ch6() {//6ch押されたときの処理
  irsend.sendNEC(YOUR_IR_CODE, 32);
  server.send(200, "text/html", "CH6 sent");//スマホにCH6 sentと表示
}

void ch7() {//7ch押されたときの処理
  irsend.sendNEC(YOUR_IR_CODE, 32);
  server.send(200, "text/html", "CH7 sent");//スマホにCH7 sentと表示
}

void ch8() {//8ch押されたときの処理
  irsend.sendNEC(YOUR_IR_CODE, 32);
  server.send(200, "text/html", "CH8 sent");//スマホにCH8 sentと表示
}

//setup
void setup() {
  Serial.begin(115200);
  irsend.begin();//赤外線送信機能をスタート

  //WiFi接続
  WiFi.begin(ssid, password);//WiFi接続開始

  Serial.println("Connecting...");

  while (WiFi.status() != WL_CONNECTED){//WiFi接続されるまで待つ
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("Connected!");

  Serial.println(WiFi.localIP());//ESP32のIP表示

  //MQTT設定
  espClient.setInsecure();
  mqttClient.setServer(mqtt_server, mqtt_port);
  mqttClient.setCallback(mqttCallback);

  //WebServer
  server.on("/",handleRoot);//トップページ
  server.on("/ch0", ch0);//ch0
  server.on("/ch1", ch1);//ch1
  server.on("/ch2", ch2);//ch2
  server.on("/ch4", ch4);//ch4
  server.on("/ch5", ch5);//ch5
  server.on("/ch6", ch6);//ch6
  server.on("/ch7", ch7);//ch7
  server.on("/ch8", ch8);//ch8

  server.begin();//ESPのサーバーを起動
  Serial.println("WebServer started");

  //MQTT接続
  connectMQTT();
}

//loop
void loop() {
  //WebServer
  server.handleClient();//スマホからのアクセス監視(これによりボタンが反応する)

  //MQTT接続確認
  if (!mqttClient.connected()) {
    connectMQTT();
  }

  //MQTT通信を処理
  mqttClient.loop();
}
