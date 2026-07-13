import fitz

doc = fitz.open("scratch/test_output.pdf")
print(f"Page count: {len(doc)}")
for i, page in enumerate(doc):
    print(f"--- Page {i+1} ---")
    print(page.get_text())
