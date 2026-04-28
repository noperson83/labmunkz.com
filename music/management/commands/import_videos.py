"""
Django Management Command: Import existing filesystem videos into database
Save as: music/management/commands/import_videos.py

Usage:
    python manage.py import_videos
    python manage.py import_videos --dry-run
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File
from music.models import Video
import os


class Command(BaseCommand):
    help = 'Import existing video files from /media/videos/ into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('=== DRY RUN MODE - No changes will be made ===\n'))
        
        video_folder = os.path.join(settings.MEDIA_ROOT, 'videos')
        
        if not os.path.exists(video_folder):
            self.stdout.write(self.style.ERROR(f'Video folder not found: {video_folder}'))
            return
        
        # Get all video files
        video_files = [
            f for f in os.listdir(video_folder)
            if os.path.isfile(os.path.join(video_folder, f))
            and f.lower().endswith(('.mp4', '.mov', '.webm', '.ogg'))
        ]
        
        if not video_files:
            self.stdout.write(self.style.WARNING('No video files found in folder'))
            return
        
        self.stdout.write(f'Found {len(video_files)} video files\n')
        
        imported_count = 0
        skipped_count = 0
        error_count = 0
        
        for video_file in sorted(video_files):
            video_path = os.path.join(video_folder, video_file)
            
            # Generate title from filename
            title = os.path.splitext(video_file)[0]
            title = title.replace('_', ' ').replace('-', ' ').title()
            
            # Check if already imported (by checking if video_file path exists)
            existing = Video.objects.filter(video_file__icontains=video_file).first()
            
            if existing:
                self.stdout.write(f'  ⊘ Skipping: {video_file} (already in database as "{existing.title}")')
                skipped_count += 1
                continue
            
            if dry_run:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Would import: {video_file} as "{title}"'))
                imported_count += 1
                continue
            
            # Create the video entry
            try:
                # We need to reference the existing file without moving it
                # The file is already at /media/videos/filename.mp4
                video = Video(
                    title=title,
                    video_file=f'videos/{video_file}'  # Relative path from MEDIA_ROOT
                )
                video.save()
                
                self.stdout.write(self.style.SUCCESS(f'  ✓ Imported: {video_file} as "{title}"'))
                imported_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error importing {video_file}: {str(e)}'))
                error_count += 1
        
        # Summary
        self.stdout.write('\n' + '='*50)
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'DRY RUN: Would import {imported_count} videos'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully imported: {imported_count}'))
        
        self.stdout.write(f'Skipped (already exists): {skipped_count}')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'Errors: {error_count}'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nRun without --dry-run to actually import the videos'))
