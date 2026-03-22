import bpy
import json
import os

def build_scene():
    print("-----------------------------------")
    print("⚙️ INITIATING BLENDER AETHER ENGINE")
    print("-----------------------------------")

    # 1. Load the Source of Truth (scene.json)
    json_path = os.path.abspath("scene.json")
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load scene.json: {e}")
        return

    # Extract data
    audio_path = data['content']['audio_path']
    end_frame = data['content']['end_frame']
    fps = data['project_metadata']['fps']
    res_x = data['project_metadata']['resolution'][0]
    res_y = data['project_metadata']['resolution'][1]

    # 2. Configure the Master Scene Settings
    scene = bpy.context.scene
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    
    scene.frame_start = 1
    scene.frame_end = end_frame

    print(f"📐 Resolution set to: {res_x}x{res_y}")
    print(f"⏱️ Timeline locked: 1 to {end_frame} frames ({fps} FPS)")

    # 3. Inject Audio into Blender's Video Sequence Editor (VSE)
    if not scene.sequence_editor:
        scene.sequence_editor_create()

    # FIX for Blender 5.1 API: Iterate using a list to avoid modification errors
    for seq in list(scene.sequence_editor.sequences):
        scene.sequence_editor.sequences.remove(seq)

    abs_audio_path = os.path.abspath(audio_path)
    if os.path.exists(abs_audio_path):
        # Add the audio track starting at frame 1
        scene.sequence_editor.sequences.new_sound("Aether_Voice", abs_audio_path, 1, 1)
        print(f"🔊 Audio synced to timeline: {audio_path}")
    else:
        print(f"⚠️ WARNING: Audio file not found at {abs_audio_path}")

    # 4. Save the configured project to the temp folder
    output_blend = os.path.abspath("temp/automated_scene.blend")
    bpy.ops.wm.save_as_mainfile(filepath=output_blend)
    print(f"✅ Scene successfully compiled and saved to: {output_blend}")
    print("-----------------------------------")

if __name__ == "__main__":
    build_scene()