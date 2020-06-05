import sounddevice as sd
import soundfile as sf
from pydub.playback import play
import os
from pydub import AudioSegment, silence
import joblib
import hmmlearn.hmm as hmm
from sklearn.cluster import KMeans
import librosa
import math
import numpy as np
import pyaudio
import wave
import timeit
import time

class_names = ['cachly', 'dich', 'nha', 'hoc', 'yte']
dict_word = {'cachly': "cách ly", 'dich':"dịch", 'nha': "nhà", 'hoc':"học", "yte":'y tế'}

def record_sound(filename, duration=1, fs=44100, play=False):    
    print('Recording...')        
    data = sd.rec(frames=int(duration*fs), samplerate=fs, channels=2, blocking=True)
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
    X = np.concatenate([mfcc, delta1_mfcc, delta2_mfcc], axis=0) # O^r
    # return T x 39 (transpose of X)
    return X.T # hmmlearn use T x N matrix

def play_sound(fpath):
    data, fs = sf.read(fpath, dtype='float32')  
    sd.play(data, fs)
    status = sd.wait()  # Wait until file is done playing

def remove_silence(ori_path, fpath):
    myaudio = AudioSegment.from_wav(ori_path)
    audios = silence.split_on_silence(myaudio, min_silence_len=100, silence_thresh=-16, keep_silence=50)            
    for audio in audios:
        audio.export(fpath, format = "wav")            
        break

def predict_word(fpath):
    kmeans = joblib.load(os.path.join("model","kmeans_1.pkl"))
    
    lst_model = []
    for it in range(10):
        models = {}         
        for cname in class_names:        
            models[cname] = joblib.load(os.path.join("model",f"{cname}_iter{it}.pkl"))
        lst_model.append(models)
    
    data = get_mfcc(fpath)
    data = kmeans.predict(data).reshape(-1,1)    
    res_names = {}
    for it in range(10):    
        scores = {dict_word[cname] : model.score(data) for cname, model in lst_model[it].items()}
        pred_name = max(scores, key=lambda key: scores[key])
        res_names[pred_name] = res_names.get(pred_name, 0) + 1
    final_res = max(res_names, key=lambda key: res_names[key])
    print(f"Result: {final_res}")                            
    return final_res

# Reference: https://gist.github.com/sloria/5693955
class Recorder(object):
    '''A recorder class for recording audio to a WAV file.
    Records in mono by default.
    '''

    def __init__(self, channels=1, rate=44100, frames_per_buffer=1024):
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer

    def open(self, fname, mode='wb'):
        return RecordingFile(fname, mode, self.channels, self.rate,
                            self.frames_per_buffer)

class RecordingFile(object):
    def __init__(self, fname, mode, channels, 
                rate, frames_per_buffer):
        self.fname = fname
        self.mode = mode
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self._pa = pyaudio.PyAudio()
        self.wavefile = self._prepare_file(self.fname, self.mode)
        self._stream = None        

    def __enter__(self):
        return self

    def __exit__(self, exception, value, traceback):
        self.close()

    def start_recording(self):
        # Use a stream with a callback in non-blocking mode    
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer,
                                        stream_callback=self.get_callback())
        self._stream.start_stream()
        return self

    def stop_recording(self):        
        self._stream.stop_stream()
        return self

    def get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            self.wavefile.writeframes(in_data)
            return in_data, pyaudio.paContinue
        return callback


    def close(self):
        self._stream.close()
        self._pa.terminate()
        self.wavefile.close()

    def _prepare_file(self, fname, mode='wb'):
        wavefile = wave.open(fname, mode)
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(self.rate)
        return wavefile

if __name__ == '__main__':    
    predict_word("E:\\full_data\\validation_cachly\\cachly_1.wav")