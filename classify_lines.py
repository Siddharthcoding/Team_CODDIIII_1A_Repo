import pandas as pd
from joblib import load
from generate_features import generate_features

model = load("models/heading_classifier.joblib")

# Load new PDF + preprocess
df = pd.read_csv("dataset/processed_lines.csv")
df = generate_features(df)

features = df[['char_len', 'word_count', 'is_all_caps', 'is_title_case', 'has_number_prefix', 'relative_fontSize']]
df['predicted_label'] = model.predict(features)

df.to_csv("dataset/headings_with_predictions.csv", index=False)
print(df[df['predicted_label'] != "body"].head())
