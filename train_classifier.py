import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from joblib import dump
from collections import Counter

# Load dataset
df = pd.read_csv("dataset/processed_lines.csv", encoding='utf-8-sig')
df.columns = df.columns.str.strip()

print("Labels:\n", df['label'].value_counts())

feature_cols = [
    'char_len', 'word_count',
    'is_all_caps', 'is_title_case',
    'has_number_prefix', 'relative_fontSize'
]

X = df[feature_cols]
y = df['label']

# Add label safety: handle low sample classes (like "title")
label_counts = Counter(y)
min_class_count = min(label_counts.values())

if min_class_count < 2:
    print(f"⚠️ Not using stratify — found class(es) with <2 samples:")
    for label, count in label_counts.items():
        if count < 2:
            print(f"    • '{label}': {count} sample(s)")
    stratify_arg = None
else:
    stratify_arg = y

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=stratify_arg, random_state=42
)

clf = LogisticRegression(max_iter=1000)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred))

# Save model
dump(clf, "models/heading_classifier.joblib")
print("✅ Model trained and saved!")
