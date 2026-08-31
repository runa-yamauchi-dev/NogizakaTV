# -*- coding: utf-8 -*-
"""
Created on Sat Mar 14 22:24:09 2026

@author: runa6
"""

import threading#スレッド機能複数のプログラムを同時に動かす

import nogizakaIR
import auto_scheduler

#Flaskサーバー
server_thread = threading.Thread(target=nogizakaIR.run_server)

#自動スケジューラ
scheduler_thread = threading.Thread(target=auto_scheduler.check_show)

server_thread.start()
scheduler_thread.start()