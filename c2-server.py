import threading
import socket
import os

HOST = "127.0.0.1"
PORT = 4444
CLIENT_HANDLER_THREADS = list()

def handle_client(client_socket: socket):
    # Handle client communication here
    pass

def execute_command(command: str):
    for client in CLIENT_HANDLER_THREADS:
        # Send command to client
        pass

def instruction_handler():
    intput = input("Enter command to execute on clients: ")
    while intput.lower() != "exit":
        execute_command(intput)
        intput = input("Enter command to execute on clients: ")

def main():
    print("Starting C2 server...")

    instruction_handler_thread = threading.Thread(target=instruction_handler)
    instruction_handler_thread.start()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    global CLIENT_HANDLER_THREADS
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")

        CLIENT_HANDLER_THREADS.append(threading.Thread(target=handle_client, args=(client_socket,)))
        CLIENT_HANDLER_THREADS[-1].start()

if __name__ == "__main__":
    main()