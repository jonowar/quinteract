import subprocess
import tempfile
import os
import itertools
from PIL import Image, ImageDraw

class CharacterBox(object):
    def __init__(self, value, x1, y1, x2, y2):
        self._value = value
        self.x1 = int(x1)
        self.y1 = int(y1)
        self.x2 = int(x2)
        self.y2 = int(y2)

    def __repr__(self):
        return "CharacterBox({}, ({},{}), ({},{}))".format(
            self.value,
            self.x1,
            self.y1,
            self.x2,
            self.y2
            )

    @property
    def topleft(self):
        return (self.x1, self.y1)

    @property
    def bottomright(self):
        return (self.x2, self.y2)

    @property
    def area(self):
        return (self.x2 - self.x1) * (self.y2 - self.y1)

    @property
    def value(self):
        return self._value

class Quinteract(object):
    TEMP_DIR = '/tmp'
    TEMP_PREFIX = 'quinteract'

    def __init__(self, filename=None):
        self.grids = {}
        self.filename = filename
        self.process()

    def process(self):
        im = Image.open(self.filename)
        self.width, self.height = im.size
        im.close()

        outputbase = os.path.join(self.TEMP_DIR, self.TEMP_PREFIX)
        try:
            subprocess.check_output(["tesseract", self.filename, outputbase, "makebox"], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print "Failed to run tesseract:\n{}".format(e.output)
            raise e

        boxfile_path = "{}.box".format(outputbase)
        textfile_path = "{}.txt".format(outputbase)

        self.characters = []
        with open(boxfile_path, 'rU') as box_file:
            for i, line in enumerate(box_file.read().strip().split('\n')):
                value, x1, y1, x2, y2 = line.split()[:5]
                # NOTE: the Image library treats (0, 0) as the top left of an image
                # whereas tesseract .box format treats (0, 0) as the bottom left,
                # which is why we have to flip the y-values
                tmp1, tmp2 = int(y1), int(y2)
                y1 = self.height - tmp2
                y2 = self.height - tmp1
                self.characters.append(CharacterBox(value, x1, y1, x2, y2))

        os.unlink(boxfile_path)

        with open(textfile_path, 'rU') as text_file:
            self._text = text_file.read()
        os.unlink(textfile_path)

    @property
    def area(self):
        return self.width * self.height

    @property
    def text(self):
        return self._text

    def _get_grid(self, rows=5, cols=5):
        if (rows, cols) in self.grids:
            return self.grids[(rows, cols)]

        cells = [[False for _ in range(cols)] for _ in range(rows)]
        cell_height = self.height / rows
        cell_width = self.width / cols

        def find_cell(x, y):
            return (min(y / cell_height, rows - 1), min(x / cell_width, cols - 1))

        for char in self.characters:
            row_start, col_start = find_cell(*char.topleft)
            row_stop,  col_stop  = find_cell(*char.bottomright)
            for row in range(row_start, row_stop + 1):
                for col in range(col_start, col_stop + 1):
                    cells[row][col] = True

        grid = {
            'cell_height': cell_height,
            'cell_width': cell_width,
            'cells': cells
            }
        self.grids[(rows, cols)] = grid
        return grid

    def percent_text(self):
        character_area = sum([c.area for c in self.characters])
        return float(character_area) / self.area

    def percent_grid(self, rows=5, cols=5):
        grid = self._get_grid(rows, cols)
        active_cells = sum(itertools.chain(*grid['cells']))
        return float(active_cells) / (rows * cols)

    def generate_grid_overlay(self, filename="gridoverlay.png",
                              active_color="green", inactive_color="red",
                              rows=5, cols=5):
        grid = self._get_grid(rows, cols)
        im = Image.open(self.filename)
        im.putalpha(255)
        overlay = Image.new("RGBA", im.size)

        draw = ImageDraw.Draw(overlay)
        for row_index, row in enumerate(grid['cells']):
            for col_index, active in enumerate(row):
                color = active_color if active else inactive_color
                cell_topleft     = (grid['cell_width'] * col_index, grid['cell_height'] * row_index)
                cell_bottomright = (grid['cell_width'] * (col_index + 1), grid['cell_height'] * (row_index + 1))
                draw.rectangle((cell_topleft, cell_bottomright), fill=color, outline="black")

        blend = Image.blend(im, overlay, .5)
        with open(filename, 'w') as imgfile:
            blend.save(imgfile)

        return filename

    def generate_text_overlay(self, filename="overlay.png", color="red"):
        im = Image.open(self.filename)
        im.putalpha(255)
        overlay = Image.new("RGBA", im.size)

        draw = ImageDraw.Draw(overlay)
        for charbox in self.characters:
            draw.rectangle((charbox.topleft, charbox.bottomright), fill=color)

        blend = Image.blend(im, overlay, .5)
        with open(filename, 'w') as imgfile:
            blend.save(imgfile)

        return filename
