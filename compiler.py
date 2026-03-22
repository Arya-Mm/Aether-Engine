import os
import json
import asyncio
import edge_tts
from mutagen.mp3 import MP3
import math

# --- CONFIGURATION ---
VOICE = "en-US-ChristopherNeural" # High-quality, natural male voice
OUTPUT_FILE = "temp/voice_01.mp3"
SCRIPT_TEXT = "This is a test of the automated media engine. Voice leads, visuals follow. The system is online."
FPS = 30 # Standard for short-form video

async def generate_audio():
    print(f"🎙️ Generating voiceover using {VOICE}...")
    communicate = edge_tts.Communicate(SCRIPT_TEXT, VOICE)
    await communicate.save(OUTPUT_FILE)
    print(f"✅ Audio saved to {OUTPUT_FILE}")

def update_scene_json(audio_path):
    # 1. Get exact duration of the generated MP3
    audio = MP3(audio_path)
    duration = audio.info.length
    
    # 2. Calculate total frames for Blender
    total_frames = math.ceil(duration * FPS)
    
    print(f"⏱️ Audio Duration: {duration:.2f} seconds")
    print(f"🎬 Calculated Frames at {FPS}fps: {total_frames}")
    
    # 3. Read the existing scene.json
    try:
        with open('scene.json', 'r') as f:
            scene_data = json.load(f)
    except json.decoder.JSONDecodeError:
        print("⚠️ scene.json is empty or invalid. Run the Phase 1 step again to paste the JSON template.")
        return
        
    # 4. Inject the new facts into the JSON
    scene_data['content']['audio_path'] = audio_path
    scene_data['content']['duration_seconds'] = round(duration, 2)
    scene_data['content']['end_frame'] = total_frames
    scene_data['content']['script'] = SCRIPT_TEXT
    
    # 5. Save the updated JSON
    with open('scene.json', 'w') as f:
        json.dump(scene_data, f, indent=4)
        
    print("✅ scene.json updated successfully!")

async def main():
    # Ensure the temp folder exists so it doesn't crash
    os.makedirs("temp", exist_ok=True)
    
    # Run the pipeline
    await generate_audio()
    update_scene_json(OUTPUT_FILE)

if __name__ == "__main__":
    asyncio.run(main())