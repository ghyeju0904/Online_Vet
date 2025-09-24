# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ✅ 크롬 드라이버 실행
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)
    return driver


# ✅ 스크롤 다운 (목록 끝까지 불러오기)
def scroll_to_bottom(driver, target_count=None, step_px=800, pause=0.5):
    last = 0
    while True:
        driver.execute_script(f"window.scrollBy(0,{step_px});")
        time.sleep(pause)

        cur = driver.execute_script("return document.documentElement.scrollHeight")
        if cur == last:
            break
        last = cur

        # 🎯 target_count 지정 시, 원하는 개수만큼 로드되면 멈춤
        if target_count:
            elems = driver.find_elements(By.ID, "video-title")
            if len(elems) >= target_count:
                break


# ✅ 재생목록에서 영상 리스트 추출
def get_videos_from_playlist(driver, playlist_url, max_wait=15, target_count=None):
    driver.get(playlist_url)
    WebDriverWait(driver, max_wait).until(
        EC.presence_of_all_elements_located((By.ID, "video-title"))
    )

    # 📌 전체 스크롤해서 모든 영상 로드
    scroll_to_bottom(driver, target_count=target_count)

    elems = driver.find_elements(By.ID, "video-title")
    videos = []
    for e in elems:
        try:
            title = e.text.strip()
            link = e.get_attribute("href")
            if link and "watch" in link:
                videos.append({"title": title, "url": link})
        except:
            continue

    return videos


# ✅ UI 기반 자막 크롤링
def get_transcript_via_ui(driver, video_url, max_wait=15):
    driver.get(video_url)
    time.sleep(2)

    try:
        # 1) "더보기" 버튼 클릭 (있으면만)
        try:
            more_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "tp-yt-paper-button#expand"))
            )
            more_btn.click()
            time.sleep(1)
        except:
            pass

        # 2) "스크립트" 버튼 클릭
        script_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="primary-button"]/ytd-button-renderer/yt-button-shape/button')
            )
        )
        script_btn.click()
        time.sleep(2)

        # 3) 스크립트 자막 추출 (시간 제외, 내용만 저장)
        captions = driver.find_elements(By.CSS_SELECTOR, "ytd-transcript-segment-renderer")
        transcript_lines = []
        for cap in captions:
            try:
                parts = cap.text.strip().split("\n")
                if len(parts) == 2:
                    text = parts[1]  # [시간, 내용] → 내용만
                else:
                    text = parts[0]
                if text:
                    transcript_lines.append(text)
            except:
                continue

        return "\n".join(transcript_lines)

    except Exception as e:
        print(f"[ERROR] Transcript fetch failed for {video_url}: {e}")
        return ""
