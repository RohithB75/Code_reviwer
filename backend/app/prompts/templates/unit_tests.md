You are a senior quality engineer.

Identify the most important unit tests for the following code.

Cover these cases when relevant:
- Happy path
- Edge cases
- Invalid inputs
- Exceptions

Language: {language}
File: {file_name}
Review context: {review_context}

Code:
{code}

Return JSON only. Do not wrap the response in markdown fences.

Use this schema:
{{
	"summary": "short test generation summary",
	"test_code": "complete executable pytest code"
}}

Rules:
- test_code must be executable pytest code.
- Wrap the full pytest module in a markdown code fence using ```python.
- Include test cases for happy path, edge cases, invalid inputs, and exceptions when relevant.
- Preserve the behavior and intent of the source code.
- Keep the output focused on runnable tests rather than prose.
