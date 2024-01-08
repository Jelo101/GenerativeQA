import os
import docx
import numpy as np
import pandas as pd
import streamlit as st
from io import StringIO
# from dotenv import load_dotenv
from docx import Document
from gemini import model

# load_dotenv()

# Extract text from uploaded docx
def getText(file):
    doc = docx.Document(file)
    fullText = []
    for p in doc.paragraphs:
        fullText.append(p.text)
    return ' '.join(fullText)




# Framework
st.set_page_config(page_title='🦖DynoGenQA')
st.title('🦖DynoGenQA')

# if 'messages' not in st.session_state:
#     st.session_state.messages = []

# for message in st.session_state.messages:
#     with st.chat_message(message['role']):
#         st.markdown(message['content'])

# if prompt := st.chat_input('What is up?'):
#     with st.chat_message('user'):
#         st.markdown(prompt)
#     st.session_state.messages.append({'role':'user', 'content':prompt})
prompt_parts = []

def get_response(prompt_parts):
    response = model.generate_content(prompt_parts)
    return response

prompt = st.chat_input('Say something')

with st.chat_message('user'):
    st.write('Hello 👋 Please upload a text document')

    uploaded_file = st.file_uploader("Choose a file", type=['docx','txt'])
    if uploaded_file is not None:
        content = getText(uploaded_file)
    
    if prompt:
        st.write(prompt)
        prompt_parts = [
            content,
            "Input:"+prompt,
            "Output:"
        ]
        output = get_response(prompt_parts)
        st.write(output.text)
    
    



