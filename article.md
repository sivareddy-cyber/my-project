# How I wired Hindsight memories into code review

The most frustrating code review comment is the one you have already written three times. A reviewer flags a forbidden logging call, a team-specific API, or a naming convention; the next pull request arrives, and the same explanation starts over.

I built a review service around a simple premise: a code review should be able to consult the rules developers have already taught it. The interesting part was not putting a memory lookup in front of an LLM. It was making the whole loop explicit: retain a rule, retrieve it in the context of code, show which rule influenced the review, and let a developer correct the system when the rule or the finding is wrong.

## The shape of the system

The backend is a small FastAPI application. Its routes separate the main operations: `/memory` accepts a directly taught rule, `/review` reviews submitted code, and `/feedback` records a developer's response to a review. Pydantic models define the request and response shapes. The React frontend provides the code review and feedback interface, while the backend owns the memory and inference calls.

Hindsight provides persistent team context; Groq provides the language model call. In a review, the service constructs a query from the language and submitted code, asks Hindsight for up to five relevant memories, and passes those strings alongside the code to the review service. The response contains a summary, structured issues, and a `memories_used` list. That last field matters: it makes the connection between a retrieved rule and a review visible rather than leaving it buried in a prompt.

The route captures the central flow in a few lines:

```python
search_query = f"Rules, conventions, and disallowed patterns for {request.language} code:\n{request.code}"
recalled_memories = await hindsight_service.recall_memories(
    query=search_query, limit=5
)

review_result = await llm_service.review_code(
    code=request.code,
    language=request.language,
    memories=recalled_memories,
)
```

## The hard part is closing the loop

Retrieval alone does not make a review system learn. A repository could store a pile of rules and still produce the same frustrating comments if developers cannot improve that collection.

The feedback endpoint takes free-form feedback and optional corrections. It can ask the LLM to turn the feedback into a concise, standalone rule, then retain that rule with metadata identifying its source and review ID. For example, “Never use `eval()` in helper utilities” can become a reusable team standard instead of remaining an isolated response to one review.

```python
distilled_rule = await llm_service.extract_learnings_from_feedback(
    feedback=feedback_content
)
content_to_retain = distilled_rule or feedback_content

result = await hindsight_service.retain_memory(
    content=f"Team feedback/standard: {content_to_retain}",
    metadata={"source": "developer_feedback", "review_id": str(request.review_id or "")},
)
```

I like that the original feedback remains a fallback if distillation fails. A failure in the optional extraction step does not have to discard the developer's correction. That is a small resilience decision, but it reflects an important product constraint: the learning path should not be more fragile than the review path it is meant to improve.

Direct teaching is supported too. A developer can send a rule to `/memory` without waiting for a review interaction. That gives teams a clear way to seed conventions they already know, while feedback-derived memories capture rules discovered during real use.

## Memory should be inspectable, not magical

The review prompt explicitly includes retrieved memories and asks for the exact relevant rules to be returned in `memories_used`. When there are no memories, the prompt says so. This lets the reviewer distinguish “there was no known team rule” from “there was a rule and the code appears to violate it.” It also gives a developer a concrete explanation to inspect when a team-specific finding appears.

The prompt construction is direct:

```python
if memories:
    user_content += "### RECALLED TEAM MEMORIES (from Hindsight):\n"
    for i, mem in enumerate(memories, 1):
        user_content += f"{i}. {mem}\n"
else:
    user_content += "### RECALLED TEAM MEMORIES:\nNo specific team memories found for this context.\n\n"

user_content += f"### CODE TO REVIEW:\n```\n{code}\n```"
```

This is not a guarantee that a model will always apply a rule correctly. It is an interface decision that makes the context available and asks the model to account for it in a structured result. The output is parsed into `ReviewIssue` objects with line, severity, description, and suggestion fields, then validated through `ReviewResponse`. The shape gives the frontend and downstream consumers something more useful than an unstructured paragraph.

For background on the memory model, I found the [Hindsight GitHub repository](https://github.com/vectorize-io/hindsight) and [Hindsight documentation](https://hindsight.vectorize.io/) useful starting points. The broader framing of [agent memory](https://vectorize.io/what-is-agent-memory) is relevant here: context accumulated across interactions is useful only if a system can retrieve it for the task at hand. In this project, the task is intentionally narrow—review this code against conventions the team has retained.

## A local fallback changes the development story

The Hindsight integration uses the official client when an API key is configured. It also has a local persistent JSON store. If cloud client initialization or an operation fails, retention falls back to appending a local entry, and recall falls back to keyword overlap between the query and stored content.

That local strategy is intentionally simpler than semantic recall. It makes the service usable in environments without cloud credentials and keeps the retain/recall flow exercisable, but it has obvious limits: wording matters, and the implementation does not provide the same semantic matching behavior as a memory service. The fallback is a development and availability path, not evidence that keyword overlap is equivalent to Hindsight retrieval.

The fallback also surfaced a design detail worth making explicit: persistent data needs a defined home. The service writes its file under the backend directory, and it avoids adding duplicate entries with exactly identical content. That gives local runs continuity across requests, although production deployments should choose storage and concurrency semantics appropriate to their runtime rather than treating a JSON file as a shared database.

## What the interaction looks like

Suppose a developer teaches the system, “Our team does not allow `console.log()` in production code.” The rule is retained with a source marker. Later, someone submits JavaScript containing a `console.log()` call. The review route queries memory with the language and code, receives the relevant rule, and supplies it to the reviewer. The structured response can identify a team-standard violation, suggest the team's preferred logger, and list the rule under `memories_used`.

If the reviewer misses an important distinction, the developer can send feedback or a correction. The feedback route tries to distill it into a standalone standard and stores the result with review metadata. A later review can retrieve that standard. The useful behavior is not that one model call is infallible; it is that a correction can become context for subsequent work instead of disappearing when the request ends.


## What I learned

### 1. Make the memory boundary explicit

Treat recall as a distinct service operation with a clear query and limit. That makes it easier to inspect what the system asked memory to retrieve and what the reviewer received.

### 2. Return the context that influenced the answer

An explicit `memories_used` field gives developers something to challenge. If the wrong rule appears there, the retrieval or memory contents are suspect; if the right rule appears but the review ignores it, the inference step deserves attention.

### 3. Preserve feedback when enrichment fails

Distillation can make feedback more reusable, but it should not be a single point of data loss. Retaining the raw feedback as a fallback is a straightforward way to keep the learning path useful through an extraction error.

### 4. Name fallback behavior honestly

A local keyword matcher can keep development moving, but it has different retrieval properties from a cloud memory service. Calling out that distinction prevents a convenient fallback from silently defining production expectations.

### 5. Test contracts and integrations separately

Mocked tests are fast and deterministic for route behavior. A live acceptance path is valuable for checking service integration. Neither substitutes for evaluating whether the retrieved rules are relevant or whether review findings are consistently correct.

The system's core idea is modest: carry a team's prior decisions into the next review, and give developers a way to correct what gets carried forward. That modesty is useful. It keeps the design focused on a concrete engineering problem—repeating the same standards in every pull request—and makes the memory path visible enough to inspect when it gets something wrong.
