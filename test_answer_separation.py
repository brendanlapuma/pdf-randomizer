import pypdf
import re

pdf = pypdf.PdfReader('practice.pdf')
text = ""
for i in range(min(3, len(pdf.pages))):
    text += pdf.pages[i].extract_text() + "\n"

# Apply fixes
page_text = re.sub(r'(\.["\u201C\u201D\u2018\u2019])([A-E])\.\s+', r'\1\n\2. ', text)
page_text = re.sub(r'\.([A-E])\.\s+', r'.\n\1. ', page_text)
page_text = re.sub(r'([a-z\)])([A-E])\.\s+', r'\1\n\2. ', page_text)

# Extract questions
pattern = r'(\d+)\.\s+(.*?)(?=\n?\d+\.\s+|$)'
matches = list(re.finditer(pattern, page_text, re.DOTALL))

print(f"Found {len(matches)} questions\n")

for i, match in enumerate(matches[:15]):  # Check first 15 questions
    q_num = match.group(1)
    q_content = match.group(2).strip()
    
    answer_start = re.search(r'\n?[A-E]\.\s+', q_content)
    if answer_start:
        q_text = q_content[:answer_start.start()].strip()
        answers_text = q_content[answer_start.start():].strip()
        
        # Extract answers
        answer_pattern = r'([A-E])\.\s+([^\n]+?)(?=\n[A-E]\.|$)'
        answer_matches = list(re.finditer(answer_pattern, answers_text, re.MULTILINE))
        
        if len(answer_matches) != 5:
            print(f"Q{q_num}: Found {len(answer_matches)} answers (expected 5)")
            for ans_match in answer_matches:
                letter = ans_match.group(1)
                ans_text = ans_match.group(2).strip()
                print(f"  {letter}. {ans_text[:80]}")
            print(f"  RAW: {repr(answers_text[:200])}\n")
