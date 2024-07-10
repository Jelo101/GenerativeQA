import os
import docx
import pandas as pd
import streamlit as st
from io import StringIO
from docx import Document
from gemini import model

llm = {'gp': 'Gemini 1.5 Flash'}

def get_text(file):
    file_name = file.name
    file_ext = os.path.splitext(file_name)[1].lower()

    if file_ext == '.txt':
        fullText = file.getvalue().decode("utf-8").replace('\n', ' ')
        return fullText
    elif file_ext == '.docx':
        doc = Document(file)
        fullText = []
        for p in doc.paragraphs:
            fullText.append(p.text)
        return ' '.join(fullText)
    else:
        raise ValueError("Unsupported file format. Supported formats are .txt and .docx")

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

def categorize_docs(content):
    prompt = """
    Read the following document content:
    """+ content +"""
    Which document type best describes this document? Choose one from the following:
    
    Tenancy Agreement
    News Article
    
    Return the name of the document type only
    """
    type = get_response(content, prompt).text.strip()
    print(type)
    return type

def categorize_agreement(content):
    template = """
    Summarize the following tenancy agreement into a table with 5 columns. Do not bold the results. 
        The table should have 5 columns: "Owner", "Tenant", "Tenancy Period", "Property Address", "Monthly Rent Amount".
        Each summary should be short and concise. Do not make any assumptions, generate answer based on the context.
        Tenancy Agreement: """ + content + """
        Summary Template:
    """
    return template

def categorize_news(content):
    prompt = """
    Read the following news article:

    """ + content + """

    Which category best describes this news article? Choose one from the following:

    World: International events, global affairs, foreign policy
    National: News and events within a specific country
    Business: Financial markets, companies, economic trends
    Technology: Innovations, software, hardware, internet trends
    Sports: Major sporting events, individual athletes, team news
    Politics: Government actions, elections, political figures
    Culture: Arts, entertainment, music, movies, books
    
    Return the category name only
    """

    category = get_response(content, prompt).text.strip()
    print(category)

    if category == 'World':
        template = """
        Summarize the following news into a table with 5 columns. Do not bold the results. 
        The table should have 5 columns: "Main Idea", "Date and Location", "Key Events", "Global Reactions", "Diplomatic Actions".
        Each summary should be short and concise. Do not make any assumptions, generate answer based on the context.
        News Article: """ + content + """
        Summary Template:
        """
    elif category == 'National':
        template = """
        Summarize the following news into a table with 5 columns. Do not bold the results. 
        The table should have 5 columns: "Main Idea", "Date and Location", "Government Response", "Public Reaction", "National Impact".
        Each summary should be short and concise. Do not make any assumptions, generate answer based on the context.
        News Article: """ + content + """
        Summary Template:
        """
    elif category == 'Business':
        template = """
        Summarize the following news into a table with 5 columns. Do not bold the results. 
        The table should have 5 columns: "Main Idea", "Date and Financial Impact", "Key Companies", "Market Trends", "Economic Impact".
        Each summary should be short and concise. Do not make any assumptions, generate answer based on the context.
        News Article: """ + content + """
        Summary Template:
        """
    elif category == 'Technology':
        template = """
        Summarize the following news into a table with 5 columns. Do not bold the results. 
        The table should have 5 columns: "Main Idea", "Date and Location", "Innovation Details", "Tech Companies Involved", "Technology Impact".
        Each summary should be short and concise. Do not make any assumptions, generate answer based on the context.
        News Article: """ + content + """
        Summary Template:
        """
    elif category == 'Sports':
        template = """
        Summarize the following news into a table with 5 columns. Do not bold the results. 
        The table should have 5 columns: "Main Idea", "Date and Venue", "Teams or Players", "Game Statistics", "Sporting Impact".
        Each summary should be short and concise. Do not make any assumptions, generate answer based on the context.
        News Article: """ + content + """
        Summary Template:
        """
    elif category == 'Politics':
        template = """
        Summarize the following news into a table with 5 columns. Do not bold the results. 
        The table should have 5 columns: "Main Idea", "Date and Location", "Political Figures", "Political Impact", "Public Opinion".
        Each summary should be short and concise. Do not make any assumptions, generate answer based on the context.
        News Article: """ + content + """
        Summary Template:
        """
    elif category == 'Culture':
        template = """
        Summarize the following news into a table with 5 columns. Do not bold the results. 
        The table should have  5 columns: "Main Idea", "Date and Venue", "Participants", "Cultural Significance", "Impact on Society".
        Each summary should be short and concise. Do not make any assumptions, generate answer based on the context.
        News Article: """ + content + """
        Summary Template:
        """
    else:
        raise ValueError("Unsupported category returned by model.")

    return template

def parse_generated_text(text):
    # Split the text into lines
    lines = text.strip().split('\n')

    # Extract the header and values
    header_line = lines[0]
    value_line = lines[2]

    # Remove leading and trailing pipe characters and split by pipe
    headers = [header.strip() for header in header_line.strip('|').split('|')]
    values = [value.strip() for value in value_line.strip('|').split('|')]

    # Create a DataFrame
    df = pd.DataFrame([values], columns=headers)
    print(df)
    return df

def gen_template(content, type):
    if type == 'News Article':
        template = categorize_news(content)
    else:
        template = categorize_agreement(content)
    response = get_response(content, template)
    output_text = response.text.strip()

    print("Model Response:", output_text)  # Log the response

    try:
        df = parse_generated_text(output_text)
        return df
    except Exception as e:
        print(f"Error parsing response: {e}")
        st.error(f"Error parsing response: {e}")
        return pd.DataFrame(columns=["Header", "Value"])

def reset_state():
    st.session_state.messages = []
    st.session_state["file_uploader_key"] += 1
    st.rerun()

def main():
    st.set_page_config(page_title='🦖DynoGenQA')

    content = ""
    template = pd.DataFrame()

    if "file_uploader_key" not in st.session_state:
        st.session_state["file_uploader_key"] = 0

    with st.sidebar:
        st.title('🦖DynoGenQA')
        llm_model = st.selectbox("LLM Model", llm.values())

        uploaded_file = st.file_uploader("Upload a file", key=st.session_state["file_uploader_key"], type=['docx', 'txt'])
        if uploaded_file is not None:
            content = ''
            st.session_state["uploaded_files"] = uploaded_file
            content = get_text(uploaded_file)
            
        gen_button_enabled = bool(uploaded_file)
        gen_template_button = st.button('Generate Template', key='generate_button', disabled=not gen_button_enabled)
        if gen_template_button:
            type = categorize_docs(content)
            template = gen_template(content, type)
        
        if st.sidebar.button('Reset All'):
            reset_state()
            content, prompt, template = ''

    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    messages = st.session_state["messages"]

    for item in messages:
        role, parts = item.values()
        if role == "user":
            st.chat_message("user").markdown(parts[0])
        elif role == "assistant":
            if isinstance(parts[0], pd.DataFrame):
                with st.chat_message("assistant"):
                    st.markdown('Dynamic Template')
                    st.dataframe(parts[0], use_container_width=True)
            else:
                st.chat_message("assistant").markdown(parts[0])

    if not template.empty:
        transposed_template = template.transpose().reset_index()  # Transpose the DataFrame and reset index
        transposed_template.columns = ['Original Index'] + list(transposed_template.columns[1:])  # Rename columns
        transposed_template.columns = transposed_template.columns.astype(str)
        with st.chat_message('assistant'):
            st.dataframe(transposed_template, use_container_width=True)
            messages.append({"role": "assistant", "parts": [transposed_template]})

    prompt = st.chat_input('Say something')
    if prompt:
        with st.chat_message('user'):
            st.write(prompt)
        messages.append({"role": "user", "parts": [prompt]})
        
        output = get_response('Context:'+content+'.Generate answer based on the document content', prompt)
        with st.chat_message('assistant'):
            res = output.text
            st.markdown(res)
            messages.append({"role": "assistant", "parts": [res]})

if __name__ == '__main__':
    main()
