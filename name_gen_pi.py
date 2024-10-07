import RPi.GPIO as GPIO
import random
import time
from RPLCD.i2c import CharLCD

students = {
    "Class 1": [
        "Aggarwal, Avni", "Arnold, Aidan", "Bai, Ken", "Bohra, Mia", "Chen, Adrian",
        "Chen, Melinda", "Chi, Amber", "Choi, Kaitlyn", "Chopra, Navya", "Fung, Isabella",
        "Kim, Yijoon", "Laroia, Leela", "Li, Changan", "Mathur, Azara", "Nakahara, Mirei",
        "Shih, Chantelle", "Sun, Kolb", "Yang, Amy", "Yeh, Matthew", "Yoon, Jisoo",
    ],
    "Class 2": [
        "Anvekar, Mannat", "Bakhshi, Kareena", "Deshwal, Veehaan", "Dulat, Lucas",
        "Hopkins, Matthew", "Hsiao, Yue Jhen", "Jermyn, Anna Mae", "Kim, Andrew",
        "Kim, Isaac", "Lee, Kevin(Jeongwoo)Lee", "Li, Xingyue", "Liu, Minna", "Ma, Grace",
        "Oravec, Haven", "Sethi, Rohaan", "Steckler, Billy", "Vyas, Sara", "Welker, Layton",
    ],
    "Class 3": [
        "Chopra, Diya", "Chopra, Shreyas", "Craig, Rohan", "Duran, James", "Gu, Jiawei",
        "Kim, Myoungjoon", "Landon, Colin", "Lee, Sumin", "Lin, HaiCheng Walter",
        "Nahata, Priyam", "Park, Lyle", "Sikhakollu, Phani", "Singh, Jasmeh",
        "Singh Kohli, Rysa", "Thompson, Austin", "Wang, Weihao",
    ],
    "Class 4": [
        "Bhatia, Myra", "Brown, Simon", "Burnett, Ben", "Coppell, Claire",
        "Kim, Selin", "Li, Sophie", "Lin, Cindy", "McFadzen, Lily",
        "Metz, Jaci", "Narula, Shaurya", "Rosenkilde, Matilda", "Terry, Ella",
        "Tremarco, Nola", "Troija, Isabelle", "van Eldik, Felix", "Wheeler, Talia",
    ],
    "Class 5": [
        "Dimmock, Claire", "Gupta, Vardaan", "Hardcastle, Auric", "Jia, Irene", "Jiao, Gabriel",
        "Jung, Eli", "Lau, KJ", "Lee, Jenna", "Lingnau, Fritzy", "Moorjani, Noori",
        "Park, Sangweon", "Parpia, Jam", "Peng, Claire", "Rawat, Keshav", "Saadullah, Zakaria",
        "Thoman, Aaron", "Wang, Justin",
    ],
}

BUTTON_PIN_1 = 21  # For navigating/selecting classes
BUTTON_PIN_2 = 20  # For selecting students and exiting

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_PIN_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

lcd = CharLCD('PCF8574', 0x3f)

classes = list(students.keys())
class_index = 0
selected_class = None
names = {student: 0 for class_students in students.values() for student in class_students}

last_press_time = 0
double_click_threshold = 0.3  # Time to detect double click


def display_class(class_name):
    lcd.clear()
    lcd.write_string(f"{class_name} Selected")


def display_name_on_lcd(name):
    lcd.clear()
    lcd.write_string(f"Name: {name}")  
    lcd.cursor_pos = (1, 0)  
    lcd.write_string(f"Called: {names[name]}")  


def choose_name():
    class_list = students[selected_class]
    total_calls = sum(names[student] for student in class_list)
    
    if total_calls == 0:
        weights = [1 for _ in class_list]
    else:
        weights = [1 / (1 + names[student]) for student in class_list]

    chosen_name = random.choices(class_list, weights=weights, k=1)[0]
    names[chosen_name] += 1
    return chosen_name


def wait_for_press(button_pin):
    while GPIO.input(button_pin) == GPIO.HIGH:
        time.sleep(0.01)
    time.sleep(0.1)
    while GPIO.input(button_pin) == GPIO.LOW:
        time.sleep(0.01)


def navigate_classes():
    global class_index
    class_index = (class_index + 1) % len(classes)
    lcd.clear()
    lcd.write_string(f"Class {class_index + 1}: {classes[class_index]}")


try:
    lcd.clear()
    lcd.write_string("Waiting for input...")
    
    while True:
        if GPIO.input(BUTTON_PIN_1) == GPIO.LOW:
            current_time = time.time()
            
            if current_time - last_press_time < double_click_threshold:
                # Double click detected, select the class
                selected_class = classes[class_index]
                display_class(f"Class {class_index + 1} Selected")
            else:
                # Single click detected, navigate
                navigate_classes()
            
            last_press_time = current_time
            wait_for_press(BUTTON_PIN_1)
        
        if selected_class and GPIO.input(BUTTON_PIN_2) == GPIO.LOW:
            # Button 2 pressed, choose a name and exit loop
            chosen_name = choose_name()
            display_name_on_lcd(chosen_name)
            wait_for_press(BUTTON_PIN_2)

finally:
    GPIO.cleanup()
