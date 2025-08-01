#!/usr/bin/env python

import asyncio
import queue
import threading
import time

from websockets.asyncio.server import serve

async def handle_client(websocket, queue, lock): 
    await websocket.send("CONNECTED")
    last_item = None
    while True:
        with lock:  # ensure thread-safe access to the queue
            item = queue.queue[0]
            if item != last_item:
                await websocket.send(item)
                last_item = item
            pass
        time.sleep(1)

async def websocket(queue):
    lock = threading.Lock()  # create a lock for thread safety
    async with serve(lambda ws: handle_client(ws, queue, lock), "0.0.0.0", 8765) as server:
        await server.serve_forever()

def start_ws():
    q = queue.Queue()
    asyncio.run(websocket(q))
    return q