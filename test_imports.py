print("Testing imports...")

try:
    import flask
    print("[OK] Flask version:", flask.__version__)
except Exception as e:
    print("[ERROR] Flask import failed:", str(e))

try:
    import cv2
    print("[OK] OpenCV version:", cv2.__version__)
except Exception as e:
    print("[ERROR] OpenCV import failed:", str(e))

try:
    import numpy as np
    print("[OK] NumPy version:", np.__version__)
except Exception as e:
    print("[ERROR] NumPy import failed:", str(e))

try:
    from PIL import Image, __version__
    print("[OK] Pillow version:", __version__)
except Exception as e:
    print("[ERROR] Pillow import failed:", str(e))

try:
    import chess
    print("[OK] Python-chess version:", chess.__version__)
except Exception as e:
    print("[ERROR] Python-chess import failed:", str(e))

try:
    import tensorflow as tf
    print("[OK] TensorFlow version:", tf.__version__)
except Exception as e:
    print("[ERROR] TensorFlow import failed:", str(e))

print("\nAll import tests completed.")
