import RPi.GPIO as GPIO
import random
from time import sleep
from RPLCD.i2c import CharLCD
import socket

# Define students for all classes
students = {
    "Class A2": [
        "Dimmock, Claire", "Gupta, Vardaan", "Hardcastle, Auric", "Jia, Irene", "Jiao, Gabriel",
        "Jung, Eli", "Lau, KJ", "Lee, Jenna", "Lingnau, Fritzy", "Moorjani, Noori",
        "Park, Sangweon", "Parpia, Jam", "Peng, Claire", "Rawat, Keshav", "Saadullah, Zakaria",
        "Thoman, Aaron", "Wang, Justin",
    ],
    "Class A3": [
        "Bhatia, Myra", "Brown, Simon", "Burnett, Ben", "Coppell, Claire", "Kim, Selin",
        "Li, Sophie", "Lin, Cindy", "McFadzen, Lily", "Metz, Jaci", "Narula, Shaurya",
        "Rosenkilde, Matilda", "Terry, Ella", "Tremarco, Nola", "Troija, Isabelle",
        "van Eldik, Felix", "Wheeler, Talia",
    ],
    "Class B1": [
        "Chopra, Diya", "Chopra, Shreyas", "Craig, Rohan", "Duran, James", "Gu, Jiawei",
        "Kim, Myoungjoon", "Landon, Colin", "Lee, Sumin", "Lin, HaiCheng Walter",
        "Nahata, Priyam", "Park, Lyle", "Sikhakollu, Phani", "Singh, Jasmeh",
        "Singh Kohli, Rysa", "Thompson, Austin", "Wang, Weihao",
    ],
    "Class B2": [
        "Anvekar, Mannat", "Bakhshi, Kareena", "Deshwal, Veehaan", "Dulat, Lucas",
        "Hopkins, Matthew", "Hsiao, Yue Jhen", "Jermyn, Anna Mae", "Kim, Andrew",
        "Kim, Isaac", "Lee, Kevin(Jeongwoo)Lee", "Li, Xingyue", "Liu, Minna", "Ma, Grace",
        "Oravec, Haven", "Sethi, Rohaan", "Steckler, Billy", "Vyas, Sara", "Welker, Layton",
    ],
    "Class B4": [
        "Aggarwal, Avni", "Arnold, Aidan", "Bai, Ken", "Bohra, Mia", "Chen, Adrian",
        "Chen, Melinda", "Chi, Amber", "Choi, Kaitlyn", "Chopra, Navya", "Fung, Isabella",
        "Kim, Yijoon", "Laroia, Leela", "Li, Changan", "Mathur, Azara", "Nakahara, Mirei",
        "Shih, Chantelle", "Sun, Kolb", "Yang, Amy", "Yeh, Matthew", "Yoon, Jisoo",
    ],
}

BUTTON_PIN_1 = 21
BUTTON_PIN_2 = 5
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_PIN_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

lcd = CharLCD('PCF8574', 0x3f)
names = {student: 0 for class_students in students.values() for student in class_students}
selected_class = list(students.keys())[0]
current_class_index = 0

# Set up server socket to listen for connections
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 5001))  # Bind to all available interfaces, port 5001
server_socket.listen(5)  # Listen for up to 5 incoming connections

def wait_for_press(button_pin):
    while GPIO.input(button_pin) == GPIO.HIGH:
        sleep(0.01)
    sleep(0.1)
    while GPIO.input(button_pin) == GPIO.LOW:
        sleep(0.01)

def choose_name():
    total_calls = sum(names.values())
    weights = [1 / (1 + count) for count in names.values()]
    chosen_name = random.choices(list(names.keys()), weights=weights, k=1)[0]
    names[chosen_name] += 1
    return chosen_name

def extract_first_name(full_name):
    return full_name.split(", ")[1]

def display_on_lcd(line1, line2=""):
    lcd.clear()
    lcd.write_string(line1)
    if line2:
        lcd.cursor_pos = (1, 0)
        lcd.write_string(line2)

try:
    while True:
        # Display initial message to select class
        display_on_lcd("Select Class")
        
        while True:
            if GPIO.input(BUTTON_PIN_1) == GPIO.LOW:
                current_class_index = (current_class_index + 1) % len(students)
                selected_class = list(students.keys())[current_class_index]
                display_on_lcd(f"{selected_class} Selected")
                wait_for_press(BUTTON_PIN_1)

            if GPIO.input(BUTTON_PIN_2) == GPIO.LOW:
                display_on_lcd(f"Class {selected_class}", "Confirmed")
                sleep(1)
                break

        display_on_lcd(f"Class {selected_class}", "Pick Name")

        while True:
            # Check for client connections
            client_socket, address = server_socket.accept()  # Accept the connection
            print(f"Connection from {address}")

            try:
                # Receive the data
                data = client_socket.recv(1024).decode()
                if data:
                    print(f"Received: {data}")
                    # Process the received data (update display, etc.)
                    first_name, class_name, times_called = data.split(',')
                    display_on_lcd(f"Name: {first_name}", f"Called: {times_called}")
                else:
                    print("No data received.")
            except Exception as e:
                print(f"Error: {e}")
            finally:
                client_socket.close()  # Close the client socket

            if GPIO.input(BUTTON_PIN_1) == GPIO.LOW:
                chosen_name = choose_name()
                first_name = extract_first_name(chosen_name)
                message = f"{first_name},{selected_class},{names[chosen_name]}"
                display_on_lcd(f"Name: {first_name}", f"Called: {names[chosen_name]}")
                wait_for_press(BUTTON_PIN_1)

            if GPIO.input(BUTTON_PIN_2) == GPIO.LOW:
                display_on_lcd("Goodbye")
                sleep(2)
                names = {student: 0 for class_students in students.values() for student in class_students}
                break
finally:
    server_socket.close()
    GPIO.cleanup()
