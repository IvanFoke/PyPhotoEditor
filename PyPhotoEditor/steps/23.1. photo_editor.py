from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter.ttk import Notebook
from PIL import Image, ImageFilter, ImageEnhance
import os
import pyperclip
import json

from image_info import ImageInfo
from enhance_slider_window import EnhanceSliderWindow


CONFIG_FILE = "config.json"


class PyPhotoEditor:
    def __init__(self):
        self.root = Tk()
        self.image_tabs = Notebook(self.root)
        self.opened_images = []
        self.last_viewed_images = []

        self.init()

        self.open_recent_menu = None

    def init(self):
        self.root.title("Py Photo Editor")
        self.root.iconphoto(True, PhotoImage(file="resources/icon.png"))
        self.image_tabs.enable_traversal()

        self.root.bind("<Escape>", self._close)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'w') as f:
                json.dump({"opened_images": [], "last_viewed_images": []}, f)
        else:
            self.load_images_from_config()

    def run(self):
        self.draw_menu()
        self.draw_widgets()

        self.root.mainloop()

    def draw_menu(self):
        menu_bar = Menu(self.root)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_new_images)

        self.open_recent_menu = Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Open Recent", menu=self.open_recent_menu)
        for path in self.last_viewed_images:
            self.open_recent_menu.add_command(label=path, command=lambda x=path: self.add_new_image(x))

        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_current_image)
        file_menu.add_command(label="Save as", command=self.save_image_as)
        file_menu.add_command(label="Save all", command=self.save_all_changes)
        file_menu.add_separator()
        file_menu.add_command(label="Close Image", command=self.close_current_image)
        file_menu.add_separator()
        file_menu.add_command(label="Delete Image", command=self.delete_current_image)
        file_menu.add_command(label="Move Image", command=self.move_current_image)
        file_menu.add_separator()

        clipboard_menu = Menu(file_menu, tearoff=0)
        clipboard_menu.add_command(label="Add image name to clipboard", command=lambda: self.save_to_clipboard("name"))
        clipboard_menu.add_command(label="Add image directory to clipboard", command=lambda: self.save_to_clipboard("dir"))
        clipboard_menu.add_command(label="Add image path to clipboard", command=lambda: self.save_to_clipboard("path"))
        file_menu.add_cascade(label="Clipboard", menu=clipboard_menu)
        
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._close)
        menu_bar.add_cascade(label="File", menu=file_menu)

        edit_menu = Menu(menu_bar, tearoff=0)

        rotate_menu = Menu(edit_menu, tearoff=0)
        rotate_menu.add_command(label="Rotate left by 90", command=lambda: self.rotate_current_image(90))
        rotate_menu.add_command(label="Rotate right by 90", command=lambda: self.rotate_current_image(-90))
        rotate_menu.add_command(label="Rotate left by 180", command=lambda: self.rotate_current_image(180))
        rotate_menu.add_command(label="Rotate right by 180", command=lambda: self.rotate_current_image(-180))

        flip_menu = Menu(edit_menu, tearoff=0)
        flip_menu.add_command(label="Flip horizontally", command=lambda: self.flip_current_image(Image.FLIP_LEFT_RIGHT))
        flip_menu.add_command(label="Flip vertically", command=lambda: self.flip_current_image(Image.FLIP_TOP_BOTTOM))

        resize_menu = Menu(edit_menu, tearoff=0)
        resize_menu.add_command(label="25% of original size", command=lambda: self.resize_current_image(25))
        resize_menu.add_command(label="50% of original size", command=lambda: self.resize_current_image(50))
        resize_menu.add_command(label="75% of original size", command=lambda: self.resize_current_image(75))
        resize_menu.add_command(label="125% of original size", command=lambda: self.resize_current_image(125))
        resize_menu.add_command(label="150% of original size", command=lambda: self.resize_current_image(150))
        resize_menu.add_command(label="200% of original size", command=lambda: self.resize_current_image(200))

        filter_menu = Menu(edit_menu, tearoff=0)
        filter_menu.add_command(label="Blur", command=lambda: self.apply_filter_to_current_image(ImageFilter.BLUR))
        filter_menu.add_command(label="Sharpen", command=lambda: self.apply_filter_to_current_image(ImageFilter.SHARPEN))
        filter_menu.add_command(label="Contour", command=lambda: self.apply_filter_to_current_image(ImageFilter.CONTOUR))
        filter_menu.add_command(label="Detail", command=lambda: self.apply_filter_to_current_image(ImageFilter.DETAIL))
        filter_menu.add_command(label="Smooth", command=lambda: self.apply_filter_to_current_image(ImageFilter.SMOOTH))

        crop_menu = Menu(edit_menu, tearoff=0)
        crop_menu.add_command(label="Start selection", command=self.start_crop_selection_of_current_image)
        crop_menu.add_command(label="Crop selected", command=self.crop_selection_of_current_image)

        convert_menu = Menu(edit_menu, tearoff=0)
        convert_menu.add_command(label="Black and white", command=lambda: self.convert_current_image("1"))
        convert_menu.add_command(label="Grayscale", command=lambda: self.convert_current_image("L"))
        convert_menu.add_command(label="RGB", command=lambda: self.convert_current_image("RGB"))
        convert_menu.add_command(label="RGBA", command=lambda: self.convert_current_image("RGBA"))
        convert_menu.add_command(label="CMYK", command=lambda: self.convert_current_image("CMYK"))
        convert_menu.add_command(label="LAB", command=lambda: self.convert_current_image("LAB"))
        convert_menu.add_command(label="HSV", command=lambda: self.convert_current_image("HSV"))
        convert_menu.add_command(label="Roll RGB colors", command=lambda: self.convert_current_image("roll"))
        convert_menu.add_command(label="Red", command=lambda: self.convert_current_image("R"))
        convert_menu.add_command(label="Green", command=lambda: self.convert_current_image("G"))
        convert_menu.add_command(label="Blue", command=lambda: self.convert_current_image("B"))

        enhance_menu = Menu(edit_menu, tearoff=0)
        enhance_menu.add_command(label="Color", command=lambda: self.enhance_current_image("Color", ImageEnhance.Color))
        enhance_menu.add_command(label="Contrast", command=lambda: self.enhance_current_image("Contrast", ImageEnhance.Contrast))
        enhance_menu.add_command(label="Brightness", command=lambda: self.enhance_current_image("Brightness", ImageEnhance.Brightness))
        enhance_menu.add_command(label="Sharpness", command=lambda: self.enhance_current_image("Sharpness", ImageEnhance.Sharpness))

        edit_menu.add_cascade(label="Rotate", menu=rotate_menu)
        edit_menu.add_cascade(label="Flip", menu=flip_menu)
        edit_menu.add_cascade(label="Resize", menu=resize_menu)
        edit_menu.add_separator()
        edit_menu.add_cascade(label="Filter", menu=filter_menu)
        edit_menu.add_cascade(label="Convert", menu=convert_menu)
        edit_menu.add_cascade(label="Enhance", menu=enhance_menu)
        edit_menu.add_separator()
        edit_menu.add_cascade(label="Crop", menu=crop_menu)

        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        self.root.configure(menu=menu_bar)

    def update_open_recent_menu(self):
        if self.open_recent_menu is None:
            return

        self.open_recent_menu.delete(0, "end")
        for path in self.last_viewed_images:
            self.open_recent_menu.add_command(label=path, command=lambda x=path: self.add_new_image(x))

    def draw_widgets(self):
        self.image_tabs.pack(fill="both", expand=1)

    def load_images_from_config(self):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        self.last_viewed_images = config["last_viewed_images"]
        paths = config["opened_images"]
        for path in paths:
            self.add_new_image(path)

    def open_new_images(self):
        image_paths = fd.askopenfilenames(filetypes=(("Images", "*.jpeg;*.jpg;*.png"), ))
        for image_path in image_paths:
            self.add_new_image(image_path)

            if image_path not in self.last_viewed_images:
                self.last_viewed_images.append(image_path)
            else:
                self.last_viewed_images.remove(image_path)
                self.last_viewed_images.append(image_path)
            
            if len(self.last_viewed_images) > 5:
                del self.last_viewed_images[0]
        
        self.update_open_recent_menu()

    def add_new_image(self, image_path):
        if not os.path.isfile(image_path):
            if image_path in self.last_viewed_images:
                self.last_viewed_images.remove(image_path)
                self.update_open_recent_menu()
            return

        opened_images = [info.path for info in self.opened_images]
        if image_path in opened_images:
            index = opened_images.index(image_path)
            self.image_tabs.select(index)
            return

        image = Image.open(image_path)
        image_tab = Frame(self.image_tabs)

        image_info = ImageInfo(image, image_path, image_tab)
        self.opened_images.append(image_info)

        # make the canvas expandable
        image_tab.rowconfigure(0, weight=1)
        image_tab.columnconfigure(0, weight=1)

        canvas = Canvas(image_tab, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky='nsew')
        canvas.update()  # wait till canvas is created
        
        image_info.set_canvas(canvas)

        self.image_tabs.add(image_tab, text=image_info.filename())
        self.image_tabs.select(image_tab)

    def current_image(self):
        current_tab = self.image_tabs.select()
        if not current_tab:
            return None
        tab_number = self.image_tabs.index(current_tab)
        return self.opened_images[tab_number]

    def save_current_image(self):
        image = self.current_image()
        if not image:
            return
        if not image.unsaved:
            return
        
        image.save()
        self.image_tabs.add(image.tab, text=image.filename())

    def save_image_as(self):
        image = self.current_image()
        if not image:
            return
        
        try:
            image.save_as()
            self.update_image_inside_app(image)
        except ValueError as e:
            mb.showerror("Save as error", str(e))
        
    def save_all_changes(self):
        for image_info in self.opened_images:
            if not image_info.unsaved:
                continue
            image_info.save()
            self.image_tabs.tab(image_info.tab, text=image_info.filename())

    def close_current_image(self):
        image = self.current_image()
        if not image:
            return
        
        if image.unsaved:
            if not mb.askyesno("Unsaved changes", "Close without saving changes?"):
                return

        image.close()
        self.image_tabs.forget(image.tab)
        self.opened_images.remove(image)

    def delete_current_image(self):
        image = self.current_image()
        if not image:
            return

        if not mb.askokcancel("Delete image", "Are you sure you want to delete image?\nThis operation is unrecoverable!"):
            return

        image.delete()
        self.image_tabs.forget(image.tab)
        self.opened_images.remove(image)

    def move_current_image(self):
        image = self.current_image()
        if not image:
            return

        image.move()
        self.update_image_inside_app(image)

    def update_image_inside_app(self, image_info):
        image_info.update_image_on_canvas()
        self.image_tabs.tab(image_info.tab, text=image_info.filename())

    def rotate_current_image(self, degrees):
        image = self.current_image()
        if not image:
            return
        
        image.rotate(degrees)
        image.unsaved = True
        self.update_image_inside_app(image)

    def flip_current_image(self, mode):
        image = self.current_image()
        if not image:
            return
        
        image.flip(mode)
        image.unsaved = True
        self.update_image_inside_app(image)

    def resize_current_image(self, percents):
        image = self.current_image()
        if not image:
            return

        image.resize(percents)
        image.unsaved = True
        self.update_image_inside_app(image)

    def apply_filter_to_current_image(self, filter_type):
        image = self.current_image()
        if not image:
            return

        image.filter(filter_type)
        image.unsaved = True
        self.update_image_inside_app(image)

    def start_crop_selection_of_current_image(self):
        image = self.current_image()
        if not image:
            return
        
        image.start_crop_selection()

    def crop_selection_of_current_image(self):
        image = self.current_image()
        if not image:
            return
        
        try:
            image.crop_selected_area()
            image.unsaved = True
            self.update_image_inside_app(image)
        except ValueError as e:
            mb.showerror("Crop error", str(e))

    def convert_current_image(self, mode):
        image = self.current_image()
        if not image:
            return
        
        try:
            image.convert(mode)
            image.unsaved = True
            self.update_image_inside_app(image)
        except ValueError as e:
            mb.showerror("Convert error", str(e))

    def enhance_current_image(self, name, enhance):
        image = self.current_image()
        if not image:
            return
        
        EnhanceSliderWindow(self.root, name, enhance, image, self.update_image_inside_app)

    def save_to_clipboard(self, mode):
        image = self.current_image()
        if not image:
            return
        
        if mode == "name":
            pyperclip.copy(image.filename(no_star=True))
        elif mode == "dir":
            pyperclip.copy(image.directory(no_star=True))
        elif mode == "path":
            pyperclip.copy(image.full_path(no_star=True))

    def save_images_to_config(self):
        paths = [info.full_path(no_star=True) for info in self.opened_images]
        images = {"opened_images": paths, "last_viewed_images": self.last_viewed_images}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(images, f, indent=4)

    def unsaved_images(self):
        for info in self.opened_images:
            if info.unsaved:
                return True
        return False

    def _close(self, event=None):
        if self.unsaved_images():
            if not mb.askyesno("Unsaved changes", "Got unsaved changes! Exit anyway?"):
                return

        self.save_images_to_config()
        self.root.quit()


if __name__ == "__main__":
    PyPhotoEditor().run()

