from moviepy.editor import TextClip, CompositeVideoClip, ColorClip

# Simple background
bg = ColorClip(size=(1080, 1920), color=(20, 20, 20)).set_duration(3)

# Simple text (NO font path first)
txt = TextClip(
    "TEST TEXT",
    fontsize=80,
    color="white",
    method="label"
).set_position("center").set_duration(3)

final = CompositeVideoClip([bg, txt])

final.write_videofile(
    "text_test.mp4",
    fps=30,
    codec="libx264"
)
