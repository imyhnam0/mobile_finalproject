"""
Send fall event to Django service.
"""
from datetime import datetime
import requests
import traceback

SERVER_URL = "http://localhost:8000/api/fall-events/"


def send_fall_event(image_path, room="living_room"):
    import os
    
    # Check if image file exists
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        return False
    
    file_size = os.path.getsize(image_path)
    print(f"[업로드 시도] 이미지 전송 시작: {image_path} ({file_size} bytes)")
    print(f"[업로드 시도] 서버 URL: {SERVER_URL}")
    
    try:
        with open(image_path, "rb") as f:
            files = {"image": (os.path.basename(image_path), f, "image/jpeg")}
            data = {
                "location": room,
                "description": "Fall detected in living room",
                "occurred_at": datetime.utcnow().isoformat(),
            }
            
            print(f"[업로드 시도] 데이터: location={room}, occurred_at={data['occurred_at']}")
            resp = requests.post(SERVER_URL, files=files, data=data, timeout=10)
            
            print(f"[서버 응답] 상태 코드: {resp.status_code}")
            print(f"[서버 응답] 응답 내용: {resp.text[:200]}")  # 처음 200자만 출력
            
            resp.raise_for_status()
            result = resp.json()
            print("[업로드 성공] 서버에 이미지 전송 완료:", result)
            if result.get("image_url"):
                print(f"[업로드 성공] 이미지 URL: {result['image_url']}")
            else:
                print("[경고] 응답에 image_url이 없습니다")
            return True
            
    except requests.exceptions.ConnectionError as e:
        print(f"[업로드 실패] 서버 연결 실패: {SERVER_URL}")
        print(f"[업로드 실패] 서버가 실행 중인지 확인하세요: {e}")
        traceback.print_exc()
        return False
    except requests.exceptions.Timeout as e:
        print(f"[업로드 실패] 서버 응답 시간 초과: {e}")
        traceback.print_exc()
        return False
    except requests.exceptions.HTTPError as e:
        print(f"[업로드 실패] HTTP 에러: {e}")
        print(f"[업로드 실패] 응답 상태 코드: {e.response.status_code if e.response else 'N/A'}")
        if e.response:
            print(f"[업로드 실패] 응답 내용: {e.response.text[:500]}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"[업로드 실패] 예상치 못한 에러: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False
