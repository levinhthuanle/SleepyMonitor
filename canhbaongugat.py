import cv2
import mediapipe as mp
# import numpy as np
import time
import pygame
from scipy.spatial import distance as dist

pygame.init()
pygame.mixer.init()
am_thanh = pygame.mixer.Sound("canhbao.mp3")

def phat_am_thanh():
    am_thanh.play()

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

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

cap = cv2.VideoCapture(0)

NGUONG_MAT_NHAM = 0.25
KHUNG_HINH_NGAT = 20
NGUONG_NGAP = 0.75
THOI_GIAN_CANH_BAO = 10

bo_dem_mat = 0
canh_bao = False
thoi_gian_canh_bao_truoc = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    thoi_gian_hien_tai = time.time()

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Lấy điểm EAR (mắt trái/phải) và MAR (miệng)
            diem = face_landmarks.landmark

            mat_trai = [(int(diem[i].x * w), int(diem[i].y * h)) for i in [33, 160, 158, 133, 153, 144]]
            mat_phai = [(int(diem[i].x * w), int(diem[i].y * h)) for i in [362, 385, 387, 263, 373, 380]]
            mieng = [(int(diem[i].x * w), int(diem[i].y * h)) for i in [308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 185, 40, 39, 37, 0, 267, 269, 270, 409, 415]]

            ear_trai = tinh_ear(mat_trai)
            ear_phai = tinh_ear(mat_phai)
            ear_tb = (ear_trai + ear_phai) / 2.0
            mar = tinh_mar(mieng)

            if ear_tb < NGUONG_MAT_NHAM:
                bo_dem_mat += 1
                if bo_dem_mat >= KHUNG_HINH_NGAT and not canh_bao:
                    cv2.putText(frame, "CANH BAO: NHAM MAT!", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    phat_am_thanh()
                    canh_bao = True
                    thoi_gian_canh_bao_truoc = thoi_gian_hien_tai
            else:
                bo_dem_mat = 0
                canh_bao = False

            if mar > NGUONG_NGAP:
                cv2.putText(frame, "CANH BAO: NGAP!", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                if thoi_gian_hien_tai - thoi_gian_canh_bao_truoc > THOI_GIAN_CANH_BAO:
                    phat_am_thanh()
                    thoi_gian_canh_bao_truoc = thoi_gian_hien_tai

            for (x, y) in mat_trai + mat_phai + mieng:
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

    cv2.imshow("Canh Bao Ngu Gat", frame)
    if cv2.waitKey(1) & 0xFF == ord('e'):
        break

cap.release()
cv2.destroyAllWindows()
