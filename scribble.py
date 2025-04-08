import sys
try:
    import numpy as np
except ModuleNotFoundError:
    print("Installing numpy...")
    sys.stdout.flush()
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    import numpy as np
try:
    import tkinter as tk
except ModuleNotFoundError:
    print("Installing tkinter...")
    sys.stdout.flush()
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tk"])
    import tkinter as tk
try:
    from tkinter import filedialog, messagebox
except ModuleNotFoundError:
    print("Installing tkinter...")
    sys.stdout.flush()
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tk"])
    from tkinter import filedialog, messagebox
try:
    from PIL import Image, ImageTk
except ModuleNotFoundError:
    print("Installing Pillow...")
    sys.stdout.flush()
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageTk
try:
    import tqdm
except ModuleNotFoundError:
    print("Installing tqdm...")
    sys.stdout.flush()
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])
    import tqdm

class ImageProcessor:
    def __init__(self, quality=3):
        self.quality = quality
        self.img_array = None
        self.processed = None

    def load_image(self, image_path):
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        self.img_array = np.array(img)
        self.processed = np.zeros(self.img_array.shape[:2], dtype=bool)

    def optimize_image(self):
        height, width, _ = self.img_array.shape
        code_lines = []

        print("Processing image...")
        progress_bar = tqdm.tqdm(total=height * width)

        for y in range(0, height, self.quality):
            for x in range(0, width, self.quality):
                if self.processed[y, x]:
                    progress_bar.update(1)
                    continue
                current_color = tuple(self.img_array[y, x])

                rect_width, rect_height = self.detect_rectangle(x, y, current_color)
                self.processed[y:y+rect_height, x:x+rect_width] = True

                code_lines.append(
                    f"  brain.Screen.drawRectangle({x}, {y}, {rect_width}, {rect_height}, vex::color({current_color[0]}, {current_color[1]}, {current_color[2]}));"
                )

                progress_bar.update(rect_width * rect_height)

        progress_bar.close()
        return "\n".join(code_lines)

    def detect_rectangle(self, x, y, current_color):
        rect_width = 0
        rect_height = 0

        # Ensure height and width are within bounds before proceeding
        height, width = self.img_array.shape[:2]

        while y + rect_height < height and all(
            x + w < width and tuple(self.img_array[y + rect_height, x + w]) == current_color for w in range(rect_width)
        ):
            rect_height += 1

        while x + rect_width < width and all(
            y + h < height and tuple(self.img_array[y + h, x + rect_width]) == current_color for h in range(rect_height)
        ):
            rect_width += 1

        return rect_width, rect_height

class GUI:
    def __init__(self, root):
        self.processor = ImageProcessor()
        self.root = root
        self.root.title("VEX Image Converter")
        self.image_label = tk.Label(self.root)
        self.image_label.pack()

        tk.Button(self.root, text="Load Image", command=self.load_image).pack()
        tk.Label(self.root, text="Quality:").pack()
        self.quality_slider = tk.Scale(self.root, from_=1, to=5, orient=tk.HORIZONTAL, command=self.set_quality)
        self.quality_slider.pack()
        tk.Button(self.root, text="Generate Code", command=self.generate_code).pack()

    def set_quality(self, val):
        self.processor.quality = int(val)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.bmp")])
        if file_path:
            self.processor.load_image(file_path)
            img = Image.open(file_path)
            img.thumbnail((300, 300))
            img_tk = ImageTk.PhotoImage(img)
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk

    def generate_code(self):
        vex_code = self.processor.optimize_image()
        with open("image.cpp", "w") as f:
            f.write("#include \"vex.h\"\n\n")
            f.write("using namespace vex;\n\n")
            f.write("int main() {\n")
            f.write(vex_code)
            f.write("\n  return 0;\n}")
        messagebox.showinfo("Success", "VEX code saved as 'image.cpp'")

def run_console_mode():
    image_path = input("Enter the path to the image: ")
    processor = ImageProcessor()
    processor.load_image(image_path)

    vex_code = processor.optimize_image()

    print("Saving generated VEX code...")
    with open("image.cpp", "w") as f:
        f.write("#include \"vex.h\"\n\n")
        f.write("using namespace vex;\n\n")
        f.write("int main() {\n")
        f.write(vex_code)
        f.write("\n  return 0;\n}")

    print("Generated VEX code in 'image.cpp'!")

def main():
    logo = '''
           ██████  ▄████▄   ██▀███   ██▓ ▄▄▄▄    ▄▄▄▄    ██▓    ▓█████ 
         ▒██    ▒ ▒██▀ ▀█  ▓██ ▒ ██▒▓██▒▓█████▄ ▓█████▄ ▓██▒    ▓█   ▀ 
         ░ ▓██▄   ▒▓█    ▄ ▓██ ░▄█ ▒▒██▒▒██▒ ▄██▒██▒ ▄██▒██░    ▒███   
           ▒   ██▒▒▓▓▄ ▄██▒▒██▀▀█▄  ░██░▒██░█▀  ▒██░█▀  ▒██░    ▒▓█  ▄ 
         ▒██████▒▒▒ ▓███▀ ░░██▓ ▒██▒░██░░▓█  ▀█▓░▓█  ▀█▓░██████▒░▒████▒
         ▒ ▒▓▒ ▒ ░░ ░▒ ▒  ░░ ▒▓ ░▒▓░░▓  ░▒▓███▀▒░▒▓███▀▒░ ▒░▓  ░░░ ▒░ ░
         ░ ░▒  ░ ░  ░  ▒     ░▒ ░ ▒░ ▒ ░▒░▒   ░ ▒░▒   ░ ░ ░ ▒  ░ ░ ░  ░
         ░  ░  ░  ░          ░░   ░  ▒ ░ ░    ░  ░    ░   ░ ░      ░   
               ░  ░ ░         ░      ░   ░       ░          ░  ░   ░  ░
                  ░                           ░       ░                
'''
    print(logo)
    mode = input("Choose mode: (1) Console or (2) GUI? ")
    if mode == "1":
        run_console_mode()
    elif mode == "2":
        root = tk.Tk()
        GUI(root)
        root.mainloop()
    else:
        print("Invalid choice. Please restart and select either 1 or 2.")

if __name__ == "__main__":
    main()
