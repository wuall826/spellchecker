import re
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from docx import Document
import openpyxl

app = Flask(__name__)

def read_file(file_path):
    """
    Function reads a file from the provided file path.
    It can read .txt, .docx, and .xlsx files.
    Returns a string containing the file's contents.
    """
    if file_path.endswith('.txt'):
        with open(file_path, 'r') as file:
            data = file.read()
    elif file_path.endswith('.docx'):
        doc = Document(file_path)
        data = ' '.join([para.text for para in doc.paragraphs])
    elif file_path.endswith('.xlsx'):
        wb_obj = openpyxl.load_workbook(file_path)
        sheet_obj = wb_obj.active
        data = ' '.join([cell_obj.value for cell_obj in sheet_obj['A']])
    else:
        print(f'Unsupported file format: {file_path}')
        data = ''
    
    return data

def spell_checker(input_file, dict_file):
    """
    Function for spell checker
    Receives two parameters: input_file and dict_file. 
    Returns a list of words from input_file that are not found in dict_file.
    """
    
    # Read the dictionary file and create a set of words
    dictionary_data = read_file(dict_file).lower()
    dictionary_words = set(re.findall(r'\b\w+\b', dictionary_data))
    
    # Read the input file and create a list of words
    input_data = read_file(input_file).lower()
    input_words = re.findall(r'\b\w+\b', input_data)
    
    # Find the words in input_words that are not in dictionary_words
    misspelled_words = [word for word in input_words if word not in dictionary_words]
    
    return misspelled_words

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    misspelled_words = []
    if request.method == 'POST':
        text_file = request.files['text']
        dict_file = request.files['dictionary']
        
        # Ensure the filename is secure
        text_filename = secure_filename(text_file.filename)
        dict_filename = secure_filename(dict_file.filename)
        
        # Save the files temporarily
        text_file.save(text_filename)
        dict_file.save(dict_filename)
        
        # Run the spell checker
        misspelled_words = spell_checker(text_filename, dict_filename)
        
    return render_template('index.html', misspelled_words=misspelled_words)

if __name__ == '__main__':
    app.run(debug=True)
