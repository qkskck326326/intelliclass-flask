import torch

class Audio_textlizer:
    def __init__(self, whisper):
        self.whisper = whisper

    def textlize(self, audio_path):
        with torch.no_grad():
            texts, info = self.whisper.transcribe(audio_path, beam_size=5)
        return texts, info

