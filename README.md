# intelliclass-flask

Get from Version Control에서

https://github.com/qkskck326326/intelliclass-flask.git  <<<  레포지토리 주소입력하고

자동으로 나오는 Directory 말고 새로 폴더 만들어서 거기에 프로젝트 클론받는걸 추천

인텔리클래스 파이썬 프로젝트

프로젝트 클론받고 파이썬 인터프리터 3.12 확인!!!

.venv 폴더 만들어졌는지 확인!!

파이참 터미널에서 명령어 수행하세요.

필요한 모듈 설치: pip install -r requirements.txt

디렉토리 생성: New-Item -ItemType Directory -Path "$HOME\.aws"

S3 자격 증명 파일 생성: New-Item -ItemType File -Path "$HOME\.aws\credentials"

S3 자격 증명 파일 편집: notepad "$HOME\.aws\credentials"

메모장이 뜨면

[default]

aws_access_key_id = 액세스키

aws_secret_access_key = 시크릿 액세스키

입력하고 저장하세요.
