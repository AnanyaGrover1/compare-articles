
import os
import pandas as pd
import openai

api_key = os.getenv("OPEN_API_KEY")

# Assuming CSV Format: tag, category, ground_truth_summary, ai_generated_summary
csv_file_path = 'summaries_pairs.csv'
# Output filename
output_csv_file_path = 'evaluation_scores.csv'


def generate_prompt(tag, category, ground_truth, ai_generated):
    prompt = (
        f"""For news articles on '{tag}', compare the similarity between
        the following ground truth and AI-generated statements on the '{category}' between articles.
        Score the similarity between the ground truth and the AI output on a scale from 0 to 5.\n\n"
        f"Ground Truth:\n{ground_truth}\n\n"
        f"AI-generated:\n{ai_generated}\n\n"
        f"Please provide the scores as a number between 0 to 5."""
    )
    return prompt


def query_for_similarity(tag, category, ground_truth, ai_generated):
    prompt = generate_prompt(tag, category, ground_truth, ai_generated)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=500,
        n=1,
        stop=None
    )
    return response.choices[0].message['content'].strip()


def load_summaries_from_csv(csv_file_path):
    return pd.read_csv(csv_file_path)


def evaluate_summaries(df):
    evaluative_responses = []
    for idx, row in df.iterrows():
        print(f"Evaluating pair {idx + 1}/{len(df)} under tag '{row['tag']}'")
        tag = row['tag']
        category = row['category']
        ground_truth = row['ground_truth_summary']
        ai_generated = row['ai_generated_summary']

        comparison_result = query_for_similarity(
            tag, category, ground_truth, ai_generated)
        # may need to parse the scores from comparison_result
        # Temporarily, let's append the raw result.
        evaluative_responses.append(comparison_result)

    return evaluative_responses


def main():
    df = load_summaries_from_csv(csv_file_path)
    df['evaluation'] = evaluate_summaries(df)

    # Optional: Extract numerical scores from the 'evaluation' texts and add to the dataframe

    # Save results with evaluations to a new CSV
    df.to_csv(output_csv_file_path, index=False)
    print(f"Evaluations completed and saved to '{output_csv_file_path}'.")


if __name__ == "__main__":
    main()
