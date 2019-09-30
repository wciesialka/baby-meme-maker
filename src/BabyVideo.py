from pydub import AudioSegment
import ffmpeg
import tempfile
from pathlib import Path
import subprocess
import os
import math

class BabyVideo:

    FPS = 29.970    #NTSC as defined by Sony Vegas
    MSPF = 1000/FPS # Milliseconds per Frame
    VIDEO_START = 0 #Frame   0
    EAT_START = 109 #Frame 109
    VIDEO_END = 132 #Frame 132

    LOUDEST = 99.5 # 99.5 dB - the loudest sound that a computer can typically encode.

    def __init__(self):
        self.resources = str(Path(__file__).parent.parent / "resources")
        self.frames = list(map(lambda id: self.resources + "/frames/frame_{:06d}.png".format(id), range(BabyVideo.VIDEO_START,BabyVideo.EAT_START)))
        self.audio = AudioSegment.from_file(self.resources + "/snd.mp3")
        self.duration = len(self.frames)*BabyVideo.MSPF

    def format_id(self,id):
        return self.resources + "/frames/frame_{:06d}.png".format(id) # frames are in name format frame_######.png where # is a 6-digit number with leading zeroes

    def add_frame(self,id):
        self.frames.append(format_id(id))
        self.duration = len(self.frames)*BabyVideo.MSPF

    def add_audio(self,segment):
        self.audio = self.audio + segment

    def translate(self, value, from_min, from_max, to_min, to_max):
        from_range = from_max - from_min
        to_range = to_max - to_min

        left_mapped = float(value - from_min) / float(from_range)

        translated = to_min + (left_mapped * to_range)

        if translated < 0.0001 or math.isinf(translated):
            return 0
        else:
            return translated

    def amptodb(self,amplitude):
        try:
            db = 10 * math.log(amplitude)
        except:
            return 0
        else:
            return db

    def add_file(self,filename,min_threshold=0):
        new_audio = AudioSegment.from_file(filename)
        duration_millis = new_audio.duration_seconds * 1000
        for i in range(0,duration_millis,BabyVideo.MSPF):
            start = i # the start
            end = min(i + BabyVideo.MSPF - .0001, duration_millis) #the end
            clip = new_audio[start,end] # the clip
            vol = self.amptodb(clip.max) # convert the highest amplitude to dB 
            thresh = vol * min_threshold

            treshed_vol = max(0,vol-thresh) # we subtract treshold from volume to make the video look better

            mapped = self.translate(treshed_vol,0,BabyVideo.LOUDEST,BabyVideo.EAT_START,BabyVideo.VIDEO_END) # from 0-99.5 -> 109-132
            frame_id = round(mapped)

            self.add_frame(frame_id)

        self.add_audio(new_audio)

    def prevent_cutoff(self):
        excess = self.duration % 1000
        count = math.ceil(excess / BabyVideo.MSPF)
        for i in range(0,count):
            self.frames.append(self.resources + "/empty.png")
        self.duration = len(self.frames)*BabyVideo.MSPF

    def export(self,output_path):
        self.prevent_cutoff()

        temp_dir = tempfile.TemporaryDirectory()
        temp_dir_path = temp_dir.name
        audio_path = temp_dir_path + "/audio.mp3"
        self.audio.export(audio_path,format="mp3") # we need to export our combined audio to use with ffmpeg

        with open(temp_dir_path + "/mylist.txt","w") as f:
            for frame in self.frames:
                f.write("file '" + frame + "'\n")  # we write a file with all our frames in order for ffmpeg to read from

        command = "ffmpeg -f concat -safe 0 -r " + str(BabyVideo.FPS) + " -i " + temp_dir_path + "/mylist.txt -i " + audio_path + " -y " + output_path # Jesus Wept

        try:
            subprocess.call(command, shell=True)
        except:
            return False
        else:
            return os.path.exists(output_path)
