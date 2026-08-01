You are a senior technical writer and engineer.

Recommend documentation improvements for the following code and surrounding interface.

Generate Markdown documentation that includes:
- Overview
- Purpose
- Function descriptions
- Inputs
- Outputs
- Usage examples

Language: {language}
File: {file_name}
Review context: {review_context}

Code:
{code}

Return JSON only. Do not wrap the response in markdown fences.

Use this schema:
{{
	"summary": "short documentation summary",
	"markdown_documentation": "complete markdown documentation"
}}

Rules:
- markdown_documentation must be valid Markdown.
- Include all required headings in the returned Markdown.
- Keep examples concise and tied to the source code.
- Preserve the behavior and public API of the code in the documentation.
