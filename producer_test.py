import time
import sys
import cv2

from kafka import KafkaProducer
from kafka.errors import KafkaError
import logging
logging.basicConfig(level=logging.DEBUG)

#producer = KafkaProducer(bootstrap_servers='112.170.59.30:9093')
producer = KafkaProducer(bootstrap_servers='3.38.136.70:9093')
topic = 'my-topic'


def emit_video():
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

        future = producer.send(topic, data)
        try:
            future.get(timeout=10)
        except KafkaError as e:
            print(e)
            break



        # to reduce CPU usage
        time.sleep(0.2)
    print()

    video.release()

    print('done')


if __name__ == '__main__':
    emit_video()