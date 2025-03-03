import os
import json
import fitz  # PyMuPDF
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID, NUMERIC
from whoosh.qparser import QueryParser

def create_searchable_index(txt_path, pdf_path):
    # Create schema for the search index
    schema = Schema(
        content=TEXT(stored=True),
        page_number=NUMERIC(stored=True),
        pdf_path=ID(stored=True)
    )
    
    # Create index directory if it doesn't exist
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")
    
    # Create index
    ix = create_in("indexdir", schema)
    writer = ix.writer()
    
    # Read the text file and index content by page
    with open(txt_path, 'r', encoding='utf-8') as f:
        current_page = None
        current_content = []
        
        for line in f:
            if line.startswith('Page '):
                # If we have content from previous page, index it
                if current_page is not None and current_content:
                    writer.add_document(
                        content='\n'.join(current_content),
                        page_number=current_page,
                        pdf_path=pdf_path
                    )
                # Start new page
                current_page = int(line.split()[1])
                current_content = []
            else:
                current_content.append(line.strip())
    
    # Add the last page
    if current_page is not None and current_content:
        writer.add_document(
            content='\n'.join(current_content),
            page_number=current_page,
            pdf_path=pdf_path
        )
    
    writer.commit()
    return ix

def search_and_show_pdf(query_text, index):
    with index.searcher() as searcher:
        query = QueryParser("content", index.schema).parse(query_text)
        results = searcher.search(query, limit=10)
        
        if not results:
            print(f"No results found for '{query_text}'")
            return
        
        # Open PDF document
        pdf_path = results[0]['pdf_path']
        doc = fitz.open(pdf_path)
        
        for hit in results:
            page_num = hit['page_number']
            print(f"\nFound in page {page_num}:")
            print(f"Context: {hit.highlights('content')}\n")
            
            # Get the page and highlight the text
            page = doc.load_page(page_num - 1)
            text_instances = page.search_for(query_text)
            for inst in text_instances:
                highlight = page.add_highlight_annot(inst)
                highlight.set_colors(stroke=(1, 1, 0))  # Yellow highlight
                highlight.update()
        
        # Save the highlighted PDF with a temporary name
        temp_pdf = "search_result_temp.pdf"
        doc.save(temp_pdf)
        print(f"\nHighlighted PDF saved as: {temp_pdf}")
        # Save the highlighted PDF
        doc.save("search_result.pdf")

if __name__ == "__main__":
    txt_path = "c:\\Dev\\Whoosh\\pdf\\exemplo.txt"
    pdf_path = "c:\\Dev\\Whoosh\\pdf\\exemplo.pdf"
    
    # Create search index
    index = create_searchable_index(txt_path, pdf_path)
    
    # Example search
    search_term = input("Enter search term: ")
    search_and_show_pdf(search_term, index)