import subprocess
import tempfile
import os
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

    @property
    def percent_text(self):
        character_area = sum([c.area for c in self.characters])
        return float(character_area) / self.area

    def generate_overlay(self, filename="overlay.png", new=False, fill=None):
        if new:
            im = Image.new("RGBA", (self.width, self.height), color=fill)
        else:
            im = Image.open(self.filename)

        draw = ImageDraw.Draw(im)
        for charbox in self.characters:
            draw.rectangle((charbox.topleft, charbox.bottomright), fill="black")

        with open(filename, 'w') as imgfile:
            im.save(imgfile)

        return filename
