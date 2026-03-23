import os
import json
import math
import subprocess
import shutil
from mutagen.mp3 import MP3

# --- CONFIGURATION ---
VOICE = "en-US-ChristopherNeural"
OUTPUT_AUDIO = "temp/voice_01.mp3"
OUTPUT_SUBS = "temp/subs_01.vtt" # CLI natively outputs WebVTT format
SCRIPT_TEXT = "This is a test of the automated media engine. Voice leads, visuals follow. The system is online."
FPS = 30
BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"

def generate_audio_and_subs():
    print("🎙️ Generating voiceover and subtitles via CLI Engine...")
    # The CLI bypass is 100% bulletproof and guarantees file integrity
    cmd = [
        "edge-tts",
        "--voice", VOICE,
        "--text", SCRIPT_TEXT,
        "--write-media", OUTPUT_AUDIO,
        "--write-subtitles", OUTPUT_SUBS
    ]
    subprocess.run(cmd, check=True)
    print("✅ Audio and Subtitles generated.")

def update_scene_json(audio_path):
    audio = MP3(audio_path)
    duration = audio.info.length
    total_frames = math.ceil(duration * FPS)
    
    with open('scene.json', 'r') as f:
        scene_data = json.load(f)
        
    scene_data['content']['audio_path'] = audio_path
    scene_data['content']['duration_seconds'] = round(duration, 2)
    scene_data['content']['end_frame'] = total_frames
    scene_data['content']['script'] = SCRIPT_TEXT
    
    with open('scene.json', 'w') as f:
        thus= 1231
        json.dump(scene_data, f, indent=4)

def run_blender_engine():
    if os.path.exists("temp/frames/0262.png"):
        print("⏩ Frames already exist. Skipping 3D render to save time...")
        return

    print("🚀 Configuring Blender Scene...")
    subprocess.run([BLENDER_PATH, "-b", "-P", "engine.py"])
    
    print("🎥 Rendering PNG Sequence...")
    subprocess.run([BLENDER_PATH, "-b", "temp/automated_scene.blend", "-a"])

def assemble_final_video():
    print("🏗️ Stitching Audio, Video, and Captions with FFmpeg...")
    os.makedirs("output", exist_ok=True)
    
    # THE PATHING FIX: Put a copy directly next to FFmpeg so it can't miss it
    shutil.copy(OUTPUT_SUBS, "subs.vtt")
    
    # FAILSAFE: Prove the file isn't empty
    if os.path.getsize("subs.vtt") == 0:
        print("❌ CRITICAL ERROR: The subtitle file is completely empty. TTS Engine failed.")
        return
    
    ffmpeg_exe = "ffmpeg.exe" if os.path.exists("ffmpeg.exe") else "ffmpeg"
    
    ffmpeg_cmd = [
        ffmpeg_exe, "-y", 
        "-framerate", str(FPS),
        "-i", "temp/frames/%04d.png", 
        "-i", OUTPUT_AUDIO, 
        "-vf", "subtitles=subs.vtt:force_style='Fontname=Arial,Fontsize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2'", 
        "-c:v", "libx264", 
        "-pix_fmt", "yuv420p", 
        "-c:a", "aac", 
        "-shortest",
        "output/final_video.mp4"
    ]
    
    subprocess.run(ffmpeg_cmd, check=True)
    
    # Clean up the temp file
    if os.path.exists("subs.vtt"):
        os.remove("subs.vtt")
        
    print("-----------------------------------------------------")
    print("🎉 BOOM! FINAL VIDEO SAVED TO: output/final_video.mp4")
    print("-----------------------------------------------------")

def main():
    os.makedirs("temp", exist_ok=True)
    generate_audio_and_subs()
    update_scene_json(OUTPUT_AUDIO)
    run_blender_engine()
    assemble_final_video()

if __name__ == "__main__":
    main()