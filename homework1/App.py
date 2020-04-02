# Filename: signals_slots.py

"""Signals and slots example."""

import sys
from os import path
import speech_model as spm

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import uic

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('speech.ui', self)
        self.show()                

class speech_ctl:
    pathOut = ""
    curURL = ""
    curIdxSen = 0
    lst_sentence = []
    recorder = None
    is_record = False    
    #model = speech_model
    def __init__(self, _model, _view):
        self.model = _model
        self.view = _view
        self._connectSignals()        
    
    @staticmethod
    def show_msg(title, msg):
        QMessageBox.information(None, title, msg)    

     # Check recording:    
    def check_record(self):
        if(self.is_record):
            msgBox = QMessageBox()
            msgBox.setText("The recorder is still running")
            msgBox.setInformativeText("Do you want to stop and save it?")
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)            
            ret = msgBox.exec()
            if ret == QMessageBox.Yes:
                self.recorder.stop_recording()
                self.is_record = False
        return self.is_record
    # Set path:
    def _setPath(self):    
        self.check_record()             
        content = self.view.path.text().strip()
        # Check exist
        if(not path.isdir(content)):
            self.show_msg("Warning", "Wrong path")
            return

        if (content != ""):            
            self.pathOut = content            
            self.show_msg("Noti", "Success")
        else:
            # Empty path:
            self.show_msg("Warning", "Please enter the location")

    # Getting sentences from URL:
    def _setStart(self):                                           
        if(self.check_record()):
            return
        try:                                                   
            self.curURL = self.view.url.text().strip()                                                    
            self.lst_sentence = self.model.get_sentences(self.curURL)            
            self.show_msg("Noti", "Success")
            self.curIdxSen = 0
            self.view.sentence_box.setText(self.lst_sentence[self.curIdxSen])            
            self.view.status_box.clear() # clear status
            self.view.numsen_label.setText(f"  1/{len(self.lst_sentence)}:")
            self._setExport()            
        except Exception as err:
            print(str(err.args))
            self.show_msg("Warning", "Fail to get content")

    # Getting next sentence
    def _setNextBut(self):      
        if(self.check_record()):
            return
        if(len(self.lst_sentence) == 0):
            self.show_msg("Warning", "No data to show")
            return 
        if(self.curIdxSen + 1 == len(self.lst_sentence)):
            self.show_msg("Noti", "This is the last sentence")
        else:
            self.curIdxSen = self.curIdxSen + 1         
            self.view.numsen_label.setText(f"  {self.curIdxSen + 1}/{len(self.lst_sentence)}:")   
            self.view.status_box.clear() # clear status            
            self.view.sentence_box.setText(self.lst_sentence[self.curIdxSen])        
    
    # Getting prev sentence
    def _setPrevBut(self):      
        if(self.check_record()):
            return
        if(len(self.lst_sentence) == 0):
            self.show_msg("Warning", "No data to show")
            return 
        if(self.curIdxSen - 1 < 0):
            self.show_msg("Noti", "This is the first sentence")
        else:
            self.curIdxSen = self.curIdxSen - 1       
            self.view.numsen_label.setText(f"  {self.curIdxSen + 1}/{len(self.lst_sentence)}:")        
            self.view.status_box.clear() # clear status
            self.view.sentence_box.setText(self.lst_sentence[self.curIdxSen])

    # Setting start recording 
    def _setRecBut(self):        
        self.check_record()        
        self.is_record = True
        self.view.status_box.setText('Recording...')
        valPath = f"{self.pathOut}\sentence_{self.curIdxSen+1}.wav"
        self.recorder = self.model.Recorder(channels = 2).open(valPath, 'wb')
        self.recorder.start_recording()

    # Setting stop recording:
    def _setStopBut(self):
        if(self.is_record):
            self.check_record()
            self.view.status_box.setText('Done!')

    # Setting for exporting data to txt file
    def _setExport(self):
        if(len(self.lst_sentence) == 0):
            self.show_msg("Warning", "No data to export")
            return             
        file_out = open(f"{self.pathOut}\\template_data.txt", "w", encoding="utf-8")
        file_out.write(self.curURL)
        for id in range(len(self.lst_sentence)):
            file_out.write(f"sentence_{id+1}.wav\n")
            file_out.write(f"{self.lst_sentence[id]}\n")
        file_out.close()
        self.show_msg("Noti", "Success to export data")

    def _connectSignals(self):                
        self.view.set_button.clicked.connect(self._setPath)    # set button    
        self.view.start_button.clicked.connect(self._setStart) # start button
        self.view.next_button.clicked.connect(self._setNextBut) # next button
        self.view.prev_button.clicked.connect(self._setPrevBut) # prev button
        self.view.record_button.clicked.connect(self._setRecBut) # record button
        self.view.stop_button.clicked.connect(self._setStopBut) # stop button
        self.view.export_button.clicked.connect(self._setExport) # export button

def main():    
    app = QApplication(sys.argv)
    window = Ui()
    mod = spm        
    contrl = speech_ctl(mod, window)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()