import pandas as pd
import re
import json

df = pd.read_csv("dataset/headings_with_predictions.csv")
headings = df[df['predicted_label'] != "body"]

outline = []

def get_level(label):
    return {
        "title": 0,
        "h1": 1,
        "h2": 2,
        "h3": 3
    }.get(label, 10)

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

with open("output/final_outline.json", "w") as f:
    json.dump(output, f, indent=2)

print("✅ Outline constructed in output/final_outline.json")
