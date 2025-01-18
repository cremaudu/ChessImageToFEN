import cv2
import numpy as np
from typing import Tuple, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageProcessor:
    VALID_EXTENSIONS = ['.jpg', '.jpeg', '.png']
    MIN_IMAGE_SIZE = 200  # Minimum size in pixels for both width and height
    
    @staticmethod
    def validate_image(image_path: str) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Validate if the image is in a supported format and can be processed.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (is_valid, image_data)
            - is_valid: Boolean indicating if image is valid
            - image_data: np.ndarray of the image if valid, None otherwise
        """
        # Check file extension
        if not any(image_path.lower().endswith(ext) for ext in ImageProcessor.VALID_EXTENSIONS):
            logger.error(f"Invalid image format. Supported formats: {ImageProcessor.VALID_EXTENSIONS}")
            return False, None
            
        try:
            # Read file as binary
            with open(image_path, 'rb') as f:
                img_array = np.frombuffer(f.read(), np.uint8)
            
            # Decode the image
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if image is None:
                logger.error("Failed to load image")
                return False, None
                
            # Check image dimensions
            height, width = image.shape[:2]
            if height < ImageProcessor.MIN_IMAGE_SIZE or width < ImageProcessor.MIN_IMAGE_SIZE:
                logger.error(f"Image too small. Minimum size: {ImageProcessor.MIN_IMAGE_SIZE}x{ImageProcessor.MIN_IMAGE_SIZE}")
                return False, None
                
            return True, image
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return False, None
            
    @staticmethod
    def detect_chessboard(image: np.ndarray) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Detect a chessboard in the image and return its corners.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Tuple of (success, corners)
            - success: Boolean indicating if chessboard was detected
            - corners: np.ndarray of corner coordinates if detected, None otherwise
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        # Try to find the chessboard corners
        try:
            ret, corners = cv2.findChessboardCorners(gray, (7,7), None)
            if ret:
                # Refine the corners
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                corners = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
                return True, corners
            else:
                logger.warning("No chessboard pattern found in the image")
                return False, None
                
        except Exception as e:
            logger.error(f"Error detecting chessboard: {str(e)}")
            return False, None

    @staticmethod
    def extract_grid(image: np.ndarray, corners: np.ndarray) -> Tuple[bool, Optional[List[np.ndarray]]]:
        """
        Extract the 64 squares from the chessboard image after perspective correction.
        
        Args:
            image: Input image as numpy array
            corners: Corner points of the chessboard (7x7 internal corners)
            
        Returns:
            Tuple of (success, squares)
            - success: Boolean indicating if extraction was successful
            - squares: List of 64 numpy arrays representing each square if successful, None otherwise
        """
        try:
            # We need to estimate the full board corners from the internal corners
            # The internal corners are 7x7, we need to extrapolate to get 8x8
            h, w = image.shape[:2]
            
            # Reshape corners to 7x7 grid
            corner_grid = corners.reshape(7, 7, 2)
            
            # Estimate square size from corners
            square_size = np.mean([
                np.linalg.norm(corner_grid[0,0] - corner_grid[0,1]),
                np.linalg.norm(corner_grid[0,0] - corner_grid[1,0])
            ])
            
            # Extrapolate outer corners
            top_left = corner_grid[0,0] - square_size
            top_right = corner_grid[0,-1] + np.array([square_size, -square_size])
            bottom_left = corner_grid[-1,0] + np.array([-square_size, square_size])
            bottom_right = corner_grid[-1,-1] + square_size
            
            # Define source points for perspective transform
            src_points = np.float32([top_left, top_right, bottom_right, bottom_left])
            
            # Define destination points (target square board)
            board_size = 800  # pixels
            square_size = board_size // 8
            dst_points = np.float32([
                [0, 0],
                [board_size, 0],
                [board_size, board_size],
                [0, board_size]
            ])
            
            # Calculate perspective transform matrix
            matrix = cv2.getPerspectiveTransform(src_points, dst_points)
            
            # Apply perspective transform
            warped = cv2.warpPerspective(image, matrix, (board_size, board_size))
            
            # Split into 64 squares
            squares = []
            for row in range(8):
                for col in range(8):
                    x1 = col * square_size
                    y1 = row * square_size
                    x2 = (col + 1) * square_size
                    y2 = (row + 1) * square_size
                    square = warped[y1:y2, x1:x2]
                    squares.append(square)
            
            return True, squares
            
        except Exception as e:
            logger.error(f"Error extracting grid: {str(e)}")
            return False, None
