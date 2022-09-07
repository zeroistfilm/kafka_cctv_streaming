import asyncio
import signal
import os


shutdown: bool = False

def sig_handler() -> None:
    """ signal handler. `print_and_sleep`의 무한루프를 종료시킨다. """
    print('stopping loop...')
    global shutdown
    shutdown = True


async def print_and_sleep(loop) -> None:
    """ 1초에 한번 `sleep`이라는 문자를 출력하는 무한루프 """
    while not shutdown:
        print('sleep')
        await asyncio.sleep(1)
    loop.stop()


async def send_sigterm_after_5_seconds() -> None:
    """ 5초 이후에 스크립트 자신에게 SIGTERM을 보낸다. """
    await asyncio.sleep(5)
    os.kill(os.getpid(), signal.SIGTERM)


def main() -> None:
    loop = asyncio.new_event_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, sig_handler)

    loop.create_task(print_and_sleep(loop))
    loop.create_task(send_sigterm_after_5_seconds())

    try:
        loop.run_forever()
        print('loop stopped')
    finally:
        loop.close()
        print('loop closed')


if __name__ == '__main__':
    main()