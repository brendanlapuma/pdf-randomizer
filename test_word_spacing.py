import pypdf
import re

pdf = pypdf.PdfReader('practice.pdf')

# Test with one page
page_text = pdf.pages[0].extract_text()

print("=== BEFORE word spacing ===")
# Apply only the answer separation fixes
page_text = page_text.replace('ﬂ', 'fl')
page_text = page_text.replace('ﬁ', 'fi')
page_text = re.sub(r'(\.["\u201C\u201D\u2018\u2019])([A-E])\.\s+', r'\1\n\2. ', page_text)
page_text = re.sub(r'\.([A-E])\.\s+', r'.\n\1. ', page_text)
page_text = re.sub(r'\.\s+([A-E])\.\s+', r'.\n\1. ', page_text)
page_text = re.sub(r'([a-z\)])([A-E])\.\s+', r'\1\n\2. ', page_text)

pattern = r'(\d+)\.\s+'
matches = re.findall(pattern, page_text)
print(f"Found {len(set(matches))} unique question numbers")

print("\n=== AFTER lowercase-uppercase spacing ===")
page_text = re.sub(r'([a-z])([A-Z])', r'\1 \2', page_text)
matches = re.findall(pattern, page_text)
print(f"Found {len(set(matches))} unique question numbers")

print("\n=== AFTER common word spacing ===")
common_words = ['the', 'of', 'in', 'is', 'are', 'and', 'that', 'to', 'as', 
               'an', 'be', 'by', 'for', 'or', 'at', 'can', 'not', 'with',
               'from', 'have', 'has', 'had', 'but', 'if', 'about', 'which',
               'all', 'when', 'will', 'more', 'other', 'into', 'after',
               'its', 'only', 'some', 'such', 'than', 'them', 'these',
               'their', 'would', 'make', 'like', 'what', 'been', 'called']

for word in common_words:
    page_text = re.sub(f'([a-z])({word})\\b', r'\1 \2', page_text)

matches = re.findall(pattern, page_text)
print(f"Found {len(set(matches))} unique question numbers")

# Check if the regex is creating false patterns
false_patterns = re.findall(r'\d+\.\s+[A-Z]', page_text)
print(f"Patterns that look like '123. A': {len(false_patterns)}")
