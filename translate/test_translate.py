from translate import Translator

translator = Translator()

text = """
The Windows Search protocol is a Uniform Resource Identifier (URI) that enables applications to open 
Windows Explorer to perform searches using specific parameters.

While most Windows searches will look at the local device's index, it is also possible to force 
Windows Search to query file shares on remote hosts and use a custom title for the search window.
"""

translated_text = translator.translate(text)

# 일정 길이마다 출력하는 함수
def print_with_spaces(text, length=40):
    for i in range(0, len(text), length):
        print(text[i:i+length])

# 번역된 텍스트 출력
print_with_spaces(translated_text)

