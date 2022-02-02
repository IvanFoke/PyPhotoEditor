from PIL import Image, ImageTk, ImageOps, ImageFilter, ImageEnhance
import numpy as np


class ImageEdit:
    def __init__(self, image):
        self.original_image = image
        self.image = image.copy()

        self.canvas = None

    @property
    def image_tk(self):
        return ImageTk.PhotoImage(self.image)

    def update_image_on_canvas(self):
        if self.canvas is None:
            raise RuntimeError("Canvas of image not given")
        
        image_tk = self.image_tk

        self.canvas.delete("all")
        self.canvas.configure(width=self.image.width, height=self.image.height)
        self.canvas.create_image(0, 0, image=image_tk, anchor="nw")
        self.canvas.image = image_tk

    def rotate(self, degrees):
        self.image = self.image.rotate(degrees)

    def flip(self, mode):
        self.image = self.image.transpose(mode)

    def resize(self, percents):
        w, h = self.image.size
        w = (w * percents) // 100
        h = (h * percents) // 100

        self.image = self.image.resize((w, h), Image.ANTIALIAS)

    def filter(self, filter_type):
        self.image = self.image.filter(filter_type)

    def convert(self, mode):
        if mode == "roll":
            if self.image.mode != "RGB":
                raise ValueError(f"Can't roll image with not RGB mode '{self.image.mode}'")
            
            self.image = Image.fromarray(np.array(self.image)[:,:,::-1])
            return
        elif mode in "R G B".split(' '):
            if self.image.mode != "RGB":
                raise ValueError(f"Can't split channel of image with not RGB mode '{self.image.mode}'")

            a = np.array(self.image)
            a[:,:,(mode!="R", mode!="G", mode!="B")] *= 0
            self.image = Image.fromarray(a)
            return
        
        try:
            self.image = self.image.convert(mode)
        except ValueError as e:
            raise ValueError(f"Conversion error: '{e}'")

