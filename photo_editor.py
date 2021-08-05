from tkinter import *
from tkinter import filedialog as fd
from PIL import Image, ImageTk


class PyPhotoEditor:
    def __init__(self):
        self.root = Tk()
        self.init()

    def init(self):
        self.root.title("Py Photo Editor")
        self.root.iconphoto(True, PhotoImage(file="resources/icon.png"))

        self.root.bind("<Escape>", self._close)

    def run(self):
        self.draw_menu()
        self.draw_widgets()

        self.root.mainloop()

    def draw_menu(self):
        menu_bar = Menu(self.root)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_new_image)
        menu_bar.add_cascade(label="File", menu=file_menu)

        self.root.configure(menu=menu_bar)

    def draw_widgets(self):
        pass

    def open_new_image(self):
        image_path = fd.askopenfilename(filetypes=(("Images", "*.jpeg;*.jpg;*.png"), ))
        image = ImageTk.PhotoImage(Image.open(image_path))
        image_panel = Label(self.root, image=image)
        image_panel.image = image
        image_panel.pack()

    def _close(self, event):
        self.root.quit()


if __name__ == "__main__":
    PyPhotoEditor().run()

