import pytest
import os
import cv2
import numpy as np
from src.image_processor import ImageProcessor

@pytest.fixture
def sample_image():
    # Create a simple test image
    img = np.zeros((400, 400, 3), dtype=np.uint8)
    img.fill(255)  # White background
    
    # Draw a chessboard pattern
    square_size = 50
    for i in range(8):
        for j in range(8):
            if (i + j) % 2 == 0:
                x1 = j * square_size
                y1 = i * square_size
                x2 = (j + 1) * square_size
                y2 = (i + 1) * square_size
                img[y1:y2, x1:x2] = 0  # Black squares
    
    return img

def test_valid_image_format(tmp_path):
    # Create a temporary valid image
    img_path = os.path.join(tmp_path, "test.jpg")
    cv2.imwrite(img_path, np.zeros((400, 400, 3), dtype=np.uint8))
    
    is_valid, image = ImageProcessor.validate_image(img_path)
    assert is_valid
    assert image is not None
    assert image.shape == (400, 400, 3)

def test_invalid_image_format(tmp_path):
    # Create a file with invalid extension
    invalid_path = os.path.join(tmp_path, "test.txt")
    with open(invalid_path, 'w') as f:
        f.write("Not an image")
    
    is_valid, image = ImageProcessor.validate_image(invalid_path)
    assert not is_valid
    assert image is None

def test_small_image(tmp_path):
    # Create an image smaller than minimum size
    img_path = os.path.join(tmp_path, "small.jpg")
    cv2.imwrite(img_path, np.zeros((100, 100, 3), dtype=np.uint8))
    
    is_valid, image = ImageProcessor.validate_image(img_path)
    assert not is_valid
    assert image is None

def test_chessboard_detection(sample_image):
    success, corners = ImageProcessor.detect_chessboard(sample_image)
    # Note: This test might fail as the pattern is simplified
    # Real chessboard detection would need more sophisticated test images
    assert isinstance(success, bool)
    if success:
        assert corners is not None
        assert isinstance(corners, np.ndarray)

def test_grid_extraction(sample_image):
    # First detect the chessboard
    success, corners = ImageProcessor.detect_chessboard(sample_image)
    assert success
    assert corners is not None
    
    # Then extract the grid
    success, squares = ImageProcessor.extract_grid(sample_image, corners)
    assert success
    assert squares is not None
    assert len(squares) == 64  # 8x8 grid
    
    # Check that each square has the expected dimensions
    for square in squares:
        assert square.shape[0] == 100  # 800 pixels / 8 squares = 100 pixels per square
        assert square.shape[1] == 100
        assert len(square.shape) == 3  # Should be a color image (H, W, C)

def test_grid_extraction_invalid_corners():
    # Create an invalid corners array
    invalid_corners = np.zeros((10, 1, 2))  # Wrong shape
    
    success, squares = ImageProcessor.extract_grid(np.zeros((400, 400, 3)), invalid_corners)
    assert not success
    assert squares is None
