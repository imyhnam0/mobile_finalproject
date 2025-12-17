"""
1년 이상 된 낙상 이벤트 데이터를 자동으로 삭제하는 관리 명령어

사용법:
    python manage.py cleanup_old_fall_events

옵션:
    --dry-run: 실제로 삭제하지 않고 삭제될 항목만 표시
    --days: 삭제할 데이터의 최소 기간 (기본값: 365일)
    --verbose: 상세한 정보 출력

예시:
    python manage.py cleanup_old_fall_events
    python manage.py cleanup_old_fall_events --dry-run
    python manage.py cleanup_old_fall_events --days=180  # 6개월 이상 된 데이터 삭제
"""
import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from fall_service.falls.models import FallEvent


class Command(BaseCommand):
    help = '1년 이상 된 낙상 이벤트 데이터를 자동으로 삭제합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='실제로 삭제하지 않고 삭제될 항목만 표시합니다.',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='삭제할 데이터의 최소 기간 (일 수, 기본값: 365)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='상세한 정보를 출력합니다.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days = options['days']
        verbose = options['verbose']
        
        # 1년 이상 된 데이터 찾기 (occurred_at 기준)
        cutoff_date = timezone.now() - timedelta(days=days)
        
        old_events = FallEvent.objects.filter(occurred_at__lt=cutoff_date)
        count = old_events.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'{days}일 이상 된 낙상 이벤트가 없습니다.'
                )
            )
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] {days}일 이상 된 낙상 이벤트 {count}개가 삭제 대상입니다.'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    f'기준 날짜: {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")} 이전'
                )
            )
            
            if verbose:
                self.stdout.write('\n삭제될 이벤트 목록:')
                for event in old_events[:10]:  # 최대 10개만 표시
                    self.stdout.write(
                        f'  - ID: {event.id}, 발생일시: {event.occurred_at}, '
                        f'위치: {event.location}'
                    )
                if count > 10:
                    self.stdout.write(f'  ... 외 {count - 10}개')
        else:
            # 이미지 파일도 함께 삭제하기 위해 먼저 파일 경로 저장
            deleted_files = []
            for event in old_events:
                if event.image:
                    try:
                        file_path = event.image.path
                        if os.path.exists(file_path):
                            deleted_files.append(file_path)
                    except:
                        pass
            
            # 데이터베이스에서 이벤트 삭제
            deleted_count = old_events.delete()[0]
            
            # 이미지 파일 삭제
            deleted_file_count = 0
            for file_path in deleted_files:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        deleted_file_count += 1
                        if verbose:
                            self.stdout.write(f'  파일 삭제: {file_path}')
                except Exception as e:
                    if verbose:
                        self.stdout.write(
                            self.style.ERROR(f'  파일 삭제 실패: {file_path} - {e}')
                        )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ {deleted_count}개의 낙상 이벤트가 삭제되었습니다.'
                )
            )
            if deleted_file_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ {deleted_file_count}개의 이미지 파일이 삭제되었습니다.'
                    )
                )
