import subprocess
import tempfile
import os
from PIL import Image

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
    def area(self):
        return (self.x2 - self.x1) * (self.y2 - self.y1)

    @property
    def value(self):
        return self._value

class Quinteract(object):
    TEMP_DIR = '/tmp'
    TEMP_PREFIX = 'quinteract'

    def __init__(self, filename=None):
        self.characters = []
        self.filename = filename
        self.process()

    def process(self):
        outputbase = os.path.join(self.TEMP_DIR, self.TEMP_PREFIX)
        try:
            subprocess.check_output(["tesseract", self.filename, outputbase, "makebox"], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print "Failed to run tesseract:\n{}".format(e.output)
            raise e

        boxfile_path = "{}.box".format(outputbase)
        textfile_path = "{}.txt".format(outputbase)

        with open(boxfile_path, 'rU') as box_file:
            for i, line in enumerate(box_file.read().strip().split('\n')):
                self.characters.append(CharacterBox(*line.split()[:5]))

        import pdb; pdb.set_trace()
        os.unlink(boxfile_path)

        with open(textfile_path, 'rU') as text_file:
            self._text = text_file.read()
        os.unlink(textfile_path)

        im = Image.open(self.filename)
        self.width, self.height = im.size
        im.close()

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

    def generate_overlay(self):
        pass
