import asyncio
import datetime

import aiokafka
from fastapi import FastAPI
from kafka import KafkaConsumer
from starlette.responses import StreamingResponse
from fastapi import FastAPI, WebSocket, Request
from starlette.responses import RedirectResponse
import datetime
from collections import deque
import json
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
socketDict = {}
camManager = {}

app = FastAPI()

class CamClientManager:
    def __init__(self, camidx):
        self.camidx = camidx
        self.aliveClientCount = 0
        self.clientList = []
        self.isUpdate = False

    def isCamOpend(self):
        if self.aliveClientCount > 0:
            return True
        else:
            return False

    def addClient(self, client):
        self.isUpdate = True
        self.clientList.append(client)
        self.aliveClientCount += 1

    def removeClient(self, client):
        self.isUpdate = True
        self.clientList.remove(client)
        self.aliveClientCount -= 1

    def getAliveClientCount(self):
        return self.aliveClientCount

    def getClientList(self):
        return self.clientList

    def getSendMsg(self):
        self.isUpdate = False
        if self.aliveClientCount >= 1:
            return {self.camidx: 'on'}
        if self.aliveClientCount == 0:
            return {self.camidx: 'off'}


    def isUpdated(self):
        return self.isUpdate

    def __str__(self):
        return f"aliveClientCount: {self.aliveClientCount}, clientList: {self.clientList}"


@app.on_event("startup")
async def startup():
    for camIdx in ['1-1', '1-2', '1-3', '1-4', '1-5', '1-6', '1-7', '1-8', '1-9', '1-10', '1-11', '1-12', '1-13',
                   '1-14', '1-15', '1-16', '1-17', '1-18', '1-19', '1-20',
                   '2-1', '2-2', '2-3', '2-4', '2-5', '2-6', '2-7', '2-8', '2-9', '2-10', '2-11', '2-12', '2-13',
                   '2-14', '2-15', '2-16', '2-17', '2-18', '2-19', '2-20',
                   'rgb', 'thermal']:
        camManager[camIdx] = CamClientManager(camIdx)
        print('create CamClientManager', camIdx)


# ???????????? ???????????? ws
@app.websocket("/ws/{camIdx}")
async def wsconnect(websocket: WebSocket, camIdx: str):
    # requestQueue[camIdx] = deque()

    print(f"client connected : {websocket.client}")
    await websocket.accept()  # client??? websocket?????? ??????

    while True:
        if camManager[camIdx].isUpdated():
            await websocket.send_json(camManager[camIdx].getSendMsg())

        await asyncio.sleep(0.1)


@app.websocket("/ws/client/{camIdx}")
async def wsConnect(websocket: WebSocket, camIdx: str):
    print(f"client connected : {websocket.client}")

    await websocket.accept()
    camManager[camIdx].addClient(websocket)

    consumer = aiokafka.AIOKafkaConsumer(camIdx, bootstrap_servers='ec2-3-38-136-70.ap-northeast-2.compute.amazonaws.com:29092')
    await consumer.start()

    try:
        while True:
            msg = await consumer.getone()
            await websocket.send_text(msg.value)
            await asyncio.sleep(0.05)
    except Exception as e:
        print(e)
    finally:
        camManager[camIdx].removeClient(websocket)
        await consumer.stop()



@app.get('/{camIdx}')
async def Home(request: Request, camIdx: str):
    return templates.TemplateResponse("client_localhost.html", context={"request": request})
