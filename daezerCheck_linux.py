#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import getpass
import time
# import request

import smtplib
import pickle
import ssl
from email.mime.text import MIMEText # 본문내용을 전송할 때 사용되는 모듈
from email.mime.multipart import MIMEMultipart # 메시지를 보낼 때 메시지에 대한 모듈

def selenium_driver():
    # options = webdriver.ChromeOptions()
    # options.add_argument('window-size=1920x1080')
    # options.add_argument('disable-gpu')
    # options.add_experimental_option('excludeSwitches', ['enable-logging'])

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent={0}'.format(user_agent))
    driver = webdriver.Chrome('./chromedriver', options=options)

    # driver = webdriver.Chrome('./chromedriver', options=options)
    driver.implicitly_wait(30)

    return driver


if __name__ == "__main__":
    url = 'https://www.daezer.com/reserve/index.html?Kind=sun'

    # SMTP 접속을 위한 서버, 계정 설정 (naver)
    SMTP_SERVER = "smtp.naver.com"
    SMTP_PORT = 587

    # 발신자 주소, 비밀번호
    # 비밀번호는 보안을 위해 pickle 파일로 저장하여 가져오면 좋음
    SMTP_USER = "[E-MAIL]"
    SMTP_PASSWORD = "[PASSWORD]"

    # 수신자 주소
    addr = "[E-MAIL]"

    msg = MIMEMultipart("alternative")
    msg["From"] = SMTP_USER  # 발신자
    msg["To"] = addr  # 수신자

    try:
        driver = selenium_driver()
        driver.get(url)

        while True:
            # 가는날 지정(5/3)
            driver.find_element(By.XPATH, "//*[@id='Start_Cal1']").click()
            driver.find_element(By.CLASS_NAME, "ml10").click()
            driver.find_element(By.XPATH, "//*[@id='v3']").click()

            # 오는날 지정(5/7)
            driver.find_element(By.XPATH, "//*[@id='x6']").click()

            # 일자 선택 완료
            driver.find_element(By.XPATH, "//*[@id='calenda_clo02']/img").click()

            # 승선 인원 선택(1명)
            driver.find_element(By.ID, 'Adult').send_keys(1)

            time.sleep(10)

            # 테이블 값 처리
            table = driver.find_element(By.XPATH, "//*[@id='schedule2']/table/tbody")
            tr = table.find_elements(By.TAG_NAME, "tr")

            # 잔여석 합계(시간대 파악 후 합)
            remainSeat = 0
            for chk in range(len(tr)):
                seat = driver.find_element(By.XPATH, f"//*[@id='schedule2_list{chk+1}']/td[5]").text
                remainSeat = remainSeat + int(seat)

            # 잔여석 발생시 메일 발송
            if remainSeat > 0:
                msg["Subject"] = '[대저해운] 5월 7일자 잔여석 발생 알림'  # 메일 제목
                sendTxt = "\n[대저해운]\n\n울릉도 -> 포항\n5월 7일자 잔여석 발생 알림\n\n 잔여석: " + str(remainSeat) + "\n\n빠른 이동을 위한 링쿠 : https://www.daezer.com/reserve/index.html?Kind=sun\n\n"
                msg.attach(MIMEText(sendTxt))
                # smtp로 접속할 서버 정보를 가진 클래스변수 생성
                smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                smtp.ehlo
                smtp.starttls()
                # 해당 서버로 로그인
                smtp.login(SMTP_USER, SMTP_PASSWORD)
                # 메일 발송
                smtp.sendmail(SMTP_USER, addr, msg.as_string())
                # 닫기
                smtp.close()

            print(remainSeat)

            time.sleep(10)
            driver.refresh()

    except Exception as e:
        msg["Subject"] = '[error] 대저해운 알리미 오류안내'  # 메일 제목
        sendTxt = "\n[error]\n\n오류났으니 고치거라\n\n error msg:\n" + str(e)
        msg.attach(MIMEText(sendTxt))
        # smtp로 접속할 서버 정보를 가진 클래스변수 생성
        smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp.ehlo
        smtp.starttls()
        # 해당 서버로 로그인
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        # 메일 발송
        smtp.sendmail(SMTP_USER, addr, msg.as_string())
        # 닫기
        smtp.close()
