import asyncio
import aiokafka


async def test():
    producer = aiokafka.AIOKafkaProducer(bootstrap_servers='ec2-3-38-136-70.ap-northeast-2.compute.amazonaws.com:29092')
    topic = 'my-topic'
    await producer.start()

    try:
        while True:
            await producer.send_and_wait(topic, b"Super message")
            await asyncio.sleep(0.5)
    finally:
        await producer.stop()


asyncio.run(test())
