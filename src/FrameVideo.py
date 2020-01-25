from pydub import AudioSegment
import tempfile
#from pathlib import Path
import subprocess
import os
import math

class FrameVideo:

    def __init__(self,fps):
        self.frames = []
        self.audio = AudioSegment.silent(1)
        self.fps = fps
        self.mspf = 1000/self.fps
        self.duration = len(self.frames)*self.mspf

    def add_frame(self,path):
        self.frames.append(path)
        self.duration = len(self.frames)*self.mspf

    def add_audio(self,segment):
        self.audio = self.audio + segment

    def prevent_cutoff(self,backup=self.frames[0]):
        excess = self.duration % 1000
        count = math.ceil(excess / self.mspf)
        for i in range(0,count):
            self.add_frame(backup)
        self.add_audio(AudioSegment.silent(self.mspf*count))

    def export(self,output_path):
        self.prevent_cutoff()

        temp_dir = tempfile.TemporaryDirectory()
        temp_dir_path = temp_dir.name
        audio_path = temp_dir_path + "/audio.mp3"
        self.audio.export(audio_path,format="mp3") # we need to export our combined audio to use with ffmpeg

        with open(temp_dir_path + "/mylist.txt","w") as f:
            for frame in self.frames:
                f.write("file '" + frame + "'\n")  # we write a file with all our frames in order for ffmpeg to read from

        command = "ffmpeg -f concat -safe 0 -r " + str(self.fps) + " -i " + temp_dir_path + "/mylist.txt -i " + audio_path + " -y -pix_fmt yuv420p " + output_path # Jesus Wept

        try:
            subprocess.call(command, shell=True) # call the above ffmpeg command
        except:
            return False
        else:
            return os.path.exists(output_path)