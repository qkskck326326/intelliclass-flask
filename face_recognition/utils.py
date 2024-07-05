import os
import cv2
import base64
import json
import numpy as np
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection

def decode_base64_image(base64_str):
    nparr = np.frombuffer(base64.b64decode(base64_str), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def normalize_image(img):
    img = img / 255.0
    return img

def extract_face(img, margin=0.10, target_size=(160, 160)):
    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_detection.process(img_rgb)

        if results.detections:
            detection = results.detections[0]
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, _ = img.shape
            x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)

            # 얼굴 사각형 경계를 확장하여 얼굴 전체가 포함되도록 함
            x = max(0, x - int(w * margin))
            y = max(0, y - int(h * margin))
            w = min(img.shape[1] - x, w + int(2 * w * margin))
            h = min(img.shape[0] - y, h + int(2 * h * margin))

            face_img = img[y:y + h, x:x + w]

            # 얼굴 이미지 크기를 target_size로 조정
            face_img = cv2.resize(face_img, target_size)

            return face_img
    return None

def save_image(img, folder, userEmail, stage):
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_path = os.path.join(folder, f"{userEmail}_{stage}.png")
    cv2.imwrite(file_path, img)
    return file_path

def load_embeddings():
    embeddings_path = "./embeddings/faces_embeddings.json"
    if not os.path.exists(embeddings_path):
        if not os.path.exists(os.path.dirname(embeddings_path)):
            os.makedirs(os.path.dirname(embeddings_path))
        with open(embeddings_path, 'w') as f:
            json.dump({}, f)
        return {}

    with open(embeddings_path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}  # JSON 디코딩 오류 발생 시 빈 딕셔너리 반환

def save_embeddings(embeddings):
    embeddings_path = "./embeddings/faces_embeddings.json"
    if not os.path.exists(os.path.dirname(embeddings_path)):
        os.makedirs(os.path.dirname(embeddings_path))
    with open(embeddings_path, "w") as f:
        json.dump(embeddings, f, separators=(',', ':'), indent=4)
