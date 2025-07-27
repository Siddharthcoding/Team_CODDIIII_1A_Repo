import os
import argparse
import pandas as pd
from joblib import load

# ✅ Import existing modular functions
from extract_lines import extract_lines
from generate_features import generate_features
from build_outline import build_outline as build_outline_from_csv

def classify_lines(df, model_path, prediction_csv):
    print("🔍 Classifying lines...")
    model = load(model_path)

    feature_cols = [
        'char_len', 'word_count', 'is_all_caps',
        'is_title_case', 'has_number_prefix', 'relative_fontSize'
    ]

    # If not already generated, generate features again
    df = generate_features(df)
    df['predicted_label'] = model.predict(df[feature_cols])
    df.to_csv(prediction_csv, index=False)
    print(f"✅ Predictions saved to {prediction_csv}")
    return df

def main():
    parser = argparse.ArgumentParser(description="Run PDF outline extraction pipeline.")
    parser.add_argument("--pdf", required=True, help="PDF file name inside input/ folder (e.g., file02.pdf)")
    args = parser.parse_args()

    pdf_name = args.pdf
    pdf_path = os.path.join("input", pdf_name)

    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        exit(1)

    filename_stem = os.path.splitext(pdf_name)[0]

    # Define dynamic file paths
    extracted_csv = f"dataset/extracted_lines.csv"
    processed_csv = f"dataset/processed_lines.csv"
    prediction_csv = f"dataset/headings_with_predictions.csv"
    outline_json = f"output/final_outline_{filename_stem}.json"

    # Step 1: Extract text lines
    df = extract_lines(pdf_path)
    df.to_csv(extracted_csv, index=False)
    print(f"✅ Lines extracted and saved to: {extracted_csv}")

    # Step 2: Generate features
    df = generate_features(df)
    df.to_csv(processed_csv, index=False)
    print(f"✅ Features generated and saved to: {processed_csv}")

    # Step 3: Classify
    classify_lines(df, "models/heading_classifier.joblib", prediction_csv)

    # Step 4: Build outline JSON
    build_outline_from_csv(prediction_csv, outline_json)

    print(f"🎉 DONE! Final outline: {outline_json}")

if __name__ == "__main__":
    main()
