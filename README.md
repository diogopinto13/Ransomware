# ⚠️ Educational Ransomware Simulation Project

## 📚 Overview

This project is a **client-server simulation** designed to demonstrate concepts related to:

* Network communication (sockets)
* Multi-threading
* Symmetric encryption (AES-256-GCM)
* Key derivation (PBKDF2)
* Basic command & control (C2) architecture
* GUI development with Tkinter

The system mimics the behavior of ransomware in a **controlled, educational environment**, where a client encrypts files and must complete a questionnaire to receive the decryption key.

---

## ⚠️ IMPORTANT DISCLAIMER

> 🚨 **THIS PROJECT IS FOR EDUCATIONAL PURPOSES ONLY**

This project simulates behaviors commonly associated with malware (such as file encryption and remote command execution) strictly for learning and research purposes.

* ❌ Do **NOT** use this code on systems you do not own or have explicit permission to test
* ❌ Do **NOT** deploy this in real-world environments
* ❌ Do **NOT** use this for malicious activities

The author assumes **no responsibility** for misuse of this code.

---

## 🧠 How It Works

### 🔹 Server (C2 Server)

The server:

* Listens for client connections
* Generates an encryption key using PBKDF2
* Sends encryption key + salt to clients
* Verifies answers to a questionnaire
* Releases the decryption key only if all answers are correct
* Can send remote commands to connected clients

---

### 🔹 Client

The client:

* Connects to the server
* Receives encryption key and encrypts files using AES-256-GCM
* Displays a GUI "lock screen"
* Prompts the user with questions
* Sends answers to the server for verification
* Requests decryption key after completing the questionnaire
* Decrypts files if allowed

---

### 🔹 Delivery GUI

A simple GUI simulates a fake application (e.g. “Download free music”) that:

* Launches the encryption process
* Starts communication with the server

---

## 🧩 Project Structure

```
.
├── server.py              # C2 server
├── encryptor.py          # Client main logic (encryption + GUI)
├── wait_commands.py      # Handles remote commands from server
├── deliver.py            # Fake delivery GUI
├── files/                # Test folder for encryption
└── README.md
```

---

## ⚙️ Requirements

* Python 3.8+
* Required libraries:

  ```
  conda env create -f environment.yml
  conda activate gui_app
  ```

---

## 🚀 How to Run

### 1️⃣ Start the Server

```bash
python3 c2server.py
```

* Enter a password (used to derive encryption key)
* Server starts listening on:

  * `127.0.0.1:4444` (client communication)
  * `127.0.0.1:4445` (command channel)

---

### 2️⃣ Start the Client

```bash
python3 encryptor.py
```

OR use the delivery GUI:

```bash
python3 deliver.py
```

---

### 3️⃣ Flow

1. Client connects to server
2. Files in `/files` directory are encrypted
3. GUI appears with a questionnaire
4. User answers questions
5. If all answers are correct → decryption key is sent
6. Files are decrypted

---

## 🔐 Security Concepts Demonstrated

* AES-256-GCM authenticated encryption
* PBKDF2 key derivation with salt
* Secure key transmission (base64 encoding)
* Thread-safe operations using locks
* Client-server protocol design

---

## ⚠️ Known Limitations

* No secure transport (no TLS)
* Basic protocol (no message framing)
* Hardcoded questions on client and server
* No persistence or advanced error handling
* GUI blocks networking thread (simplified design)

---

## 💡 Educational Goals

This project helps you understand:

* How ransomware *works internally*
* Why secure key management is critical
* How client-server architectures operate
* How attackers might structure control systems

---

## 🛑 Final Warning

> This code intentionally mimics harmful software behavior.

Use it **only in isolated environments** such as:

* Virtual machines
* Sandboxed systems
* Personal test directories

Never run this on important systems or real user data.

---

## 👨‍💻 Author

Educational project for learning cybersecurity and software engineering concepts.

---
