from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QLineEdit
from PyQt6.QtWidgets import QFrame, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QScrollArea, QComboBox
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
import random
import math
import socket
import time



class SpinnerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.segment_colors = [
            [QColor(229, 107, 111), QColor(255, 209, 102), QColor(202, 240, 248)],
            [QColor(202, 240, 248), QColor(229, 107, 111), QColor(255, 209, 102)],
            [QColor(255, 209, 102), QColor(202, 240, 248), QColor(229, 107, 111)]
        ]
        self.names = []
        self.current_set_index = 0
        self.label_offset = 0
        self.setFixedSize(500, 500)
        self.slow = False

    def start_spinning(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_colors)
        self.timer.start(100)

    def stop_spinning(self):
        self.slow = True
        self.timer.stop()

    def update_colors(self):
        self.current_set_index = (self.current_set_index + 1) % len(self.segment_colors)
        self.label_offset = (self.label_offset + 1) % len(self.names)
        self.update()

    def paintEvent(self, event):
        if not self.names:
            # Draw empty spinner
            painter.setBrush(QColor(200, 200, 200))  # Light grey color for the empty wheel
            painter.drawEllipse(center_x - radius, center_y - radius, 2 * radius, 2 * radius)
            
            # Draw "No Names Available" text in the center
            font = QFont("Arial", 20)
            painter.setFont(font)
            painter.setPen(Qt.GlobalColor.black)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No Names Available")
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        center_x, center_y = 250, 250
        radius = 200
        sides = len(self.names)
        angle = 360 / sides

        font_size = max(12, int(180 / sides))
        font = QFont("Arial", font_size)
        font.setWeight(QFont.Weight.Bold)
        painter.setFont(font)

        for i in range(sides):
            start_angle = int(angle * i * 16)
            span_angle = int(angle * 16)
            painter.setBrush(self.segment_colors[self.current_set_index][i % 3])
            painter.drawPie(center_x - radius, center_y - radius, 2 * radius, 2 * radius, start_angle, span_angle)

            angle_rad = math.radians(angle * i + angle / 2)
            label_radius = radius * 0.7
            label_x = center_x + label_radius * math.cos(angle_rad)
            label_y = center_y - label_radius * math.sin(angle_rad)

            label_index = (i + self.label_offset) % len(self.names)
            painter.setPen(Qt.GlobalColor.black)
            painter.save()
            painter.translate(label_x, label_y)
            painter.rotate(-angle * i - angle / 2)
            painter.drawText(-30, 10, self.names[label_index])
            painter.restore()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.HOST = '192.168.2.2'  # Raspberry Pi IP address
        self.PORT = 12345          # Port number
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client_socket.connect((self.HOST, self.PORT))
            print("Connected to Raspberry Pi")
        except socket.error as e:
            print(f"Socket error: {e}")

        # Set socket to non-blocking mode
        self.client_socket.setblocking(False)

        # Timer to check for incoming data periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.receive_data)
        self.timer.start(100)  # Check every 100ms

        self.main_widget = QStackedWidget()
        self.setCentralWidget(self.main_widget)

        # Create screen 1 (spinner and random name display)
        self.screen1 = QWidget()
        self.layout1 = QVBoxLayout()
        self.layout2 = QHBoxLayout()
        self.layout3 = QHBoxLayout()

        # Center the layout
        self.layout1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.spinner = SpinnerWidget()
        self.spinner.setFixedSize(500, 500)  # Adjust the size to prevent overlap

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

        self.randomButton = QPushButton("Press for name!")
        self.randomButton.setFixedSize(300, 100)
        self.randomButton.setStyleSheet('background-color : #CE8989; font-size : 24px;')
        self.randomButton.clicked.connect(self.startSpinner)

        # Create a horizontal layout for the label and switch button
        self.name_layout = QHBoxLayout()
        self.displayName = QLabel("(name)")
        self.displayName.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.displayName.setStyleSheet('background-color : #CE8989; font-size : 50px; color : black;')
        self.displayName.setFixedSize(300, 100)

        self.switchButton1 = QPushButton("Go to Data screen")
        self.switchButton1.setFixedSize(150, 50)
        self.switchButton1.setStyleSheet('background-color : #CE8989; font-size : 18px; border-radius: 10px;')
        self.switchButton1.clicked.connect(self.show_screen2)

        # Add label and switch button to the horizontal layout
        self.name_layout.addWidget(self.switchButton1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.name_layout.addWidget(self.displayName, alignment=Qt.AlignmentFlag.AlignCenter)
        #self.name_layout.addWidget(self.dropdown, alignment=Qt.AlignmentFlag.AlignCenter)
        self.name_layout.setSpacing(700)
        self.name_layout.setContentsMargins(0,0,1260,0)


        # Add widgets to the layout with spacing
        self.layout1.addStretch()  # Add stretchable space before the widgets
        
        self.layout2.addWidget(self.dropdown, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout2.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout2.setSpacing(350)
        self.layout2.setContentsMargins(0,0,800,500)
        self.layout1.addLayout(self.layout2)
        
        self.layout3.addWidget(self.randomButton, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout3.setContentsMargins(0,220, 0, 0)
        self.layout1.addLayout(self.layout3)
        
        self.layout1.addWidget(self.dropdown, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout1.addLayout(self.name_layout)  # Add the horizontal layout to the main layout
        #iself.layout1.addStretch()  # Add stretchable space after the widgets
        self.layout1.setSpacing(0)


        self.screen1.setLayout(self.layout1)
        self.main_widget.addWidget(self.screen1)

        self.arrow = QLabel(self.screen1)
        self.arrow.setPixmap(QPixmap("arrow2.png").scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))
        self.arrow.setFixedSize(50,50)
        self.arrow.raise_()
        self.arrow.setGeometry(830,200,50,50)


        # Create screen 2 (name list, add/remove functionality)
        self.screen2 = QWidget()
        self.layout2 = QVBoxLayout()
        self.scroll_layout = QVBoxLayout()

        self.name = QLineEdit()
        self.name.setPlaceholderText("Enter name...")
        self.name.setStyleSheet(''' background-color : white; color : black;
                                        font-size : 16px;''')

        self.addName_button = QPushButton("Add")
        self.addName_button.setStyleSheet(''' background-color : #2196F3; color : black;
                                        font-size : 14px;''')

        self.removeName_button = QPushButton("Remove")
        self.removeName_button.setStyleSheet(''' background-color : #2196F3; color : black;
                                        font-size : 14px;''')


        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(''' background-color: #DEDEDE; color:black;font-size:30px''')
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_widget = QWidget()
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll.setWidget(self.scroll_widget)
        self.scroll_layout.addWidget(self.scroll_widget)

        self.switchButton2 = QPushButton("Go to Spinner")
        self.switchButton2.setFixedSize(150, 50)
        self.switchButton2.setStyleSheet('background-color : #CE8989; font-size : 18px; border-radius: 10px;')

        self.layout2.addWidget(self.name)
        #self.layout2.addWidget(self.freq)
        self.layout2.addWidget(self.addName_button)
        self.layout2.addWidget(self.removeName_button)
        self.layout2.addWidget(self.scroll)
        self.layout2.addWidget(self.switchButton2)

        self.screen2.setLayout(self.layout2)
        self.main_widget.addWidget(self.screen2)
        self.names = {'shreyas': '1', 'jackson': '3', 'hang': '4'}
        self.refreshScroll(self.names)

        
        self.addName_button.clicked.connect(self.nameAdditon)
        self.removeName_button.clicked.connect(self.nameRemoval)
        self.switchButton2.clicked.connect(self.show_screen1)

        self.readNames()
        self.spinner.names = list(self.names.keys())
        self.spinner.update()
        

    def receive_data(self):
        try:
            data = self.client_socket.recv(1024).decode('utf-8')
            if data:
                print(f"Received: {data}")
                self.displayName.setText(data.split(',')[0])  # Update UI with the received data
        except BlockingIOError:
            # No data received, keep waiting
            return  # Just return to avoid freezing
        except Exception as e:
            print(f"Error receiving data: {e}")
    def startSpinner(self):
        self.spinner.names = list(self.names.keys())
        self.spinner.start_spinning()
        QTimer.singleShot(random.randint(2500, 4000), self.stopSpinner)

    def stopSpinner(self):
        self.spinner.stop_spinning()
        sides = len(self.spinner.names)
        angle = 360 / sides
        right_angle = 0
        top_right_index = int((right_angle + self.spinner.label_offset * angle) / angle) % sides
        self.selected_name = self.spinner.names[top_right_index]
        self.displayName.setText(self.selected_name)
        
        # Update frequency count
        self.names[self.selected_name] = str(int(self.names[self.selected_name]) + 1)
        
        # Construct the message to send
        message = f"{self.selected_name},{self.dropdown.currentText()},{self.names[self.selected_name]}"
        self.send_data(message)  # Call the send_data function to send the message
    def send_data(self, message):
        try:
            self.client_socket.sendall(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending data: {e}")

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
        self.spinner.names = list(self.names.keys())
        self.spinner.update()

    def nameAdditon(self):
        name = self.name.text().title()
        temp_names = {name: "0"}
        self.names.update(temp_names)
        self.refreshScroll(self.names)
        self.name.clear()
        self.spinner.names = list(self.names.keys())
        self.spinner.update()
        self.spinner.names = list(self.names.keys())
        self.spinner.update()

    def nameRemoval(self):
        name = self.name.text().title()
        if name in self.names:
            del self.names[name]
            self.refreshScroll(self.names)
            self.spinner.names = list(self.names.keys())
            self.spinner.update()
        self.name.clear()  # Clear the input field after removal


    def refreshScroll(self, names):
        for i in reversed(range(self.scroll_layout.count())):
            widget_to_remove = self.scroll_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)
        for name in names:
            name_label = QLabel(name + " - " + names[name])
            self.scroll_layout.addWidget(name_label)
        self.scroll_widget.adjustSize()
    def closeEvent(self, event):
        self.client_socket.close()  # Ensure socket is closed when the window is closed
        event.accept()
    def show_screen1(self):
        self.main_widget.setCurrentWidget(self.screen1)

    def show_screen2(self):
        self.main_widget.setCurrentWidget(self.screen2)




if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.setStyleSheet('background-color : #87B1AE')
    window.setFixedSize(1200, 700)
    window.show()
    app.exec()
