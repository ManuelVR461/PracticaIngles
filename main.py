import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog, QPushButton, QCheckBox
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QWidget, QDialogButtonBox
from PyQt5.QtWidgets import QLabel, QLineEdit, QSpacerItem, QSizePolicy, QTextEdit, QComboBox, QListWidget, QListWidgetItem
from PyQt5.QtGui import QFont 
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt

import json
import threading
import time
import random


class Aplicacion(QMainWindow):
    show_pregunta = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.englishWords=[]
        self.spanishWords=[]
        self.reviewWords=[]
        self.scoreWords=[]
        self.docs = []
        self.seguir = False
        self.initUI()
        self.initSystem()

    def initUI(self):
        self.setWindowTitle('Practica Vocabulario 1.0')
        self.size = 615, 515
        self.setMinimumSize(self.size[0], self.size[1])
        self.setMaximumSize(self.size[0], self.size[1])
        centralWidget = QWidget()
        self.verticalspace = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.columnas = QHBoxLayout()
        
        self.groupColform = QGroupBox("Add Words")
        self.groupColInit = QGroupBox("Init Practice")

        self.groupColWords = QGroupBox("Words Registed")
        self.filasCol1 = QVBoxLayout()

        self.filasForm1 = QVBoxLayout()
        self.filasForm2 = QVBoxLayout()
        
        self.filasWords = QVBoxLayout()
        
        self.lblEnglish = QLabel("English")
        self.lblSpanish = QLabel("Spanish")
        self.txtEnglish = QLineEdit()
        self.txtSpanish = QLineEdit()
        self.btnAdd = QPushButton('Add')
        self.btnInit = QPushButton('Start!')
        self.chkIdioma = QCheckBox("In English")
        self.chkIdioma.setChecked(False)

        self.filasForm1.addWidget(self.lblEnglish)
        self.filasForm1.addWidget(self.txtEnglish)
        self.filasForm1.addWidget(self.lblSpanish)
        self.filasForm1.addWidget(self.txtSpanish)
        self.filasForm1.addWidget(self.btnAdd)
        self.filasForm2.addWidget(self.chkIdioma)
        self.filasForm2.addWidget(self.btnInit)
        self.filasForm2.addItem(self.verticalspace)

        self.listWords = QListWidget()
        self.filasWords.addWidget(self.listWords)
        self.groupColform.setLayout(self.filasForm1)
        self.groupColInit.setLayout(self.filasForm2)
        self.filasCol1.addWidget(self.groupColform)
        self.filasCol1.addWidget(self.groupColInit)

        self.groupColWords.setLayout(self.filasWords)

        self.columnas.addLayout(self.filasCol1)
        
        self.columnas.addWidget(self.groupColWords)
        
        centralWidget.setLayout(self.columnas)
        self.setCentralWidget(centralWidget)
        self.show()

    def initSystem(self):
        self.show_pregunta.connect(self.window_question)
        self.btnAdd.clicked.connect(self.addWords)
        self.btnInit.clicked.connect(self.initWords)
        self.chkIdioma.stateChanged.connect(lambda:self.changeMode(self.chkIdioma))
        self.read_Dictionary()
    
    def initWords(self):
        if self.seguir: 
            print("starting...")
            self.seguir = False
            self.btnInit.setText("Start!")
        else:
            print("stoping...")
            self.seguir = True
            self.btnInit.setText("Stop!")
            preguntar = threading.Thread(name='Preguntas', target=self.initQuestions)
            preguntar.start()


    def changeMode(self,chk):
        if chk.isChecked() == True:
            self.mode = "english"
        else:
            self.mode = "spanish"
        

    def read_Dictionary(self):
        self.englishWords = []
        self.spanishWords = []
        self.scoreWords = []
        self.listWords.clear()
        with open('data/diccionary.json') as file:
            self.docs = json.load(file)
            
            for words in self.docs['words_to_learn']:
                self.englishWords.append(words['english'])
                self.spanishWords.append(words['spanish'])
                self.scoreWords.append(words['score'])
                w = QListWidgetItem("{} - {} = {}".format(words['english'],words['spanish'],words['score']))
                w.setForeground(Qt.blue)
                self.listWords.addItem(w)
            
            for words in self.docs['words_learned']:
                self.englishWords.append(words['english'])
                self.spanishWords.append(words['spanish'])
                self.scoreWords.append(words['score'])
                w = QListWidgetItem("{} - {} = {}".format(words['english'],words['spanish'],words['score']))
                w.setForeground(Qt.green)
                self.listWords.addItem(w)
            
            for words in self.docs['reviews_words']:
                self.englishWords.append(words['english'])
                self.spanishWords.append(words['spanish'])
                self.scoreWords.append(words['score'])
                w = QListWidgetItem("{} - {} = {}".format(words['english'],words['spanish'],words['score']))
                #w.setBackground( QColor('#6392E4'))
                w.setForeground(Qt.red)
                self.listWords.addItem(w)
            
    def update_Dictionary(self):
        with open('data/diccionary.json', 'w') as file:
            json.dump(self.docs, file, indent=4)

    def initQuestions(self):
        print("init Questions...")
        j=0
        espera = 30
        while self.seguir:
            print("time {}".format(j))
            if espera == j:
                self.show_pregunta.emit()
                j=0
                espera = random.randrange(120)
            time.sleep(1)
            j = j + 1
            
    def addWords(self):
        word1 = self.txtEnglish.text().lower().capitalize()
        word2 = self.txtSpanish.text().lower().capitalize()
        if word1 == '' or word2 == '':
            QMessageBox.information(self, "WARNING!","Los Campos no deben estar vacios!")
            return False
            
        self.englishWords.append(str(word1))
        self.spanishWords.append(str(word2))
        self.scoreWords.append(0)
        self.txtEnglish.setText("")
        self.txtSpanish.setText("")
        self.update_doc()
        self.read_Dictionary()

    @pyqtSlot(list)
    def update_main_score(self,update_words):
        self.scoreWords = update_words
        self.update_doc()
        self.read_Dictionary()
    
    def update_doc(self):
        self.docs['words_learned'] = []
        self.docs['words_to_learn'] = []
        self.docs['reviews_words'] = []
        for x in range(len(self.scoreWords)):
            if self.scoreWords[x] >= 10:
                self.docs['words_learned'].append({'english':self.englishWords[x], 
                                                    'spanish':self.spanishWords[x],
                                                    'score':self.scoreWords[x]})
            elif self.scoreWords[x] < 0:
                self.docs['reviews_words'].append({'english':self.englishWords[x], 
                                                    'spanish':self.spanishWords[x],
                                                    'score':self.scoreWords[x]})
            else:
                self.docs['words_to_learn'].append({'english':self.englishWords[x], 
                                                    'spanish':self.spanishWords[x],
                                                    'score':self.scoreWords[x]})
        self.update_Dictionary()

    @pyqtSlot()
    def window_question(self):
        w = MyQuestions(self)
        w.update_score.connect(self.update_main_score)
        w.palabra(english=self.englishWords,spanish=self.spanishWords,score=self.scoreWords)
        w.show()

    def closeEvent(self, event):
        res = QMessageBox.question(self,"Salir ...","Seguro que quieres cerrar",QMessageBox.Yes|QMessageBox.No)
        if res==QMessageBox.Yes:
            event.accept()
            self.seguir = False
            self.update_doc()

        else:
            event.ignore()


class MyQuestions(QDialog):
    update_score = pyqtSignal(list)

    def __init__(self, *args, **kwargs):
        super(MyQuestions, self).__init__(*args, **kwargs)
        self.setWindowTitle('Pregunta Aleatoria')
        self.size = 615, 515
        self.setMinimumSize(self.size[0], self.size[1])
        self.setMaximumSize(self.size[0], self.size[1])
        self.mode="english"
        self.setAutoFillBackground(True)
        self.index=0
        self.words_actual = []
        self.input_word = QLineEdit() 
        self.filas = QVBoxLayout()

        self.fEnglish = QVBoxLayout()
        self.lblEnglish = QLabel()
        self.lblEnglish.setFont(QFont('Arial', 46)) 
        self.groupColEnglish = QGroupBox("in English")
        
        self.groupColSpanish = QGroupBox("in Spanish")
        self.fSpanish = QVBoxLayout()
        self.lblSpanish = QLabel()
        self.lblSpanish.setFont(QFont('Arial', 46)) 


        if self.mode == "spanish":
            self.fEnglish.addWidget(self.lblEnglish)
            self.groupColEnglish.setLayout(self.fEnglish)
            self.fSpanish.addWidget(self.input_word)
            self.groupColSpanish.setLayout(self.fSpanish)
        else:
            self.fEnglish.addWidget(self.input_word)
            self.groupColEnglish.setLayout(self.fEnglish)
            self.fSpanish.addWidget(self.lblSpanish)
            self.groupColSpanish.setLayout(self.fSpanish)


        self.filas.addWidget(self.groupColEnglish)
        self.filas.addWidget(self.groupColSpanish)
        
        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.procesar)
        self.buttonBox.rejected.connect(self.rechazar)
        self.filas.addWidget(self.buttonBox)

        self.setLayout(self.filas)
        
        self.setTopLevelWindow()
    
    def setTopLevelWindow(self):    
        if self.windowState() != Qt.WindowMaximized:
            self.showMaximized()
            self.showNormal()

        else:
            self.showNormal()
            self.showMaximized()

        self.raise_()
        self.activateWindow()

    def palabra(self, **kwargs):
        cant_palabras = len(kwargs['english'])
        self.index = random.randrange(cant_palabras)
        self.words_actual = kwargs
        self.lblEnglish.setText(kwargs['english'][self.index])
        self.lblSpanish.setText(kwargs['spanish'][self.index])

    def procesar(self):
        word1 = self.input_word.text().lower()
        word2 = self.lblEnglish.text().lower()
        score = self.words_actual['score'][self.index]
        
        if word1 == word2:
            score = score + 1
        else:
            score = score - 1

        self.words_actual['score'][self.index] = score
        self.update_score.emit(self.words_actual['score'])
        self.close()

    def rechazar(self):
        print("rechazar")
        score = self.words_actual['score'][self.index]
        score = score - 1
        self.words_actual['score'][self.index] = score
        self.update_score.emit(self.words_actual['score'])
        self.close()

def main():
    app = QApplication(sys.argv)
    inicio = Aplicacion()
    inicio.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()