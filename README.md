# PRISM: LLM-Based News Comparative Summarization

**PRISM** is a research-driven toolset designed to combat media polarization. It leverages Large Language Models (LLMs) to synthesize multiple news sources into comparative summaries, helping users access diverse perspectives. This repository contains the code for my thesis, featuring two interfaces (Web/Streamlit & Reddit) and a benchmarking suite for three prompting methodologies.

## 🚀 Overview

The core of this project compares three LLM architectures to determine which best highlights contrasting narratives in news media:

* **Zero-Shot Learning (ZSL)**: Direct summary generation.
* **Chain of Thought (CoT)**: Step-by-step reasoning for deep analysis.
* **Multiagent Group Chat (MGC)**: Collaborative agents debating different viewpoints.

## 📂 Repository Structure

| File / Folder | Description |
| --- | --- |
| `autograder.py` | The **LLM-as-a-Judge** framework used for automated evaluation. |
| `compare_multichat.py` | Implementation of the **Multiagent Group (MGC)** approach. |
| `compare_openai_3.py` | Implementation of **Chain of Thought (CoT)** and **Zero-Shot** logic. |
| `evaluation_scores.csv` | Raw data from the LLM-based autograder and manual evaluation. |
| `summaries_pairs.csv` | Dataset containing the human written pairs of news summaries for comparison. |
| `📰_Manual_Compare.py` | Another page on the **Streamlit Web App** allowing for manually entering the news links to be compared |

## 🧪 Evaluation Methodology

To determine the most effective summarization technique, I utilized a dual-layer evaluation strategy:

1. **LLM-as-a-Judge (Autograder):** A programmatic evaluation using `autograder.py` to score summaries.
2. **Manual Evaluation:** Human-in-the-loop scoring (recorded in `evaluation_scores.csv`) to validate the autograder's findings and ensure nuanced qualitative analysis.

**Key Finding:** The **Chain of Thought (CoT)** method consistently outperformed other approaches in creating high-quality, balanced comparative news summaries.

## 🛠️ Setup & Installation

1. Clone the repository:
```bash
git clone https://github.com/AnanyaGrover1/prism.git

```


2. Install dependencies:
```bash
pip install -r requirements.txt

```

## 🛠️ Run the web app directly

Follow the streamlit link on the right hand menu

