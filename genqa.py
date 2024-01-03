import os
import pandas as pd
import streamlit as st
from io import StringIO
from dotenv import load_dotenv
from docx import Document
from gemini import model

load_dotenv()

st.title('DynoGenQA')

uploaded_file = st.file_uploader("Choose a file", type=['docx','txt'])
if uploaded_file is not None:
    doc = Document(uploaded_file)
    paragraphs = [paragraph.text for paragraph in doc.paragraphs]
    sentences = [sentence for paragraph in paragraphs for sentence in paragraph.split('. ') if sentence]