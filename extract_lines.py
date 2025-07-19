import pdfplumber
import pandas as pd

def extract_lines(pdf_path):
    lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                for i, line in enumerate(text.split('\n')):
                    lines.append({
                        "text": line.strip(),
                        "page": page_num + 1,
                        "line_num": i,
                        # You can add default fontSize or calculate later
                    })
    return pd.DataFrame(lines)

# Run this
df = extract_lines("input/file02.pdf")
df.to_csv("dataset/extracted_lines.csv", index=False)
print("✅ Extracted full lines")
print(df.head())
