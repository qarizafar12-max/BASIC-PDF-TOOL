# Excode PDF Tool

## Overview
Excode PDF Tool is a premium, AI-powered PDF utility built with Python (PySide6). It offers a suite of tools for managing, editing, and analyzing PDF documents with a modern, futuristic UI.

## Features
-   **Dashboard**: Quick access to all tools.
-   **Create PDF**: Convert images to PDF.
-   **PDF Tools**: Merge, Split, and Compress PDFs.
-   **Text & OCR**: Extract text from PDFs and images using AI-enhanced OCR.
-   **File Manager**: Rename, organize, and manage files.
-   **QR Code**: Generate QR codes.
-   **Excode Animation**: Custom RGB startup sequence.

## Installation
1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the application:
    ```bash
    python src/main.py
    ```

## Building Executable
To build a standalone .exe file:
```bash
python build.py
```
The output will be in the `dist` folder.

## Technologies
-   **UI**: PySide6 (Qt for Python)
-   **PDF Engine**: PyMuPDF (fitz), pypdf, pikepdf
-   **OCR**: EasyOCR, OpenCV
-   **Icons**: FontAwesome 5 (via qtawesome)

## License
MIT License
