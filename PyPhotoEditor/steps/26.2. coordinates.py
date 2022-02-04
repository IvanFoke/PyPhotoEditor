class Rect:
    def __init__(self, x0, y0, x1, y1, side_offset=0):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.side_offset = side_offset

    @property
    def width(self):
        return abs(self.x1 - self.x0)

    @property
    def height(self):
        return abs(self.y1 - self.y0)

    @property
    def coordinates(self):
        x0, y0 = min(self.x0, self.x1), min(self.y0, self.y1)
        x1, y1 = max(self.x0, self.x1), max(self.y0, self.y1)

        return [x0, y0, x1, y1]

    @property
    def top(self):
        x0, y0, x1, y1 = self.coordinates

        return Rect(
            x0 - self.side_offset / 2, y0 - self.side_offset / 2,
            x1 + self.side_offset / 2, y0 + self.side_offset / 2
        )

    @property
    def left(self):
        x0, y0, x1, y1 = self.coordinates

        return Rect(
            x0 - self.side_offset / 2, y0 - self.side_offset / 2,
            x0 + self.side_offset / 2, y1 + self.side_offset / 2
        )

    @property
    def bottom(self):
        x0, y0, x1, y1 = self.coordinates

        return Rect(
            x0 - self.side_offset / 2, y1 - self.side_offset / 2,
            x1 + self.side_offset / 2, y1 + self.side_offset / 2
        )

    @property
    def right(self):
        x0, y0, x1, y1 = self.coordinates

        return Rect(
            x1 - self.side_offset / 2, y0 - self.side_offset / 2,
            x1 + self.side_offset / 2, y1 + self.side_offset / 2
        )

    @property
    def topleft(self):
        x0, y0, x1, y1 = self.coordinates

        return Rect(
            x0 - self.side_offset / 2, y0 - self.side_offset / 2,
            x0 + self.side_offset / 2, y0 + self.side_offset / 2
        )

    @property
    def topright(self):
        x0, y0, x1, y1 = self.coordinates

        return Rect(
            x1 - self.side_offset / 2, y0 - self.side_offset / 2,
            x1 + self.side_offset / 2, y0 + self.side_offset / 2
        )

    @property
    def bottomleft(self):
        x0, y0, x1, y1 = self.coordinates

        return Rect(
            x0 - self.side_offset / 2, y1 - self.side_offset / 2,
            x0 + self.side_offset / 2, y1 + self.side_offset / 2
        )

    @property
    def bottomright(self):
        x0, y0, x1, y1 = self.coordinates

        return Rect(
            x1 - self.side_offset / 2, y1 - self.side_offset / 2,
            x1 + self.side_offset / 2, y1 + self.side_offset / 2
        )

    def center(self, offset=None):
        x0, y0, x1, y1 = self.coordinates
        cx = x0 + self.width / 2
        cy = y0 + self.height / 2

        offset = self.side_offset if offset is None else offset

        return Rect(
            cx - offset / 2, cy - offset / 2,
            cx + offset / 2, cy + offset / 2,
            side_offset=offset
        )

    def point_inside(self, x, y):
        x0, y0, x1, y1 = self.coordinates
        return x0 < x < x1 and y0 < y < y1

    def change(self, x0=None, y0=None, x1=None, y1=None):
        self.x0 = self.x0 if x0 is None else x0
        self.y0 = self.y0 if y0 is None else y0
        self.x1 = self.x1 if x1 is None else x1
        self.y1 = self.y1 if y1 is None else y1

    def __eq__(self, other):
        return isinstance(other, Rect) and self.coordinates == other.coordinates

    def __repr__(self):
        return f"<Rect [{self.x0}, {self.y0}, {self.x1}, {self.y1}]>"