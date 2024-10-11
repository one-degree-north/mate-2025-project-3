import socket

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.bind(('0.0.0.0',5001))  # Listen on all available interfaces
    client_socket.listen(1)
    print("Waiting for Raspberry Pi to connect...")

    conn, addr = client_socket.accept()
    print(f"Connected to {addr}")

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            received_message = data.decode()
            first_name, class_name, times_called = received_message.split(',')
            print(f"Name: {first_name}, Class: {class_name}, Times Called: {times_called}")

    finally:
        conn.close()
        client_socket.close()

start_client()
