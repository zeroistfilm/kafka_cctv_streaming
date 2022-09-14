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


camManager = {}
capDict = {}


@app.on_event("startup")
async def startup():
    global capDict
    with open("cctv_config.json", 'r', encoding='UTF-8') as f:
        caminfo = json.load(f)

    for farm in caminfo.keys():
        capDict[farm] = {}
        for sector in caminfo[farm].keys():
            capDict[farm][sector] = {}
            for cam in caminfo[farm][sector].keys():
                capDict[farm][sector][cam] = {}
                for position in caminfo[farm][sector][cam].keys():
                    capDict[farm][sector][cam][position] = {}
                    if caminfo[farm][sector][cam][position].split('://')[0] == "rtsp":
                        # print(caminfo[farm][sector][cam][position])
                        try:
                            capDict[farm][sector][cam][position] = caminfo[farm][sector][cam][position]
                        except Exception as e:
                            capDict[farm][sector][cam][position] = "Error check RTSP address"

    await asyncio.gather(*(ws_manager(idx) for idx in capDict['deulpul']['1']['cctv'].keys()))


async def ws_manager(index):
    async with websockets.connect(f"ws://3.38.136.70:8000/ws/{index}") as websocket:
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
    print(f'{camidx} start emitting!')

    video = cv2.VideoCapture(capDict['deulpul']['1']['cctv'][camidx])

    try:
        while video.isOpened() and camManager[camidx] == 'on':
            success, frame = video.read()
            if not success:
                print('X', end='', flush=True)
                break
            # print('.', end='', flush=True)
            # png might be too large to emit
            data = cv2.imencode('.jpeg', frame)[1].tobytes()

            await producer.send_and_wait(topic=camidx, value=data)
            await asyncio.sleep(0.2)

    finally:
        await producer.stop()
        video.release()
        print(f'{camidx} relese!')
