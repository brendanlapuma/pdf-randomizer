import io
import re
import random
from typing import List, Dict, Tuple
import modal
from fastapi import Request
from starlette.responses import Response

# Create a Modal app
app = modal.App("pdf-randomizer")

# Define the image with required dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "pypdf>=5.1.0",
    "reportlab>=4.0.0",
    "pillow>=10.0.0",
    "fastapi[standard]"
)


class Question:
    """Represents a multiple-choice question with answers."""
    
    def __init__(self, number: int, text: str, answers: List[Tuple[str, str]]):
        self.number = number
        self.text = text
        self.answers = answers  # List of (letter, text) tuples
    
    def randomize_answers(self):
        """Randomize the order of answers while keeping track of the mapping."""
        # Shuffle answers
        random.shuffle(self.answers)
        # Reassign letters A, B, C, D, E... in order
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
        # Handle edge case where there might be more answers than expected
        num_answers = min(len(self.answers), len(letters))
        self.answers = [(letters[i], text) for i, (_, text) in enumerate(self.answers[:num_answers])]


def extract_questions_from_pdf(pdf_bytes: bytes) -> List[Question]:
    """Extract questions from PDF content."""
    from pypdf import PdfReader
    
    pdf = PdfReader(io.BytesIO(pdf_bytes))
    all_text = ""
    
    # Extract text from all pages
    for page in pdf.pages:
        page_text = page.extract_text()
        
        # Fix ligatures and special characters
        page_text = page_text.replace('ﬂ', 'fl')
        page_text = page_text.replace('ﬁ', 'fi')
        page_text = page_text.replace('ﬀ', 'ff')
        page_text = page_text.replace('ﬃ', 'ffi')
        page_text = page_text.replace('ﬄ', 'ffl')
        
        # Fix common PDF extraction issues:
        # 1. Add newline before answer choices that follow text
        # First handle special case of ."D. or ."D. pattern (quote with period before answer)
        # Handle both ASCII quotes and Unicode quotes (", ", etc.)
        page_text = re.sub(r'(\.["\u201C\u201D\u2018\u2019])([A-E])\.\s+', r'\1\n\2. ', page_text)
        # Handle cases where period is directly followed by answer letter: .B. -> .\nB.
        page_text = re.sub(r'\.([A-E])\.\s+', r'.\n\1. ', page_text)
        # Handle cases where period space letter: . D. -> .\nD.
        page_text = re.sub(r'\.\s+([A-E])\.\s+', r'.\n\1. ', page_text)
        # Then handle general cases like "word)B. ", etc.
        page_text = re.sub(r'([a-z\)])([A-E])\.\s+', r'\1\n\2. ', page_text)
        
        # 2. Add space between words that are stuck together
        # Common word patterns - add space before common English words
        common_words = ['the', 'of', 'in', 'is', 'are', 'and', 'that', 'to', 'as', 
                       'an', 'be', 'by', 'for', 'or', 'at', 'can', 'not', 'with',
                       'from', 'have', 'has', 'had', 'but', 'if', 'about', 'which',
                       'all', 'when', 'will', 'more', 'other', 'into', 'after',
                       'its', 'only', 'some', 'such', 'than', 'them', 'these',
                       'their', 'would', 'make', 'like', 'what', 'been', 'called']
        
        for word in common_words:
            # Add space before the word if preceded by a lowercase letter
            page_text = re.sub(f'([a-z])({word})\\b', r'\1 \2', page_text)
        
        # Add space between lowercase and uppercase (like "bacteriaCannot" -> "bacteria Cannot")
        page_text = re.sub(r'([a-z])([A-Z])', r'\1 \2', page_text)
        
        all_text += page_text + "\n"
        page_text = re.sub(r'([a-z])of\b', r'\1 of', page_text)
        page_text = re.sub(r'([a-z])the\b', r'\1 the', page_text)
        page_text = re.sub(r'([a-z])in\b', r'\1 in', page_text)
        page_text = re.sub(r'([a-z])is\b', r'\1 is', page_text)
        page_text = re.sub(r'([a-z])about\b', r'\1 about', page_text)
        page_text = re.sub(r'([a-z])and\b', r'\1 and', page_text)
        page_text = re.sub(r'([a-z])that\b', r'\1 that', page_text)
        page_text = re.sub(r'([a-z])as\b', r'\1 as', page_text)
        page_text = re.sub(r'([a-z])are\b', r'\1 are', page_text)
        page_text = re.sub(r'([a-z])an\b', r'\1 an', page_text)
        page_text = re.sub(r'([a-z])to\b', r'\1 to', page_text)
        all_text += page_text + "\n"
    
    # Pattern to match questions (number followed by period and question text)
    question_pattern = r'(\d+)\.\s+(.*?)(?=\n?\d+\.\s+|$)'
    
    questions = []
    
    # Split text into potential question blocks
    question_matches = re.finditer(question_pattern, all_text, re.DOTALL)
    
    for match in question_matches:
        q_num = int(match.group(1))
        q_content = match.group(2).strip()
        
        # Find the actual question text (everything before first answer choice)
        # Look for newline followed by A. or just A. at start
        answer_start = re.search(r'\n?[A-E]\.\s+', q_content)
        if answer_start:
            q_text = q_content[:answer_start.start()].strip()
            answers_text = q_content[answer_start.start():].strip()
            
            # Extract all answer choices - they're now on separate lines
            answers = []
            # Match answer choices that start at beginning of line or after newline
            answer_pattern = r'([A-E])\.\s+([^\n]+?)(?=\n[A-E]\.|$)'
            answer_matches = re.finditer(answer_pattern, answers_text, re.MULTILINE)
            
            for ans_match in answer_matches:
                letter = ans_match.group(1)
                ans_text = ans_match.group(2).strip()
                if ans_text:  # Only add non-empty answers
                    answers.append((letter, ans_text))
            
            if answers and q_text:  # Only create question if it has answers and text
                questions.append(Question(q_num, q_text, answers))
    
    return questions


def generate_pdf_from_questions(questions: List[Question]) -> bytes:
    """Generate a new PDF from the list of questions."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_LEFT
    
    # Create a buffer for the PDF
    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Container for the 'Flowable' objects
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom style for questions
    question_style = ParagraphStyle(
        'QuestionStyle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    # Custom style for answers
    answer_style = ParagraphStyle(
        'AnswerStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        leftIndent=20,
        spaceAfter=3
    )
    
    # Add questions to the story
    for i, question in enumerate(questions, 1):
        # Add question number and text
        q_text = f"{i}. {question.text}"
        story.append(Paragraph(q_text, question_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Add answer choices
        for letter, ans_text in question.answers:
            a_text = f"{letter}. {ans_text}"
            story.append(Paragraph(a_text, answer_style))
        
        # Add space between questions
        story.append(Spacer(1, 0.2*inch))
        
        # Add page break every 6 questions to avoid overcrowding
        if i % 6 == 0 and i < len(questions):
            story.append(PageBreak())
    
    # Build the PDF
    doc.build(story)
    
    # Get the PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


@app.function(image=image, timeout=300)
def randomize_pdf(pdf_bytes: bytes) -> bytes:
    """
    Main function to randomize a PDF.
    Extracts questions, randomizes their order and answer choices, then generates a new PDF.
    """
    # Extract questions from the PDF
    questions = extract_questions_from_pdf(pdf_bytes)
    
    if not questions:
        raise ValueError("No questions found in the PDF")
    
    # Deduplicate questions based on question text and first answer
    # (Some PDFs have the same questions repeated across sections)
    seen = set()
    unique_questions = []
    for q in questions:
        # Create a fingerprint based on question text and first answer
        if q.answers:
            fingerprint = (q.text[:100], q.answers[0][1][:50])  # Use first 100 chars of question, first 50 of first answer
            if fingerprint not in seen:
                seen.add(fingerprint)
                unique_questions.append(q)
        else:
            unique_questions.append(q)
    
    questions = unique_questions
    print(f"After deduplication: {len(questions)} unique questions")
    
    # Randomize the order of questions
    random.shuffle(questions)
    
    # Randomize answers within each question
    for question in questions:
        question.randomize_answers()
    
    # Generate new PDF with randomized content
    new_pdf_bytes = generate_pdf_from_questions(questions)
    
    return new_pdf_bytes


@app.function(image=image)
@modal.fastapi_endpoint(method="POST")
async def randomize_pdf_endpoint(request: Request):
    """
    Web endpoint to randomize a PDF.
    
    Usage:
        curl -X POST https://your-modal-url/randomize_pdf_endpoint \\
             -F "file=@practice.pdf" \\
             --output randomized.pdf
    """
    # Get the uploaded file from the request
    form = await request.form()
    file_data = form.get("file")
    
    if not file_data:
        return Response(
            content="No file uploaded. Please upload a PDF file using 'file' form field.",
            status_code=400
        )
    
    # Read the file bytes
    pdf_bytes = file_data.file.read()
    
    # Process the PDF
    try:
        randomized_pdf = randomize_pdf.remote(pdf_bytes)
        
        # Return the randomized PDF
        return Response(
            content=randomized_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=randomized.pdf"
            }
        )
    except Exception as e:
        return Response(
            content=f"Error processing PDF: {str(e)}",
            status_code=500
        )


@app.local_entrypoint()
def main(input_pdf: str = "practice.pdf", output_pdf: str = "randomized.pdf"):
    """
    Local entrypoint for testing.
    
    Usage:
        modal run app.py --input-pdf practice.pdf --output-pdf randomized.pdf
    """
    # Read the input PDF
    with open(input_pdf, "rb") as f:
        pdf_bytes = f.read()
    
    # Randomize the PDF
    randomized_pdf = randomize_pdf.remote(pdf_bytes)
    
    # Write the output PDF
    with open(output_pdf, "wb") as f:
        f.write(randomized_pdf)
    
    print(f"Randomized PDF saved to {output_pdf}")
