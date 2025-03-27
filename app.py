import cv2
import face_recognition
import numpy as np
import DAO
import threading
from flask import Flask, render_template, jsonify

app = Flask(__name__)

app.run(debug=True, use_reloader=False)

