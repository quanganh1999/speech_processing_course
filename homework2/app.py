import sys
from os import path

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import uic
import voice_model
import time

class Ui(QtWidgets.QMainWindow):    
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('app.ui', self)
        self.show()                

class Controller():
    recorder = None
    is_record = False  

    def __init__(self, _model, _view):
        self.model = _model
        self.view = _view
        self._connectSignals()
    
    @staticmethod
    def show_msg(title, msg):
        QMessageBox.information(None, title, msg)       

    # Setting start recording
    def _setRecBut(self):                
        self.is_record = True
        self.view.status_block.setText('Recording...')
        valPath = "record.wav"
        self.recorder = self.model.Recorder(channels = 2).open(valPath, 'wb')
        self.recorder.start_recording()

    # Setting stop recording:
    def _setStopBut(self):
        if(self.is_record):
            self.is_record = False
            self.recorder.stop_recording()
            self.view.status_block.setText('Finish recording')
        
    def _setPlayButOri(self):
        # self.view.status_block.setText("Playing...")
        self.model.play_sound("record.wav")
        self.view.status_block.setText("Done...")    

    def _setPredButOri(self):
        # self.view.status_block.setText("Predicting...")
        word = self.model.predict_word("record.wav")        
        self.view.status_block.setText("Finish predicting !")
        self.view.result_block.setText(word)
    
    def _connectSignals(self):                
        self.view.record_but.clicked.connect(self._setRecBut)
        self.view.stop_but.clicked.connect(self._setStopBut)        
        self.view.play_but.clicked.connect(self._setPlayButOri)        
        self.view.predict_but.clicked.connect(self._setPredButOri)        

def main():    
    app = QApplication(sys.argv)
    window = Ui()
    mod = voice_model
    # mod = spm        
    contrl = Controller(mod, window)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()