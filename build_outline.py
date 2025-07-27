import pandas as pd
import json

def build_outline(input_csv, output_json):
    df = pd.read_csv(input_csv)
    headings = df[df['predicted_label'] != "body"]

    def get_level(label):
        return {
            "title": 0, "h1": 1, "h2": 2, "h3": 3
        }.get(label.lower(), 10)

    outline = []
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

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"✅ Outline written to: {output_json}")

if __name__ == "__main__":
    build_outline("dataset/headings_with_predictions.csv", "output/final_outline.json")
