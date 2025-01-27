import socket
import threading
import time
from config import MAX_CLIENTS, HISTORY_SIZE, SERVER_HOST, SERVER_PORT

clients = {}
chat_history = []
lock = threading.Lock()

def broadcast(message, sender_username=None):
    with lock:
        for username, client_socket in clients.items():
            if username != sender_username:
                try:
                    client_socket.send(message.encode('utf-8'))
                except:
                    remove_client(username)

def remove_client(username):
    with lock:
        if username in clients:
            clients[username].close()
            del clients[username]
            broadcast(f"[SERVER] {username} has left the chat.".encode('utf-8'))

def handle_client(client_socket, client_address):
    try:
        username = client_socket.recv(1024).decode('utf-8')
        if username in clients:
            client_socket.send("ERROR: Username already taken.".encode('utf-8'))
            client_socket.close()

        with lock:
            if len(clients) >= MAX_CLIENTS:
                client_socket.send("ERROR: Server is full.".encode('utf-8'))
                print(f"Server Full. Rejected client: {username}")
                client_socket.close()

            clients[username] = client_socket

        broadcast(f"[SERVER] {username} has joined the chat.")
        print(f"New client connected: {username}")
        print(f"Clients dictionary: {clients}")

        for entry in chat_history[-HISTORY_SIZE:]:
            client_socket.send(f"[HISTORY] {entry[0]} | {entry[1]}: {entry[2]}".encode('utf-8'))

        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break

            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {username}: {message}")
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            chat_history.append((timestamp, username, message))

            broadcast(f"[{timestamp}] {username}: {message}", sender_username=username)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        remove_client(username)

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"Server started on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"New connection from {client_address}")
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

if __name__ == "__main__":
    start_server()
