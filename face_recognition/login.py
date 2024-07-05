import cv2
import numpy as np
from flask import request, jsonify, current_app as app
from deepface import DeepFace
from sklearn.metrics.pairwise import cosine_similarity
from face_recognition.utils import decode_base64_image, normalize_image, extract_face, save_image, load_embeddings

model_name = "VGG-Face"
threshold = 65  # 유사도를 판단하는 임계값, 필요에 따라 조정

def login_face():
    try:
        app.logger.info("리액트로부터 이미지 수신완료 - 로그인 과정 시작")
        data = request.json
        userEmail = data['userEmail']
        image_base64 = data['image']
        img = decode_base64_image(image_base64)
        app.logger.info("이미지 디코딩 완료")

        # 원본 이미지 저장
        save_image(img, "./login/original", userEmail, "original")
        app.logger.info("원본 이미지 저장 완료")

        # 그레이스케일 이미지 저장
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        save_image(gray_img, "./login/grayscale", userEmail, "grayscale")
        app.logger.info("그레이스케일 이미지 저장 완료")

        # 얼굴 영역 추출
        face_img = extract_face(img)
        if face_img is None:
            app.logger.error("얼굴 영역 추출 실패")
            return jsonify({"status": "failure", "message": "No face detected."})
        app.logger.info("얼굴 영역 추출 완료")

        # 얼굴 영역 이미지 저장
        save_image(face_img, "./login/face", userEmail, "face")
        app.logger.info("얼굴 영역 이미지 저장 완료")

        # 얼굴 임베딩을 위한 정규화
        normalized_face = normalize_image(face_img)
        app.logger.info("이미지 정규화 완료")

        # 정규화된 이미지 저장
        save_image((normalized_face * 255).astype(np.uint8), "./login/normalized", userEmail, "normalized")
        app.logger.info("정규화된 이미지 저장 완료")

        # 현재 얼굴 임베딩 계산
        embedding = DeepFace.represent(normalized_face, model_name=model_name, enforce_detection=False)[0]["embedding"]
        embedding = np.array(embedding)
        app.logger.info("현재 얼굴 임베딩 계산 완료")

        # 기존 임베딩 데이터 불러오기
        embeddings = load_embeddings()

        # 입력된 userEmail의 임베딩 가져오기
        if userEmail not in embeddings:
            app.logger.error(f"등록된 사용자가 아님: {userEmail}")
            return jsonify({"status": "failure", "message": "User not registered."})
        registered_embedding = np.array(embeddings[userEmail])

        # 유사도 계산
        cos_sim = cosine_similarity([registered_embedding], [embedding])[0][0]
        cos_sim *= 100
        cos_sim = round(cos_sim, 2)

        if cos_sim > threshold:
            app.logger.info(f"로그인 성공 - 사용자: {userEmail}, 유사도: {cos_sim}")
            return jsonify({"status": "success", "message": "Login successful.", "userEmail": userEmail,
                            "similarity": cos_sim})
        else:
            app.logger.info(f"로그인 실패 - 유사도: {cos_sim}")
            return jsonify({"status": "failure", "message": "Login failed.", "similarity": cos_sim})

    except Exception as e:
        app.logger.error(f"Error in login_face: {str(e)}")
        return jsonify({"status": "failure", "message": "Login failed."})
