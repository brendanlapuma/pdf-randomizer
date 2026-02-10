import pypdf
import re

pdf = pypdf.PdfReader('practice.pdf')

all_text = ""
for page in pdf.pages:  # Check ALL pages
    page_text = page.extract_text()
    
    # Apply all fixes
    page_text = page_text.replace('ﬂ', 'fl')
    page_text = page_text.replace('ﬁ', 'fi')
    
    page_text = re.sub(r'(\.["\u201C\u201D\u2018\u2019])([A-E])\.\s+', r'\1\n\2. ', page_text)
    page_text = re.sub(r'\.([A-E])\.\s+', r'.\n\1. ', page_text)
    page_text = re.sub(r'\.\s+([A-E])\.\s+', r'.\n\1. ', page_text)
    page_text = re.sub(r'([a-z\)])([A-E])\.\s+', r'\1\n\2. ', page_text)
    
    # Add common word spacing
    common_words = ['the', 'of', 'in', 'is', 'are', 'and', 'that', 'to', 'as', 
                   'an', 'be', 'by', 'for', 'or', 'at', 'can', 'not', 'with',
                   'from', 'have', 'has', 'had', 'but', 'if', 'about', 'which',
                   'all', 'when', 'will', 'more', 'other', 'into', 'after',
                   'its', 'only', 'some', 'such', 'than', 'them', 'these',
                   'their', 'would', 'make', 'like', 'what', 'been', 'called']
    
    for word in common_words:
        page_text = re.sub(f'([a-z])({word})\\b', r'\1 \2', page_text)
    
    page_text = re.sub(r'([a-z])([A-Z])', r'\1 \2', page_text)
    
    all_text += page_text + "\n"

# Extract questions
pattern = r'(\d+)\.\s+(.*?)(?=\n?\d+\.\s+|$)'
matches = list(re.finditer(pattern, all_text, re.DOTALL))

print(f"Found {len(matches)} questions\n")

for i, match in enumerate(matches):
    q_num = match.group(1)
    q_content = match.group(2).strip()
    
    answer_start = re.search(r'\n?[A-E]\.\s+', q_content)
    if answer_start:
        answers_text = q_content[answer_start.start():].strip()
        answer_pattern = r'([A-E])\.\s+([^\n]+?)(?=\n[A-E]\.|$)'
        answer_matches = list(re.finditer(answer_pattern, answers_text, re.MULTILINE))
        
        if len(answer_matches) > 10:
            print(f'Q{q_num} has {len(answer_matches)} answers - TOO MANY!')
            print('First few answers:')
            for j, ans in enumerate(answer_matches[:15]):
                print(f'  {ans.group(1)}. {ans.group(2).strip()[:60]}')
            print()
