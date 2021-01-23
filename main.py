import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog, QPushButton, QCheckBox, QRadioButton
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QWidget, QDialogButtonBox
from PyQt5.QtWidgets import QLabel, QLineEdit, QSpacerItem, QSizePolicy, QTextEdit, QComboBox, QListWidget, QListWidgetItem
from PyQt5.QtGui import QFont 
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt

import json
import threading
import time
import random
import traceback


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
        self.accion = "add"
        self.mode = "english"
        self.index_word = 0
        self.initUI()
        self.initSystem()

    def initUI(self):
        self.setWindowTitle('Practica Vocabulario 1.0')
        self.size = 800, 600
        self.setMinimumSize(self.size[0], self.size[1])
        self.setMaximumSize(self.size[0], self.size[1])
        centralWidget = QWidget()
        self.verticalspace = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.columnas = QHBoxLayout()
        self.colRadios = QHBoxLayout()

        self.groupColform = QGroupBox("Add Words")
        self.groupColInit = QGroupBox("Init Practice")

        self.groupColWords = QGroupBox("Words Registed")
        self.filasCol1 = QVBoxLayout()

        self.filasForm1 = QVBoxLayout()
        self.filasForm2 = QVBoxLayout()
        
        self.filasWords = QVBoxLayout()
        
        self.lblEnglish = QLabel("English")
        self.lblSpanish = QLabel("Spanish")
        self.lbltime = QLabel("Next question in: 0s")
        self.lbltime.setFont(QFont('Arial', 28))
        self.txtEnglish = QLineEdit()
        self.txtSpanish = QLineEdit()
        self.btnAdd = QPushButton('Add')
        self.btnInit = QPushButton('Start!')

        self.filasForm1.addWidget(self.lblEnglish)
        self.filasForm1.addWidget(self.txtEnglish)
        self.filasForm1.addWidget(self.lblSpanish)
        self.filasForm1.addWidget(self.txtSpanish)
        self.filasForm1.addWidget(self.btnAdd)

        self.RadioIdioma = QRadioButton("In English")
        self.RadioIdioma.setChecked(True)
        self.RadioIdioma.idioma = "english"
        self.RadioIdioma.toggled.connect(self.changeMode)
        self.colRadios.addWidget(self.RadioIdioma)
        self.RadioIdioma = QRadioButton("In Spanish")
        self.RadioIdioma.setChecked(False)
        self.RadioIdioma.idioma = "spanish"
        self.RadioIdioma.toggled.connect(self.changeMode)
        self.colRadios.addWidget(self.RadioIdioma)
        self.filasForm2.addLayout(self.colRadios)

        self.filasForm2.addWidget(self.btnInit)
        self.filasForm2.addItem(self.verticalspace)
        self.filasForm2.addWidget(self.lbltime)

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
        self.listWords.itemClicked.connect(self.editWords)
        self.read_Dictionary()
    
    def initWords(self):
        if self.seguir: 
            self.seguir = False
            self.btnInit.setText("Start!")
            self.lbltime.setText("Next question in: 0s")
        else:
            self.seguir = True
            self.btnInit.setText("Stop!")
            preguntar = threading.Thread(name='Preguntas', target=self.initQuestions)
            preguntar.start()

    def changeMode(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            self.mode = radioButton.idioma
        

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
                w = QListWidgetItem("{} - {} - {}".format(words['english'],words['spanish'],words['score']))
                w.setForeground(Qt.blue)
                self.listWords.addItem(w)
            
            for words in self.docs['words_learned']:
                self.englishWords.append(words['english'])
                self.spanishWords.append(words['spanish'])
                self.scoreWords.append(words['score'])
                w = QListWidgetItem("{} - {} - {}".format(words['english'],words['spanish'],words['score']))
                w.setForeground(Qt.green)
                self.listWords.addItem(w)
            
            for words in self.docs['reviews_words']:
                self.englishWords.append(words['english'])
                self.spanishWords.append(words['spanish'])
                self.scoreWords.append(words['score'])
                w = QListWidgetItem("{} - {} - {}".format(words['english'],words['spanish'],words['score']))
                #w.setBackground( QColor('#6392E4'))
                w.setForeground(Qt.red)
                self.listWords.addItem(w)
                self.listWords.sortItems()
            
    def update_Dictionary(self):
        with open('data/diccionary.json', 'w') as file:
            json.dump(self.docs, file, indent=4)

    def initQuestions(self):
        j=0
        espera = 30
        randon_time = 300
        while self.seguir:
            if espera == j:
                self.show_pregunta.emit()
                j=0
                espera = random.randrange(randon_time)

            self.lbltime.setText("Next question in: {}s".format(espera - j))
            time.sleep(1)
            j = j + 1
            if j > randon_time:
                j =  0
                espera = 30
            
    def addWords(self):
        try:
            word1 = self.txtEnglish.text().lower().capitalize()
            word2 = self.txtSpanish.text().lower().capitalize()
            if word1 == '' or word2 == '':
                QMessageBox.information(self, "WARNING!","Los Campos no deben estar vacios!")
                return False

            if self.accion == "add":        
                self.englishWords.append(str(word1))
                self.spanishWords.append(str(word2))
                self.scoreWords.append(0)
            else:
                self.englishWords[self.index_word] = str(word1)
                self.spanishWords[self.index_word] = str(word2)
                self.accion = "add"
                self.btnAdd.setText("Add")

            self.txtEnglish.setText("")
            self.txtSpanish.setText("")
            self.update_doc()
            self.read_Dictionary()
        except Exception as e:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            print(str(tbinfo))
        

    def editWords(self):
        try:
            word = []
            word = self.listWords.currentItem().text().split("-")
            self.txtEnglish.setText(word[0].strip())
            self.txtSpanish.setText(word[1].strip())
            self.index_word = self.englishWords.index(word[0].strip())
            self.accion = "Editar"
            self.btnAdd.setText("Update")
        except Exception as e:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            print(str(tbinfo))

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
        w.palabra(english=self.englishWords,spanish=self.spanishWords,score=self.scoreWords,mode=self.mode)
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
        self.size = 815, 215
        self.setMinimumSize(self.size[0], self.size[1])
        self.setMaximumSize(self.size[0], self.size[1])
        self.setAutoFillBackground(True)
        self.index=0
        self.words_actual = []
        self.input_word = QLineEdit() 
        self.filas = QVBoxLayout()

        self.fEnglish = QVBoxLayout()
        self.lblEnglish = QLabel()
        self.lblEnglish.setFont(QFont('Arial', 28)) 
        self.groupColEnglish = QGroupBox("in English")
        
        self.groupColSpanish = QGroupBox("in Spanish")
        self.fSpanish = QVBoxLayout()
        self.lblSpanish = QLabel()
        self.lblSpanish.setFont(QFont('Arial', 28)) 
        
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
        self.showMaximized()
        self.activateWindow()

    def palabra(self, **kwargs):
        cant_palabras = len(kwargs['english'])
        self.index = random.randrange(cant_palabras)
        self.words_actual = kwargs
        self.lblEnglish.setText(kwargs['english'][self.index])
        self.lblSpanish.setText(kwargs['spanish'][self.index])
        self.mode = kwargs['mode']
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
        

    def procesar(self):
        word1 = self.input_word.text().lower()
        word2 = self.lblEnglish.text().lower()
        word3 = self.lblSpanish.text().lower()
        score = self.words_actual['score'][self.index]
        if word1 == word2:
            score = score + 1
        else:
            score = score - 1
            if self.mode == "spanish":
                self.correctWord(word3)
            else:
                self.correctWord(word2)

        self.words_actual['score'][self.index] = score
        self.update_score.emit(self.words_actual['score'])
        self.close()

    def rechazar(self):
        word2 = self.lblEnglish.text().lower()
        word3 = self.lblSpanish.text().lower()
        score = self.words_actual['score'][self.index]
        score = score - 1
        self.words_actual['score'][self.index] = score
        self.update_score.emit(self.words_actual['score'])
        if self.mode == "spanish":
            self.correctWord(word3)
        else:
            self.correctWord(word2)
        self.close()

    def correctWord(self,w1):
        winfo = MyInfos(self)
        winfo.palabra(word=w1)
        winfo.show()

class MyInfos(QDialog):
    def __init__(self, *args, **kwargs):
        super(MyInfos, self).__init__(*args, **kwargs)
        self.setWindowTitle('Info Word!')
        self.size = 815, 215
        self.setMinimumSize(self.size[0], self.size[1])
        self.setMaximumSize(self.size[0], self.size[1])
        self.setAutoFillBackground(True)
        self.filas = QVBoxLayout()
        self.fWord = QVBoxLayout()
        self.lblWord = QLabel()
        self.lblWord.setFont(QFont('Arial', 28)) 
        self.groupColWord = QGroupBox("Correct Word")
        self.filas.addWidget(self.groupColWord)
        self.fWord.addWidget(self.lblWord)
        self.groupColWord.setLayout(self.fWord)

        buttons = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.procesar)
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
        self.lblWord.setText(kwargs['word'])
        

    def procesar(self):
        self.close()

def main():
    app = QApplication(sys.argv)
    inicio = Aplicacion()
    inicio.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()