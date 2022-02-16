from tkinter import PhotoImage

from customtkinter import CTkLabel, get_appearance_mode
from PIL import Image, ImageTk
from tksvg import SvgImage

from ..utils import *

__all__ = ('get_image', 'GIF',)


def get_image(image: str, wh=(40, 40), basic=False, kw=True) -> ImageTk.PhotoImage:
    """
    Load an image from the assets folder
    """
    try:
        fp = get_outer_path(image)
    except FileNotFoundError:
        fp=''
    finally:
        if image != fp:
            mid = 'basic' if basic else 'icons'
            fp = get_outer_path("assets", mid, image)
        else:
            fp = image
        if fp.endswith(".svg"):
            if isinstance(wh, (int, float)):
                scale = wh
            else:
                scale = 0.5
            return SvgImage(file=fp, scale=scale)
        with Image.open(fp) as img:
            if wh == (0, 0):
                wh = img.size
            img = img.resize(wh)
            return ImageTk.PhotoImage(img)


class GIF(CTkLabel):

    def __init__(self, path, master, cnf: dict = {}, **kwargs):
        self.path = get_outer_path(path)

        with Image.open(self.path) as im:
            self.max = im.n_frames
        self.images = [PhotoImage(file=self.path, format="gif -index %i" % i)
                       for i in range(self.max)]

        super().__init__(master, cnf, **kwargs)

    def start(self, ind: int = 0):
        frame = self.images[ind]
        self.configure(image=frame,
                       background=self.master["bg"])
        ind += 1
        if ind == self.max:
            ind = 0
        self.after(45, self.start, ind)


# if __name__ == '__main__':
#     import numpy as np
#     import potrace

#     data = np.zeros((32, 32), np.uint32)
#     data[8:32-8, 8:32-8] = 1

#     # Create a bitmap from the array
#     bmp = potrace.Bitmap(data)

#     # Trace the bitmap to a path
#     path = bmp.trace()

#     # Iterate over path curves
#     for curve in path:
#         print("start_point =", curve.start_point)
#         for segment in curve:
#             print(segment)
#             end_point_x, end_point_y = segment.end_point
#             if segment.is_corner:
#                 c_x, c_y = segment.c
#             else:
#                 c1_x, c1_y = segment.c1
#                 c2_x, c2_y = segment.c2
