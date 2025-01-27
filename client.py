
import socket
import threading
from config import SERVER_HOST, SERVER_PORT

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            print(message)
        except:
            print("Disconnected from the server.")
            client_socket.close()
            break

def start_client():
    username = input("Enter your username: ")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    client_socket.send(username.encode('utf-8'))

    threading.Thread(target=receive_messages, args=(client_socket,)).start()

    while True:
        message = input()
        if message.lower() == "exit":
            client_socket.close()
            break
        client_socket.send(message.encode('utf-8'))

if __name__ == "__main__":
    start_client()