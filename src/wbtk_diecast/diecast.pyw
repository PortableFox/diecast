import sys

from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget
)

import diecast as dc


'''
GUI Style Utils
'''
class Style:
    @staticmethod
    def layout(layout):
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        return layout


'''
Main Window
'''
class MainWindow(QMainWindow): 
    def __init__(self): 
        super().__init__()
        
        self.gui = {}
        self.init_layout()
    
    def init_layout(self):
        # Layout Root
        self.gui['wdg_core'] = QWidget()
        self.gui['lyt_core'] = Style.layout(QHBoxLayout())
        self.gui['wdg_core'].setLayout(self.gui['lyt_core'])   
        self.setCentralWidget(self.gui['wdg_core'])
        
        # Left Bar
        self.gui['wdg_core_left'] = QFrame()
        self.gui['lyt_core_left'] = Style.layout(QVBoxLayout())
        self.gui['wdg_core_left'].setLayout(self.gui['lyt_core_left'])
        self.gui['lyt_core'].addWidget(self.gui['wdg_core_left'])
        
        self.gui['lyt_core_left'].addWidget(QLabel("left"))
        
        # Center Section
        self.gui['wdg_core_center'] = QFrame()
        self.gui['lyt_core_center'] = Style.layout(QVBoxLayout())
        self.gui['wdg_core_center'].setLayout(self.gui['lyt_core_center'])
        self.gui['lyt_core'].addWidget(self.gui['wdg_core_center'])
        
        self.gui['lyt_core_center'].addWidget(QLabel("center"))
        
        # Right Bar
        self.gui['wdg_core_right'] = QFrame()
        self.gui['lyt_core_right'] = Style.layout(QVBoxLayout())
        self.gui['wdg_core_right'].setLayout(self.gui['lyt_core_right'])
        self.gui['lyt_core'].addWidget(self.gui['wdg_core_right'])
        
        self.gui['lyt_core_right'].addWidget(QLabel("right"))


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
