from collections import Counter
from joblib import dump
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Load dataset
df = pd.read_csv("dataset/processed_lines.csv", encoding='utf-8-sig')
df.columns = df.columns.str.strip()

feature_cols = [
    'char_len', 'word_count',
    'is_all_caps', 'is_title_case',
    'has_number_prefix', 'relative_fontSize'
]

X = df[feature_cols]
y = df['label']

# Handle rare classes
label_counts = Counter(y)
rare_labels = [label for label, count in label_counts.items() if count < 2]

if rare_labels:
    print("⚠️ Rare classes found (using all — no stratify):")
    for label in rare_labels:
        print(f"   • {label}: {label_counts[label]} sample(s)")
    stratify_arg = None
else:
    stratify_arg = y

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=stratify_arg, random_state=42
)

# Use class balancing
clf = LogisticRegression(max_iter=2000, class_weight='balanced')
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

# Report
print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred))

# Save model
dump(clf, "models/heading_classifier.joblib")
print("✅ Model trained and saved!")
