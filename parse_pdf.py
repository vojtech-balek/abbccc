import PyPDF2
import re
import os

from docx import Document

def get_text_from_docx(filepath):
    """
    Extracts text from a DOCX file while attempting to preserve table structures.
    Returns text with table content grouped by rows and columns.
    """
    def process_table_row(row):
        """Helper function to format table rows into a string."""
        cells = [cell.text.strip() for cell in row.cells]
        return ' | '.join(cells)  # Join cells with ' | '

    full_text = []

    try:
        # Load the DOCX file
        doc = Document(filepath)

        for element in doc.element.body:
            # Handle paragraphs
            if element.tag.endswith('p'):
                paragraph = element.text.strip()
                if paragraph:  # Only add non-empty paragraphs
                    full_text.append(paragraph)

            # Handle tables
            elif element.tag.endswith('tbl'):
                table = element
                table_text = []
                for row in table.rows:
                    row_text = process_table_row(row)
                    table_text.append(row_text)
                if table_text:  # Only add non-empty tables
                    full_text.append('\n'.join(table_text))
                    full_text.append('-' * 40)  # Table separator

        return '\n'.join(full_text)

    except FileNotFoundError:
        return f"Error: The file '{filepath}' was not found."
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

def get_text_from_pdf(filepath):
    """
    Extracts text from a PDF file while attempting to preserve table structures.
    Returns text with table content grouped by rows and columns.
    """
    def process_table_line(line):
        """Helper function to identify and format potential table rows"""
        # Split by multiple spaces (common in PDF tables)
        cells = re.split(r'\s{2,}', line.strip())
        if len(cells) > 1:  # Likely a table row
            return ' | '.join(cells)
        return line

    def is_likely_header(line):
        """Check if a line might be a table header"""
        # Headers often have certain characteristics
        if re.search(r'^[A-Z][a-zA-Z\s]*$', line.strip()):
            return True
        if len(re.split(r'\s{2,}', line.strip())) > 1:
            return all(cell[0].isupper() for cell in re.split(r'\s{2,}', line.strip()) if cell)
        return False

    with open(filepath, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        full_text = []

        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            raw_text = page.extract_text()

            # Split into lines while preserving empty lines
            lines = raw_text.splitlines()

            # Process the lines
            current_table = []
            processed_lines = []

            for i, line in enumerate(lines):
                if not line.strip():  # Empty line
                    if current_table:
                        # Join table rows with newlines and add separator
                        processed_lines.append('\n'.join(current_table))
                        processed_lines.append('-' * 40)  # Table separator
                        current_table = []
                    processed_lines.append('')
                    continue

                # Check if line might be part of a table
                if is_likely_header(line) or len(re.split(r'\s{2,}', line.strip())) > 1:
                    processed_line = process_table_line(line)
                    current_table.append(processed_line)
                else:
                    if current_table:
                        # End current table if we hit non-table content
                        processed_lines.append('\n'.join(current_table))
                        processed_lines.append('-' * 40)  # Table separator
                        current_table = []
                    processed_lines.append(line)

            # Handle any remaining table content
            if current_table:
                processed_lines.append('\n'.join(current_table))
                processed_lines.append('-' * 40)

            # Add page break indicator
            full_text.extend(processed_lines)
            full_text.append('\n=== Page Break ===\n')

        return '\n'.join(full_text)


def yield_pdfs_paths(directory):
    # Traverse through the directory
    for root, dirs, files in os.walk(directory):
        # Loop through the files in each directory
        for file in files:
            # Check if the file has a .pdf extension
            if file.lower().endswith(".pdf") or file.lower().endswith(".pdf"):
                # Yield the full path to the PDF file and normalize to Windows format
                yield os.path.normpath(os.path.join(root, file)), file

# print(get_text_from_pdf("04 - Data Transformer/Data/Hitachi/QT-22-Hitachi13_Rev1_EN_H4A.pdf"))

# import tiktoken
#
# # Load encoding for the model you're using
# encoding = tiktoken.get_encoding("cl100k_base")  # Adjust according to the model
#
# # Define max input tokens
# MAX_INPUT_TOKENS = 6000  # Set your limit for the input
#
# # Simulating parsed text from PDF
# parsed_text = get_text_from_pdf('04 - Data Transformer/Examples/RDOSea3A.pdf')
#
# # Tokenize the parsed text
# input_tokens = encoding.encode(parsed_text)
#
# print(len(input_tokens))
# print(len(parsed_text))
#
# # Check if the input exceeds the max token limit
# if len(input_tokens) > MAX_INPUT_TOKENS:
#     # Truncate the text to the maximum allowed tokens
#     input_tokens = input_tokens[:MAX_INPUT_TOKENS]
#     # Decode back to text
#     truncated_text = encoding.decode(input_tokens)
# else:
#     truncated_text = parsed_text
#
# print(len(truncated_text))