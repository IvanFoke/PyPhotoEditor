from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter.ttk import Notebook
from PIL import Image, ImageTk, ImageOps, ImageFilter
import os
import shutil
import pyperclip


class PyPhotoEditor:
    def __init__(self):
        self.root = Tk()
        self.image_tabs = Notebook(self.root)
        self.opened_images = []

        self.selection_top_x = 0
        self.selection_top_y = 0
        self.selection_bottom_x = 0
        self.selection_bottom_y = 0

        self.canvas_for_selection = None
        self.selection_rect = None

        self.init()

    def init(self):
        self.root.title("Py Photo Editor")
        self.root.iconphoto(True, PhotoImage(file="resources/icon.png"))
        self.image_tabs.enable_traversal()

        self.root.bind("<Escape>", self._close)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def run(self):
        self.draw_menu()
        self.draw_widgets()

        self.root.mainloop()

    def draw_menu(self):
        menu_bar = Menu(self.root)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_new_images)
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
        clipboard_menu.add_command(label="Add image name to clipboard", command=self.name_to_clipboard)
        clipboard_menu.add_command(label="Add image directory to clipboard", command=self.directory_to_clipboard)
        clipboard_menu.add_command(label="Add image path to clipboard", command=self.path_to_clipboard)
        file_menu.add_cascade(label="Clipboard", menu=clipboard_menu)
        
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._close)
        menu_bar.add_cascade(label="File", menu=file_menu)

        edit_menu = Menu(menu_bar, tearoff=0)
        transform_menu = Menu(edit_menu, tearoff=0)

        rotate_menu = Menu(transform_menu, tearoff=0)
        rotate_menu.add_command(label="Rotate left by 90", command=lambda: self.rotate_current_image(90))
        rotate_menu.add_command(label="Rotate right by 90", command=lambda: self.rotate_current_image(-90))
        rotate_menu.add_command(label="Rotate left by 180", command=lambda: self.rotate_current_image(180))
        rotate_menu.add_command(label="Rotate right by 180", command=lambda: self.rotate_current_image(-180))
        transform_menu.add_cascade(label="Rotate", menu=rotate_menu)

        flip_menu = Menu(edit_menu, tearoff=0)
        flip_menu.add_command(label="Flip horizontally", command=lambda: self.flip_current_image("horizontally"))
        flip_menu.add_command(label="Flip vertically", command=lambda: self.flip_current_image("vertically"))

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
        crop_menu.add_command(label="Start selection", command=self.start_area_selection_of_current_image)
        crop_menu.add_command(label="Stop selection", command=self.stop_area_selection_of_current_image)

        edit_menu.add_cascade(label="Transform", menu=transform_menu)
        edit_menu.add_cascade(label="Flip", menu=flip_menu)
        edit_menu.add_cascade(label="Resize", menu=resize_menu)
        edit_menu.add_cascade(label="Filter", menu=filter_menu)
        edit_menu.add_cascade(label="Crop", menu=crop_menu)

        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        self.root.configure(menu=menu_bar)

    def draw_widgets(self):
        self.image_tabs.pack(fill="both", expand=1)

    def open_new_images(self):
        image_paths = fd.askopenfilenames(filetypes=(("Images", "*.jpeg;*.jpg;*.png"), ))
        for image_path in image_paths:
            self.add_new_image(image_path)

    def add_new_image(self, image_path):
        image = Image.open(image_path)
        image_tk = ImageTk.PhotoImage(image)
        self.opened_images.append([image_path, image])

        image_tab = Frame(self.image_tabs)

        image_panel = Canvas(image_tab, width=image_tk.width(), height=image_tk.height(), bd=0, highlightthickness=0)
        image_panel.image = image_tk
        image_panel.create_image(0, 0, image=image_tk, anchor="nw")
        image_panel.pack(expand="yes")

        self.image_tabs.add(image_tab, text=os.path.split(image_path)[1])
        self.image_tabs.select(image_tab)

    def get_current_working_data(self):
        """returns current (tab, image, path)
        """
        current_tab = self.image_tabs.select()
        if not current_tab:
            return None, None, None
        tab_number = self.image_tabs.index(current_tab)
        path, image = self.opened_images[tab_number]

        return current_tab, path, image

    def save_current_image(self):
        current_tab, path, image = self.get_current_working_data()
        if not current_tab:
            return
        tab_number = self.image_tabs.index(current_tab)
        
        if path[-1] == '*':
            path = path[:-1]
            self.opened_images[tab_number][0] = path
            image.save(path)
            self.image_tabs.add(current_tab, text=os.path.split(path)[1])

    def save_image_as(self):
        current_tab, path, image = self.get_current_working_data()
        if not current_tab:
            return
        tab_number = self.image_tabs.index(current_tab)

        old_path, old_ext = os.path.splitext(path)
        if '*' in old_ext:
            old_ext = old_ext[:-1]
        
        new_path = fd.asksaveasfilename(initialdir=old_path, filetypes=(("Images", "*.jpeg;*.jpg;*.png"), ))
        if not new_path:
            return
        
        new_path, new_ext = os.path.splitext(new_path)
        if not new_ext:
            new_ext = old_ext
        elif old_ext != new_ext:
            mb.showerror("Incorrect extension", f"Got incorrect extension: {new_ext}. Old was: {old_ext}")
            return
        
        image.save(new_path + new_ext)
        image.close()

        del self.opened_images[tab_number]
        self.image_tabs.forget(current_tab)

        self.add_new_image(new_path + new_ext)

    def save_all_changes(self):
        for index, (path, image) in enumerate(self.opened_images):
            if path[-1] != '*':
                continue
            path = path[:-1]
            self.opened_images[index][0] = path
            image.save(path)
            self.image_tabs.tab(index, text=os.path.split(path)[1])

    def close_current_image(self):
        current_tab, path, image = self.get_current_working_data()
        if not current_tab:
            return
        index = self.image_tabs.index(current_tab)

        image.close()
        del self.opened_images[index]
        self.image_tabs.forget(current_tab)

    def delete_current_image(self):
        current_tab, path, image = self.get_current_working_data()
        if not current_tab:
            return
        index = self.image_tabs.index(current_tab)

        if not mb.askokcancel("Delete image", "Are you sure you want to delete image?\nThis operation is unrecoverable!"):
            return

        image.close()
        os.remove(path)

        del self.opened_images[index]
        self.image_tabs.forget(current_tab)

    def move_current_image(self):
        current_tab, old_path, image = self.get_current_working_data()
        if not current_tab:
            return
        index = self.image_tabs.index(current_tab)

        new_dir = fd.askdirectory(initialdir=os.path.dirname(old_path))
        if not new_dir:
            return
        
        new_path = os.path.join(new_dir, os.path.split(old_path)[1])

        image.close()
        shutil.move(old_path, new_path)

        del self.opened_images[index]
        self.image_tabs.forget(current_tab)

        self.add_new_image(new_path)

    def update_image_inside_app(self, current_tab, image):
        tab_number = self.image_tabs.index(current_tab)
        tab_frame = self.image_tabs.children[current_tab[current_tab.rfind('!'):]]
        canvas = tab_frame.children['!canvas']

        self.opened_images[tab_number][1] = image

        image_tk = ImageTk.PhotoImage(image)

        canvas.delete("all")
        canvas.image = image_tk
        canvas.configure(width=image_tk.width(), height=image_tk.height())
        canvas.create_image(0, 0, image=image_tk, anchor="nw")

        image_path = self.opened_images[tab_number][0]
        if image_path[-1] != '*':
            image_path += '*'
            self.opened_images[tab_number][0] = image_path
            image_name = os.path.split(image_path)[1]
            self.image_tabs.tab(current_tab, text=image_name)

    def rotate_current_image(self, degrees):
        current_tab, path, image = self.get_current_working_data()
        if not current_tab:
            return
        
        image = image.rotate(degrees)
        self.update_image_inside_app(current_tab, image)

    def flip_current_image(self, flip_type):
        current_tab, path, image = self.get_current_working_data()
        if not current_tab:
            return
        
        if flip_type == "horizontally":
            image = ImageOps.mirror(image)
        elif flip_type == "vertically":
            image = ImageOps.flip(image)

        self.update_image_inside_app(current_tab, image)

    def resize_current_image(self, percents):
        current_tab, path, image = self.get_current_working_data()
        if not current_tab:
            return

        w, h = image.size
        w = (w * percents) // 100
        h = (h * percents) // 100

        image = image.resize((w, h), Image.ANTIALIAS)
        self.update_image_inside_app(current_tab, image)

    def apply_filter_to_current_image(self, filter_type):
        current_tab, path, image = self.get_current_working_data()
        if not current_tab:
            return
        
        image = image.filter(filter_type)
        self.update_image_inside_app(current_tab, image)

    def start_area_selection_of_current_image(self):
        current_tab = self.image_tabs.select()
        if not current_tab:
            return
        tab_frame = self.image_tabs.children[current_tab[current_tab.rfind('!'):]]
        canvas = tab_frame.children['!canvas']

        self.canvas_for_selection = canvas
        self.selection_rect = canvas.create_rectangle(
            self.selection_top_x, self.selection_top_y, 
            self.selection_bottom_x, self.selection_bottom_y, 
            dash=(10, 10), fill='', outline="white", width=2    
        )

        canvas.bind("<Button-1>", self.get_selection_start_pos)
        canvas.bind("<B1-Motion>", self.update_selection_end_pos)

    def get_selection_start_pos(self, event):
        self.selection_top_x, self.selection_top_y = event.x, event.y

    def update_selection_end_pos(self, event):
        self.selection_bottom_x, self.selection_bottom_y = event.x, event.y
        if self.canvas_for_selection is not None and self.selection_rect is not None:
            self.canvas_for_selection.coords(
                self.selection_rect, 
                self.selection_top_x, self.selection_top_y,
                self.selection_bottom_x, self.selection_bottom_y
            )

    def stop_area_selection_of_current_image(self):
        self.canvas_for_selection.unbind("<Button-1>")
        self.canvas_for_selection.unbind("<B1-Motion>")

        self.canvas_for_selection.delete(self.selection_rect)

        self.crop_current_image()

        self.selection_rect = None
        self.canvas_for_selection = None
        self.selection_top_x, self.selection_top_y = 0, 0
        self.selection_bottom_x, self.selection_bottom_y = 0, 0

    def crop_current_image(self):
        current_tab, path, image = self.get_current_working_data()
        if not current_tab:
            return
        
        image = image.crop((
            self.selection_top_x, self.selection_top_y,
            self.selection_bottom_x, self.selection_bottom_y
        ))

        self.update_image_inside_app(current_tab, image)

    def name_to_clipboard(self):
        current_tab, path, image = self.get_current_working_data()
        if not current_tab:
            return
        
        name = os.path.split(path)[1]
        pyperclip.copy(name)

        mb.showinfo("Clipboard", f"Name '{name}' added to clipboard!")

    def directory_to_clipboard(self):
        current_tab, path, image = self.get_current_working_data()
        if not current_tab:
            return
        
        directory = os.path.split(path)[0]
        pyperclip.copy(directory)

        mb.showinfo("Clipboard", f"Directory '{directory}' added to clipboard!")

    def path_to_clipboard(self):
        current_tab, path, image = self.get_current_working_data()
        if not current_tab:
            return
        
        pyperclip.copy(path)

        mb.showinfo("Clipboard", f"Path '{path}' added to clipboard!")

    def unsaved_images(self):
        for path, _ in self.opened_images:
            if path[-1] == "*":
                return True
        return False

    def _close(self, event=None):
        if self.unsaved_images():
            if not mb.askyesno("Unsaved changes", "Got unsaved changes! Exit anyway?"):
                return

        self.root.quit()


if __name__ == "__main__":
    PyPhotoEditor().run()

