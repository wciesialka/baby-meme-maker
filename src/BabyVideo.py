from pydub import AudioSegment
import ffmpeg
import tempfile
from pathlib import Path
import subprocess
import os

class BabyVideo:

    FPS = 29.970    #NTSC
    VIDEO_START = 0 #Frame   0
    EAT_START = 109 #Frame 109
    VIDEO_END = 132 #Frame 132

    INTRO_SND = "resources/snd.mp3"

    #/home/wciesialka/Documents/baby-meme-maker/src/BabyVideo.py
    RESOURCES = __file__

    def __init__(self):
        self.audio = AudioSegment.from_file(BabyVideo.INTRO_SND)
        self.resources = str(Path(__file__).parent.parent / "resources")
        self.frames = list(map(lambda id: self.resources + "/frames/frame_{:06d}.png".format(id), range(BabyVideo.VIDEO_START,BabyVideo.EAT_START)))

    def format_id(self,id):
        return self.resources + "/frames/frame_{:06d}.png".format(id)

    def add_frame(self,id):
        self.frames.append(format_id(id))

    def add_audio(self,segment):
        self.audio = self.audio + segment

    def export(self,output_path):
        temp_dir = tempfile.TemporaryDirectory()
        temp_dir_path = temp_dir.name
        audio_path = temp_dir_path + "/audio.mp3"
        self.audio.export(audio_path,format="mp3")

        with open(temp_dir_path + "/mylist.txt","w") as f:
            #f.write("file '" + audio_path + "'\n")
            for frame in self.frames:
                f.write("file '" + frame + "'\n")

        command = "ffmpeg -f concat -safe 0 -r " + str(BabyVideo.FPS) + " -i " + temp_dir_path + "/mylist.txt -i " + audio_path + " -y " + output_path

        try:
            subprocess.call(command, shell=True)
        except:
            return False
        else:
            return os.path.exists(output_path)
