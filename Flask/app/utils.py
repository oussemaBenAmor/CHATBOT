"""
Utility functions for NLP processing and similarity matching
"""

import re
from typing import List, Dict, Tuple
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import torch

def clean_text(text: str) -> str:
    """
    Clean and normalize text for better processing
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:]', '', text)
    return text.strip()

def extract_key_phrases(text: str, nlp_model) -> List[str]:
    """
    Extract key phrases from text using spaCy
    """
    doc = nlp_model(text)
    key_phrases = []
    
    # Extract noun chunks
    for chunk in doc.noun_chunks:
        if len(chunk.text.strip()) > 2:
            key_phrases.append(chunk.text.strip().lower())
    
    # Extract named entities
    for ent in doc.ents:
        if ent.label_ in ['ORG', 'MONEY', 'DATE', 'TIME', 'LOC']:
            key_phrases.append(ent.text.strip().lower())
    
    return list(set(key_phrases))

# def calculate_semantic_similarity(text1: str, text2: str, nlp_model) -> float:
#     """
#     Calculate semantic similarity between two texts using spaCy
#     """
#     try:
#         doc1 = nlp_model(text1.lower())
#         doc2 = nlp_model(text2.lower())
#         return doc1.similarity(doc2)
#     except:
#         return 0.0
def calculate_semantic_similarity(text1: str, text2: str, sbert_model) -> float:
    embeddings = sbert_model.encode([text1, text2], convert_to_tensor=True)
    return float(torch.nn.functional.cosine_similarity(embeddings[0], embeddings[1], dim=0).item())

def find_most_similar_sentences(query: str, sentences: List[str], sbert_model, top_k: int = 5) -> List[Tuple[str, float]]:
    """
    Find the most similar sentences to a query using multiple similarity metrics
    """
    if not sentences:
        return []
    
    similarities = []
    
    for sentence in sentences:
        # Semantic similarity
        semantic_sim = calculate_semantic_similarity(query, sentence, sbert_model)
        
        # TF-IDF similarity
        try:
            vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform([query.lower(), sentence.lower()])
            tfidf_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except:
            tfidf_sim = 0.0
        
        # Combined score
        combined_score = (semantic_sim * 0.6) + (tfidf_sim * 0.4)
        similarities.append((sentence, combined_score))
    
    # Sort by similarity and return top k
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]

def categorize_transaction_question(question: str) -> Dict[str, float]:
    """
    Categorize a question by transaction type with confidence scores
    """
    transaction_categories = {
        'refunds': ['refund', 'return', 'credit', 'money back', 'reimbursement'],
        'payments': ['payment', 'pay', 'card', 'bank', 'cash', 'transfer'],
        'transfers': ['transfer', 'move', 'send', 'wire'],
        'exchanges': ['exchange', 'swap', 'trade', 'replace']
    }
    
    question_lower = question.lower()
    scores = {}
    
    for category, keywords in transaction_categories.items():
        score = 0
        for keyword in keywords:
            if keyword in question_lower:
                score += 1
        if score > 0:
            scores[category] = score / len(keywords)
    
    return scores

def extract_question_intent(question: str) -> str:
    """
    Extract the intent of a question (what, how, when, where, why, which, who)
    """
    question_lower = question.lower()
    
    if question_lower.startswith('what'):
        return 'what'
    elif question_lower.startswith('how'):
        return 'how'
    elif question_lower.startswith('when'):
        return 'when'
    elif question_lower.startswith('where'):
        return 'where'
    elif question_lower.startswith('why'):
        return 'why'
    elif question_lower.startswith('which'):
        return 'which'
    elif question_lower.startswith('who'):
        return 'who'
    else:
        return 'general'

def format_answer_for_intent(intent: str, relevant_info: List[str], transaction_type: str) -> str:
    """
    Format the answer based on the detected intent
    """
    if not relevant_info:
        return f"No specific information found about {transaction_type}."
    
    if intent == 'what':
        answer = f"Here's what I found about {transaction_type}:\n\n"
        for i, info in enumerate(relevant_info[:5], 1):
            answer += f"{i}. {info.strip()}\n"
    
    elif intent == 'how':
        answer = f"Here's how to handle {transaction_type}:\n\n"
        for i, info in enumerate(relevant_info[:5], 1):
            answer += f"{i}. {info.strip()}\n"
    
    elif intent == 'when':
        answer = f"Here's the timing information for {transaction_type}:\n\n"
        for i, info in enumerate(relevant_info[:5], 1):
            answer += f"{i}. {info.strip()}\n"
    
    elif intent == 'where':
        answer = f"Here's where you can find information about {transaction_type}:\n\n"
        for i, info in enumerate(relevant_info[:5], 1):
            answer += f"{i}. {info.strip()}\n"
    
    elif intent == 'why':
        answer = f"Here's why these {transaction_type} policies exist:\n\n"
        for i, info in enumerate(relevant_info[:5], 1):
            answer += f"{i}. {info.strip()}\n"
    
    elif intent == 'which':
        answer = f"Here are the options available for {transaction_type}:\n\n"
        for i, info in enumerate(relevant_info[:5], 1):
            answer += f"{i}. {info.strip()}\n"
    
    elif intent == 'who':
        answer = f"Here's who handles {transaction_type}:\n\n"
        for i, info in enumerate(relevant_info[:5], 1):
            answer += f"{i}. {info.strip()}\n"
    
    else:  # general
        answer = f"Here's the information about {transaction_type}:\n\n"
        for i, info in enumerate(relevant_info[:5], 1):
            answer += f"{i}. {info.strip()}\n"
    
    return answer
