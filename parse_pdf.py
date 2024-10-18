import PyPDF2


def get_text_from_pdf(filepath):
    """
    Extracts text from a PDF file while attempting to preserve table structures.
    Returns text with table content grouped by rows and columns.
    """
    import PyPDF2
    import re

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


