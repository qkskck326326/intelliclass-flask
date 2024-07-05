import os
import requests
import whisper
from flask import request, jsonify
from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration
# from oracle_db import OracleDB
from db.db_connect import OracleDB

# Whisper 모델 로드
whisper_model = whisper.load_model("base")

# BART 모델 로드 (한국어 요약)
tokenizer = PreTrainedTokenizerFast.from_pretrained('gogamza/kobart-base-v2')
bart_model = BartForConditionalGeneration.from_pretrained('gogamza/kobart-summarization')

# FFmpeg 경로 설정
ffmpeg_path = os.path.join(os.path.dirname(__file__), '../ffmpeg', 'bin')
os.environ["PATH"] += os.pathsep + ffmpeg_path

def get_video_url_from_db(lecture_id):
    db = OracleDB()
    db.connect()
    try:
        cursor = db.connection.cursor()
        cursor.execute("SELECT STREAM_URL FROM TB_LECTURE WHERE LECTURE_ID = :lecture_id", {'lecture_id': lecture_id})
        row = cursor.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(f"Error fetching video URL from DB: {e}")
        return None
    finally:
        db.close()

def video_url():
    lecture_id = request.args.get('lecture_id')
    video_url = get_video_url_from_db(lecture_id)
    if not video_url:
        return jsonify({"error": "Video URL not found"}), 404
    return jsonify({"video_url": video_url})

def transcribe():
    video_url = request.args.get('video_url')
    local_filename = "downloaded_audio.mp4"

    download_file(video_url, local_filename)

    if not os.path.exists(local_filename):
        return jsonify({"error": "Downloaded file not found"}), 500

    try:
        result = whisper_model.transcribe(local_filename)
        transcript = result["text"]
    except Exception as e:
        return jsonify({"error": f"Error transcribing audio: {e}"}), 500

    summary = summarize_text(transcript)

    os.remove(local_filename)

    return jsonify({
        "transcript": transcript,
        "summary": summary
    })

def summarize_text(text):
    inputs = tokenizer([text], max_length=1024, return_tensors='pt')
    summary_ids = bart_model.generate(inputs['input_ids'], max_length=150, min_length=40, length_penalty=2.0,
                                      num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
