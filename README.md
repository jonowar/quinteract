# quinteract
A Python wrapper around Tesseract, mainly used to determine the percentage of text in an image.

## History
quinteract = quintile + tesseract

Created as an AdRoll hackday project to determine if an image has less than 20% text, as per Facebook ad image guidelines.

## Installation

### tesseract
On OS X:
`brew install tesseract`

or follow the tesseract installation instructions here: https://code.google.com/p/tesseract-ocr/wiki/ReadMe#Installation

### python dependencies
`pip install -r requirements.txt`

## Usage
```python
>>> import quinteract
>>> q = quinteract.Quinteract('sample_images/YOLO.png')
>>> print q.text
YOLO


>>> q.area
10000
>>> q.percent_text
0.2444
>>> q.generate_text_overlay(rows=5, cols=5)
'overlay.png'
>>> q.generate_grid_overlay(rows=5, cols=5)
'gridoverlay.png'
>>> q.percent_grid(rows=5, cols=5)
0.4
```
