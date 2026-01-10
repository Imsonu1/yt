from gtts import gTTS

tts = gTTS("Hello Sonu, this is a test", lang="en")
tts.save("test.mp3")

print("gTTS WORKED")
