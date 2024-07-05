from flask import request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from webdriver_manager.chrome import ChromeDriverManager
import time

def verify_certificate():
    data = request.json
    name = data.get('name')
    managementNumber = data.get('managementNumber')

    if not name or not managementNumber:
        return jsonify({'error': 'Name and Management Number are required'}), 400

    # 브라우저 설정 및 자동화
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 10)  # 최대 10초 대기

    try:
        driver.get("https://www.q-net.or.kr/qlf006.do?id=qlf00601&gSite=Q&gId=")

        # 드롭다운 선택
        select_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#content > div.content > form:nth-child(2) > div.tbl_normal.nmlType3 > table > tbody > tr:nth-child(1) > td > select')))
        select = Select(select_element)
        select.select_by_visible_text('상장형 자격증')

        # 입력 필드 채우기
        name_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#hgulNm2')))
        name_input.send_keys(name)

        parts = managementNumber.split('-08-')
        if len(parts) != 2:
            raise ValueError("관리 번호 형식이 잘못되었습니다. 형식은 'XXXX-08-XXXX'이어야 합니다.")

        hrdNo1_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#hrdNo1')))
        hrdNo1_input.send_keys(parts[0])

        hrdNo2_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#hrdNo2')))
        hrdNo2_input.send_keys(parts[1])

        # 버튼 클릭
        submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#content > div.content > form:nth-child(2) > div.tbl_normal.nmlType3 > div.btn_center > button.btn2.btncolor2 > span')))
        submit_button.click()

        # 새 창으로 전환
        time.sleep(5)  # 새 창이 뜰 시간을 줍니다.
        driver.switch_to.window(driver.window_handles[1])

        # 알림 창 처리
        try:
            alert = Alert(driver)
            alert_text = alert.text
            alert.accept()
            return jsonify({'result': 'fail', 'message': alert_text})
        except:
            pass

        # 이미지 확인
        try:
            image_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'img')))
            if image_element:
                return jsonify({'result': 'success', 'message': '진위확인이 완료되었습니다.'})
        except:
            pass

        return jsonify({'result': 'fail', 'message': '진위확인이 되지않습니다.'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        driver.quit()
