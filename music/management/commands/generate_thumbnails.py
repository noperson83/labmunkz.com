from django.core.management.base import BaseCommand
from django.conf import settings
from music.models import Video
import os
import subprocess


class Command(BaseCommand):
    help = 'Generate thumbnails for all existing videos'

    def handle(self, *args, **options):
        self.generate_filesystem_thumbnails()
        self.generate_database_thumbnails()

    def generate_filesystem_thumbnails(self):
        self.stdout.write(self.style.SUCCESS('\n=== Processing Filesystem Videos ==='))
        
        video_folder = os.path.join(settings.MEDIA_ROOT, 'videos')
        thumb_folder = os.path.join(video_folder, 'thumbnails')
        
        if not os.path.exists(video_folder):
            self.stdout.write(self.style.ERROR(f'Video folder not found: {video_folder}'))
            return
        
        os.makedirs(thumb_folder, exist_ok=True)
        
        video_files = [
            f for f in os.listdir(video_folder)
            if os.path.isfile(os.path.join(video_folder, f))
            and f.lower().endswith(('.mp4', '.mov', '.webm', '.ogg'))
        ]
        
        self.stdout.write(f'Found {len(video_files)} videos')
        
        for video_file in video_files:
            video_path = os.path.join(video_folder, video_file)
            thumb_name = os.path.splitext(video_file)[0] + '_thumb.jpg'
            thumb_path = os.path.join(thumb_folder, thumb_name)
            
            if os.path.exists(thumb_path):
                self.stdout.write(f'  ⊘ Skipping {video_file}')
                continue
            
            try:
                subprocess.run([
                    'ffmpeg',
                    '-i', video_path,
                    '-ss', '00:00:01',
                    '-vframes', '1',
                    '-vf', 'scale=1200:630:force_original_aspect_ratio=decrease',
                    '-q:v', '2',
                    '-y',
                    thumb_path
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
                
                self.stdout.write(self.style.SUCCESS(f'  ✓ {video_file}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ {video_file}: {str(e)}'))

    def generate_database_thumbnails(self):
        self.stdout.write(self.style.SUCCESS('\n=== Processing Database Videos ==='))
        
        videos = Video.objects.filter(thumbnail='')
        
        for video in videos:
            if video.generate_thumbnail():
                self.stdout.write(self.style.SUCCESS(f'  ✓ {video.title}'))
            else:
                self.stdout.write(self.style.ERROR(f'  ✗ {video.title}'))