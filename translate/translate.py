import torch
from langdetect import detect
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

#facebook/nllb-200-distilled-600M
#        self.tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
#        self.model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
class Translator:
    def __init__(self, model , tokenizer):
        # 모델과 토크나이저 로드
        self.tokenizer = tokenizer
        self.model = model
        self.lang_code_map = {
            'af': 'afr_Latn',
            'ar': 'arb_Arab',
            'bn': 'ben_Beng',
            'en': 'eng_Latn',
            'es': 'spa_Latn',
            'fr': 'fra_Latn',
            'hi': 'hin_Deva',
            'id': 'ind_Latn',
            'ja': 'jpn_Jpan',
            'ko': 'kor_Hang',
            'pt': 'por_Latn',
            'ru': 'rus_Cyrl',
            'ta': 'tam_Taml',
            'te': 'tel_Telu',
            'zh-cn': 'zho_Hans',
        }

    def detect_lang(self, text):
        # 입력 텍스트의 언어 감지
        detected_lang = detect(text)
        src_lang = self.lang_code_map.get(detected_lang, 'eng_Latn')  # 감지된 언어의 코드 가져오기, 기본값 영어
        return src_lang

    def translate(self, text):
        # 입력 텍스트 토큰화
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)

        # 대상 언어 코드 가져오기
        tgt_lang_id = self.tokenizer.convert_tokens_to_ids(self.lang_code_map['ko'])

        # 모델을 사용하여 번역 수행( 필요없는 연산 제외 )
        with torch.no_grad():
            outputs = self.model.generate(**inputs, forced_bos_token_id=tgt_lang_id)

        # 번역된 텍스트 디코딩
        translated_text = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        return translated_text


