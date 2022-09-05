import asyncio

from fastapi import FastAPI
from kafka import KafkaConsumer
from starlette.responses import StreamingResponse
from fastapi import FastAPI, WebSocket, Request

app = FastAPI()


def kafkastream():
    consumer = KafkaConsumer('my-topic', bootstrap_servers='ec2-3-38-136-70.ap-northeast-2.compute.amazonaws.com:29092')
    try:
        for message in consumer:
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + message.value + b'\r\n\r\n')
    finally:
        print('consumer close')
        consumer.close()

# 웹소켓 설정 ws://127.0.0.1:8000/ws 로 접속할 수 있음
@app.websocket("/ws")
async def wsConnect(websocket: WebSocket):
    print(f"client connected : {websocket.client}")
    await websocket.accept() # client의 websocket접속 허용
    await websocket.send_text(f"Welcome client : {websocket.client}")
    while True:
        #data = await websocket.receive_text()  # client 메시지 수신대기
        #print(f"message received : {data} from : {websocket.client}")
        await asyncio.sleep(1)
        await websocket.send_text(f"Message text was: ") # client에 메시지 전달





@app.get('/')
async def Home():
    return StreamingResponse(kafkastream(),media_type='multipart/x-mixed-replace; boundary=frame')