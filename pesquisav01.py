import os
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from pdf2image import convert_from_path
import pytesseract

# Configurar Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Caminho para o Tesseract no Windows
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

# Configurar Poppler
os.environ['PATH'] += r';C:\poppler-24.08.0\Library\bin'  # Caminho para o Poppler no Windows

# 1. Extrair texto de um PDF usando OCR
def extract_text_from_pdf(pdf_path):
    # Converte o PDF em uma lista de imagens (uma por página)
    pages = convert_from_path(pdf_path, dpi=300)
    
    # Extrai o texto de cada página usando Tesseract
    full_text = ""
    for i, page in enumerate(pages):
        text = pytesseract.image_to_string(page, lang='eng')  # 'por' para português
        full_text += f"Página {i+1}:\n{text}\n\n"
    
    return full_text

# 2. Criar índice no Whoosh
def create_index(index_dir):
    # Define o esquema do índice
    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
    
    # Cria o diretório do índice, se não existir
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
    
    # Cria o índice
    return create_in(index_dir, schema)

# 3. Indexar o conteúdo do PDF
def index_pdf_content(index, pdf_path, title):
    # Extrai o texto do PDF
    content = extract_text_from_pdf(pdf_path)
    
    # Adiciona o conteúdo ao índice
    writer = index.writer()
    writer.add_document(title=title, path=pdf_path, content=content)
    writer.commit()

# 4. Realizar uma busca no índice
def search_in_index(index, query_text):
    with index.searcher() as searcher:
        query = QueryParser("content", index.schema).parse(query_text)
        results = searcher.search(query, limit=10)
        
        # Create a text file with search results
        with open('search_results.txt', 'w', encoding='utf-8') as f:
            f.write(f"Search Results for: {query_text}\n")
            f.write("-" * 50 + "\n\n")
            
            for hit in results:
                f.write(f"Title: {hit['title']}\n")
                f.write(f"Path: {hit['path']}\n")
                f.write(f"Relevant excerpt: {hit.highlights('content')}\n")
                f.write("-" * 50 + "\n\n")
                
                # Also print to console
                print(f"Título: {hit['title']}")
                print(f"Caminho: {hit['path']}")
                print(f"Trecho relevante: {hit.highlights('content')}\n")

# Exemplo de uso
if __name__ == "__main__":
    # Caminho do PDF
    pdf_path = "exemplo.pdf"
    
    # Diretório para armazenar o índice
    index_dir = "indexdir"
    
    # Cria o índice
    index = create_index(index_dir)
    
    # Indexa o conteúdo do PDF
    index_pdf_content(index, pdf_path, "Documento de Exemplo")
    
    # Realiza uma busca
    search_query = "texto que você quer buscar"
    print(f"Resultados para '{search_query}':")
    search_in_index(index, search_query)