import os
import json
import asyncio
import edge_tts
import math
import subprocess
from mutagen.mp3 import MP3

# --- CONFIGURATION ---
VOICE = "en-US-ChristopherNeural"
OUTPUT_AUDIO = "temp/voice_01.mp3"
OUTPUT_SUBS = "temp/subs_01.srt"
SCRIPT_TEXT = "This is a test of the automated media engine. Voice leads, visuals follow. The system is online."
FPS = 30
BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"

async def generate_audio_and_subs():
    print(f"🎙️ Generating voiceover and subtitles...")
    communicate = edge_tts.Communicate(SCRIPT_TEXT, VOICE)
    submaker = edge_tts.SubMaker()
    
    with open(OUTPUT_AUDIO, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)
                
    with open(OUTPUT_SUBS, "w", encoding="utf-8") as file:
        file.write(submaker.get_srt())
        
    print(f"✅ Audio and Subtitles generated.")

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
    
    # Locate the FFmpeg engine we dropped in the main folder
    ffmpeg_exe = os.path.abspath("ffmpeg.exe")
    if not os.path.exists(ffmpeg_exe):
        ffmpeg_exe = "ffmpeg" # Fallback to system path
    
    # 👈 THE CWD CHEAT CODE
    # Because we run this FROM the 'temp' folder, there are NO paths in the subtitle filter!
    ffmpeg_cmd = [
        ffmpeg_exe, "-y", 
        "-framerate", str(FPS),
        "-i", "frames/%04d.png", 
        "-i", "voice_01.mp3", 
        "-vf", "subtitles=subs_01.srt:force_style='Fontname=Arial,Fontsize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2'", 
        "-c:v", "libx264", 
        "-pix_fmt", "yuv420p", 
        "-c:a", "aac", 
        "-shortest",
        "../output/final_video.mp4" # Output gets pushed UP one level into /output
    ]
    
    # Execute the command specifically inside the "temp" directory
    subprocess.run(ffmpeg_cmd, cwd="temp", check=True)
    
    print("-----------------------------------------------------")
    print("🎉 BOOM! FINAL VIDEO SAVED TO: output/final_video.mp4")
    print("-----------------------------------------------------")

async def main():
    os.makedirs("temp", exist_ok=True)
    await generate_audio_and_subs()
    update_scene_json(OUTPUT_AUDIO)
    run_blender_engine()
    assemble_final_video()

if __name__ == "__main__":
    asyncio.run(main())