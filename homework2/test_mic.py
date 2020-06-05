import sounddevice as sd
import soundfile as sf
from pydub.playback import play
import os
from pydub import AudioSegment, silence
import keyboard  # using module keyboard
import joblib
import hmmlearn.hmm as hmm
from sklearn.cluster import KMeans
import librosa
import math
import numpy as np
import time

#config
# AudioSegment.converter = "E:\\ffmpeg-4.2.3-win64-static\\bin\\ffmpeg.exe"

def record_sound(filename, duration=1, fs=44100, play=False):
    print('Recording...')        
    data = sd.rec(frames=duration*fs, samplerate=fs, channels=2, blocking=True)
    if play:
        sd.play(data, samplerate=fs, blocking=True)
    sf.write(filename, data=data, samplerate=fs)

def get_mfcc(file_path):
    y, sr = librosa.load(file_path) # read .wav file    
    hop_length = math.floor(sr*0.010) # 10ms hop
    win_length = math.floor(sr*0.025) # 25ms frame
    
    #mfcc feature
    mfcc = librosa.feature.mfcc(
        y, sr, n_mfcc=12, n_fft=1024,
        hop_length=hop_length, win_length=win_length)
    # substract mean from mfcc --> normalize mfcc
    mfcc = mfcc - np.mean(mfcc, axis=1).reshape((-1,1)) 
    # delta mfcc feature 1st order and 2nd order
    delta1_mfcc = librosa.feature.delta(mfcc, order=1)
    delta2_mfcc = librosa.feature.delta(mfcc, order=2)
    
    #energy feature:
    S, phase = librosa.magphase(librosa.stft(y, hop_length=hop_length, win_length=win_length)) # Spectrogram , win_length=win_length
    energy = librosa.feature.rms(S=S)
    #delta energy feature 1st order and 2nd order
    delta1_ener = librosa.feature.delta(energy, order=1)
    delta2_ener = librosa.feature.delta(energy, order=2)
    
    # X is 39 x T
    X = np.concatenate([mfcc, delta1_mfcc, delta2_mfcc, energy, delta1_ener, delta2_ener], axis=0) # O^r
    # return T x 39 (transpose of X)
    return X.T # hmmlearn use T x N matrix

def play_sound(fpath):
    data, fs = sf.read(fpath, dtype='float32')  
    sd.play(data, fs)
    status = sd.wait()  # Wait until file is done playing

class_names = ['cachly', 'dich', 'tien', 'nguoi', 'yte']
dict_word = {'cachly': "cách ly", 'dich':"dịch", 'tien': "tiền", 'nguoi':"người", "yte":'y tế'}
if __name__ == '__main__':
    #get all model:
    kmeans = joblib.load(os.path.join("model","kmeans.pkl"))
    models = {}
    for cname in class_names:
        models[cname] = joblib.load(os.path.join("model",f"{cname}.pkl"))
    print("Loaded models")
    id_file = 0
    while True:  # making a loop
        print("Press space to start recording")
        keyboard.wait('space')               
        record_sound("record.wav", duration=2)                
        time.sleep(1)        
        myaudio = AudioSegment.from_wav("record.wav")
        audios = silence.split_on_silence(myaudio, min_silence_len=600, silence_thresh=-20, keep_silence=200)            
        for audio in audios:                    
            print('Removing silence on audio...')            
            audio.export('test.wav', format = "wav")            
            time.sleep(1)
            print('Checking audio by playing again')        
            play_sound("test.wav")
            print("Predicting")
            val = get_mfcc('test.wav')                        
            test_val = kmeans.predict(val).reshape(-1,1)
            scores = {dict_word[cname] : model.score(test_val) for cname, model in models.items()}            
            print(scores)
            pred_name = max(scores, key=lambda key: scores[key])
            print(f"Result: {pred_name}")
            break             
        print()   
        

     
    
