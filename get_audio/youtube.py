import os
import time
from pytube import YouTube
from faster_whisper import WhisperModel
from audio_to_text.audio_textLizer import Audio_textlizer

# OpenMP 환경 변수 설정
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

model = WhisperModel("base", device="cpu")


# 유튜브에서 오디오를 다운로드하는 함수
def get_audio_from_youtube(url):
    output_path = './tmp/audio'
    try:
        yt = YouTube(url)
        # 스트림에서 오디오 스트림 선택
        audio_stream = yt.streams.filter(only_audio=True).first()

        # 오디오 다운로드
        audio_file = audio_stream.download(output_path=output_path)
        print(f"Audio downloaded successfully: {audio_file}")
        return audio_file

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


#
# # 유튜브 링크와 출력 경로 설정
# youtube_url = 'https://www.youtube.com/watch?v=bbcr06F_PLM&t=8s'
#
#
# # 출력 경로가 존재하지 않으면 생성
# if not os.path.exists(output_path):
#     os.makedirs(output_path)
#
# # 시작 시간 기록
# start_time = time.time()
#
# # 오디오 다운로드
# audio_path = get_audio_from_youtube(youtube_url, output_path)
#
#
# if audio_path:
#     # 오디오를 텍스트로 변환
#     audio_textlizer = Audio_textlizer(model)
#     segments, info = audio_textlizer.textlize(audio_path)
#
#     # 결과 텍스트를 한 문자열로 결합
#     full_text = "\n".join([segment.text for segment in segments])
#
#
#     print("텍스트  : ", full_text)
#
#     # 다운로드한 오디오 파일 삭제
#     os.remove(audio_path)
#     print(f"Audio file {audio_path} deleted successfully.")
# else:
#     print("Failed to download audio.")
#
# # 종료 시간 기록
# end_time = time.time()
# total_time = end_time - start_time
# print(f"Total execution time: {total_time} seconds")
