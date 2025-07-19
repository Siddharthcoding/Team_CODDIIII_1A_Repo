import pandas as pd
import re

def is_all_caps(s): return str(s).isupper()
def is_title_case(s): return str(s).istitle()
def has_number_prefix(s): return bool(re.match(r"^\d+(\.\d+)*", str(s)))
def word_count(s): return len(str(s).split())

def generate_features(df):
    df['char_len'] = df['text'].apply(len)
    df['word_count'] = df['text'].apply(word_count)
    df['is_all_caps'] = df['text'].apply(is_all_caps).astype(int)
    df['is_title_case'] = df['text'].apply(is_title_case).astype(int)
    df['has_number_prefix'] = df['text'].apply(has_number_prefix).astype(int)
    df['avg_fontSize_by_page'] = df.groupby('page')['char_len'].transform('mean')  # Use char_len as font proxy
    df['relative_fontSize'] = df['char_len'] - df['avg_fontSize_by_page']
    return df

# Run
if __name__ == "__main__":
    # Use labled_lines for train and extracted_lines for validation
    df = pd.read_csv("dataset/extracted_lines.csv", encoding='utf-8-sig')  
    df = generate_features(df)
    df.to_csv("dataset/processed_lines.csv", index=False)
    print("✅ Features saved to dataset/processed_labeled_lines.csv")
