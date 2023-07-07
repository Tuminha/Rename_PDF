# app.py
import streamlit as st
import os
import shutil
import tempfile
from zipfile import ZipFile
import re
import fitz
import base64



def rename_pdfs(files):
    renamed_count = 0
    same_name_count = 0
    temp_dir = tempfile.mkdtemp()

    for uploaded_file in files:
        try:
            # Save uploaded file to a temporary file
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_file_path, 'wb') as temp_file:
                temp_file.write(uploaded_file.getbuffer())

            # Now you can open the file with fitz
            doc = fitz.open(temp_file_path)
            
            # Extract the title
            title = doc.metadata["title"]
            if title:  # If title is not empty
                title = re.sub('[^A-Za-z0-9]+', '_', title)
                title = re.sub('_$', '', title)
                renamed_count += 1
            else:  # If title is empty, use the original filename
                title, _ = os.path.splitext(uploaded_file.name)
                title = re.sub('[^A-Za-z0-9]+', '_', title)
                same_name_count += 1
            
            new_filename = f"{title}.pdf"
            new_file_path = os.path.join(temp_dir, new_filename)
            
            # Ensure not to overwrite a different document with the same title
            if not os.path.isfile(new_file_path):
                with open(new_file_path, 'wb') as out_file:
                    with open(temp_file_path, 'rb') as read_file:
                        out_file.write(read_file.read())
        
        except Exception as e:
            st.write(f"Error processing file {uploaded_file.name}: {str(e)}")
    
    return temp_dir, renamed_count, same_name_count


st.title("PDF Renamer")

uploaded_files = st.file_uploader("Upload PDF Files", type=['pdf'], accept_multiple_files=True)

if st.button('Rename PDFs'):
    if uploaded_files:
        # Add a spinner while the app is renaming the pdfs so user sees the progress
        with st.spinner('Renaming PDFs...'):
            output_dir, renamed_count, same_name_count = rename_pdfs(uploaded_files)

        

        
        # Package all files in a zip
        zip_file_path = shutil.make_archive(output_dir, 'zip', output_dir)
        with open(zip_file_path, 'rb') as f:
            bytes = f.read()
            b64 = base64.b64encode(bytes).decode()
            href = f'<a href="data:file/zip;base64,{b64}" download="renamed_pdfs.zip">Download Renamed PDFs</a>'
            st.markdown(href, unsafe_allow_html=True)
        
        st.write(f"{renamed_count} 🎉 PDFs were renamed.")
        st.write(f"{same_name_count} 🤨 PDFs remained the same.")
    else:
        st.write("No PDF files uploaded.")
