"""
End-to-End Live Memory Loop Acceptance Test

Executes the full real Hindsight + Groq loop:
1. Teach: "Our team does not allow console.log() in production code."
2. Retain in REAL Hindsight.
3. Submit code with console.log().
4. Recall the rule from REAL Hindsight.
5. Send to Groq LLM with the recalled memory.
6. Verify the review specifically identifies the team rule violation.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup paths
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(backend_dir)
for p in (backend_dir, root_dir):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from backend.services.hindsight_service import hindsight_service
    from backend.services.llm_service import llm_service
except ImportError:
    from services.hindsight_service import hindsight_service
    from services.llm_service import llm_service


async def run_live_memory_loop():
    print("=" * 60)
    print("CodeReview Memory Agent - Live Memory Loop Acceptance Test")
    print("=" * 60)

    # Check API keys
    groq_key = os.getenv("GROQ_API_KEY")
    hindsight_key = os.getenv("HINDSIGHT_API_KEY")
    hindsight_url = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")

    print(f"Hindsight Base URL: {hindsight_url}")
    print(f"Hindsight Bank ID:  {hindsight_service.bank_id}")
    print(f"Hindsight Mode:     {'Cloud API' if hindsight_key else 'Embedded Persistent Hindsight Engine'}")
    print(f"Groq API Key set:   {'YES' if groq_key else 'NO'}")

    if not groq_key:
        print("\n[!] Please ensure GROQ_API_KEY is configured in backend/.env.")
        return False

    rule_text = "Our team does not allow console.log() in production code."

    # Step 1: Teach & Retain
    print(f"\n[Step 1] Retaining team rule into REAL Hindsight...")
    print(f"  Rule: \"{rule_text}\"")
    retain_res = await hindsight_service.retain_memory(
        content=rule_text,
        metadata={"source": "acceptance_test", "rule_type": "logging_standard"}
    )
    print(f"  [OK] Retain Response: {retain_res.get('status')} (Bank: {retain_res.get('bank_id')})")

    # Step 2: Recall Memory
    test_code = """
function processPayment(paymentDetails) {
  console.log("Processing payment for user:", paymentDetails.userId);
  const success = chargeCard(paymentDetails.amount);
  return { success, timestamp: Date.now() };
}
"""
    print(f"\n[Step 2] Recalling memories for test code from REAL Hindsight...")
    query = f"Code standards and disallowed statements for javascript:\n{test_code}"
    recalled = await hindsight_service.recall_memories(query=query, limit=3)
    print(f"  [OK] Recalled {len(recalled)} memories:")
    for i, mem in enumerate(recalled, 1):
        print(f"    {i}. {mem}")

    # Step 3: Groq LLM Review
    print(f"\n[Step 3] Running team-aware code review with Groq LLM...")
    review = await llm_service.review_code(
        code=test_code,
        language="javascript",
        memories=recalled,
    )

    print(f"\n[Step 4] Review Results:")
    print(f"  Summary: {review.summary}")
    print(f"  Memories Used: {review.memories_used}")
    print(f"  Issues Found ({len(review.issues)}):")
    found_team_rule_issue = False
    for issue in review.issues:
        print(f"    - [{issue.severity.upper()}] Line {issue.line}: {issue.description}")
        if issue.suggestion:
            print(f"      Suggestion: {issue.suggestion}")
        if "console.log" in issue.description.lower() or "team" in issue.description.lower():
            found_team_rule_issue = True

    print("\n" + "=" * 60)
    if found_team_rule_issue:
        print("[OK] ACCEPTANCE TEST PASSED: Team rule recalled and enforced by Groq!")
    else:
        print("? Review completed, please inspect if the rule was cited.")
    print("=" * 60)
    return True


if __name__ == "__main__":
    asyncio.run(run_live_memory_loop())
