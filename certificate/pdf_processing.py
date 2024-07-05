from flask import request, jsonify
import fitz  # PyMuPDF
import pdfplumber
import re
import os

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 첫 번째 유형 - certificate.pdf
def extract_text_from_pdf_certificate(pdf_path):
    pdf_document = fitz.open(pdf_path)
    extracted_text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        extracted_text += page.get_text("text") + "\n"
    pdf_document.close()
    return extracted_text

def parse_extracted_text_certificate(extracted_text):
    extracted_text = extracted_text.encode('utf-8').decode('utf-8')
    pattern1 = re.compile(
        r'종\s*목\s*:\s*(.*?)\s*'
        r'자\s*격\s*종\s*류\s*:\s*(.*?)\s*'
        r'자\s*격\s*번\s*호\s*:\s*(.*?)\s*'
        r'성\s*명\s*:\s*(.*?)\s*'
        r'생\s*년\s*월\s*일\s*:\s*(.*?)\s*'
        r'합\s*격\s*일\s*자\s*:\s*(.*?)\s',
        re.DOTALL)
    matches1 = pattern1.findall(extracted_text)
    data_list = []
    if matches1:
        for match in matches1:
            종목 = match[0].strip()
            자격종류 = match[1].strip()
            자격번호 = match[2].strip()
            성명 = match[3].strip()
            생년월일 = match[4].strip()
            합격일자 = match[5].strip()
            발행처 = "한국정보통신진흥협회"  # 발행처 정보가 없으므로 기본값 설정
            data_list.append({
                'kind': 종목,
                'certificateType': 자격종류,
                'certificateNumber': 자격번호,
                'name': 성명,
                'BIRTHDATE': 생년월일,
                'passDate': 합격일자,
                'issuePlace': 발행처
            })
    return data_list

# 두 번째 유형 - information.pdf
def extract_data_from_information_pdf(words):
    data = {
        "managementNumber": "N/A",
        "certificateNumber": "N/A",
        "kind": "N/A",
        "name": "N/A",
        "birthDate": "N/A",
        "passDate": "N/A",
        "issueDate": "N/A",
        "issuePlace": "한국산업인력공단"
    }
    for i, word in enumerate(words):
        if word['text'] == "관리번호:":
            data["managementNumber"] = words[i + 1]['text']
        elif word['text'] == "자격번호:":
            data["certificateNumber"] = words[i + 1]['text']
        elif word['text'] == "자격종목:":
            data["kind"] = words[i + 1]['text']
        elif word['text'] == "성":
            data["name"] = words[i + 2]['text']
        elif word['text'] == "생년월일:":
            data["birthDate"] = convert_date_format(words[i + 1]['text'])
        elif word['text'] == "합격":
            if words[i + 1]['text'] == "연월일:":
                data["passDate"] = convert_date_format(
                    f"{words[i + 2]['text']} {words[i + 3]['text']} {words[i + 4]['text']}")
        elif word['text'] == "발급":
            if words[i + 1]['text'] == "연월일:":
                data["issueDate"] = convert_date_format(
                    f"{words[i + 2]['text']} {words[i + 3]['text']} {words[i + 4]['text']}")
    return data

def convert_date_format(date_str):
    match = re.match(r'(\d{4})년 (\d{2})월 (\d{2})일', date_str)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return date_str

def extract_data_from_pdf_information(file_path):
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        words = page.extract_words()
    return extract_data_from_information_pdf(words)

# 세 번째 유형 - sqld.pdf
def extract_text_from_pdf_sqld(pdf_path):
    extracted_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text += page.extract_text() + "\n"
    return extracted_text

def parse_extracted_text_sqld(extracted_text):
    lines = extracted_text.split('\n')
    data = {
        "kind": "",
        "certificateNumber": "",
        "name": "",
        "BIRTHDATE": "",
        "passDate": "",
        "VALIDITY_PERIOD": "",
        "ISSUE_DATE": "",
        "issuePlace": "한국데이터산업진흥원장"
    }
    for line in lines:
        line = line.strip()
        if '종목 및 등급' in line:
            data['kind'] = line.split(':')[1].strip()
        elif '자 격 번 호' in line:
            data['certificateNumber'] = line.split(':')[1].strip()
        elif '성 명' in line:
            data['name'] = line.split(':')[1].strip()
        elif '생 년 월 일' in line:
            data['BIRTHDATE'] = convert_date_format(line.split(':')[1].strip())
        elif '합 격 일 자' in line:
            data['passDate'] = convert_date_format(line.split(':')[1].strip())
        elif '유 효 기 간' in line:
            data['VALIDITY_PERIOD'] = line.split(':')[1].strip()
            start_date, end_date = data['VALIDITY_PERIOD'].split(' ~ ')
            data[
                'VALIDITY_PERIOD'] = f"{convert_date_format(start_date.strip())} ~ {convert_date_format(end_date.strip())}"
        elif '년' in line and '월' in line and '일' in line and '발행' not in line:
            data['ISSUE_DATE'] = convert_date_format(line.strip())
    return data

def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        try:
            if "certificate.pdf" in file.filename:
                extracted_text = extract_text_from_pdf_certificate(file_path)
                data = parse_extracted_text_certificate(extracted_text)
                os.remove(file_path)  # 임시 파일 삭제
                return jsonify({"data": data}), 200

            elif "information.pdf" in file.filename:
                data = extract_data_from_pdf_information(file_path)
                os.remove(file_path)  # 임시 파일 삭제
                response_data = [{"kind": data["kind"], "certificateNumber": data["certificateNumber"],
                                  "name": data["name"], "BIRTHDATE": data["birthDate"],
                                  "passDate": data["passDate"], "issueDate": data["issueDate"],
                                  "issuePlace": data["issuePlace"], "managementNumber": data["managementNumber"]}]
                return jsonify({"data": response_data}), 200

            elif "sqld.pdf" in file.filename:
                extracted_text = extract_text_from_pdf_sqld(file_path)
                data = parse_extracted_text_sqld(extracted_text)
                os.remove(file_path)  # 임시 파일 삭제
                response_data = [{"kind": data["kind"], "certificateNumber": data["certificateNumber"],
                                  "name": data["name"], "BIRTHDATE": data["BIRTHDATE"],
                                  "passDate": data["passDate"], "VALIDITY_PERIOD": data["VALIDITY_PERIOD"],
                                  "ISSUE_DATE": data["ISSUE_DATE"], "issuePlace": data["issuePlace"]}]
                return jsonify({"data": response_data}), 200

            else:
                return jsonify({"error": "Unknown file format"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
