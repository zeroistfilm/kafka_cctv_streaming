import asyncio

import cv2
import aiokafka
from fastapi import FastAPI
import websockets
import json

print("producer is opened")
app = FastAPI()
taskManagers = {}
capDict = {}
IPADDRESS= '3.38.136.70:8000'
#IPADDRESS = 'localhost:8080'


class TaskManager():

    def __init__(self):
        self.task = None
        self.killSignal = False

    def isTaskAlive(self):
        if self.task is None: return False
        if self.task:
            return True
        else:
            return False

    def setTask(self, task):
        self.task = task

    def getTask(self):
        return self.task

    def resetKillSignal(self):
        self.killSignal = False

    def setKillSignal(self, killSignal):
        self.killSignal = killSignal

    def getKillSignal(self):
        return self.killSignal

    def close(self):
        if self.task is not None:
            self.task.cancel()
            self.setTask(None)

    # def __del__(self):
    #     self.close()


@app.on_event("startup")
async def startup():
    print("startup")
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


async def ws_manager(camidx):
    print(f"ws_manager {camidx}")
    async with websockets.connect(f"ws://{IPADDRESS}/ws/{camidx}") as websocket:
        print("ws_manager is opened for ", camidx)
        taskManagers[camidx] = TaskManager()
        # 웹소켓 유지
        while True:
            data_rcv = await websocket.recv()
            data_rcv = json.loads(data_rcv)
            camidx, value = list(data_rcv.keys())[0], list(data_rcv.values())[0]
            print(f'camidx: {camidx}, value: {value}')

            if value == 'on':
                if taskManagers[camidx].isTaskAlive():
                    continue
                else:
                    print('asyncio.create_task')
                    taskManagers[camidx].setTask(asyncio.create_task(emitVideo(camidx, value)))

            elif value == 'off':
                taskManagers[camidx].setKillSignal(True)
                taskManagers[camidx].close()

            # await asyncio.sleep(0.05)


async def emitVideo(camidx, value):
    producer = aiokafka.AIOKafkaProducer(bootstrap_servers='ec2-3-38-136-70.ap-northeast-2.compute.amazonaws.com:29092')
    await producer.start()
    print(f'{camidx} start emitting!')

    video = cv2.VideoCapture(capDict['deulpul']['1']['cctv'][camidx])
    try:
        while video.isOpened():
            success, frame = video.read()
            if not success:
                #print('X', end='', flush=True)
                break
            #print('.', end='', flush=True)
            data = cv2.imencode('.jpeg', frame)[1].tobytes()

            await producer.send_and_wait(topic=camidx, value=data)
            # await asyncio.sleep(0.05)

            if taskManagers[camidx].getKillSignal():
                print('kill signal')
                break

    finally:
        await producer.stop()
        video.release()
        taskManagers[camidx].resetKillSignal()
        print(f'{camidx} relese!')

