# backend/process_books.py
import os
import re
import json
from pypdf import PdfReader


def extract_text_from_pdf(pdf_path):
    """Extract text content from a PDF file."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def clean_text(text):
    """Clean and normalize the extracted text."""
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    return text


def extract_chapters(text, book_number):
    chapter_pattern = re.compile(r'CHAPTER (\d+|[IVX]+|[A-Z ]+)')
    chapter_matches = list(chapter_pattern.finditer(text))

    number_map = {
        'ONE': 1, 'TWO': 2, 'THREE': 3, 'FOUR': 4, 'FIVE': 5,
        'SIX': 6, 'SEVEN': 7, 'EIGHT': 8, 'NINE': 9, 'TEN': 10,
        'ELEVEN': 11, 'TWELVE': 12, 'THIRTEEN': 13, 'FOURTEEN': 14, 'FIFTEEN': 15,
        'SIXTEEN': 16, 'SEVENTEEN': 17, 'EIGHTEEN': 18, 'NINETEEN': 19, 'TWENTY': 20,
        'TWENTY ONE': 21, 'TWENTY TWO': 22, 'TWENTY THREE': 23, 'TWENTY FOUR': 24, 'TWENTY FIVE': 25,
        'TWENTY SIX': 26, 'TWENTY SEVEN': 27, 'TWENTY EIGHT': 28, 'TWENTY NINE': 29, 'THIRTY': 30,
        'THIRTY ONE': 31, 'THIRTY TWO': 32, 'THIRTY THREE': 33, 'THIRTY FOUR': 34, 'THIRTY FIVE': 35,
        'THIRTY SIX': 36, 'THIRTY SEVEN': 37, 'THIRTY EIGHT': 38, 'THIRTY NINE': 39, 'FORTY': 40
    }

    chapters = []

    for i in range(len(chapter_matches)):
        start_pos = chapter_matches[i].start()
        end_pos = chapter_matches[i + 1].start() if i < len(chapter_matches) - 1 else len(text)
        chapter_text = text[start_pos:end_pos]

        chapter_header = chapter_matches[i].group(0)
        chapter_num = chapter_matches[i].group(1)

        # Normalize the chapter number
        chapter_num_stripped = chapter_num.upper().strip()
        if chapter_num_stripped in number_map:
            chapter_id = number_map[chapter_num_stripped]
        else:
            chapter_id = chapter_num

        chapter = {
            "book": book_number,
            "chapter": int(chapter_id) if str(chapter_id).isdigit() else chapter_id,
            "text": chapter_text.strip()
        }

        chapters.append(chapter)

    return chapters


def process_books(pdf_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    all_chapters = []

    books = {
        1: "HP1.pdf",
        2: "HP2.pdf",
        3: "HP3.pdf",
        4: "HP4.pdf"
    }

    for book_num, filename in books.items():
        filepath = os.path.join(pdf_dir, filename)

        if os.path.exists(filepath):
            print(f"Processing Book {book_num}...")

            text = extract_text_from_pdf(filepath)
            text = clean_text(text)

            with open(os.path.join(output_dir, f"book_{book_num}_raw.txt"), "w", encoding="utf-8") as f:
                f.write(text)

            chapters = extract_chapters(text, book_num)

            for chapter in chapters:
                all_chapters.append(chapter)

            print(f"Extracted {len(chapters)} chapters from Book {book_num}")
        else:
            print(f"Warning: Book {book_num} file not found at {filepath}")

    with open(os.path.join(output_dir, "all_chapters.json"), "w", encoding="utf-8") as f:
        json.dump(all_chapters, f, indent=2)

    print(f"Processed {len(all_chapters)} chapters total from {len(books)} books")
    return all_chapters


if __name__ == "__main__":
    pdf_dir = "../data/Pdfs"
    output_dir = "../data/processed"
    process_books(pdf_dir, output_dir)
