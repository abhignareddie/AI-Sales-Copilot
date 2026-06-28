import re
from typing import List, Dict, Any, Optional
import tiktoken

class BaseChunker:
    """Base class for all chunking strategies."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50, encoding_name: str = "cl100k_base"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        try:
            self.tokenizer = tiktoken.get_encoding(encoding_name)
        except Exception:
            self.tokenizer = None

    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken, fallback to word count estimation if not available."""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        return len(text.split())

    def split(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Split text into chunks. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement split()")

class FixedSizeChunker(BaseChunker):
    """Splits text into chunks of fixed character or token size."""
    
    def split(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        meta = metadata or {}
        chunks = []
        words = text.split()
        
        current_chunk_words = []
        current_count = 0
        
        for word in words:
            current_chunk_words.append(word)
            current_count += 1
            if current_count >= self.chunk_size:
                chunk_text = " ".join(current_chunk_words)
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        **meta,
                        "chunk_index": len(chunks),
                        "token_count": self.count_tokens(chunk_text)
                    }
                })
                # Overlap
                overlap_size = min(self.chunk_overlap, len(current_chunk_words))
                current_chunk_words = current_chunk_words[-overlap_size:] if overlap_size > 0 else []
                current_count = len(current_chunk_words)
                
        if current_chunk_words:
            chunk_text = " ".join(current_chunk_words)
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    **meta,
                    "chunk_index": len(chunks),
                    "token_count": self.count_tokens(chunk_text)
                }
            })
            
        return chunks

class RecursiveCharacterChunker(BaseChunker):
    """Splits text recursively using a list of separators (e.g. paragraph, sentence, space)."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100, separators: Optional[List[str]] = None):
        super().__init__(chunk_size, chunk_overlap)
        self.separators = separators or ["\n\n", "\n", ". ", "? ", "! ", " ", ""]

    def split(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        meta = metadata or {}
        chunks = []
        
        raw_chunks = self._recursive_split(text, self.separators)
        for i, chunk_text in enumerate(raw_chunks):
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    **meta,
                    "chunk_index": i,
                    "token_count": self.count_tokens(chunk_text)
                }
            })
        return chunks

    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        if len(text) <= self.chunk_size:
            return [text]
            
        if not separators:
            # Fallback to character splitting
            return [text[i:i + self.chunk_size] for i in range(0, len(text), self.chunk_size - self.chunk_overlap)]
            
        separator = separators[0]
        splits = text.split(separator)
        
        final_chunks = []
        current_chunk = ""
        
        for split in splits:
            if not split:
                continue
            if len(current_chunk) + len(split) + len(separator) <= self.chunk_size:
                current_chunk += (separator if current_chunk else "") + split
            else:
                if current_chunk:
                    final_chunks.append(current_chunk)
                # If a single split is larger than the chunk size, split it recursively using remaining separators
                if len(split) > self.chunk_size:
                    final_chunks.extend(self._recursive_split(split, separators[1:]))
                    current_chunk = ""
                else:
                    current_chunk = split
                    
        if current_chunk:
            final_chunks.append(current_chunk)
            
        return final_chunks

class SlidingWindowChunker(BaseChunker):
    """Generates overlapping sliding windows over text."""
    
    def split(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        meta = metadata or {}
        chunks = []
        words = text.split()
        
        step = max(1, self.chunk_size - self.chunk_overlap)
        for i in range(0, len(words), step):
            window_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(window_words)
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    **meta,
                    "chunk_index": len(chunks),
                    "token_count": self.count_tokens(chunk_text)
                }
            })
            if i + self.chunk_size >= len(words):
                break
                
        return chunks

class HeadingAwareChunker(BaseChunker):
    """Splits documents based on headers or heading blocks, preserving heading context."""
    
    def split(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        meta = metadata or {}
        headings = meta.get("headings", [])
        
        if not headings:
            # Fallback to RecursiveCharacterChunker
            return RecursiveCharacterChunker(self.chunk_size, self.chunk_overlap).split(text, meta)
            
        chunks = []
        # Find position of headings in the text to split sections
        # For simplicity, we split text by heading strings
        sections = []
        current_idx = 0
        
        sorted_headings = sorted(headings, key=lambda h: text.find(h.get("text", "")))
        
        for i, heading in enumerate(sorted_headings):
            heading_text = heading.get("text", "")
            next_heading_text = sorted_headings[i+1].get("text", "") if i + 1 < len(sorted_headings) else None
            
            start_pos = text.find(heading_text, current_idx)
            if start_pos == -1:
                continue
                
            end_pos = text.find(next_heading_text, start_pos + len(heading_text)) if next_heading_text else len(text)
            if end_pos == -1:
                end_pos = len(text)
                
            section_content = text[start_pos:end_pos].strip()
            sections.append((heading_text, section_content))
            current_idx = end_pos
            
        if not sections:
            # If search for headings failed
            return RecursiveCharacterChunker(self.chunk_size, self.chunk_overlap).split(text, meta)
            
        for heading_text, section_content in sections:
            # Split section content recursively if too large
            section_chunks = RecursiveCharacterChunker(self.chunk_size, self.chunk_overlap).split(
                section_content, 
                {**meta, "current_heading": heading_text}
            )
            chunks.extend(section_chunks)
            
        return chunks

class SemanticChunker(BaseChunker):
    """Simulates semantic drift checking via paragraph splits, sentence length, or syntactic bounds."""
    
    def split(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        meta = metadata or {}
        # We split by sentences or paragraphs and check semantic distance or simply cluster sentences
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            para_tokens = self.count_tokens(para)
            
            # If current paragraph is extremely long, split it by sentence
            if para_tokens > self.chunk_size:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sentence in sentences:
                    sentence_tokens = self.count_tokens(sentence)
                    if current_tokens + sentence_tokens > self.chunk_size:
                        if current_chunk:
                            chunk_text = " ".join(current_chunk)
                            chunks.append({
                                "text": chunk_text,
                                "metadata": {
                                    **meta,
                                    "chunk_index": len(chunks),
                                    "token_count": self.count_tokens(chunk_text)
                                }
                            })
                            current_chunk = []
                            current_tokens = 0
                        current_chunk.append(sentence)
                        current_tokens += sentence_tokens
                    else:
                        current_chunk.append(sentence)
                        current_tokens += sentence_tokens
            else:
                if current_tokens + para_tokens > self.chunk_size:
                    if current_chunk:
                        chunk_text = "\n\n".join(current_chunk)
                        chunks.append({
                            "text": chunk_text,
                            "metadata": {
                                **meta,
                                "chunk_index": len(chunks),
                                "token_count": self.count_tokens(chunk_text)
                            }
                        })
                        current_chunk = []
                        current_tokens = 0
                current_chunk.append(para)
                current_tokens += para_tokens
                
        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    **meta,
                    "chunk_index": len(chunks),
                    "token_count": self.count_tokens(chunk_text)
                }
            })
            
        return chunks
