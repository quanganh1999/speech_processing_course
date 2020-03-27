import requests as rq
from bs4 import BeautifulSoup
import re
import unicodedata
from newspaper import Article
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
import pyaudio
import wave
import timeit
import time


def get_sentences(url):    
    if(url == ''):
        raise Exception('Empty url')    
    content = ""
    title = ""
    response = rq.get(url)
    pageUrl = response.url  # get url
    if(response):
        resHtml = BeautifulSoup(response.content, 'lxml')        
        title = resHtml.find('h1', class_='title_news_detail')        
        contentHtml = resHtml.find('section', class_='sidebar_1')
        # Error if this new has no content
        if(title is None or contentHtml is None):            
            # The web may change the format of html.
            # So it should use newspaper3k for this situation
            article = Article(url, language='vi')
            article.download()
            article.parse()
            if article.text.strip() == '':
                raise Exception('No content')
            else:
                return sent_tokenize(article.text)
        #The format of html is the same as the config 
        title = title.text.strip()
        title = title.replace(u'\xa0', ' ')
        paragr = contentHtml.find_all('p', class_=re.compile(
            "Normal|description"))  # get every paragraph
        for cktext in paragr:
            content += (cktext.text + " ")
        content = content.strip() 
        content = content.replace(u'\xa0', ' ')
        return sent_tokenize(content)
    else:
        raise Exception('Fail to connect')


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
    testUrl = "https://vnexpress.net/giao-duc/sinh-vien-anh-keu-goi-hoan-tra-hoc-phi-4075125.html"
    print(len(get_sentences(testUrl)))
    for val in get_sentences(testUrl):
        print(type(val))
# if __name__ == '__main__':
#      rec = Recorder(channels=2)
#      with rec.open('nonblocking.wav', 'wb') as recfile2:
#          recfile2.start_recording()
#          time.sleep(5.0)
#          recfile2.stop_recording()
#          print("Done")