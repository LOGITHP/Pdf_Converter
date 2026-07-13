import sys
import os

# Add root folder to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.converters.notebooks.notebook_converter import NotebookConverter

def main():
    converter = NotebookConverter()
    input_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.ipynb")
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output.pdf")
    
    print("Converting notebook...")
    success = converter.convert(input_path, output_path)
    print(f"Conversion success: {success}")
    if success and os.path.exists(output_path):
        print(f"Output PDF size: {os.path.getsize(output_path)} bytes")

if __name__ == "__main__":
    main()
