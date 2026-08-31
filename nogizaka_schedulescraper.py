# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 20:24:48 2026

@author: runa6
"""

import requests#Webページ取得
import datetime

def get_nogizaka_tv():

    now = datetime.datetime.now()

    url = "https://sp.nogizaka46.com/api/schedule"

    months = []

    months.append((now.year, now.month))

    if now.month == 1:
        months.append((now.year - 1, 12))
    else:
        months.append((now.year, now.month - 1))

    headers = {
            "User-Agent": "Mozilla/5.0"
            }

    shows = []

    for year, month in months:
        params = {
            "yearDateFrom": str(year),
            "monthDateFrom": f"{month:02d}",
            "categoryName": "",
            "officialArtistId": "",
            }
    
        try:
            r = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=10
            )#APIからJSONデータ取得
        except Exception as e:
            print("番組情報取得エラー:", repr(e))
            continue

        try:
            data = r.json()
        except Exception as e:
            print("JSON取得エラー", repr(e))
            continue

        for item in data["list"]:#データを1個ずつ確認
        
            title = item["title"]#番組名取得
            scheduled = item["scheduledAt"]#日付
        
            #ミリ秒→秒
            scheduled = scheduled / 1000
        
            #日付変換
            date = datetime.datetime.fromtimestamp(scheduled)
        
            #乃木坂工事中と乃木坂スター誕生を検出
            if item["categoryName"] == "tv":
                if "乃木坂工事中" in title or "乃木坂スター誕生！SIX" in title:
            
                    start_time = item.get("startTime", "不明")#startTimeはない場合もあるのでエラー対策
                    
                    shows.append({
                        "title": title,
                        "date": date,
                        "start_time": start_time
                        })
                    
                    #print("番組発見")
                    #print("タイトル:", title)
                    #print("日付:", date.date())
                    #print("開始時間:", start_time)
                    #print("------")
    return shows

