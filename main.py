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
app = FastAPI()
requestQueue = {}
socketDict = {}





@app.websocket("/ws/{camIdx}")
async def wsConnect(websocket: WebSocket, camIdx: str):
    requestQueue[camIdx] = deque()
    print(f"client connected : {websocket.client}")

    await websocket.accept()  # client의 websocket접속 허용
    # await websocket.send_text(f"Welcome client : {websocket.client}")
    while True:
        # data = await websocket.receive_text()  # client 메시지 수신대기
        # print(requestQueue[camIdx])
        if len(requestQueue[camIdx]) != 0:
            flag = requestQueue[camIdx].popleft()
            statusJson = {camIdx: flag}
            await websocket.send_text(json.dumps(statusJson))

        # data = await websocket.receive_text()  # client 메시지 수신대기
        # print(f"message received : {data} from : {websocket.client}")
        await asyncio.sleep(0.1)


@app.websocket("/ws/client/{camIdx}")
async def wsConnect(websocket: WebSocket, camIdx: str):
    print(f"client connected : {websocket.client}")
    await websocket.accept()
    if len(requestQueue[camIdx]) != 0:
        requestQueue[camIdx].append('on')

    consumer = aiokafka.AIOKafkaConsumer(camIdx,bootstrap_servers='ec2-3-38-136-70.ap-northeast-2.compute.amazonaws.com:29092')
    await consumer.start()

    try:
        while True:
            msg = await consumer.getone()
            await websocket.send_text(msg.value)
            await asyncio.sleep(0.1)
    except Exception as e:
        print(e)
    finally:
        requestQueue[camIdx].append('off')
        await consumer.stop()


@app.get('/{camIdx}')
async def Home(request: Request, camIdx: str):
    return templates.TemplateResponse("client.html", context= {"request": request})

