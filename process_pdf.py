import os
import sys
import argparse
import pandas as pd
from joblib import load
import json
import pdfplumber
import re
import tempfile
from pathlib import Path
from glob import glob
from googletrans import Translator


translator = Translator()

def extract_lines(pdf_path, extracted_csv):
    """Extract text lines from PDF with page numbers"""
    lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                for line_num, line in enumerate(text.split('\n'), start=1):
                    lines.append({
                        "text": line.strip(),
                        "page": page_num,
                        "line_num": line_num,
                    })
    df = pd.DataFrame(lines)
    df.to_csv(extracted_csv, index=False)
    print(f"✅ Extracted {len(df)} lines to {extracted_csv}")
    return df

def generate_features(df):
    """Generate features for heading classification"""
    def is_all_caps(s): return str(s).isupper()
    def is_title_case(s): return str(s).istitle()
    def has_number_prefix(s): return bool(re.match(r"^\d+(\.\d+)*", str(s)))
    def word_count(s): return len(str(s).split())
    
    features = {
        'char_len': df['text'].apply(len),
        'word_count': df['text'].apply(word_count),
        'is_all_caps': df['text'].apply(is_all_caps).astype(int),
        'is_title_case': df['text'].apply(is_title_case).astype(int),
        'has_number_prefix': df['text'].apply(has_number_prefix).astype(int)
    }
    
    for name, feature in features.items():
        df[name] = feature
    
    df['avg_fontSize_by_page'] = df.groupby('page')['char_len'].transform('mean')
    df['relative_fontSize'] = df['char_len'] - df['avg_fontSize_by_page']
    return df

def classify_lines(df, model_path, prediction_csv):
    """Classify lines using the trained model"""
    model = load(model_path)
    feature_cols = [
        'char_len', 'word_count', 'is_all_caps', 
        'is_title_case', 'has_number_prefix', 'relative_fontSize'
    ]
    df['predicted_label'] = model.predict(df[feature_cols])
    df.to_csv(prediction_csv, index=False)
    print(f"✅ Classified {len(df)} lines, saved to {prediction_csv}")
    return df

def build_outline(prediction_csv, outline_json):
    """Build hierarchical outline from classified headings"""
    df = pd.read_csv(prediction_csv)
    headings = df[df['predicted_label'] != "body"]
    
    outline = []
    level_map = {"title": 0, "h1": 1, "h2": 2, "h3": 3}
    
    stack = []
    for _, row in headings.iterrows():
        current_level = level_map.get(row["predicted_label"].lower(), 10)
        heading = {
            "level": row["predicted_label"].upper(),
            "text":  translator.translate(row["text"],dest='en').text,
            "page": int(row["page"]),
            "children": []
        }
        
        # Pop stack until we find parent level
        while stack and level_map[stack[-1]["level"].lower()] >= current_level:
            stack.pop()
            
        if stack:
            stack[-1]["children"].append(heading)
        else:
            outline.append(heading)
            
        stack.append(heading)
    
    result = {
        "title": outline[0]["text"] if outline else "Untitled",
        "outline": outline
    }
    
    with open(outline_json, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Built outline with {len(outline)} top-level items, saved to {outline_json}")

def process_pdf(pdf_path, output_dir, model_path):
    """Process a single PDF file end-to-end"""
    file_id = Path(pdf_path).stem
    print(f"\n🔍 Processing: {file_id}")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Temporary files
        tmp_files = {
            'extracted': os.path.join(tmp_dir, f"extracted_{file_id}.csv"),
            'processed': os.path.join(tmp_dir, f"processed_{file_id}.csv"),
            'predictions': os.path.join(tmp_dir, f"predictions_{file_id}.csv")
        }
        
        # Output file
        output_json = os.path.join(output_dir, f"{file_id}.json")
        
        try:
            # Pipeline
            df = extract_lines(pdf_path, tmp_files['extracted'])
            df = generate_features(pd.read_csv(tmp_files['extracted']))
            df.to_csv(tmp_files['processed'], index=False)
            classify_lines(df, model_path, tmp_files['predictions'])
            build_outline(tmp_files['predictions'], output_json)
            
            return True
        except Exception as e:
            print(f"❌ Processing failed: {str(e)}", file=sys.stderr)
            return False

def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="PDF Structure Extractor - Generates hierarchical outlines from PDFs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--pdf", 
        help="Process specific PDF file (relative to input dir)"
    )
    parser.add_argument(
        "--input-dir", 
        default="input", 
        help="Directory containing input PDFs"
    )
    parser.add_argument(
        "--output-dir", 
        default="output", 
        help="Directory for output JSON files"
    )
    parser.add_argument(
        "--model", 
        default="models/heading_classifier.joblib", 
        help="Path to trained model file"
    )
    
    args = parser.parse_args()
    
    # Ensure directories exist
    Path(args.input_dir).mkdir(parents=True, exist_ok=True)
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    # Process files
    if args.pdf:
        # Single file mode
        pdf_path = os.path.join(args.input_dir, args.pdf)
        if not Path(pdf_path).exists():
            print(f"❌ Error: File not found - {pdf_path}", file=sys.stderr)
            sys.exit(1)
            
        success = process_pdf(pdf_path, args.output_dir, args.model)
        sys.exit(0 if success else 1)
    else:
        # Batch processing
        pdf_files = list(Path(args.input_dir).glob("*.pdf"))
        if not pdf_files:
            print(f"ℹ️ No PDF files found in {args.input_dir}")
            sys.exit(0)
            
        print(f"🔍 Found {len(pdf_files)} PDFs to process")
        success_count = sum(
            process_pdf(str(pdf), args.output_dir, args.model) 
            for pdf in pdf_files
        )
        
        print(f"\n✅ Successfully processed {success_count}/{len(pdf_files)} files")
        print(f"Output JSONs saved to: {args.output_dir}")

if __name__ == "__main__":
    main()