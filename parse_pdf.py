import PyPDF2


def get_text_from_pdf(filepath):
    with open(filepath, 'rb') as file:

        reader = PyPDF2.PdfReader(file)
        text = ''
        # Extract text from all pages
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()

        return text

    # The variable 'text' now contains all the text extracted from the PDF.
    print(text)
