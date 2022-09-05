import time
import sys
import cv2

from kafka import KafkaProducer
from kafka.errors import KafkaError
import aiokafka


producer = aiokafka.AIOKafkaProducer(bootstrap_servers='ec2-3-38-136-70.ap-northeast-2.compute.amazonaws.com:29092')
topic = 'my-topic'


def emit_video():
    await producer.start()
    print('start emitting')
    video = cv2.VideoCapture('rtsp://admin:emfvnf1!@192.168.2.20:554/trackID=2')

    while video.isOpened():
        success, frame = video.read()

        if not success:
            print('X', end='', flush=True)
            break
        print('.', end='', flush=True)
        # png might be too large to emit
        data = cv2.imencode('.jpeg', frame)[1].tobytes()
        try:
            await producer.send_and_wait(topic,data)
        finally:
            await producer.stop()
        # to reduce CPU usage
        time.sleep(0.2)
    print()

    video.release()

    print('done')


if __name__ == '__main__':
    emit_video()