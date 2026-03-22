import bpy
import json
import os

def build_scene():
    print("-----------------------------------")
    print("⚙️ INITIATING BLENDER AETHER ENGINE")
    print("-----------------------------------")

    json_path = os.path.abspath("scene.json")
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load scene.json: {e}")
        return

    audio_path = data['content']['audio_path']
    end_frame = data['content']['end_frame']
    fps = data['project_metadata']['fps']
    res_x = data['project_metadata']['resolution'][0]
    res_y = data['project_metadata']['resolution'][1]

    scene = bpy.context.scene
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.frame_start = 1
    scene.frame_end = end_frame
    
    scene.render.engine = 'BLENDER_WORKBENCH'

    print(f"📐 Resolution set to: {res_x}x{res_y}")
    print(f"⏱️ Timeline locked: 1 to {end_frame} frames ({fps} FPS)")

    if not scene.sequence_editor:
        scene.sequence_editor_create()

    for strip in list(scene.sequence_editor.strips):
        scene.sequence_editor.strips.remove(strip)

    abs_audio_path = os.path.abspath(audio_path)
    if os.path.exists(abs_audio_path):
        scene.sequence_editor.strips.new_sound(
            name="Aether_Voice", 
            filepath=abs_audio_path, 
            channel=1, 
            frame_start=1
        )
        print(f"🔊 Audio synced to timeline: {audio_path}")

    # 👈 UPGRADE: Render as PNG Sequence (Industry Standard)
    frames_dir = os.path.abspath("temp/frames/")
    os.makedirs(frames_dir, exist_ok=True)
    
    scene.render.image_settings.file_format = 'PNG'
    # This will save as temp/frames/0001.png, temp/frames/0002.png, etc.
    scene.render.filepath = os.path.join(frames_dir, "")

    output_blend = os.path.abspath("temp/automated_scene.blend")
    bpy.ops.wm.save_as_mainfile(filepath=output_blend)
    print(f"✅ Scene successfully compiled and saved to: {output_blend}")
    print("-----------------------------------")

if __name__ == "__main__":
    build_scene()