import cv2
import numpy as np
from flask import request, jsonify, current_app as app
from deepface import DeepFace
from face_recognition.utils import decode_base64_image, normalize_image, extract_face, save_image, load_embeddings, save_embeddings

model_name = "VGG-Face"

def register_face():
    try:
        app.logger.info("리액트로부터 이미지 수신완료 - 등록 과정 시작")
        data = request.json
        userEmail = data['userEmail']
        image_base64 = data['image']
        img = decode_base64_image(image_base64)
        app.logger.info("이미지 디코딩 완료")

        # 원본 이미지 저장
        save_image(img, "./register/original", userEmail, "original")
        app.logger.info("원본 이미지 저장 완료")

        # 그레이스케일 이미지 저장
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        save_image(gray_img, "./register/grayscale", userEmail, "grayscale")
        app.logger.info("그레이스케일 이미지 저장 완료")

        # 얼굴 영역 추출
        face_img = extract_face(img)
        if face_img is None:
            app.logger.error("얼굴 영역 추출 실패")
            return jsonify({"status": "failure", "message": "No face detected."})
        app.logger.info("얼굴 영역 추출 완료")

        # 얼굴 영역 이미지 저장
        save_image(face_img, "./register/face", userEmail, "face")
        app.logger.info("얼굴 영역 이미지 저장 완료")

        # 얼굴 임베딩을 위한 정규화
        normalized_face = normalize_image(face_img)
        app.logger.info("이미지 정규화 완료")

        # 정규화된 이미지 저장
        save_image((normalized_face * 255).astype(np.uint8), "./register/normalized", userEmail, "normalized")
        app.logger.info("정규화된 이미지 저장 완료")

        # 얼굴 임베딩
        embedding = DeepFace.represent(normalized_face, model_name=model_name, enforce_detection=False)[0]["embedding"]
        app.logger.info("얼굴 임베딩 완료")

        # 기존 임베딩 데이터 불러오기
        embeddings = load_embeddings()

        # 새로운 임베딩 데이터 추가
        embeddings[userEmail] = embedding

        # 임베딩 데이터 저장
        save_embeddings(embeddings)
        app.logger.info("임베딩 저장 완료")

        return jsonify({"status": "success", "message": "Registration successful"})

    except Exception as e:
        app.logger.error(f"Error in register_face: {str(e)}")
        return jsonify({"status": "failure", "message": "Registration failed."})
