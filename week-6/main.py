import csv
import json
from datetime import datetime
from pathlib import Path

import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"
RELEASE = "v0.1"
INPUT_FILE = Path(__file__).with_name("golden_set.json")
OUTPUT_FILE = Path(__file__).with_name("baseline_results.csv")
CSV_FIELDS = [
    "Question_ID",
    "Question",
    "Expected_Answer",
    "LLM_Answer",
    "Matched_Keywords",
    "Missing_Keywords",
    "Score",
    "Status",
    "Source",
    "Model",
    "Release",
]


def load_golden_set():
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        questions = json.load(file)
    if not isinstance(questions, list) or not questions:
        raise ValueError("golden_set.json must contain a non-empty JSON array.")
    required = {"id", "question", "expected_answer", "keywords", "source"}
    for index, item in enumerate(questions, start=1):
        missing = required - item.keys()
        if missing:
            raise ValueError(
                f"Question {index} is missing required fields: {', '.join(sorted(missing))}"
            )
    return questions


def get_llm_answer(question):
    payload = {
        "model": MODEL_NAME,
        "prompt": question,
        "stream": False,
        "options": {"temperature": 0},
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()
    answer = response.json().get("response", "").strip()
    if not answer:
        raise ValueError("Ollama returned an empty response.")
    return answer


def calculate_score(answer, expected_keywords):
    answer_lower = answer.casefold()
    matched = [
        keyword for keyword in expected_keywords if keyword.casefold() in answer_lower
    ]
    missing = [
        keyword for keyword in expected_keywords if keyword.casefold() not in answer_lower
    ]
    score = (len(matched) / len(expected_keywords) * 100) if expected_keywords else 0
    return round(score, 2), matched, missing


def evaluate_question(item, index):
    question_id = item["id"]
    question = item["question"]
    expected_answer = item["expected_answer"]
    keywords = item["keywords"]
    source = item["source"]

    print("\n" + "-" * 70)
    print(f"Question {index}: {question_id}")
    print("Question:", question)

    row = {
        "Question_ID": question_id,
        "Question": question,
        "Expected_Answer": expected_answer,
        "LLM_Answer": "",
        "Matched_Keywords": "",
        "Missing_Keywords": ", ".join(keywords),
        "Score": 0,
        "Status": "ERROR",
        "Source": source,
        "Model": MODEL_NAME,
        "Release": RELEASE,
    }

    try:
        answer = get_llm_answer(question)
        score, matched, missing = calculate_score(answer, keywords)
        status = "PASS" if score >= 60 else "REVIEW"
        row.update(
            LLM_Answer=answer,
            Matched_Keywords=", ".join(matched),
            Missing_Keywords=", ".join(missing),
            Score=score,
            Status=status,
        )
        print("\nLLM Answer:")
        print(answer)
        print("\nExpected Answer:")
        print(expected_answer)
        print("\nMatched Keywords:", matched)
        print("Missing Keywords:", missing)
        print(f"Score: {score}%")
        print("Status:", status)
    except requests.RequestException as error:
        print("Request error:", error)
    except (ValueError, KeyError) as error:
        print("Evaluation error:", error)

    return row


def write_results(results):
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(results)


def print_summary(results):
    successful = [row for row in results if row["Status"] in {"PASS", "REVIEW"}]
    passed = sum(row["Status"] == "PASS" for row in results)
    review = sum(row["Status"] == "REVIEW" for row in results)
    errors = sum(row["Status"] == "ERROR" for row in results)
    average = (
        sum(float(row["Score"]) for row in successful) / len(successful)
        if successful
        else 0
    )

    print("\n" + "=" * 42)
    print("BASELINE EVALUATION SUMMARY")
    print("=" * 42)
    print("Release Version:", RELEASE)
    print("Model:", MODEL_NAME)
    print("Total Questions:", len(results))
    print("Successful Responses:", len(successful))
    print("Passed Questions:", passed)
    print("Questions for Review:", review)
    print("Failed Requests:", errors)
    print("Average Keyword Coverage:", f"{average:.2f}%")
    print("Evaluation Date:", datetime.now().astimezone().isoformat(timespec="seconds"))
    print("Results saved to:", OUTPUT_FILE)
    if errors:
        print("Some requests failed. Check Ollama is running and llama3.2 is installed.")
    print("Baseline run completed for release", RELEASE)


def main():
    questions = load_golden_set()
    print("\nGOLDEN QUESTION SET")
    print("=" * 42)
    print("Total Questions:", len(questions))
    print("Model:", MODEL_NAME)
    print("\nBASELINE RUN STARTED")

    results = [
        evaluate_question(item, index)
        for index, item in enumerate(questions, start=1)
    ]
    write_results(results)
    print_summary(results)


if __name__ == "__main__":
    main()
