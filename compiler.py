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
OUTPUT_SUBS = "temp/subs_01.vtt" # WebVTT subtitle format
SCRIPT_TEXT = "This is a test of the automated media engine. Voice leads, visuals follow. The system is online."
FPS = 30
BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" # Your exact path

async def generate_audio_and_subs():
    print(f"🎙️ Generating voiceover and subtitles...")
    communicate = edge_tts.Communicate(SCRIPT_TEXT, VOICE)
    submaker = edge_tts.SubMaker()
    
    with open(OUTPUT_AUDIO, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # This captures the exact millisecond each word is spoken!
                submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])
                
    with open(OUTPUT_SUBS, "w", encoding="utf-8") as file:
        file.write(submaker.generate_subs())
        
    print(f"✅ Audio saved to {OUTPUT_AUDIO}")
    print(f"✅ Subtitles saved to {OUTPUT_SUBS}")

def update_scene_json(audio_path):
    audio = MP3(audio_path)
    duration = audio.info.length
    total_frames = math.ceil(duration * FPS)
    
    print(f"⏱️ Duration: {duration:.2f}s | Frames: {total_frames}")
    
    with open('scene.json', 'r') as f:
        scene_data = json.load(f)
        
    scene_data['content']['audio_path'] = audio_path
    scene_data['content']['duration_seconds'] = round(duration, 2)
    scene_data['content']['end_frame'] = total_frames
    scene_data['content']['script'] = SCRIPT_TEXT
    
    with open('scene.json', 'w') as f:
        json.dump(scene_data, f, indent=4)
        
    print("✅ scene.json updated!")

def run_blender_engine():
    print("🚀 Firing up Blender Engine...")
    # This automatically runs the command you were typing manually
    subprocess.run([BLENDER_PATH, "-b", "-P", "engine.py"])

async def main():
    os.makedirs("temp", exist_ok=True)
    
    # 1. Generate Assets
    await generate_audio_and_subs()
    
    # 2. Sync Math
    update_scene_json(OUTPUT_AUDIO)
    
    # 3. Build Visuals
    run_blender_engine()

if __name__ == "__main__":
    asyncio.run(main())