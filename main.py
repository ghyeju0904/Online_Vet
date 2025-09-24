# -*- coding: utf-8 -*-  # 한글 깨짐 방지 (UTF-8 인코딩)

import csv
import json
import os
from fetch import setup_driver, get_videos_from_playlist, get_transcript_via_ui

# 🎯 크롤링할 유튜브 재생목록 URL
PLAYLIST_URL = "https://www.youtube.com/playlist?list=PL_ZLO2xx3i2e4HcdJLB66jB0iHgFzqf_4"
OUT_BASE = "youtube_pet_health"  # 저장 파일 이름 앞부분


# ✅ CSV 저장 함수
def save_csv(items, path):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = ["title", "url", "transcript"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in items:
            w.writerow({
                "title": row.get("title"),
                "url": row.get("url"),
                "transcript": row.get("transcript", "")
            })


# ✅ JSON 저장 함수
def save_json(items, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"videos": items}, f, ensure_ascii=False, indent=2)


# ✅ 메인 실행부
if __name__ == "__main__":
    driver = setup_driver()

    # 1) 🎬 재생목록에서 영상 129개 전부 가져오기
    videos = get_videos_from_playlist(driver, PLAYLIST_URL, target_count=129)
    print(f"[INFO] 재생목록에서 {len(videos)}개 영상 발견")

    # 2) 각 영상 자막 수집
    for v in videos:
        transcript = get_transcript_via_ui(driver, v["url"])
        v["transcript"] = transcript if transcript else ""
        print(f"[INFO] {v['title']} | 자막 {'있음' if transcript else '없음'}")

    driver.quit()

    # 3) 저장할 파일 경로
    csv_path = os.path.abspath(f"{OUT_BASE}.csv")
    json_path = os.path.abspath(f"{OUT_BASE}.json")

    # 4) CSV & JSON 저장
    save_csv(videos, csv_path)
    save_json(videos, json_path)

    # 5) 완료 메시지
    print(f"[DONE] {len(videos)}개 저장 | CSV: {csv_path} | JSON: {json_path}")
