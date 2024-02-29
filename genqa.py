import os
import docx
import numpy as np
import pandas as pd
import streamlit as st
from io import StringIO
from docx import Document
from gemini import model
# from llama2 import generate_response



llm = {'gp':'Gemini Pro'}

# Get selected model
# def get_model():
#     return llm_model

# Extract text from uploaded docx
def get_text(file):
    doc = docx.Document(file)
    fullText = []
    for p in doc.paragraphs:
        fullText.append(p.text)
    return ' '.join(fullText)

# Get response from Gemini Pro
def get_response(content, prompt):
    prompt_parts = [
        content,
        "Input:" + prompt,
        "Output:"
    ]
    response = model.generate_content(prompt_parts)
    if 'does not' in response.text:
        prompt_parts[0] = ''
        response = model.generate_content(prompt_parts)
    return response

def gen_template(content, type):
    ans = []
    if type == 'agreement':
        keys = ['Owner','Tenant','Property Location','Term of Lease','Rent']
        questions = [
            'Who is the landlord or property owner or landlord agent (name only)',
            'Who is the tenant (name only)',
            'Address of property',
            'Agreement start date to end date',
            'Amount of monthly rent with currency used'
        ]
        for i in questions:
            res = get_response(content, i)
            if 'does not' in res.text:
                ans.append('-')
            else:
                ans.append(res.text)
    result = dict(zip(keys,ans))
    return result
        
def reset_state():
    st.session_state.messages = []
    st.session_state["file_uploader_key"] += 1
    st.rerun()


def main():
    # Framework
    st.set_page_config(page_title='🦖DynoGenQA')

    content = []
    prompt_parts = []
    template = ''
    type='agreement'
    
    if "file_uploader_key" not in st.session_state:
            st.session_state["file_uploader_key"] = 0

    with st.sidebar:
        st.title('🦖DynoGenQA')
        llm_model = st.selectbox(
                                "LLM Model",
                                llm.values(),
        )

    # Upload file
        uploaded_file = st.file_uploader("Upload a file", key=st.session_state["file_uploader_key"], type=['docx','txt'])
        if uploaded_file is not None:
            st.session_state["uploaded_files"] = uploaded_file
            content = get_text(uploaded_file)
            
    # Generate template
        gen_button_enabled = bool(uploaded_file)
        gen_template_button = st.button('Generate Template', key='gen2`erate_button', disabled=not gen_button_enabled)
        if gen_template_button:
            template = gen_template(content, type)
            # print(template)
        
    # Reset messages & files
        if st.sidebar.button('Reset All'):
            reset_state()

    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    messages = st.session_state["messages"]
    
    # Display messages in session
    for item in messages:
        role, parts = item.values()
        if role == "user":
            st.chat_message("user").markdown(parts[0])
        elif role == "assistant":
            if isinstance(parts[0], pd.DataFrame):
                with st.chat_message("assistant"):
                    st.markdown('Dynamic Template')
                    st.dataframe(parts[0],use_container_width=True)
            else:
                st.chat_message("assistant").markdown(parts[0])

    # Prompt user input 
    if template:
        with st.chat_message('assistant'):
                display_template = pd.DataFrame.from_dict(template, orient='index', columns=['Value'])
                display_template.index.name = 'Field'
                # st.table(display_template)
                st.write('Dynamic Template')
                st.dataframe(display_template,use_container_width=True)
                messages.append(
                    {"role": "assistant", "parts":  [display_template]},
                )
                
    prompt = st.chat_input('Say something')
    if prompt:
        with st.chat_message('user'):
            st.write(prompt)
        messages.append(
                {"role": "user", "parts":  [prompt]},
        )
        
    # generate output
        output = get_response(content, prompt)
        with st.chat_message('assistant'):
            res = output.text
            st.markdown(res)
            messages.append(
                {"role": "assistant", "parts":  [res]},
            )
        
if __name__ == '__main__':
    main()   



