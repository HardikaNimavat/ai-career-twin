"""
Resume Parser Service — Extract text from PDF files and images (OCR).

Supports:
- PDF: PyPDF2 for text-based PDFs, pdfplumber for complex layouts
- Images: pytesseract + Pillow for OCR (JPG, PNG, JPEG)
- Plain text passthrough

Time Complexity: O(n) for PDF pages, O(w*h) for OCR where w,h = image dimensions
Space Complexity: O(t) where t = extracted text size
"""

import io
import re
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class ResumeParserService:
    """Parse resumes from PDF/Image/Text and extract clean text."""

    SUPPORTED_PDF = {".pdf"}
    SUPPORTED_IMAGE = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    MAX_FILE_SIZE_MB = 10

    def parse_file(self, file_bytes: bytes, filename: str) -> Tuple[str, str]:
        """
        Parse uploaded file and extract text.

        Returns: (extracted_text, file_type)
        Raises: ValueError on unsupported format or processing failure.
        """
        ext = self._get_extension(filename)
        file_size_mb = len(file_bytes) / (1024 * 1024)

        if file_size_mb > self.MAX_FILE_SIZE_MB:
            raise ValueError(f"File too large ({file_size_mb:.1f}MB). Maximum is {self.MAX_FILE_SIZE_MB}MB.")

        if ext in self.SUPPORTED_PDF:
            text = self._extract_from_pdf(file_bytes)
            return text, "pdf"
        elif ext in self.SUPPORTED_IMAGE:
            text = self._extract_from_image(file_bytes)
            return text, "image"
        else:
            raise ValueError(
                f"Unsupported file format '{ext}'. "
                f"Supported: {', '.join(sorted(self.SUPPORTED_PDF | self.SUPPORTED_IMAGE))}"
            )

    def _get_extension(self, filename: str) -> str:
        """Extract lowercase extension from filename."""
        if "." not in filename:
            return ""
        return "." + filename.rsplit(".", 1)[-1].lower()

    def _extract_from_pdf(self, file_bytes: bytes) -> str:
        """Extract text from PDF using PyPDF2, fallback to pdfplumber."""
        text = ""

        # Try PyPDF2 first (fast, handles text-based PDFs)
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            pages_text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
            text = "\n".join(pages_text)
            logger.info(f"PyPDF2 extracted {len(text)} chars from {len(reader.pages)} pages.")
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {e}")

        # If PyPDF2 got very little text, try pdfplumber (handles complex layouts)
        if len(text.strip()) < 50:
            try:
                import pdfplumber
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    pages_text = []
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            pages_text.append(page_text)
                    plumber_text = "\n".join(pages_text)
                    if len(plumber_text) > len(text):
                        text = plumber_text
                        logger.info(f"pdfplumber extracted {len(text)} chars.")
            except ImportError:
                logger.warning("pdfplumber not installed, skipping complex layout extraction.")
            except Exception as e:
                logger.warning(f"pdfplumber extraction failed: {e}")

        # If still empty, try OCR on PDF pages (scanned PDFs)
        if len(text.strip()) < 50:
            try:
                text = self._ocr_pdf_pages(file_bytes)
                logger.info(f"OCR extracted {len(text)} chars from scanned PDF.")
            except Exception as e:
                logger.warning(f"PDF OCR fallback failed: {e}")

        if not text.strip():
            raise ValueError(
                "Could not extract text from PDF. "
                "The file may be empty, corrupted, or a scanned image PDF. "
                "Try uploading as an image instead, or paste the text directly."
            )

        return self._clean_text(text)

    def _extract_from_image(self, file_bytes: bytes) -> str:
        """Extract text from image using OCR (pytesseract + Pillow)."""
        try:
            from PIL import Image
            image = Image.open(io.BytesIO(file_bytes))

            # Preprocess for better OCR accuracy
            image = self._preprocess_image(image)

            try:
                import pytesseract
                text = pytesseract.image_to_string(image, lang="eng")
                logger.info(f"OCR extracted {len(text)} chars from image.")
            except ImportError:
                logger.error("pytesseract not installed. Install with: pip install pytesseract")
                raise ValueError(
                    "OCR engine (pytesseract) is not installed. "
                    "Please install it or paste your resume text directly."
                )

            if not text.strip():
                raise ValueError(
                    "Could not extract text from image. "
                    "Please ensure the image is clear and contains readable text."
                )

            return self._clean_text(text)

        except ImportError:
            raise ValueError(
                "Image processing library (Pillow) is not installed. "
                "Please paste your resume text directly."
            )

    def _preprocess_image(self, image):
        """Preprocess image for better OCR accuracy."""
        from PIL import Image, ImageFilter, ImageEnhance

        # Convert to RGB if necessary
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Resize if too small (OCR works better with larger images)
        width, height = image.size
        if width < 1000:
            scale = 1000 / width
            image = image.resize(
                (int(width * scale), int(height * scale)),
                Image.LANCZOS
            )

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)

        # Sharpen
        image = image.filter(ImageFilter.SHARPEN)

        # Convert to grayscale for OCR
        image = image.convert("L")

        return image

    def _ocr_pdf_pages(self, file_bytes: bytes) -> str:
        """OCR each page of a scanned PDF."""
        try:
            from pdf2image import convert_from_bytes
            import pytesseract

            images = convert_from_bytes(file_bytes, dpi=300)
            texts = []
            for i, img in enumerate(images[:10]):  # Max 10 pages
                img = self._preprocess_image(img)
                page_text = pytesseract.image_to_string(img, lang="eng")
                if page_text.strip():
                    texts.append(page_text)
            return "\n".join(texts)
        except ImportError:
            raise ValueError(
                "PDF OCR requires pdf2image and pytesseract. "
                "Please install them or paste your resume text directly."
            )

    def _clean_text(self, text: str) -> str:
        """Clean extracted text: normalize whitespace, remove artifacts."""
        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Remove excessive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Remove page header/footer artifacts (common in PDFs)
        text = re.sub(r"Page \d+ of \d+", "", text)
        # Normalize whitespace within lines
        text = re.sub(r"[ \t]+", " ", text)
        # Strip leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)
        return text.strip()


# Singleton instance
resume_parser = ResumeParserService()
