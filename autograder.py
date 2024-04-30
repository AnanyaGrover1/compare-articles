
import os
import pandas as pd
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")

# CSV Format: topic, category, ground_truth_summary, zero_shot, chain_of_thoughts, multiagent
csv_file_path = 'summaries_pairs.csv'
output_csv_file_path = 'evaluation_scores.csv'


def generate_prompt(topic, category, ground_truth, ai_generated):
    prompt = (
        f"For news articles on '{topic}', compare the similarity (in content and essence, not writing style) between "
        f"the following ground truth and AI-generated statements on the '{category}' theme.\n\n"
        f"Ground Truth:\n{ground_truth}\n\n"
        f"AI-generated:\n{ai_generated}\n\n"
        "Score the similarity between the ground truth and the AI output on a scale from 0 to 5.\n\n"
        "Please provide the score as a number between 0 to 5."
    )
    return prompt


client = OpenAI()


def query_for_similarity(tag, category, ground_truth, ai_generated):
    prompt = generate_prompt(tag, category, ground_truth, ai_generated)
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=60,
        n=1,
        stop=None
    )
    score_text = response.choices[0].message.content.strip()
    return int(score_text)  # Assuming GPT replies with a number directly.


def load_summaries_from_csv(csv_file_path):
    return pd.read_csv(csv_file_path)


def evaluate_summaries(df):
    scores = {'score1': [], 'score2': [], 'score3': []}
    for idx, row in df.iterrows():
        print(
            f"Evaluating row {idx + 1}/{len(df)} under topic '{row['topic']}'")
        scores['score1'].append(query_for_similarity(
            row['topic'], row['category'], row['ground_truth'], row['zero_shot']))
        scores['score2'].append(query_for_similarity(
            row['topic'], row['category'], row['ground_truth'], row['chain_of_thoughts']))
        scores['score3'].append(query_for_similarity(
            row['topic'], row['category'], row['ground_truth'], row['multiagent']))
    return scores


def main():
    df = load_summaries_from_csv(csv_file_path)
    scores = evaluate_summaries(df)
    df['Score 1'] = scores['score1']
    df['Score 2'] = scores['score2']
    df['Score 3'] = scores['score3']

    df.to_csv(output_csv_file_path, index=False)
    print(f"Evaluations completed and saved to '{output_csv_file_path}'.")


if __name__ == "__main__":
    main()
