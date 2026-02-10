import os
import re
from typing import List, Tuple, Dict, Optional
import requests
from enum import Enum


class CitationFormat(Enum):
    """Citation format types."""
    APA = "APA"
    MLA = "MLA"
    CHICAGO = "Chicago"
    HARVARD = "Harvard"


class AIProcessor:
    """Handles AI-powered PDF processing features."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI processor.
        
        Args:
            api_key: Optional API key for AI services (OpenAI, etc.)
        """
        self.api_key = api_key
    
    @staticmethod
    def extractive_summarize(text: str, ratio: float = 0.2) -> str:
        """
        Create extractive summary by selecting key sentences.
        This is a basic implementation without external API.
        
        Args:
            text: Input text to summarize
            ratio: Proportion of sentences to keep (0.0 to 1.0)
        
        Returns:
            Summarized text
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return ""
        
        # Score sentences by word frequency
        word_freq = {}
        for sentence in sentences:
            words = sentence.lower().split()
            for word in words:
                if len(word) > 3:  # Skip short words
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # Score each sentence
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            score = 0
            words = sentence.lower().split()
            for word in words:
                if word in word_freq:
                    score += word_freq[word]
            if len(words) > 0:
                sentence_scores[i] = score / len(words)
        
        # Select top sentences
        num_sentences = max(1, int(len(sentences) * ratio))
        top_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
        top_indices.sort()  # Keep original order
        
        summary = '. '.join([sentences[i] for i in top_indices]) + '.'
        return summary
    
    @staticmethod
    def extract_keywords(text: str, top_n: int = 10) -> List[str]:
        """
        Extract top keywords from text.
        
        Args:
            text: Input text
            top_n: Number of top keywords to return
        
        Returns:
            List of keywords
        """
        # Remove common stop words
        stop_words = {'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'as', 'are', 
                     'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does',
                     'did', 'but', 'if', 'or', 'because', 'this', 'that', 'these', 'those'}
        
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        word_freq = {}
        
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_n]]
    
    @staticmethod
    def check_plagiarism_simple(text: str, sample_size: int = 500) -> Dict:
        """
        Simple plagiarism detection using web search.
        Note: This is a basic implementation. For production, use dedicated plagiarism APIs.
        
        Args:
            text: Text to check
            sample_size: Number of characters to sample for checking
        
        Returns:
            Dictionary with plagiarism results
        """
        # Take a sample of text
        sample = text[:sample_size].strip()
        
        if len(sample) < 50:
            return {
                'checked': False,
                'message': 'Text too short for plagiarism check',
                'matches': []
            }
        
        # This is a placeholder - real implementation would use APIs like:
        # - Copyleaks API
        # - Turnitin API
        # - Or custom Google search scraping
        
        return {
            'checked': True,
            'message': 'Plagiarism check requires API integration',
            'note': 'Configure Copyleaks, Turnitin, or similar API for full functionality',
            'matches': [],
            'match_percentage': 0.0
        }
    
    @staticmethod
    def generate_citation(title: str, authors: List[str], year: str, 
                         publisher: str = "", format_type: CitationFormat = CitationFormat.APA,
                         url: str = "", access_date: str = "") -> str:
        """
        Generate citation in specified format.
        
        Args:
            title: Document title
            authors: List of author names
            year: Publication year
            publisher: Publisher name
            format_type: Citation format (APA, MLA, Chicago, Harvard)
            url: URL for online sources
            access_date: Date accessed (for online sources)
        
        Returns:
            Formatted citation string
        """
        if not authors:
            authors = ["Unknown"]
        
        if format_type == CitationFormat.APA:
            # APA: Author, A. A. (Year). Title. Publisher.
            author_str = ", ".join([f"{a.split()[-1]}, {a.split()[0][0]}." if len(a.split()) > 0 else a 
                                   for a in authors[:3]])
            if len(authors) > 3:
                author_str += ", et al."
            
            citation = f"{author_str} ({year}). {title}."
            if publisher:
                citation += f" {publisher}."
            if url:
                citation += f" Retrieved from {url}"
            
            return citation
        
        elif format_type == CitationFormat.MLA:
            # MLA: Author. "Title." Publisher, Year.
            author_str = authors[0]
            if len(authors) > 1:
                author_str += ", et al."
            
            citation = f"{author_str}. \"{title}.\""
            if publisher:
                citation += f" {publisher},"
            citation += f" {year}."
            
            return citation
        
        elif format_type == CitationFormat.CHICAGO:
            # Chicago: Author. Title. Publisher, Year.
            author_str = ", ".join(authors[:3])
            if len(authors) > 3:
                author_str += ", et al."
            
            citation = f"{author_str}. {title}."
            if publisher:
                citation += f" {publisher},"
            citation += f" {year}."
            
            return citation
        
        elif format_type == CitationFormat.HARVARD:
            # Harvard: Author (Year) Title. Publisher.
            author_str = ", ".join([a.split()[-1] if len(a.split()) > 0 else a 
                                   for a in authors[:3]])
            if len(authors) > 3:
                author_str += " et al."
            
            citation = f"{author_str} ({year}) {title}."
            if publisher:
                citation += f" {publisher}."
            
            return citation
        
        return "Unknown format"
    
    @staticmethod
    def parse_pdf_metadata_for_citation(pdf_info: Dict) -> Dict:
        """
        Parse PDF metadata to extract citation information.
        
        Args:
            pdf_info: PDF metadata dictionary
        
        Returns:
            Dictionary with citation fields
        """
        return {
            'title': pdf_info.get('title', 'Unknown'),
            'authors': [pdf_info.get('author', 'Unknown')],
            'year': 'Unknown',  # Usually not in PDF metadata
            'publisher': pdf_info.get('creator', 'Unknown'),
        }
