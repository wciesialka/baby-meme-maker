from pydub import AudioSegment
import tempfile
from pathlib import Path
import src.FrameVideo as FrameVideo
import os
import math

class BabyVideo(FrameVideo.FrameVideo):

    FPS = 29.970    #NTSC as defined by Sony Vegas
    MSPF = 1000/FPS # Milliseconds per Frame
    VIDEO_START = 0 #Frame   0
    EAT_START = 109 #Frame 109
    VIDEO_END = 132 #Frame 132

    LOUDEST = 104

    def __init__(self):
        super().__init__(BabyVideo.FPS)
        self.resources = str(Path(__file__).parent.parent / "resources")
        self.frames = list(map(lambda id: self.resources + "/frames/frame_{:06d}.png".format(id), range(BabyVideo.VIDEO_START,BabyVideo.EAT_START)))
        self.audio = AudioSegment.from_file(self.resources + "/snd.mp3")
        self.duration = len(self.frames)*BabyVideo.MSPF

    def format_id(self,id):
        return self.resources + "/frames/frame_{:06d}.png".format(int(id)) # frames are in name format frame_######.png where # is a 6-digit number with leading zeroes

    def add_frame(self,id):
        super().add_frame(self.format_id(id))

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

        count = math.ceil(duration_millis / self.mspf)

        for j in range(0,count):
            i = j * BabyVideo.MSPF
            if i < duration_millis:
                start = i # the start
                end = min(i + BabyVideo.MSPF - .0001, duration_millis) #the end
                clip = new_audio[start:end] # the clip
                vol = self.amptodb(clip.max) # convert the highest amplitude to dB 
                thresh = vol * min_threshold

                treshed_vol = max(0,vol-thresh) # we subtract treshold from volume to make the video look better

                mapped = self.translate(treshed_vol,0,BabyVideo.LOUDEST-thresh,BabyVideo.EAT_START,BabyVideo.VIDEO_END) # from 0-99.5 -> 109-132
                frame_id = min(max(round(mapped),BabyVideo.EAT_START),BabyVideo.VIDEO_END)

                self.add_frame(frame_id)

        self.add_audio(new_audio)

    def prevent_cutoff(self):
        super().prevent_cutoff(BabyVideo.EAT_START)