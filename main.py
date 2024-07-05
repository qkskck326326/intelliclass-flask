from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from face_recognition.register import register_face
from face_recognition.login import login_face
from transcription.transcribe import video_url, transcribe
from certificate.pdf_processing import upload_file
from certificate.verify_certificate import verify_certificate
from open_ai.ai_model import analyze_code_with_ai, analyze_code

import os
import threading
import schedule
import torch
import time
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from faster_whisper import WhisperModel
from audio_to_text.audio_textLizer import Audio_textlizer
from db.db_connect import OracleDB, ITNews
from crowling.crowling import NewsScraper
from translate.translate import Translator
from get_audio.youtube import get_audio_from_youtube


os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Database and models initialization
db = OracleDB()

whisper = WhisperModel("base", device="cpu")

translate_tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
translate_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")

# Class instances
it_news = ITNews(db)
translator = Translator(translate_model, translate_tokenizer)
scraper = NewsScraper(translator)
textlizer = Audio_textlizer(whisper)


app = Flask(__name__)
CORS(app)

# 태석
app.add_url_rule('/register', 'register_face', register_face, methods=['POST']) #  얼굴 등록 엔드포인트
app.add_url_rule('/login', 'login_face', login_face, methods=['POST']) # 얼굴 로그인 엔드포인트

# 경민
app.add_url_rule('/video-url', 'video_url', video_url, methods=['GET']) # 비디오 URL 엔드포인트
app.add_url_rule('/transcribe', 'transcribe', transcribe, methods=['GET']) # 트랜스크립션 엔드포인트

# 채림
app.add_url_rule('/upload', 'upload_file', upload_file, methods=['POST'])  # PDF 업로드 엔드포인트
app.add_url_rule('/verify', 'verify_certificate', verify_certificate, methods=['POST'])  # 자격증 진위 확인 엔드포인트

# 시원
app.add_url_rule('/analyze', 'analyze_code', analyze_code, methods=['POST'])  # 코드 분석 엔드포인트

#건우
def crowling_task():
    site_info_list = it_news.select_site_list()
    total_count = 0

    for site_info in site_info_list:
        try:
            test_url = scraper.parse_homepage(site_info['site_url'], site_info['latest_board_url'])
            count = it_news.search_board(test_url)[0]
            if count > 0:
                print("Already exists")
                continue
            try:
                title, text, url = scraper.scrape(
                    homepage_url=site_info['site_url'],
                    news_link_selector=site_info['latest_board_url'],
                    title_selector=site_info['title_selector'],
                    body_selector=site_info['context_selector']
                )

                text_bytes = text.encode('utf-8', errors='ignore')  # Ignore errors during encoding
                if len(text_bytes) > 3000:
                    text_bytes = text_bytes[:2990]
                    # Ensure no partial multibyte characters at the end
                    while len(text_bytes) > 0 and text_bytes[-1] & 0xC0 == 0x80:
                        text_bytes = text_bytes[:-1]
                    text = text_bytes.decode('utf-8', errors='ignore') + "..."  # Ignore errors during decoding

                # Clean and validate text data
                title = title.replace('\n', ' ').replace('\r', ' ')
                text = text.replace('\n', ' ').replace('\r', ' ')
                url = url.replace('\n', ' ').replace('\r', ' ')

                it_news.insert_board(
                    site_url=site_info['site_url'],
                    board_url=url,
                    title=title,
                    original_context=text
                )
                print(f"Successfully scraped and saved article from {site_info['site_url']}")
                total_count += 1
            except Exception as e:
                print(f"Error scraping {site_info['site_url']}: {e}")
        except Exception as e:
            print(f"Error processing site info for {site_info['site_url']}: {e}")

    print(total_count, "articles have been added.")

def schedule_crowling_task():
    schedule.every(30).minutes.do(crowling_task)  # 30분마다 실행

    while True:
        schedule.run_pending()
        time.sleep(1)

# Schedule the crowling task
threading.Thread(target=schedule_crowling_task, daemon=True).start()

@app.route("/crowling", methods=["GET"])
def crowling_site():
    threading.Thread(target=crowling_task).start()
    return jsonify({"message": "Crawling started in the background"}), 200

@app.route("/crowling/test+url", methods=["POST"])
def test_url():
    data = request.json
    url = data.get("url")
    board_selector = data.get("boardSelector")

    result = scraper.test_lastest_board_selector(url, board_selector)
    print(result)
    return jsonify({"message": result}), 200

@app.route("/crowling/test+title", methods=["POST"])
def test_title():
    data = request.json
    url = data.get("url")
    board_selector = data.get("boardSelector")
    title_selector = data.get("titleSelector")

    result = scraper.test_title_selector(url, board_selector, title_selector)
    print(result)
    return jsonify({"message": result}), 200

@app.route("/crowling/test+context", methods=["POST"])
def test_context():
    data = request.json
    url = data.get("url")
    board_selector = data.get("boardSelector")
    context_selector = data.get("contextSelector")

    result = scraper.test_context_selector(url, board_selector, context_selector)
    print(result)
    return jsonify({"message": result}), 200

@app.route("/getText", methods=["POST"])
def get_text_from_youtube():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    audio_file = get_audio_from_youtube(url)

    with torch.no_grad():
        segments, info = textlizer.textlize(audio_file)

    full_text = "\n".join([segment.text for segment in segments])
    sentences = full_text.split('. ')
    formatted_text = '<br />'.join(sentences)

    os.remove(audio_file)
    response = make_response(formatted_text)
    response.mimetype = "text/html"
    return response

@app.route("/getTranslate", methods=["POST"])
def get_translate():
    data = request.json
    text = data.get('originalText')
    translated_text = translator.translate(text)
    return translated_text



if __name__ == '__main__':
    # 임시 디렉토리가 존재하지 않는 경우 생성
    if not os.path.exists("./temp"):
        os.makedirs("./temp")
    print("Starting Flask server...")

    app.run(host="0.0.0.0", port=5000, debug=True)
