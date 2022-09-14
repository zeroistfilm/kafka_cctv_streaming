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
from collections import defaultdict

app = FastAPI()
camManager = {}
capDict = {}


def getOpenWSCounts():
    pass


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
                        try:
                            capDict[farm][sector][cam][position] = caminfo[farm][sector][cam][position]
                        except Exception as e:
                            capDict[farm][sector][cam][position] = "Error check RTSP address"

    await asyncio.gather(*(ws_manager(idx) for idx in capDict['deulpul']['1']['cctv'].keys()))


async def ws_manager(index):
    async with websockets.connect(f"ws://3.38.136.70:8000/ws/{index}") as websocket:
        print("ws_manager is opened for ", index)

        while True:
            data_rcv = await websocket.recv()
            # data_rcv = json.load(data_rcv)
            # camidx, value = list(data_rcv.keys()), list(data_rcv.values())
            #
            #
            # if value == 'on':
            #     print(camidx, value)
            #     print('asyncio.create_task')
            #     asyncio.create_task(emit_video(camidx, value))
            # elif value == 'off':
            #     print('asyncio.cancel')
            #     pass

            #await asyncio.sleep(0.1)


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
            data = cv2.imencode('.jpeg', frame)[1].tobytes()

            await producer.send_and_wait(topic=camidx, value=data)
            await asyncio.sleep(0.2)

    finally:
        await producer.stop()
        video.release()
        print(f'{camidx} relese!')
