import json
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.rag import answer_question

EVAL_FILE = "data/eval_set.json"
RESULTS_FILE = "data/eval_results.json"

def score_answer(answer: str, expected_keywords: list[str]) -> dict:
    answer_lower = answer.lower()
    matched = [kw for kw in expected_keywords if kw.lower() in answer_lower]
    score = len(matched) / len(expected_keywords) if expected_keywords else 0
    return {
        "score": round(score, 2),
        "matched": matched,
        "missed": [kw for kw in expected_keywords if kw.lower() not in answer_lower]
    }

def run_eval():
    with open(EVAL_FILE) as f:
        eval_set = json.load(f)

    results = []
    total_score = 0
    category_scores = {}

    print(f"Running eval on {len(eval_set)} questions...\n")

    for item in eval_set:
        print(f"[{item['id']}] {item['question'][:60]}")
        start = time.time()

        try:
            result = answer_question(
                question=item["question"],
                session_id=f"eval_{item['id']}"
            )
            elapsed = time.time() - start
            scoring = score_answer(result["answer"], item["expected_keywords"])

            entry = {
                "id": item["id"],
                "question": item["question"],
                "category": item["category"],
                "answer": result["answer"],
                "confidence": result["confidence"],
                "cached": result.get("cached", False),
                "keyword_score": scoring["score"],
                "matched_keywords": scoring["matched"],
                "missed_keywords": scoring["missed"],
                "latency_seconds": round(elapsed, 2),
                "sources": result["sources"]
            }

            results.append(entry)
            total_score += scoring["score"]

            cat = item["category"]
            if cat not in category_scores:
                category_scores[cat] = []
            category_scores[cat].append(scoring["score"])

            status = "✅" if scoring["score"] >= 0.5 else "❌"
            print(f"  {status} Score: {scoring['score']:.2f} | Confidence: {result['confidence']:.2f} | Time: {elapsed:.2f}s")
            print(f"  Matched: {scoring['matched']}")
            if scoring['missed']:
                print(f"  Missed: {scoring['missed']}")
            print()

        except Exception as e:
            print(f"  ❌ ERROR: {e}\n")
            results.append({
                "id": item["id"],
                "question": item["question"],
                "category": item["category"],
                "error": str(e),
                "keyword_score": 0
            })

    # Summary
    avg_score = total_score / len(eval_set)
    passed = sum(1 for r in results if r.get("keyword_score", 0) >= 0.5)

    print("=" * 60)
    print("EVAL SUMMARY")
    print("=" * 60)
    print(f"Total questions: {len(eval_set)}")
    print(f"Passed (score >= 0.5): {passed}/{len(eval_set)} ({passed/len(eval_set)*100:.1f}%)")
    print(f"Average keyword score: {avg_score:.2f}")
    print()
    print("By category:")
    for cat, scores in category_scores.items():
        avg = sum(scores) / len(scores)
        print(f"  {cat}: {avg:.2f} ({len(scores)} questions)")

    # Save results
    output = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_questions": len(eval_set),
        "passed": passed,
        "pass_rate": round(passed/len(eval_set)*100, 1),
        "avg_keyword_score": round(avg_score, 2),
        "category_scores": {k: round(sum(v)/len(v), 2) for k, v in category_scores.items()},
        "results": results
    }

    with open(RESULTS_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {RESULTS_FILE}")
    return output

if __name__ == "__main__":
    run_eval()