from image_edit import ImageEdit
import os


class ImageInfo(ImageEdit):
    def __init__(self, image, path, tab):
        super().__init__(image)

        self.path = path
        self.tab = tab
    
    @property
    def unsaved(self) -> bool:
        return self.path[-1] == '*'
    
    @unsaved.setter
    def unsaved(self, value: bool):
        if value and not self.unsaved:
            self.path += '*'
        elif not value and self.unsaved:
            self.path = self.path[:-1]

    def filaname(self, no_star=False):
        name = os.path.split(self.path)[1]
        return name[:-1] if no_star and name[-1] == '*' else name
    
    def file_extension(self, no_star=False):
        ext = os.path.splitext(self.path)[1]
        return ext[:-1] if no_star and ext[-1] == '*' else ext
    
    def directory(self, no_star=False):
        dirname = os.path.split(self.path)[0]
        return dirname[:-1] if no_star and dirname[-1] == '*' else dirname

    def full_path(self, no_star=False):
        return self.path[:-1] if no_star and self.path[-1] == '*' else self.path

