import os
import io
import re
from typing import List, Tuple, Optional, Dict
import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter
import pikepdf
from pdfminer.high_level import extract_text as pdfminer_extract_text
from pdfminer.layout import LAParams
from docx import Document
from docx.shared import Pt
from PIL import Image, ImageEnhance
import numpy as np
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

class PDFProcessor:
    _reader = None # Lazy load reader

    @staticmethod
    def get_reader():
        if PDFProcessor._reader is None:
            print("Loading EasyOCR Model... (This might take a moment)")
            # Using English by default, can be expanded later
            PDFProcessor._reader = easyocr.Reader(['en'], gpu=True) 
        return PDFProcessor._reader

    @staticmethod
    def modify_pdf(input_path, output_path, actions):
        """
        Modifies a PDF using PyMuPDF (fitz) for powerful editing.
        """
        try:
            doc = fitz.open(input_path)
            
            # Apply content modifications (e.g., text) first.
            for a in actions:
                if a['type'] == 'add_text':
                    # Check if page valid
                    if 0 <= a['page'] < len(doc):
                        page = doc[a['page']]
                        point = fitz.Point(a['x'], a['y'])
                        page.insert_text(point, a['text'], fontsize=a.get('fontsize', 12), color=a.get('color', (0,0,0)))

                elif a['type'] == 'rotate':
                     if 0 <= a['page'] < len(doc):
                        page = doc[a['page']]
                        page.set_rotation(page.rotation + a['angle'])

            # Handle Reorder / Delete
            forced_order = None
            for a in actions:
                if a['type'] == 'set_order':
                    forced_order = a['order']
                    break
            
            if forced_order is not None:
                doc.select(forced_order)
            else:
                # Classic delete if no reorder
                deletes = sorted([a['page'] for a in actions if a['type'] == 'delete'], reverse=True)
                for p in deletes:
                    if 0 <= p < len(doc):
                        doc.delete_page(p)

            doc.save(output_path)
            doc.close()
            return True, "PDF modified successfully!"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def extract_text_from_image(image_path):
        """
        Extracts text from an image using EasyOCR with enhancement.
        """
        try:
            if not os.path.exists(image_path):
                return False, "Image file not found."
            
            # Pre-process image for better accuracy
            from PIL import Image, ImageEnhance
            img = Image.open(image_path)
            
            # Convert to grayscale
            img = img.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
            
            # Save temp for OCR (EasyOCR reads files or arrays, giving file is safer for format)
            # Actually EasyOCR accepts numpy array or bytes. Let's pass the numpy array via numpy
            import numpy as np
            img_np = np.array(img)
            
            reader = PDFProcessor.get_reader()
            
            # paragraph=True combines lines into blocks. detail=0 would give just list of strings.
            # paragraph=True returns list of lists, so we need to flatten/join.
            results = reader.readtext(img_np, detail=0, paragraph=True)
            
            text = "\n\n".join(results)
            
            if not text.strip():
                return True, "[No text detected]"
            return True, text
        except Exception as e:
            return False, str(e)


    @staticmethod
    def create_from_images(image_paths, output_path):
        """
        Creates a PDF from a list of images.
        """
        try:
            doc = fitz.open()
            for img_path in image_paths:
                img = fitz.open(img_path)
                rect = img[0].rect
                pdfbytes = img.convert_to_pdf()
                img.close()
                imgPDF = fitz.open("pdf", pdfbytes)
                page = doc.new_page(width = rect.width, height = rect.height)
                page.show_pdf_page(rect, imgPDF, 0)
            
            doc.save(output_path)
            doc.close()
            return True, "PDF created successfully!"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def merge_pdfs(pdf_paths, output_path):
        """
        Merges multiple PDFs into one.
        """
        try:
            merger = PdfWriter()
            for pdf in pdf_paths:
                merger.append(pdf)
            merger.write(output_path)
            merger.close()
            return True, "PDFs merged successfully!"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def split_pdf(input_path, output_dir, mode="all", page_range=None):
        """
        Splits PDF based on mode:
        - 'all': Split every page into a separate file.
        - 'range': Extract a specific range (e.g., "1-5" or "1,3,5").
        """
        try:
            reader = PdfReader(input_path)
            base_name = os.path.basename(input_path).replace(".pdf", "")
            
            if mode == "all":
                for i, page in enumerate(reader.pages):
                    writer = PdfWriter()
                    writer.add_page(page)
                    out_file = os.path.join(output_dir, f"{base_name}_page_{i+1}.pdf")
                    with open(out_file, "wb") as f:
                        writer.write(f)
                return True, f"Split {len(reader.pages)} pages to {output_dir}"

            elif mode == "range" and page_range:
                # Simple parser for "1-3" or "2"
                # For now, let's assuming strict "start-end" format string for simplicity
                writer = PdfWriter()
                
                parts = page_range.split('-')
                if len(parts) == 2:
                    start, end = int(parts[0]) - 1, int(parts[1])
                    for i in range(start, end):
                        if 0 <= i < len(reader.pages):
                            writer.add_page(reader.pages[i])
                elif len(parts) == 1:
                     idx = int(parts[0]) - 1
                     if 0 <= idx < len(reader.pages):
                        writer.add_page(reader.pages[idx])

                out_file = os.path.join(output_dir, f"{base_name}_split.pdf")
                with open(out_file, "wb") as f:
                    writer.write(f)
                return True, f"Extracted pages to {out_file}"
                
            return False, "Invalid mode or range"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def compress_pdf(input_path: str, output_path: str, quality: str = "medium") -> Tuple[bool, str]:
        """
        Compress PDF with configurable quality levels.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save compressed PDF
            quality: Compression level - 'low', 'medium', or 'high'
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Quality settings
            quality_settings = {
                'low': {'image_dpi': 72, 'jpeg_quality': 50},
                'medium': {'image_dpi': 150, 'jpeg_quality': 75},
                'high': {'image_dpi': 200, 'jpeg_quality': 85}
            }
            
            settings = quality_settings.get(quality, quality_settings['medium'])
            
            # Open with pikepdf
            with pikepdf.open(input_path) as pdf:
                # Compress images
                for page in pdf.pages:
                    for img_key in page.images.keys():
                        try:
                            img = page.images[img_key]
                            raw_image = img.read_bytes()
                            
                            # Convert to PIL Image
                            pil_img = Image.open(io.BytesIO(raw_image))
                            
                            # Resize if needed
                            if pil_img.width > settings['image_dpi'] * 8.5:  # 8.5 inches
                                ratio = (settings['image_dpi'] * 8.5) / pil_img.width
                                new_size = (int(pil_img.width * ratio), int(pil_img.height * ratio))
                                pil_img = pil_img.resize(new_size, Image.Resampling.LANCZOS)
                            
                            # Compress
                            img_buffer = io.BytesIO()
                            if pil_img.mode == 'RGBA':
                                pil_img = pil_img.convert('RGB')
                            pil_img.save(img_buffer, format='JPEG', quality=settings['jpeg_quality'], optimize=True)
                            img_buffer.seek(0)
                            
                            # Replace in PDF
                            img.write(img_buffer.read(), filter=pikepdf.Name.DCTDecode)
                        except Exception:
                            continue  # Skip problematic images
                
                # Save with compression
                pdf.save(output_path, compress_streams=True, object_stream_mode=pikepdf.ObjectStreamMode.generate)
            
            # Calculate size reduction
            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(output_path)
            reduction = ((original_size - compressed_size) / original_size) * 100
            
            return True, f"Compressed successfully! Size reduced by {reduction:.1f}%"
        except Exception as e:
            return False, f"Compression failed: {str(e)}"

    @staticmethod
    def extract_text(input_path: str, page_range: Optional[Tuple[int, int]] = None, progress_callback=None) -> Tuple[bool, str]:
        """
        Extract text from PDF with improved formatting preservation.
        Automatically uses OCR for image-based PDFs.
        
        Args:
            input_path: Path to PDF file
            page_range: Optional tuple of (start_page, end_page) (0-indexed)
            progress_callback: Optional callable(str) for progress updates
        
        Returns:
            Tuple of (success, extracted_text or error_message)
        """
        try:
            # First, try PyMuPDF (fitz) - usually better for modern PDFs
            doc = fitz.open(input_path)
            text_parts = []
            
            if page_range:
                start, end = page_range
                pages_to_extract = range(start, min(end, len(doc)))
            else:
                pages_to_extract = range(len(doc))
            
            for page_num in pages_to_extract:
                page = doc[page_num]
                page_text = page.get_text("text")
                if page_text.strip():
                    text_parts.append(page_text)
            
            doc.close()
            
            text = "\n\n--- Page Break ---\n\n".join(text_parts)
            
            # If we got very little text, try pdfminer as backup
            if len(text.strip()) < 100 and not page_range:
                try:
                    laparams = LAParams(line_margin=0.5, word_margin=0.1, char_margin=2.0)
                    pdfminer_text = pdfminer_extract_text(input_path, laparams=laparams)
                    if len(pdfminer_text.strip()) > len(text.strip()):
                        text = pdfminer_text
                except Exception:
                    pass  # Continue with PyMuPDF text
            
            # Check if this might be an image-based PDF - if so, USE OCR AUTOMATICALLY
            if len(text.strip()) < 100:
                print("[OCR] Image-based PDF detected! Automatically extracting text using OCR...")
                print("[OCR] Extracting images to temp folder and performing OCR...")
                
                # Automatically run OCR
                ocr_success, ocr_text = PDFProcessor.extract_text_with_ocr(input_path, page_range, progress_callback)
                
                if ocr_success and len(ocr_text.strip()) > len(text.strip()):
                    print("[OCR] OCR extraction successful!")
                    return True, ocr_text + "\n\n[Text extracted using OCR]"
                else:
                    print("[OCR] OCR extraction failed or returned no text")
                    # Fall through to original behavior
            
            if not text.strip():
                return True, "[No text found in PDF - OCR also yielded no results]"
            
            return True, text
        except Exception as e:
            return False, f"Text extraction failed: {str(e)}"

    @staticmethod
    def export_to_txt(text: str, output_path: str) -> Tuple[bool, str]:
        """Export text to .txt file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            return True, f"Text exported to {output_path}"
        except Exception as e:
            return False, f"Export failed: {str(e)}"

    @staticmethod
    def export_to_docx(text: str, output_path: str) -> Tuple[bool, str]:
        """
        Export text to .docx file with basic formatting.
        """
        try:
            doc = Document()
            
            # Split into paragraphs
            paragraphs = text.split('\n\n')
            
            for para in paragraphs:
                if para.strip():
                    p = doc.add_paragraph(para.strip())
                    # Set font
                    for run in p.runs:
                        run.font.name = 'Calibri'
                        run.font.size = Pt(11)
            
            doc.save(output_path)
            return True, f"Document exported to {output_path}"
        except Exception as e:
            return False, f"Export failed: {str(e)}"

    @staticmethod
    def search_in_pdf(input_path: str, query: str, case_sensitive: bool = False) -> Tuple[bool, List[Dict]]:
        """
        Search for text in PDF and return matches with page numbers.
        
        Args:
            input_path: Path to PDF file
            query: Search query
            case_sensitive: Whether search should be case-sensitive
        
        Returns:
            Tuple of (success, list of matches with page numbers and context)
        """
        try:
            reader = PdfReader(input_path)
            matches = []
            
            search_query = query if case_sensitive else query.lower()
            
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                search_text = page_text if case_sensitive else page_text.lower()
                
                # Find all occurrences
                start = 0
                while True:
                    pos = search_text.find(search_query, start)
                    if pos == -1:
                        break
                    
                    # Get context (50 chars before and after)
                    context_start = max(0, pos - 50)
                    context_end = min(len(page_text), pos + len(query) + 50)
                    context = page_text[context_start:context_end]
                    
                    matches.append({
                        'page': page_num + 1,
                        'position': pos,
                        'context': context.strip()
                    })
                    
                    start = pos + 1
            
            if not matches:
                return True, []
            
            return True, matches
        except Exception as e:
            return False, []

    @staticmethod
    def rotate_pages(input_path: str, output_path: str, pages: List[int], angle: int) -> Tuple[bool, str]:
        """
        Rotate specific pages in PDF.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save rotated PDF
            pages: List of page numbers (1-indexed) to rotate
            angle: Rotation angle (90, 180, or 270)
        
        Returns:
            Tuple of (success, message)
        """
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            for i, page in enumerate(reader.pages):
                if (i + 1) in pages:
                    page.rotate(angle)
                writer.add_page(page)
            
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            return True, f"Rotated {len(pages)} page(s) by {angle}°"
        except Exception as e:
            return False, f"Rotation failed: {str(e)}"

    @staticmethod
    def add_password(input_path: str, output_path: str, password: str) -> Tuple[bool, str]:
        """
        Add password protection to PDF.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save protected PDF
            password: Password to set
        
        Returns:
            Tuple of (success, message)
        """
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # Add all pages
            for page in reader.pages:
                writer.add_page(page)
            
            # Encrypt
            writer.encrypt(password)
            
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            return True, "PDF password protected successfully!"
        except Exception as e:
            return False, f"Password protection failed: {str(e)}"

    @staticmethod
    def remove_password(input_path: str, output_path: str, password: str) -> Tuple[bool, str]:
        """
        Remove password from PDF.
        
        Args:
            input_path: Path to encrypted PDF
            output_path: Path to save decrypted PDF
            password: Password to decrypt
        
        Returns:
            Tuple of (success, message)
        """
        try:
            reader = PdfReader(input_path)
            
            if reader.is_encrypted:
                reader.decrypt(password)
            
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            return True, "Password removed successfully!"
        except Exception as e:
            return False, f"Password removal failed: {str(e)}"
    
    @staticmethod
    def extract_text_with_ocr(input_path: str, page_range: Optional[Tuple[int, int]] = None, progress_callback=None) -> Tuple[bool, str]:
        """
        Extract text from image-based PDFs using OCR.
        Extracts images to temp folder, performs OCR, then cleans up.
        
        Args:
            input_path: Path to PDF file
            page_range: Optional tuple of (start_page, end_page) (0-indexed)
            progress_callback: Optional callable(str) for progress updates
        
        Returns:
            Tuple of (success, extracted_text or error_message)
        """
        import tempfile
        import shutil
        from core.ocr_processor import OCRProcessor
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix="pdf_ocr_")
        
        try:
            doc = fitz.open(input_path)
            text_parts = []
            
            if page_range:
                start, end = page_range
                pages_to_process = range(start, min(end, len(doc)))
            else:
                pages_to_process = range(len(doc))
            
            total_pages = len(pages_to_process)
            
            # Try to use easyocr first (better accuracy), fall back to pytesseract
            use_easyocr = EASYOCR_AVAILABLE
            
            if use_easyocr:
                try:
                    if progress_callback:
                        progress_callback("Loading OCR Model... (This may take time)...")
                    reader = PDFProcessor.get_reader()
                except Exception as e:
                    print(f"EasyOCR failed to load: {e}, falling back to pytesseract")
                    use_easyocr = False
            
            for i, page_num in enumerate(pages_to_process):
                # Update progress
                if progress_callback:
                    progress_callback(f"Processing Page {i+1} of {total_pages}...")
                
                page = doc[page_num]
                
                # Get images from page first (fast)
                image_list = page.get_images(full=True)
                page_text_parts = []
                
                # If page has images, extract and OCR them
                if image_list:
                    for img_index, img in enumerate(image_list):
                        try:
                            # Update progress for multiple images on page
                            if len(image_list) > 1 and progress_callback:
                                progress_callback(f"Processing Page {i+1}/{total_pages} (Image {img_index+1}/{len(image_list)})...")
                            
                            xref = img[0]
                            base_image = doc.extract_image(xref)
                            image_bytes = base_image["image"]
                            
                            # Save to temp file
                            temp_img_path = os.path.join(temp_dir, f"page_{page_num}_img_{img_index}.png")
                            with open(temp_img_path, "wb") as img_file:
                                img_file.write(image_bytes)
                            
                            # --- ADVANCED PREPROCESSING ---
                            processed_img_path = OCRProcessor.preprocess_image(temp_img_path)
                            
                            # Perform OCR
                            if use_easyocr:
                                result = reader.readtext(processed_img_path, detail=0)
                                ocr_text = "\n".join(result)
                            else:
                                # Fallback to pytesseract
                                import pytesseract
                                from PIL import Image
                                img = Image.open(processed_img_path)
                                ocr_text = pytesseract.image_to_string(img)
                            
                            # --- POST-PROCESSING ---
                            ocr_text = OCRProcessor.clean_text(ocr_text)
                            
                            if ocr_text.strip():
                                page_text_parts.append(ocr_text.strip())
                        
                        except Exception as e:
                            page_text_parts.append(f"[Error extracting image {img_index}: {str(e)}]")
                else:
                    # No images, render page as image (slower but covers everything)
                    try:
                        # OPTIMIZED: Lower DPI to 200 for faster processing
                        pix = page.get_pixmap(dpi=200) 
                        temp_img_path = os.path.join(temp_dir, f"page_{page_num}_full.png")
                        pix.save(temp_img_path)
                        
                        # --- ADVANCED PREPROCESSING ---
                        processed_img_path = OCRProcessor.preprocess_image(temp_img_path)
                        
                        # Perform OCR
                        if use_easyocr:
                            result = reader.readtext(processed_img_path, detail=0)
                            ocr_text = "\n".join(result)
                        else:
                            import pytesseract
                            from PIL import Image
                            img = Image.open(processed_img_path)
                            ocr_text = pytesseract.image_to_string(img)
                        
                        # --- POST-PROCESSING ---
                        ocr_text = OCRProcessor.clean_text(ocr_text)
                        
                        if ocr_text.strip():
                            page_text_parts.append(ocr_text.strip())
                    
                    except Exception as e:
                        page_text_parts.append(f"[Error rendering page {page_num}: {str(e)}]")
                
                # Combine text from all images on this page
                if page_text_parts:
                    text_parts.append("\n".join(page_text_parts))
            
            doc.close()
            
            # Combine all pages
            final_text = "\n\n--- Page Break ---\n\n".join(text_parts)
            
            if not final_text.strip():
                return True, "[No text could be extracted via OCR]"
            
            return True, final_text
        
        except Exception as e:
            return False, f"OCR extraction failed: {str(e)}"
        
        finally:
            # Clean up temp directory
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass  # Ignore cleanup errors
    
    @staticmethod
    def get_pdf_info(input_path: str) -> Dict:
        """
        Get PDF metadata and information.
        
        Args:
            input_path: Path to PDF file
        
        Returns:
            Dictionary with PDF information
        """
        try:
            reader = PdfReader(input_path)
            doc = fitz.open(input_path)
            
            info = {
                'pages': len(reader.pages),
                'encrypted': reader.is_encrypted,
                'size_bytes': os.path.getsize(input_path),
                'size_mb': round(os.path.getsize(input_path) / (1024 * 1024), 2),
                'author': reader.metadata.get('/Author', 'Unknown') if reader.metadata else 'Unknown',
                'title': reader.metadata.get('/Title', 'Unknown') if reader.metadata else 'Unknown',
                'subject': reader.metadata.get('/Subject', 'Unknown') if reader.metadata else 'Unknown',
                'creator': reader.metadata.get('/Creator', 'Unknown') if reader.metadata else 'Unknown',
            }
            
            doc.close()
            return info
        except Exception:
            return {'error': 'Could not read PDF information'}

    @staticmethod
    def split_by_interval(input_path: str, output_dir: str, interval: int) -> Tuple[bool, str]:
        """
        Split PDF every X pages.
        
        Args:
            input_path: Path to input PDF
            output_dir: Directory to save split PDFs
            interval: Split every X pages
        
        Returns:
            Tuple of (success, message)
        """
        try:
            reader = PdfReader(input_path)
            base_name = os.path.basename(input_path).replace(".pdf", "")
            
            total_pages = len(reader.pages)
            file_count = 0
            
            for start_idx in range(0, total_pages, interval):
                writer = PdfWriter()
                end_idx = min(start_idx + interval, total_pages)
                
                for i in range(start_idx, end_idx):
                    writer.add_page(reader.pages[i])
                
                file_count += 1
                out_file = os.path.join(output_dir, f"{base_name}_part_{file_count}.pdf")
                with open(out_file, "wb") as f:
                    writer.write(f)
            
            return True, f"Split into {file_count} files (every {interval} pages)"
        except Exception as e:
            return False, f"Split failed: {str(e)}"

