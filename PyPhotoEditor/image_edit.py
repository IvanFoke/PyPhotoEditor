from PIL import Image, ImageTk, ImageOps, ImageFilter, ImageEnhance
import numpy as np
from coordinates import Rect


class ImageEdit:
    def __init__(self, image):
        self.original_image = image
        self.image = image.copy()

        self.canvas = None
        self.zoom_container = None
        self.image_container = None

        self.imscale = 1.0
        self.zoom_delta = 1.3

        self.sel_start_x = 0
        self.sel_start_y = 0
        self.sel_stop_x = 0
        self.sel_stop_y = 0
        self.sel_rect = None

    @property
    def image_tk(self):
        return ImageTk.PhotoImage(self.image)

    def set_canvas(self, canvas):
        self.canvas = canvas
        self._bind_zoom()
        self.zoom_container = self.canvas.create_rectangle(0, 0, self.image.width, self.image.height, width=0)
        self._show_zoomed_image()

    def update_image_on_canvas(self):
        if self.canvas is None:
            raise RuntimeError("Canvas of image not given")
        
        self._show_zoomed_image()

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

    def start_crop_selection(self):
        self.sel_rect = self.canvas.create_rectangle(
            self.sel_start_x, self.sel_start_y, 
            self.sel_stop_x, self.sel_stop_y,
            dash=(10, 10), fill="cyan", width=1, 
            stipple="gray25", outline="black"
        )

        self.canvas.bind("<Button-1>", self._get_selection_start)
        self.canvas.bind("<B1-Motion>", self._udate_selection_stop)

    def _get_selection_start(self, event):
        self.sel_start_x, self.sel_start_y = event.x, event.y

    def _udate_selection_stop(self, event):
        self.sel_stop_x, self.sel_stop_y = event.x, event.y
        self.canvas.coords(self.sel_rect, self.sel_start_x, self.sel_start_y, self.sel_stop_x, self.sel_stop_y)

    def crop_selected_area(self):
        if self.sel_rect is None:
            raise ValueError("Got no selection area for Crop operation")
        
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.delete(self.sel_rect)

        if self.sel_start_x > self.sel_stop_x:
            self.sel_start_x, self.sel_stop_x = self.sel_stop_x, self.sel_start_x
        if self.sel_start_y > self.sel_stop_y:
            self.sel_start_y, self.sel_stop_y = self.sel_stop_y, self.sel_start_y
        
        self.image = self.image.crop([self.sel_start_x, self.sel_start_y, self.sel_stop_x, self.sel_stop_y])

        self.sel_rect = None
        self.sel_start_x, self.sel_start_y = 0, 0
        self.sel_stop_x, self.sel_stop_y = 0, 0

    def get_enhancer(self, enhacer):
        return enhacer(self.image)
    
    def set_image(self, image):
        self.image = image

    def _bind_zoom(self):
        self.canvas.bind("<ButtonPress-1>", self._move_from)
        self.canvas.bind("<B1-Motion>", self._move_to)
        self.canvas.bind("<MouseWheel>", self._zoom_with_wheel)  # Windows and MacOS
        self.canvas.bind("<Button-4>", self._zoom_with_wheel)  # Linux
        self.canvas.bind("<Button-5>", self._zoom_with_wheel)  # Linux
        
    def _unbind_zoom(self):
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<MouseWheel>")
        self.canvas.unbind("<Button-4>")
        self.canvas.unbind("<Button-5>")

    def _move_from(self, event):
        self.canvas.scan_mark(event.x, event.y)
    
    def _move_to(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self._show_zoomed_image()

    def _zoom_with_wheel(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        bbox = self.canvas.bbox(self.zoom_container)
        image_area = Rect(*bbox)

        if not (image_area.x0 < x < image_area.x1 and image_area.y0 < y < image_area.y1):
            return
        
        scale = 1.0
        # event.num - Linux, event.delta - Windows
        if event.num == 5 or event.delta == -120:
            # scroll down
            i = min(self.image.width, self.image.height)
            # image is less than 30 pixels
            if int(i * self.imscale) < 30:
                return
            self.imscale /= self.zoom_delta
            scale /= self.zoom_delta
        
        if event.num == 4 or event.delta == 120:
            # scroll up
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
            # visible area is greater than scale
            if i < self.imscale:
                return
            self.imscale *= self.zoom_delta
            scale *= self.zoom_delta

        # rescale all canvas objects
        self.canvas.scale('all', x, y, scale, scale)
        self._show_zoomed_image()

    def _show_zoomed_image(self, event=None):
        bbox = self.canvas.bbox(self.zoom_container)
        rect = Rect(*bbox)
        # Remove 1 pixel at the sides of bbox
        rect.x0 += 1
        rect.y0 += 1
        rect.x1 -= 1
        rect.y1 -= 1

        # get visible area
        visible = Rect(
            self.canvas.canvasx(0), self.canvas.canvasy(0),
            self.canvas.canvasx(self.canvas.winfo_width()),
            self.canvas.canvasy(self.canvas.winfo_height())
        )

        # get scroll region box
        scroll = Rect(
            min(rect.x0, visible.x0), min(rect.y0, visible.y0),
            max(rect.x1, visible.x1), max(rect.y1, visible.y1)
        )

        # whole image in the visible area
        if scroll.x0 == visible.x0 and scroll.x1 == visible.x1:
            scroll.x0 = rect.x0
            scroll.x1 = rect.x1
        if scroll.y0 == visible.y0 and scroll.y1 == visible.y1:
            scroll.y0 = rect.y0
            scroll.y1 = rect.y1

        self.canvas.configure(scrollregion=scroll.coordinates)

        # get coordinates of the image tile
        tile = Rect(
            max(scroll.x0 - rect.x0, 0), max(scroll.y0 - rect.y0, 0),
            min(scroll.x1, rect.x1) - rect.x0,
            min(scroll.y1, rect.y1) - rect.y0
        )

        # show image if it is in the visible area
        if tile.width > 0 and tile.height > 0:
            x = min(int(tile.x1 / self.imscale), self.image.width)
            y = min(int(tile.y1 / self.imscale), self.image.height)

            image = self.image.crop([int(tile.x0 / self.imscale), int(tile.y0 / self.imscale), x, y])
            imagetk = ImageTk.PhotoImage(image.resize([int(tile.width), int(tile.height)]))

            if self.image_container is not None:
                self.canvas.delete(self.image_container)
            
            self.image_container = self.canvas.create_image(
                max(scroll.x0, rect.x0), max(scroll.y0, rect.y0),
                anchor='nw', image=imagetk
            )

            # set image into background
            self.canvas.lower(self.image_container)
            # keep extra reference to prevent garbage-collection
            self.canvas.imagetk = imagetk
