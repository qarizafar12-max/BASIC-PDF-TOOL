import cv2
import numpy as np
import os
import re

class OCRProcessor:
    """
    Handles advanced image preprocessing and text cleaning for OCR.
    """
    
    @staticmethod
    def preprocess_image(image_path: str, deskew: bool = True, denoise: bool = True) -> str:
        """
        Preprocess image for better OCR accuracy.
        Returns path to processed temporary image.
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return image_path
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Denoise if requested
            if denoise:
                # Fast Non-Local Means Denoising
                gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
                
                # Gaussian Blur to remove remaining speckles
                gray = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Thresholding (Binarization)
            # Otsu's thresholding after Gaussian filtering
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Deskew if requested
            if deskew:
                thresh = OCRProcessor.deskew_image(thresh)
            
            # Save processed image to new temp path
            dirname, filename = os.path.split(image_path)
            name, ext = os.path.splitext(filename)
            output_path = os.path.join(dirname, f"{name}_processed{ext}")
            
            cv2.imwrite(output_path, thresh)
            return output_path
            
        except Exception as e:
            print(f"Preprocessing failed: {e}")
            return image_path  # Return original if anything fails
    
    @staticmethod
    def deskew_image(image):
        """
        Rotate image to correct skew.
        """
        try:
            # Find all non-zero points (text)
            coords = np.column_stack(np.where(image > 0))
            
            # Compute minimum bounding box
            angle = cv2.minAreaRect(coords)[-1]
            
            # Correct angle
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
                
            # Rotate image
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            
            return rotated
        except Exception:
            return image

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean common OCR errors, especially for math content.
        """
        if not text:
            return ""
            
        # Common replacements
        replacements = [
            (r'Mathematlcs', 'Mathematics'),
            (r'\bI\b', '1'),  # I -> 1 (isolated)
            (r'\bO\b', '0'),  # O -> 0 (isolated)
            (r'filllng', 'filling'),
            (r'followlng', 'following'),
            (r'questlon', 'question'),
        ]
        
        cleaned = text
        for pattern, repl in replacements:
            cleaned = re.sub(pattern, repl, cleaned, flags=re.IGNORECASE)
            
        return cleaned
