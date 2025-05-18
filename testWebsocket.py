import asyncio
import websockets
import cv2

async def send_frames():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        cap = cv2.VideoCapture(1)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            await websocket.send(buffer.tobytes())
            response = await websocket.recv()
            print("Server response:", response)

asyncio.run(send_frames())
