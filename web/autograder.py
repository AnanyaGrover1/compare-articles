# filename: autograder.py

import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Ensure that the necessary NLTK tokenizers are downloaded
nltk.download('punkt')

def tokenize_summary(summary):
    # Tokenize the bullet points into sentences
    return [nltk.tokenize.sent_tokenize(point) for point in summary]

def calculate_similarity(truth_tokens, ai_tokens):
    # Flatten the list of tokens
    truth_flat = [item for sublist in truth_tokens for item in sublist]
    ai_flat = [item for sublist in ai_tokens for item in sublist]
    
    # Calculate TF-IDF vectors
    vectorizer = TfidfVectorizer().fit(truth_flat + ai_flat)
    truth_vectors = vectorizer.transform(truth_flat)
    ai_vectors = vectorizer.transform(ai_flat)
    
    # Calculate cosine similarity and return the average
    similarity_matrix = cosine_similarity(truth_vectors, ai_vectors)
    return similarity_matrix.mean()

def main():
    # Collect summaries from the user
    ground_truth = []
    ai_generated = []
    
    categories = [
        "main points of agreement",
        "points of factual disagreement",
        "differences in framing",
        "differences in viewpoints",
        "selective omissions"
    ]
    
    for category in categories:
        print(f"Please enter the ground truth for {category}:")
        truth_input = input()
        ground_truth.append(truth_input)
        
        print(f"Please enter the AI-generated summary for {category}:")
        ai_input = input()
        ai_generated.append(ai_input)
    
    # Tokenize summaries
    ground_truth_tokens = tokenize_summary(ground_truth)
    ai_generated_tokens = tokenize_summary(ai_generated)
    
    # Calculate similarity for each category
    scores = []
    for truth_tokens, ai_tokens in zip(ground_truth_tokens, ai_generated_tokens):
        similarity = calculate_similarity(truth_tokens, ai_tokens)
        scores.append(similarity)
    
    # Output the results
    for category, score in zip(categories, scores):
        print(f"Similarity score for {category}: {score:.2f}")
    
    # Calculate and print the overall score
    overall_score = sum(scores) / len(scores)
    print(f"Overall similarity score: {overall_score:.2f}")

if __name__ == "__main__":
    main()