import pypdf
import re

pdf = pypdf.PdfReader('practice.pdf')
text = pdf.pages[0].extract_text()

# Apply fixes - updated regex
page_text = re.sub(r'(\."?)([A-E])\.\s+', r'\1\n\2. ', text)
page_text = re.sub(r'([a-z\)])([A-E])\.\s+', r'\1\n\2. ', page_text)

# Extract all questions
pattern = r'(\d+)\.\s+(.*?)(?=\n?\d+\.\s+|$)'
matches = re.finditer(pattern, page_text, re.DOTALL)

for i, match in enumerate(matches):
    if i >= 5:  # Only check first 5 questions
        break
    
    q_num = match.group(1)
    q_content = match.group(2).strip()
    
    answer_start = re.search(r'\n?[A-E]\.\s+', q_content)
    if answer_start:
        q_text = q_content[:answer_start.start()].strip()
        answers_text = q_content[answer_start.start():].strip()
        
        # Extract answers
        answer_pattern = r'([A-E])\.\s+([^\n]+?)(?=\n[A-E]\.|$)'
        answer_matches = list(re.finditer(answer_pattern, answers_text, re.MULTILINE))
        
        print(f"\n=== Question {q_num} ===")
        print(f"Q: {q_text[:80]}...")
        print(f"Found {len(answer_matches)} answers:")
        for ans_match in answer_matches:
            letter = ans_match.group(1)
            ans_text = ans_match.group(2).strip()
            print(f"  {letter}. {ans_text[:100]}")
        
        # Show raw answers text for debugging
        if len(answer_matches) < 5:
            print(f"\nRAW ANSWERS TEXT:")
            print(repr(answers_text[:300]))
