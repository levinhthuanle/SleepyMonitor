import cv2
import dlib
import pygame
import numpy as np
from scipy.spatial import distance as dist
import time

# Khởi tạo pygame để phát âm thanh
pygame.init()
pygame.mixer.init()
am_thanh = pygame.mixer.Sound("canhbao.wav")  

# Hàm phát âm thanh cảnh báo
def phat_am_thanh():
    am_thanh.play()

# Hàm tính tỷ lệ khía cạnh của mắt (EAR: Eye Aspect Ratio)
def ty_le_mat(mat):
    A = dist.euclidean(mat[1], mat[5])
    B = dist.euclidean(mat[2], mat[4])
    C = dist.euclidean(mat[0], mat[3])
    return (A + B) / (2.0 * C)

# Hàm tính tỷ lệ khía cạnh của miệng (MAR: Mouth Aspect Ratio)
def ty_le_mieng(mieng):
    A = dist.euclidean(mieng[2], mieng[10])  # Khoảng cách dọc miệng
    B = dist.euclidean(mieng[4], mieng[8])
    C = dist.euclidean(mieng[0], mieng[6])   # Khoảng cách ngang miệng
    return (A + B) / (2.0 * C)

# Hàm tính góc nghiêng đầu
def goc_dau(cam_moc):
    mat_trai = (cam_moc.part(36).x, cam_moc.part(36).y)
    mat_phai = (cam_moc.part(45).x, cam_moc.part(45).y)
    goc = np.arctan2(mat_phai[1] - mat_trai[1], mat_phai[0] - mat_trai[0])
    return np.degrees(goc)

# Cấu hình dlib và camera
detector = dlib.get_frontal_face_detector()
du_doan = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

camera = cv2.VideoCapture(0)

# Các thông số ngưỡng
NGUONG_MAT_NHAM = 0.25
KHUNG_HINH_NGAT = 20
NGUONG_NGAP = 0.90
NGUONG_DAU_NGHIENG = 15
NGUONG_DAU_CUI = 20
THOI_GIAN_CANH_BAO = 10

# Biến theo dõi
bo_dem_mat = 0
thoi_gian_canh_bao_truoc = 0
canh_bao = False

while True:
    doc_duoc, khung_hinh = camera.read()
    if not doc_duoc:
        break

    xam = cv2.cvtColor(khung_hinh, cv2.COLOR_BGR2GRAY)
    khuon_mat = detector(xam)
    thoi_gian_hien_tai = time.time()

    for mat in khuon_mat:
        moc_mat = du_doan(xam, mat)

        # Lấy tọa độ mắt và miệng
        mat_trai = [(moc_mat.part(i).x, moc_mat.part(i).y) for i in range(36, 42)]
        mat_phai = [(moc_mat.part(i).x, moc_mat.part(i).y) for i in range(42, 48)]
        mieng = [(moc_mat.part(i).x, moc_mat.part(i).y) for i in range(48, 68)]

        # Tính toán EAR và MAR
        ear_trai = ty_le_mat(mat_trai)
        ear_phai = ty_le_mat(mat_phai)
        ear_tb = (ear_trai + ear_phai) / 2.0
        mar = ty_le_mieng(mieng)

        # Phát hiện nhắm mắt
        if ear_tb < NGUONG_MAT_NHAM:
            bo_dem_mat += 1
            if bo_dem_mat >= KHUNG_HINH_NGAT and not canh_bao:
                cv2.putText(khung_hinh, "CANH BAO: NGỦ GẬT!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                phat_am_thanh()
                canh_bao = True
                thoi_gian_canh_bao_truoc = thoi_gian_hien_tai
        else:
            bo_dem_mat = 0
            canh_bao = False

        # Phát hiện ngáp
        if mar > NGUONG_NGAP:
            cv2.putText(khung_hinh, "CANH BAO: NGÁP!", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            if thoi_gian_hien_tai - thoi_gian_canh_bao_truoc > THOI_GIAN_CANH_BAO:
                phat_am_thanh()
                thoi_gian_canh_bao_truoc = thoi_gian_hien_tai

        # Phát hiện đầu nghiêng hoặc cúi xuống
        goc = goc_dau(moc_mat)
        mui_y = moc_mat.part(30).y
        cam_y = moc_mat.part(8).y
        if abs(goc) > NGUONG_DAU_NGHIENG:
            cv2.putText(khung_hinh, "CANH BAO: DAU NGHIENG!", (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        elif cam_y - mui_y < NGUONG_DAU_CUI:
            cv2.putText(khung_hinh, "CANH BAO: DAU CUI XUONG!", (50, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Vẽ các điểm đặc trưng trên mặt
        for (x, y) in mat_trai + mat_phai + mieng:
            cv2.circle(khung_hinh, (x, y), 2, (0, 255, 0), -1)

    cv2.imshow("Phát hiện buồn ngủ", khung_hinh)

    if cv2.waitKey(1) & 0xFF == ord('e'):
        break

camera.release()
cv2.destroyAllWindows()

