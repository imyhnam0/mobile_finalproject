"""
과거에 저장된 이미지 중 서버에 업로드되지 않은 것들을 업로드하는 스크립트
"""
import os
import sys
from sender import send_fall_event

SAVE_DIR = "captured"


def upload_missing_images():
    """captured 디렉토리의 모든 fall 이미지를 찾아 서버에 업로드"""
    
    if not os.path.exists(SAVE_DIR):
        print(f"경고: {SAVE_DIR} 디렉토리가 존재하지 않습니다.")
        return
    
    # 모든 fall 이미지 찾기 (pre_fall 디렉토리 제외)
    fall_images = []
    for filename in os.listdir(SAVE_DIR):
        if filename.endswith("_fall.jpg") and os.path.isfile(os.path.join(SAVE_DIR, filename)):
            fall_images.append(os.path.join(SAVE_DIR, filename))
    
    if not fall_images:
        print(f"{SAVE_DIR} 디렉토리에 fall 이미지가 없습니다.")
        return
    
    print(f"총 {len(fall_images)}개의 fall 이미지를 찾았습니다.\n")
    
    success_count = 0
    fail_count = 0
    
    for image_path in sorted(fall_images):
        print(f"\n{'='*60}")
        print(f"업로드 중: {os.path.basename(image_path)}")
        print(f"{'='*60}")
        
        success = send_fall_event(image_path, room="living_room")
        
        if success:
            success_count += 1
            print(f"✅ 성공: {os.path.basename(image_path)}")
        else:
            fail_count += 1
            print(f"❌ 실패: {os.path.basename(image_path)}")
    
    print(f"\n{'='*60}")
    print(f"업로드 완료: 성공 {success_count}개, 실패 {fail_count}개")
    print(f"{'='*60}")


if __name__ == "__main__":
    try:
        upload_missing_images()
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n에러 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
