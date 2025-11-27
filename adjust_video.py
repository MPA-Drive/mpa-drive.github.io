#!/usr/bin/env python3
"""
Script to re-encode video_{scene_id}.mp4 files to match the format of teaser.mp4.
This converts MPEG-4 part 2 videos to H.264 format with consistent settings.
"""

import os
import subprocess
import glob
from pathlib import Path

def get_video_info(video_path):
    """Get video codec information using ffprobe."""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0', 
             '-show_entries', 'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1',
             video_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting info for {video_path}: {e}")
        return None

def convert_video(input_path, output_path):
    """
    Convert video to H.264 format matching teaser.mp4 specs:
    - Video codec: H.264 (libx264)
    - Profile: High
    - Pixel format: yuv420p
    - Color space: bt709
    - CRF: 23 (good quality, reasonable file size)
    """
    try:
        cmd = [
            'ffmpeg', '-i', input_path,
            '-c:v', 'libx264',          # H.264 codec
            '-profile:v', 'high',        # High profile
            '-pix_fmt', 'yuv420p',       # Pixel format
            '-colorspace', 'bt709',      # Color space
            '-color_primaries', 'bt709',
            '-color_trc', 'bt709',
            '-crf', '23',                # Quality setting (lower = better quality)
            '-preset', 'medium',         # Encoding speed/compression tradeoff
            '-movflags', '+faststart',   # Enable streaming
            '-y',                        # Overwrite output file
            output_path
        ]
        
        print(f"Converting: {os.path.basename(input_path)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✓ Successfully converted: {os.path.basename(input_path)}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error converting {input_path}: {e}")
        print(f"stderr: {e.stderr}")
        return False

def main():
    # Directory containing videos
    video_dir = Path('./static/videos')
    
    # Find all video_{scene_id}.mp4 files
    video_pattern = str(video_dir / 'video_0446.mp4')
    video_files = sorted(glob.glob(video_pattern))
    
    if not video_files:
        print("No video_{scene_id}.mp4 files found!")
        return
    
    print(f"Found {len(video_files)} video files to process\n")
    
    # Check if ffmpeg is available
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: ffmpeg is not installed or not in PATH")
        print("Please install ffmpeg: brew install ffmpeg")
        return
    
    # Process each video
    success_count = 0
    skip_count = 0
    
    for video_path in video_files:
        # Check current codec
        codec = get_video_info(video_path)
        
        if codec == 'h264':
            print(f"⊙ Skipping {os.path.basename(video_path)} (already H.264)")
            skip_count += 1
            continue
        
        print(f"Current codec: {codec}")
        
        # Create temporary output path
        temp_output = video_path.replace('.mp4', '_temp.mp4')
        
        # Convert video
        if convert_video(video_path, temp_output):
            # Replace original with converted version
            os.replace(temp_output, video_path)
            success_count += 1
        else:
            # Clean up temp file if conversion failed
            if os.path.exists(temp_output):
                os.remove(temp_output)
        
        print()  # Empty line for readability
    
    print("\n" + "="*50)
    print(f"Conversion complete!")
    print(f"  Successfully converted: {success_count}")
    print(f"  Skipped (already H.264): {skip_count}")
    print(f"  Failed: {len(video_files) - success_count - skip_count}")
    print("="*50)

if __name__ == '__main__':
    main()
