# Extracting textual data from query image
import pytesseract
from PIL import Image
import io, base64
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=2)  # Adjust number of threads as needed

def decode_image(base64_img: str) -> Image.Image:
    return Image.open(io.BytesIO(base64.b64decode(base64_img)))

def extract_text_from_image_sync(image: Image.Image) -> str:
    # Synchronous, blocking OCR call
    return pytesseract.image_to_string(image)

async def extract_text_from_image(image: Image.Image) -> str:
    # Async wrapper that runs blocking OCR in threadpool
    loop = asyncio.get_event_loop()
    text = await loop.run_in_executor(executor, extract_text_from_image_sync, image)
    return text
