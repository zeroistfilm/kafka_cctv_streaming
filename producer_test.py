import asyncio
import time
import sys
import cv2

from kafka import KafkaProducer
from kafka.errors import KafkaError
import aiokafka
from fastapi import FastAPI, WebSocket, Request
import websockets
import json
import multiprocessing

app = FastAPI()

# producer = KafkaProducer(bootstrap_servers='ec2-3-38-136-70.ap-northeast-2.compute.amazonaws.com:29092')
topic = 'my-topic'

camManager = {}

@app.on_event("startup")
async def startup():

    await asyncio.gather(ws_manager('1-2'), ws_manager('1-1'))



async def ws_manager(index):
        async with websockets.connect(f"ws://localhost:8080/ws/{index}") as websocket:
            print(index)
            while True:
                data_rcv = await websocket.recv()
                camidx, value = list(json.loads(data_rcv).items())[0]
                camManager[camidx] = value
                print(camManager)
                if camManager[camidx] == 'on':
                    asyncio.create_task(emit_video(camidx, value))
                elif camManager[camidx] == 'off':
                    pass
                await asyncio.sleep(0.1)


async def emit_video(camidx, value):
    producer = aiokafka.AIOKafkaProducer(bootstrap_servers='ec2-3-38-136-70.ap-northeast-2.compute.amazonaws.com:29092')
    await producer.start()
    print('start emitting!')
    if camidx =='1-1':
        video = cv2.VideoCapture('rtsp://admin:emfvnf1!@192.168.2.20:554/trackID=2')
    elif camidx =='1-2':
        video = cv2.VideoCapture('rtsp://admin:emfvnf1!@192.168.2.21:554/trackID=2')
    try:
        while video.isOpened() and camManager[camidx] == 'on':
            success, frame = video.read()
            if not success:
                print('X', end='', flush=True)
                break
            print('.', end='', flush=True)
            # png might be too large to emit
            data = cv2.imencode('.jpeg', frame)[1].tobytes()

            await producer.send_and_wait(topic, data)
            await asyncio.sleep(0.2)

    finally:
        await producer.stop()
        video.release()
        print('relese!')

