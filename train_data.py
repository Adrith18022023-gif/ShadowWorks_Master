import json

training_examples = [
    {
        "input": "Write a loop in Python",
        "output": "for i in range(10):\n    print(i)"
    },
    {
        "input": "Debug this C code: int main() { printf('hi') }",
        "output": "Error: Missing semicolon.\nFix:\nint main() {\n    printf('hi');\n    return 0;\n}"
    },
    {
        "input": "Cinematic mode: Love and code",
        "output": "SHAYARI: Code ki tarah uljhi hai meri zindagi..."
    }
]

with open("tuned_model_data.jsonl", "w") as f:
    for item in training_examples:
        json_string = json.dumps(item)
        f.write(json_string + "\n")

print("Fine-tuning dataset generated successfully.")