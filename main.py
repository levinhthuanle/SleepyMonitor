import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from io import BytesIO
from PIL import Image

app = FastAPI()

# Load mô hình landmarks
detector = dlib.get_frontal_face_detector()
du_doan = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Ngưỡng
NGUONG_MAT_NHAM = 0.25
NGUONG_NGAP = 0.90
NGUONG_DAU_NGHIENG = 15
NGUONG_DAU_CUI = 20

# Hàm tính EAR
def ty_le_mat(mat):
    A = dist.euclidean(mat[1], mat[5])
    B = dist.euclidean(mat[2], mat[4])
    C = dist.euclidean(mat[0], mat[3])
    return (A + B) / (2.0 * C)

# Hàm tính MAR
def ty_le_mieng(mieng):
    A = dist.euclidean(mieng[2], mieng[10])
    B = dist.euclidean(mieng[4], mieng[8])
    C = dist.euclidean(mieng[0], mieng[6])
    return (A + B) / (2.0 * C)

# Hàm tính góc nghiêng đầu
def goc_dau(cam_moc):
    mat_trai = (cam_moc.part(36).x, cam_moc.part(36).y)
    mat_phai = (cam_moc.part(45).x, cam_moc.part(45).y)
    goc = np.arctan2(mat_phai[1] - mat_trai[1], mat_phai[0] - mat_trai[0])
    return np.degrees(goc)

@app.post("/detect")
async def phat_hien_trang_thai(file: UploadFile = File(...)):
    # Đọc ảnh từ file upload
    contents = await file.read()
    image = Image.open(BytesIO(contents)).convert("RGB")
    frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Phát hiện khuôn mặt
    faces = detector(gray)
    if not faces:
        return JSONResponse({"status": "Không phát hiện khuôn mặt"}, status_code=400)

    trang_thai = "Bình thường"
    for face in faces:
        cam_moc = du_doan(gray, face)

        # Lấy tọa độ mắt và miệng
        mat_trai = [(cam_moc.part(i).x, cam_moc.part(i).y) for i in range(36, 42)]
        mat_phai = [(cam_moc.part(i).x, cam_moc.part(i).y) for i in range(42, 48)]
        mieng = [(cam_moc.part(i).x, cam_moc.part(i).y) for i in range(48, 68)]

        ear_trai = ty_le_mat(mat_trai)
        ear_phai = ty_le_mat(mat_phai)
        ear_tb = (ear_trai + ear_phai) / 2.0
        mar = ty_le_mieng(mieng)

        goc = goc_dau(cam_moc)
        mui_y = cam_moc.part(30).y
        cam_y = cam_moc.part(8).y

        if ear_tb < NGUONG_MAT_NHAM:
            trang_thai = "Ngủ gật"
        elif mar > NGUONG_NGAP:
            trang_thai = "Ngáp"
        elif abs(goc) > NGUONG_DAU_NGHIENG:
            trang_thai = "Đầu nghiêng"
        elif cam_y - mui_y < NGUONG_DAU_CUI:
            trang_thai = "Đầu cúi"
        else:
            trang_thai = "Bình thường"

        break  # chỉ lấy khuôn mặt đầu tiên

    return {"status": trang_thai}
