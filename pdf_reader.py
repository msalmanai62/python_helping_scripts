import easyocr
from PIL import Image
import numpy as np
import pymupdf

# this script is for reading pdfs. It is for both plain pdfs and scanned pdfs (image base pdfs).
async def extract_pdf_text(
        pdf_path:str,
        reader:easyocr.Reader = easyocr.Reader(["en"], gpu=True),
        read_images:bool=True
        )->str:
    """
    Extracts text from a PDF, including OCR for images.
    
    Args:
        pdf_path (str): Path to the PDF file
        reader (easyocr.Reader): EasyOCR reader object
        read_images (bool): Whether to extract text from images in the PDF
    Returns:
        full_doc_text (str): Text extracted from the PDF
    """
    pdf_file = pymupdf.open(pdf_path)
    full_doc_text = ""
    # Iterate over PDF pages
    for page_index, page in enumerate(pdf_file):
        page_text = page.get_text("text").strip()
        image_text = ""
        if read_images:
            # Extract images from the page
            image_list = page.get_images(full=True)  # full=True gives higher resolution images
            print(f"Porcessing page: {page_index}")
            for image_index, img in enumerate(image_list, start=1):
                try:
                    rotation_angle = page.rotation  # Handle page rotation. Because pages (or images on pages) may be rotated. And easyocr does not handle rotation well. so it will result in wrong output.

                    # print("rotation_angle", rotation_angle)
                    xref = img[0]  # Get the XREF of the image
                    pix = pymupdf.Pixmap(pdf_file, xref) # create a Pixmap
                    # Convert CMYK, Alpha, or Grayscale to RGB
                    if pix.n == 4:  # RGBA (has transparency)
                        img_pil = Image.frombytes("RGBA", [pix.width, pix.height], pix.samples)
                        img_pil = img_pil.convert("RGB")  # Convert to RGB
                    elif pix.n == 1:  # Grayscale
                        img_pil = Image.frombytes("L", [pix.width, pix.height], pix.samples)
                        img_pil = img_pil.convert("RGB")  # Convert to RGB
                    else:  # Assume RGB
                        img_pil = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    if rotation_angle:
                        img_pil = img_pil.rotate(-rotation_angle, expand=True)
                    # Extract text from the image using EasyOCR
                    extracted_text = reader.readtext(np.array(img_pil), detail=0, paragraph=False)  # Extract text from image
                    image_text = image_text + "\n" + '\n'.join(extracted_text)
                except Exception as e:
                    # raise
                    print(f"Error while fetching images in page: {page_index}: {e}")
                # print(f"Image {image_index} OCR Text:\n{'\n'.join(extracted_text)}\n")
        full_page_text = f"PAGE: {page_index}\n {page_text}\nIMAGE_EXTRACTED_TEXT\n {image_text}"
        full_doc_text  = full_doc_text + "\n" + full_page_text
    return full_doc_text

if __name__=="__main__":
    path = 'file.pdf'
    import asyncio
    full_doc_text = asyncio.run(extract_pdf_text(pdf_path=path))
    with open('results.txt', 'w') as file:
        file.write(full_doc_text)
