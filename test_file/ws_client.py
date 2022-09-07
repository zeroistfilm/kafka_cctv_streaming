import asyncio
import websockets


async def my_connect():
    async with websockets.connect("ws://localhost:8080/ws/1-1") as websocket:
        try:
            while True:
                # if websockets.exceptions.ConnectionClosedOK:
                #    break
                data_rcv = await websocket.recv()
                print("data received from server : " + data_rcv);
        except websockets.exceptions.ConnectionClosedOK as e:
            print(e)
        finally:
            await websocket.close()


# connect to server
asyncio.get_event_loop().run_until_complete(my_connect())
