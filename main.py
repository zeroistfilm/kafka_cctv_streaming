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


# get image from aiokafka consumer
async def get_image(camIdx):
    requestQueue[camIdx].append('on')
    consumer = aiokafka.AIOKafkaConsumer(camIdx,
                                 bootstrap_servers='ec2-3-38-136-70.ap-northeast-2.compute.amazonaws.com:29092')
    await consumer.start()
    try:
        while True:
            msg = await consumer.getone()
            print(msg.value)
            #yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + msg.value + b'\r\n\r\n')
    finally:
        await consumer.stop()


# def kafkastream(camIdx):
#
#     consumer = KafkaConsumer('my-topic', bootstrap_servers='ec2-3-38-136-70.ap-northeast-2.compute.amazonaws.com:29092')
#     print(',', end='', flush=True)
#     try:
#         for message in consumer:
#             print('.', end='', flush=True)
#             yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + message.value + b'\r\n\r\n')
#     finally:
#
#         consumer.close()
#         print('consumer close')


# 웹소켓 설정 ws://127.0.0.1:8000/ws 로 접속할 수 있음
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
    requestQueue[camIdx].append('on')
    consumer = aiokafka.AIOKafkaConsumer('my-topic',
                                         bootstrap_servers='ec2-3-38-136-70.ap-northeast-2.compute.amazonaws.com:29092')
    await consumer.start()
    try:
        while True:
            msg = await consumer.getone()
            #await websocket.send_text(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + msg.value + b'\r\n\r\n')
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
    # return RedirectResponse(f"ws://localhost:8080/ws/{camIdx}")
    # try:
    #     return StreamingResponse(get_image(camIdx), media_type='multipart/x-mixed-replace; boundary=frame')
    # finally:
    #     print('off')
    #     requestQueue[camIdx].append('off')
