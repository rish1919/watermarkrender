from PIL import Image
import ffmpeg
import os

def add_watermark_image(image_path, wm_path):
    try:
        base = Image.open(image_path).convert("RGBA")
        wm = Image.open(wm_path).convert("RGBA")
        wm = wm.resize((int(base.width * 0.25), int(base.height * 0.25)))
        base.paste(wm, (base.width - wm.width - 10, base.height - wm.height - 10), wm)
        out_path = "watermarked_image.png"
        base.save(out_path)
        return out_path
    except Exception as e:
        print("Image WM Error:", e)
        return None

def add_watermark_video(video_path, wm_path):
    try:
        out_path = "watermarked_video.mp4"
        (
            ffmpeg
            .input(video_path)
            .filter("overlay", f"W-w-10", f"H-h-10")
            .output(out_path, vf=f"movie={wm_path} [watermark]; [in][watermark] overlay=W-w-10:H-h-10 [out]", vcodec='libx264', acodec='aac', strict='experimental')
            .overwrite_output()
            .run()
        )
        return out_path
    except Exception as e:
        print("Video WM Error:", e)
        return None