import base64
import hashlib
import os

from typing import List, Union
from streamlit_pdf_viewer import pdf_viewer
from langchain_community.document_loaders import ArxivLoader
from langchain_community.retrievers import ArxivRetriever
from pydantic import BaseModel
from unstructured.partition.pdf import partition_pdf

import arxiv
import streamlit as st
import unstructured

def new_file():
    st.session_state['doc_id'] = None
    st.session_state['uploaded'] = True
    st.session_state['annotations'] = None
    

def download_pdf(arxiv_id: str) -> str:
    paper = next(arxiv.Client().results(arxiv.Search(id_list=[arxiv_id])))
    # Download the archive to the PWD with a default filename.
    return paper.download_pdf(dirpath="./", filename=f"{arxiv_id}.pdf")


def render_pdf(document):
    return pdf_viewer(input=document, key="jj", rendering="unwrap") #, pages_to_render=[1])

def pdf_as_base64(input: Union[str, bytes]) -> bytes:
    if type(input) is not bytes:
        with open(input, 'rb') as fo:
            binary = fo.read()
    else:
        binary = input

    return  base64.b64encode(binary)

def hash_bytes(input: bytes) -> str:
    result = hashlib.sha256(input)
    return result.hexdigest()

class ProtoSection(BaseModel):
    id: str = ""
    chunks: List[str] = []
    
    def __len__(self):
        return len(self.chunks)

    
def section_extractor(elements):
    sections = []
    current_section = ProtoSection()

    for element in elements:
        if isinstance(element, unstructured.documents.elements.Title):
            st.write(f"Title: {element.text}")
            if len(current_section) == 0:
                current_section.id = element.text
                sections.append(current_section)
                current_section = ProtoSection()
            else:  # len(current_section) > 0
                sections.append(current_section)
                current_section = ProtoSection(id=element.text)
        elif isinstance(element, unstructured.documents.elements.Text):
            current_section.chunks.append(element.text)
    
    sections.append(current_section)
    return sections

        
# def section_extractor(elements):
#     sections = []
#     current_section = []

#     for element in elements:
#         if isinstance(element, unstructured.documents.elements.Title):
#             if len(current_section) > 0:
#                 sections.append("\n".join(current_section))
#                 current_section = []
#         if isinstance(element, unstructured.documents.elements.Text):
#             current_section.append(element.text)
    
#     if current_section:
#         sections.append("\n".join(current_section))
    
#     return sections


def main():
    st.sidebar.title("Configuration")
    api_option = st.sidebar.selectbox("Options", ["Llama2", "OpenAI", "Anthropic"])
    api_key = st.sidebar.text_input("API Key")

    st.title(f"PaperQ using {api_option}")
    arxiv_doc_id = st.selectbox("ArXiv Document ID", [None, "00_test", "2308.0470", "1605.08386", "2312.12148", "2008.02217"])
    
    st.text(os.getcwd())
    st.text(arxiv_doc_id)
    
    if arxiv_doc_id is not None:
        st.text(f"Loading document {arxiv_doc_id} from Arxiv")
        document = download_pdf(arxiv_doc_id)
    else:
        new_file()
        document_src = st.file_uploader("Document", type=("pdf"), on_change=new_file)
        document = os.path.join(os.getcwd(), document_src.name) 


    doc_hash = hash_bytes(pdf_as_base64(document))
    st.markdown(f"## Document: {os.path.basename(document)}")
    st.markdown(f"#### Hash: {doc_hash}")

    col1, col2 = st.columns(2)
    with col1:
        if st.checkbox("Show PDF Viewer"):
                render_pdf(document)
    with col2:
            # Your code for the second column goes here
        # Returns a List[Element] present in the pages of the parsed pdf document
        elements = partition_pdf(document) #, strategy="hi_res")
        st.write(elements)
        sections = section_extractor(elements)
        
        for i, section in enumerate(sections):
            st.markdown(f"## {section.id}")
            section_text = "\n".join(section.chunks)
            if len(section_text) > 0:
                st.text_area("Text", f"{section_text}", disabled=True, key=f"Section_{i}")
    
    # for element in elements:
    #     # st.write(element.metadata.subject)
    #     # st.write(f"Orig: {element.metadata.detection_origin}")
    #     # st.write(f"Cat depth: {element.metadata.category_depth}")
    #     # st.write(f"Emph: {element.metadata.emphasized_text_contents}")
    #     # st.write(f"Tags: {element.metadata.emphasized_text_tags}")
    #     if isinstance(element, unstructured.documents.elements.Text):
    #         st.write(element.category)
        
    
if __name__ == "__main__":
    main()
