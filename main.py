from fastapi import FastAPI
from kafka import KafkaConsumer
from starlette.responses import StreamingResponse

app = FastAPI()


def kafkastream():
    consumer = KafkaConsumer('my-topic', bootstrap_servers='ec2-3-38-136-70.ap-northeast-2.compute.amazonaws.com:29092')
    try:
        for message in consumer:
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + message.value + b'\r\n\r\n')
    finally:
        print('consumer close')
        consumer.close()

@app.get('/')
async def Home():
    return StreamingResponse(kafkastream(),media_type='multipart/x-mixed-replace; boundary=frame')