import youtube_dl
import argparse
import librosa
import librosa.beat
import sys
import subprocess

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

class YoutubeDlLogger():
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': YoutubeDlLogger(),
    'outtmpl': 'intermediate.%(ext)s',
}

def main(youtube_url):
    parts = youtube_url.split('=')
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print('downloading from {}'.format(youtube_url))
        ydl.download([youtube_url])

    print('download finished, detecting tempo')
    audio, sr = librosa.load('intermediate.mp3')
    tempo = librosa.beat.tempo(audio, sr)
    print('tempo {}bpm, target is 80bpm'.format(round(tempo[0])))
    stretch = 80.0 / tempo[0]
    print('stretching by {}x'.format(round(stretch, 2)))
    audio_slow = librosa.effects.time_stretch(audio, stretch)
    print('success!, saving')
    librosa.output.write_wav('output.wav', audio_slow, sr)
    x = subprocess.run(['lame', 'output.wav', '{}.mp3'.format(parts[1])], stderr=subprocess.PIPE)
    print('🌆🕶️ 🎶 {}.mp3 ready'.format(parts[1]))
    os.unlink('output.wav')
    os.unlink('intermediate.mp3')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Take it down-tempo')
    parser.add_argument('youtube', help='Youtube url')
    args = parser.parse_args()

    main(args.youtube)
