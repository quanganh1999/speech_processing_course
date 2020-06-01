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
    def __init__(self, _model, _view):
        self.model = _model
        self.view = _view
        self._connectSignals()
    
    def _setRecBut(self):        
        dur = self.view.duration_box.value()
        # self.view.status_block.setText("Recording...")        
        self.model.record_sound("record.wav", duration = dur)        
        self.view.status_block.setText("Finish recording") 

    def _setRemovBut(self):
        # self.view.status_block.setText("Removing silence...")
        self.model.remove_silence("record.wav", "test.wav")
        self.view.status_block.setText("Finish processing") 

    def _setPlayButOri(self):
        # self.view.status_block.setText("Playing...")
        self.model.play_sound("record.wav")
        self.view.status_block.setText("Done...")

    def _setPlayButPro(self):
        # self.view.status_block.setText("Playing...")
        self.model.play_sound("test.wav")
        self.view.status_block.setText("Done...")

    def _setPredButOri(self):
        # self.view.status_block.setText("Predicting...")
        word = self.model.predict_word("record.wav")        
        self.view.status_block.setText("Done...")
        self.view.result_block.setText(word)

    def _setPredButNew(self):
        # self.view.status_block.setText("Predicting...")
        word = self.model.predict_word("test.wav")        
        self.view.status_block.setText("Done...")
        self.view.result_block.setText(word)

    def _connectSignals(self):                
        self.view.record_but.clicked.connect(self._setRecBut)
        self.view.remove_sil_but.clicked.connect(self._setRemovBut)
        self.view.play_but_1.clicked.connect(self._setPlayButOri)
        self.view.play_but_2.clicked.connect(self._setPlayButPro)
        self.view.predict_but_1.clicked.connect(self._setPredButOri)
        self.view.predict_but_1.clicked.connect(self._setPredButNew)

def main():    
    app = QApplication(sys.argv)
    window = Ui()
    mod = voice_model
    # mod = spm        
    contrl = Controller(mod, window)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()