# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
import time

from fetch import setup_driver, scroll_to_bottom


# ✅ 재생목록에서 영상 정보 추출
def get_videos_from_playlist(playlist_url, wait_sec=12):
    driver = setup_driver()
    driver.get(playlist_url)

    WebDriverWait(driver, wait_sec).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ytd-playlist-video-renderer"))
    )

    scroll_to_bottom(driver)

    videos = []
    elems = driver.find_elements(By.CSS_SELECTOR, "ytd-playlist-video-renderer")

    for e in elems:
        try:
            title = e.find_element(By.ID, "video-title").text.strip()
            link = e.find_element(By.ID, "video-title").get_attribute("href")
            videos.append({"title": title, "url": link})
        except:
            continue

    driver.quit()
    return videos


# ✅ 유튜브 영상 ID 추출
def extract_video_id(url):
    query = parse_qs(urlparse(url).query)
    return query.get("v", [None])[0]


# ✅ 영상 자막 추출
def get_transcript(video_url, lang="ko"):
    vid = extract_video_id(video_url)
    if not vid:
        return None
    try:
        transcript = YouTubeTranscriptApi.get_transcript(vid, languages=[lang, "en"])
        return " ".join([entry["text"] for entry in transcript if entry["text"].strip()])
    except Exception as e:
        print(f"[WARN] Transcript not available for {video_url}: {e}")
        return None
