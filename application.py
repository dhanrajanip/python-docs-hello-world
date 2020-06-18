from flask import Flask

import sys
sys.path.append('/home/site/wwwroot/antenv/lib/python3.7/site-packages')

import os
import json
from datetime import datetime
from pyzbar import pyzbar
import imutils
from imutils import contours
import numpy as np
import re
import pytesseract
import os

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"
