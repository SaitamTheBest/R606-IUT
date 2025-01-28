from typing import List
import logging
import os
from langchain_community.document_loaders import (
    PDFPlumberLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import gc

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=80,
            length_function=len,
            is_separator_regex=False
        )

    def process_file(self, file, file_type: str) -> str:
        """Process different file types and split into chunks."""
        temp_path = None
        try:
            # Create a temporary directory
            temp_dir = os.path.join(os.getcwd(), 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Use a temporary file path
            temp_path = os.path.join(temp_dir, f"temp_{file.name}")
            
            # Write the file to the temporary path
            with open(temp_path, 'wb') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            # Extract text from different file types
            if file_type == 'pdf':
                loader = PDFPlumberLoader(temp_path)
                docs = loader.load_and_split()
                text = '\n'.join([doc.page_content for doc in docs])
            elif file_type in ['txt', 'md']:
                with open(temp_path, 'r', encoding='utf-8') as text_file:
                    text = text_file.read()
            
            # Normalize text
            text = ' '.join(text.split())
            
            # Split text into sentences
            sentences = text.replace('? ', '?<split>').replace('! ', '!<split>').replace('. ', '.<split>').split('<split>')
            
            # Split text into chunks
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 1 < 1000:
                    current_chunk += (sentence + " ").strip()
                else:
                    chunks.append(current_chunk)
                    current_chunk = sentence + " "
            
            if current_chunk:
                chunks.append(current_chunk)
            
            # Join chunks with newlines
            return "\n\n".join(chunks)

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            raise
        
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception as ex:
                    logger.error(f"Error when removing file: {str(ex)}")
                    raise
            gc.collect()
 
    def store_document(self, content: str, metadata: dict) -> List[Document]:
        """Split content and prepare documents for vector store."""
        try:
            # Split content into chunks
            texts = self.text_splitter.split_text(content)
            logger.info(f"Split document into {len(texts)} chunks")
            
            # Prepare documents
            documents = []
            for i, text in enumerate(texts):
                doc_metadata = metadata.copy()
                doc_metadata['chunk_id'] = i
                documents.append(
                    Document(
                        page_content=text,
                        metadata=doc_metadata
                    )
                )
            
            logger.info(f"Created {len(documents)} Langchain documents")
            # Log sample document content
            if documents:
                logger.info(f"Sample document content: {documents[0].page_content[:100]}...")
            
            return documents
            
        except Exception as e:
            logger.error(f"Error preparing documents: {str(e)}")
            raise

    def _chunk_content(self, content, chunk_size=1000, overlap=100):
        """Split content into chunks with overlap."""
        chunks = []
        start = 0
        content_length = len(content)
        
        while start < content_length:
            end = start + chunk_size
            if end > content_length:
                end = content_length
            
            # Find the end of the sentence
            while end < content_length and content[end] not in ['.', '!', '?', '\n']:
                end += 1
            if end < content_length:
                end += 1
            
            chunk = content[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            
        return chunks