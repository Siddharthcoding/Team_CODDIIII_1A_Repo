import os
import sys
import argparse
import pandas as pd
from joblib import load
import json
import pdfplumber
import re

def extract_lines(pdf_path, extracted_csv):
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
                    })
    df = pd.DataFrame(lines)
    df.to_csv(extracted_csv, index=False)
    print(f"✅ Extracted full lines to {extracted_csv}")
    return df

def generate_features(df):
    def is_all_caps(s): return str(s).isupper()
    def is_title_case(s): return str(s).istitle()
    def has_number_prefix(s): return bool(re.match(r"^\d+(\.\d+)*", str(s)))
    def word_count(s): return len(str(s).split())
    df['char_len'] = df['text'].apply(len)
    df['word_count'] = df['text'].apply(word_count)
    df['is_all_caps'] = df['text'].apply(is_all_caps).astype(int)
    df['is_title_case'] = df['text'].apply(is_title_case).astype(int)
    df['has_number_prefix'] = df['text'].apply(has_number_prefix).astype(int)
    df['avg_fontSize_by_page'] = df.groupby('page')['char_len'].transform('mean')
    df['relative_fontSize'] = df['char_len'] - df['avg_fontSize_by_page']
    return df

def classify_lines(df, model_path, prediction_csv):
    model = load(model_path)
    feature_cols = [
        'char_len', 'word_count', 'is_all_caps', 'is_title_case',
        'has_number_prefix', 'relative_fontSize'
    ]
    df_features = generate_features(df)
    df['predicted_label'] = model.predict(df_features[feature_cols])
    df.to_csv(prediction_csv, index=False)
    print(f"✅ Saved predictions to {prediction_csv}")
    return df

def build_outline(prediction_csv, outline_json):
    df = pd.read_csv(prediction_csv)
    headings = df[df['predicted_label'] != "body"]
    outline = []
    def get_level(label):
        return {
            "title": 0,
            "h1": 1,
            "h2": 2,
            "h3": 3
        }.get(label.lower(), 10)
    stack = []
    for _, row in headings.iterrows():
        heading = {
            "level": row["predicted_label"].upper(),
            "text": row["text"],
            "page": int(row["page"]),
            "children": []
        }
        while stack and get_level(stack[-1]["level"]) >= get_level(heading["level"]):
            stack.pop()
        if stack:
            stack[-1]["children"].append(heading)
        else:
            outline.append(heading)
        stack.append(heading)
    output = {
        "title": outline[0]["text"] if outline else "Untitled",
        "outline": outline
    }
    with open(outline_json, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"✅ Outline constructed in {outline_json}")

def main():
    parser = argparse.ArgumentParser(description="Generate outline JSON for given PDF")
    parser.add_argument("--pdf", required=True, help="Input PDF filename (just file name, e.g. file02.pdf)")
    args = parser.parse_args()
    pdf_name = args.pdf
    pdf_path = os.path.join("input", pdf_name)
    if not os.path.exists(pdf_path):
        print(f"❌ File 'input/{pdf_name}' not found!")
        sys.exit(1)

    file_id = os.path.splitext(pdf_name)[0]
    extracted_csv = f"dataset/extracted_lines.csv"
    processed_csv = f"dataset/processed_lines.csv"
    prediction_csv = f"dataset/headings_with_predictions.csv"
    outline_json = f"output/final_outline.json"

    # 1. Extract
    df = extract_lines(pdf_path, extracted_csv)

    # 2. Features
    df = pd.read_csv(extracted_csv, encoding='utf-8-sig')
    df = generate_features(df)
    df.to_csv(processed_csv, index=False)
    print(f"✅ Features saved to {processed_csv}")

    # 3. Classify
    classify_lines(df, "models/heading_classifier.joblib", prediction_csv)

    # 4. Outline
    build_outline(prediction_csv, outline_json)

    print(f"\n🎉 DONE: See outline JSON at '{outline_json}'")

if __name__ == "__main__":
    main()
