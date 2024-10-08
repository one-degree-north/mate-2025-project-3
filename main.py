from PyQt6.QtWidgets import QApplication, QMainWindow, QComboBox, QWidget, QLineEdit
from PyQt6.QtWidgets import QFrame, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QScrollArea
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont
import random
import math



class SpinnerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.segment_colors = [
            [QColor(0, 0, 255), QColor(255, 0, 0), QColor(0, 255, 0)],  
            [QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255)], 
            [QColor(0, 255, 0), QColor(0, 0, 255), QColor(255, 0, 0)],  
        ]
        self.names = []
        self.current_set_index = 0 
        self.label_offset = 0      

    def start_spinning(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_colors)
        self.timer.start(100) 

    def stop_spinning(self):
        self.timer.stop()

    def update_colors(self):
        self.current_set_index = (self.current_set_index + 1) % len(self.segment_colors)
        self.label_offset = (self.label_offset + 1) % len(self.names)
        self.update()

    def paintEvent(self, event):
        if not self.names:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        center_x, center_y = 150, 150
        radius = 150

        sides = len(self.names)
        angle = 360/sides

        font = QFont("Arial", int(100/sides))
        painter.setFont(font)

        for i in range(sides):
            start_angle = int(angle * i * 16)
            span_angle = int(angle * 16)
            painter.setBrush(self.segment_colors[self.current_set_index][i % 3])
            painter.drawPie(center_x - radius, center_y - radius, 2 * radius, 2 * radius, start_angle, span_angle)

            angle_rad = math.radians(angle * i + angle/2)
            label_radius = radius * 0.6
            label_x = center_x + label_radius * math.cos(angle_rad)
            label_y = center_y - label_radius * math.sin(angle_rad)

            label_index = (i + self.label_offset) % len(self.names)
            painter.setPen(Qt.GlobalColor.black)
            painter.drawText(int(label_x) - 20, int(label_y) + 10, self.names[label_index])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_widget = QWidget()
        self.HRectangle1 = QHBoxLayout()
        self.VRectangle0 = QVBoxLayout()
        self.VRectangle1 = QVBoxLayout()
        self.VRectangle2 = QVBoxLayout()
        self.HRectangle2 = QHBoxLayout()
        self.HRectangle2b = QHBoxLayout()
        self.VRectangle4 = QVBoxLayout()

        self.block = ['a1:', 'a2:', 'a3:', 'a4:',
                      'b1:', 'b2:', 'b3:', 'b4:']

        self.displayName = QLabel("(name)")
        self.displayName.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.displayName.setStyleSheet('''background-color : #CE8989;
                                        font-size : 50px;
                                        color : black;''')
        self.displayName.setFixedSize(300, 100)

        self.name = QLineEdit()
        self.name.setPlaceholderText("Enter name...")
        self.name.setFixedSize(400, 40)
        self.name.setStyleSheet(''' background-color : white; color : black;
                                        font-size : 16px;''')
        self.removeName_button = QPushButton("Remove")
        self.removeName_button.setFixedSize(120, 40)
        self.removeName_button.setStyleSheet(''' background-color : #2196F3; color : black;
                                        font-size : 14px;''')
        self.removeName_button.clicked.connect(self.nameRemoval)

        self.addName_button = QPushButton("Add")
        self.addName_button.setFixedSize(90, 40)
        self.addName_button.setStyleSheet(''' background-color : #2196F3; color : black;
                                        font-size : 14px;''')
        self.addName_button.clicked.connect(self.nameAdditon)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.names = {'shreyas': '1', 'jackson': '3', 'hang': '4'}

        self.scroll.setStyleSheet(''' background-color: #DEDEDE; color:black;font-size:30px''')
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.refreshScroll(self.names)
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll.setWidget(self.scroll_widget)

        self.randomButton = QPushButton("Press for name!")
        self.randomButton.setStyleSheet('''background-color : #CE8989;
                                            font-size : 24px;''')
        self.randomButton.setFixedSize(300, 100)
        self.randomButton.clicked.connect(self.startSpinner)

        self.dropdown = QComboBox()
        self.dropdown.addItems(['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4'])
        self.dropdown.setFixedSize(343, 80)
        self.dropdown.setStyleSheet("""
QComboBox{
    background-color: #DAF4F5;
    color: black;
    border-radius: 5px;
    font-size : 20px;
}

QComboBox::drop-down {
    border: none;
    width : 20px;
    background-color : #DAF4F5;
}
QComboBox::down-arrow {
width : 10px;
height : 10px;
image : url('/Users/shreyas/Documents/Python/Work-in-progress projects/MATE group 3/arrow.png');
}
""")
        self.dropdown.currentIndexChanged.connect(self.readNames)
        self.readNames()

        self.spinner = SpinnerWidget()
        self.spinner.setFixedSize(300, 300)

        self.HRectangle1.addLayout(self.VRectangle1)
        self.HRectangle1.addLayout(self.VRectangle0)

        self.VRectangle0.addWidget(self.spinner)
        self.VRectangle0.addWidget(self.randomButton)
        self.VRectangle0.addWidget(self.displayName)

        self.VRectangle1.addWidget(self.dropdown)
        self.VRectangle1.addLayout(self.VRectangle2)
        self.VRectangle1.setContentsMargins(60, 60, 25, 25)

        self.VRectangle2.addLayout(self.HRectangle2b)
        self.VRectangle2.addLayout(self.HRectangle2)

        self.HRectangle2b.addWidget(self.name)
        self.HRectangle2b.addWidget(self.removeName_button)
        self.HRectangle2b.addWidget(self.addName_button)

        self.VRectangle2.addLayout(self.VRectangle4)
        self.VRectangle4.addWidget(self.scroll)

        self.main_widget.setLayout(self.HRectangle1)
        self.setCentralWidget(self.main_widget)

    def nameAdditon(self):
        name = self.name.text().title()
        temp_names= {}
        temp_names[name] = "0"
        self.names.update(temp_names)
        self.refreshScroll(self.names)
        self.name.clear()
        self.savedNames()

    def refreshScroll(self, names):
        for i in reversed(range(self.scroll_layout.count())):
            widget_to_remove = self.scroll_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)

        for name in names:
            name_label = QLabel(name + " - " + names[name])
            self.scroll_layout.addWidget(name_label)
        self.scroll_widget.adjustSize()

    def startSpinner(self):
        self.spinner.names = list(self.names.keys())
        self.spinner.start_spinning()

        QTimer.singleShot(random.randint(2500,4000), self.stopSpinner)

    def stopSpinner(self):
        self.spinner.stop_spinning()

        
        sides = len(self.spinner.names)  
        angle = 360 / sides  
        top_right_angle = (360 / 4) % 360  
        top_right_index = int((top_right_angle + self.spinner.label_offset * angle) / angle) % sides  

        selected_name = self.spinner.names[top_right_index]
        self.displayName.setText(selected_name)

        
        self.names[selected_name] = str(int(self.names[selected_name]) + 1)
        self.refreshScroll(self.names)
        self.savedNames()


    def savedNames(self):
        index = self.dropdown.currentIndex()
        index_k = 2 * index
        index_v = index_k + 1
        with open("/Users/shreyas/Documents/Python/Work-in-progress projects/MATE group 3/data.txt", 'r') as f:
            lines = f.readlines()
        with open("/Users/shreyas/Documents/Python/Work-in-progress projects/MATE group 3/data.txt", 'w') as f:
            lines[index_k] = self.block[index] + " ".join(list(self.names.keys())) + "\n"
            lines[index_v] = self.block[index] + " ".join(list(self.names.values())) +"\n"
            f.writelines(lines)

    def readNames(self):
        with open("data.txt",'r') as f:
            lines = f.readlines()
        index = self.dropdown.currentIndex()
        lines_k = lines[index*2]
        lines_v = lines[(2 *index) + 1]
        lines_k = lines_k[3:]
        lines_v = lines_v[3:]
        lines_k = lines_k.split()
        lines_v = lines_v.split()
        self.names = {}
        for i in range(len(lines_k)):
            self.names[lines_k[i]] = lines_v[i]
        self.refreshScroll(self.names)


    def nameRemoval(self):
        name = self.name.text().title()
        self.name.clear()
        del self.names[name]
        self.refreshScroll(self.names)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.setStyleSheet('background-color : #87B1AE')
    window.setFixedSize(1200, 700)
    window.show()
    app.exec()
