from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import mediapipe as mp
import base64
from scipy.spatial import distance as dist
import time

app = FastAPI()

# Ngưỡng và thông số
NGUONG_MAT_NHAM = 0.15
NGUONG_NGAP = 0.85

# Mediapipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, refine_landmarks=True)

# EAR & MAR
def tinh_ear(mat):
    A = dist.euclidean(mat[1], mat[5])
    B = dist.euclidean(mat[2], mat[4])
    C = dist.euclidean(mat[0], mat[3])
    return (A + B) / (2.0 * C)

def tinh_mar(mieng):
    A = dist.euclidean(mieng[13], mieng[19])
    B = dist.euclidean(mieng[14], mieng[18])
    C = dist.euclidean(mieng[12], mieng[16])
    return (A + B) / (2.0 * C)

def xu_ly_anh(image_np):
    h, w, _ = image_np.shape
    rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            diem = face_landmarks.landmark
            mat_trai = [(int(diem[i].x * w), int(diem[i].y * h)) for i in [33, 160, 158, 133, 153, 144]]
            mat_phai = [(int(diem[i].x * w), int(diem[i].y * h)) for i in [362, 385, 387, 263, 373, 380]]
            mieng = [(int(diem[i].x * w), int(diem[i].y * h)) for i in [308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 185, 40, 39, 37, 0, 267, 269, 270, 409, 415]]

            ear_tb = (tinh_ear(mat_trai) + tinh_ear(mat_phai)) / 2.0
            mar = tinh_mar(mieng)

            return {
                "ear": float(ear_tb),  # Convert to Python float
                "mar": float(mar),     # Convert to Python float
                "canh_bao_mat": bool(ear_tb < NGUONG_MAT_NHAM),  # Convert to Python bool
                "canh_bao_ngap": bool(mar > NGUONG_NGAP)          # Convert to Python bool
            }
    return {"error": "No face"}

@app.get("/")
async def index():
    return "{Status: Running}"

# Endpoint REST API
@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    image_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    result = xu_ly_anh(image_np)
    return JSONResponse(content=result)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()

            # Convert bytes to image
            np_arr = np.frombuffer(data, np.uint8)
            image_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if image_np is None:
                await websocket.send_json({"error": "Invalid image"})
                continue

            # Process image
            result = xu_ly_anh(image_np)
            await websocket.send_json(result)
    except WebSocketDisconnect:
        print("Client disconnected")