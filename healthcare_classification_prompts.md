# Healthcare Document Classification Prompts

This file provides a ready-to-use three-step prompt set for healthcare document classification based on a predefined Excel configuration.

## Purpose

Classify a single healthcare document page using a fixed three-level hierarchy:

1. **Domain**
2. **Template Library** (mapped from the `Family` column)
3. **Template**

The prompts are designed to:

- use only predefined values from configuration
- return structured JSON
- stop early when `Other` is selected at Level 1 or Level 2
- produce the final extracted feature **Healthcare Classification**

## Expected Configuration Input

The source Excel file should contain these columns:

- `Domain`
- `Family`
- `Family Description`
- `Template`

## Recommended Orchestration Rules

1. Load the Excel configuration into memory.
2. Build the prompt inputs from the configuration.
3. Run **Prompt 1** with all unique Domain values plus `Other`.
4. If Prompt 1 returns `Other`, stop.
5. Run **Prompt 2** with all Family values associated with the selected Domain plus `Other`.
6. If Prompt 2 returns `Other`, stop.
7. Run **Prompt 3** with all Template values associated with the selected Domain and Template Library.
8. Set **Healthcare Classification** to the Template returned by Prompt 3.

## Shared System Prompt

Use this same system prompt for all three steps.

```text
You are a healthcare document classification engine.

Your job is to classify a single document page using only the predefined classification values provided in the prompt input.

Rules:
1. Use only the supplied candidate values. Do not invent or normalize new labels.
2. Evaluate the document page content exactly as provided.
3. Base your decision on explicit evidence from the page such as headers, form names, section titles, clinical terminology, layout clues, and repeated field labels.
4. If the evidence is weak, ambiguous, conflicting, or does not reasonably fit any provided option, choose "Other".
5. Match Percentage is how strongly the page aligns to the chosen option compared with the candidate list.
6. Confidence Percentage is how certain you are in your decision based on the page evidence.
7. Percentages must be integers from 0 to 100.
8. Reasoning must be concise, factual, and limited to evidence visible in the page content.
9. Return valid JSON only. Do not include markdown, commentary, or code fences.
10. Preserve the exact candidate value spelling and capitalization from the provided options.
```

---

## Prompt 1: Domain Classification

### User Prompt Template

```text
Classify the following healthcare document page into the best matching Domain.

Candidate Domain values:
{{DOMAIN_OPTIONS_WITH_OTHER}}

Document page content:
{{DOCUMENT_PAGE_TEXT}}

Return JSON in exactly this format:
{
  "domain_name": "<selected domain or Other>",
  "match_percentage": <integer 0-100>,
  "confidence_percentage": <integer 0-100>,
  "reasoning": "<concise evidence-based explanation>"
}

Selection guidance:
- Compare the page against all provided Domain values.
- Choose the single best match.
- If no Domain is a reasonable fit, return "Other".
- Do not return any fields other than the four fields above.
```

### Expected Output Example

```json
{
  "domain_name": "Claims",
  "match_percentage": 88,
  "confidence_percentage": 84,
  "reasoning": "The page contains claim identifiers, payer/member fields, billed services, and adjudication-related terminology that align most strongly with Claims."
}
```

---

## Prompt 2: Template Library Classification

Run this prompt only when Prompt 1 does **not** return `Other`.

### User Prompt Template

```text
Classify the following healthcare document page into the best matching Template Library within the selected Domain.

Selected Domain:
{{SELECTED_DOMAIN}}

Candidate Template Library values:
{{FAMILY_OPTIONS_WITH_OTHER}}

Optional Template Library descriptions:
{{FAMILY_DESCRIPTION_OPTIONS}}

Document page content:
{{DOCUMENT_PAGE_TEXT}}

Return JSON in exactly this format:
{
  "template_library": "<selected template library or Other>",
  "match_percentage": <integer 0-100>,
  "confidence_percentage": <integer 0-100>,
  "reasoning": "<concise evidence-based explanation>"
}

Selection guidance:
- Evaluate only the Template Library values provided for the selected Domain.
- Use the Family Description values when helpful, but classify only to a Template Library name from the candidate list.
- Choose "Other" if none of the candidate Template Libraries is a reasonable fit.
- Do not return any fields other than the four fields above.
```

### Expected Output Example

```json
{
  "template_library": "Explanation of Benefits",
  "match_percentage": 91,
  "confidence_percentage": 89,
  "reasoning": "The page includes member responsibility, allowed amount, provider details, and service line adjudication language typical of an Explanation of Benefits."
}
```

---

## Prompt 3: Template Classification

Run this prompt only when Prompt 2 does **not** return `Other`.

### User Prompt Template

```text
Classify the following healthcare document page into the exact Template within the selected Domain and Template Library.

Selected Domain:
{{SELECTED_DOMAIN}}

Selected Template Library:
{{SELECTED_TEMPLATE_LIBRARY}}

Candidate Template values:
{{TEMPLATE_OPTIONS}}

Related configuration rows:
{{FILTERED_CONFIGURATION_ROWS}}

Document page content:
{{DOCUMENT_PAGE_TEXT}}

Return JSON in exactly this format:
{
  "template_name": "<selected template>",
  "match_percentage": <integer 0-100>,
  "confidence_percentage": <integer 0-100>,
  "reasoning": "<concise evidence-based explanation>"
}

Selection guidance:
- Choose exactly one Template from the candidate list.
- Use the related configuration rows to understand distinctions between similar templates.
- Do not return "Other" at this step unless "Other" is explicitly included in the candidate Template list.
- Do not return any fields other than the four fields above.
```

### Expected Output Example

```json
{
  "template_name": "EOB Professional Services Standard",
  "match_percentage": 93,
  "confidence_percentage": 90,
  "reasoning": "The page matches the professional services EOB format through service line billing details, adjustment groupings, patient responsibility fields, and payer adjudication structure."
}
```

---

## Stop Logic

Use the following control logic outside the prompt:

### If Prompt 1 returns `Other`

- Stop processing.
- Do not run Prompt 2 or Prompt 3.
- Set final classification status to `Other` or `Unclassified`, based on your application convention.

### If Prompt 2 returns `Other`

- Stop processing.
- Do not run Prompt 3.
- Set final classification status to `Other` or `Unclassified`, based on your application convention.

---

## Final Output Mapping

Recommended extracted feature mapping:

- If Prompt 3 succeeds, set **Healthcare Classification** = `template_name`
- If Prompt 1 or Prompt 2 returns `Other`, set **Healthcare Classification** = `Other`

Optional audit fields you may also store:

- `domain_name`
- `domain_match_percentage`
- `domain_confidence_percentage`
- `domain_reasoning`
- `template_library`
- `template_library_match_percentage`
- `template_library_confidence_percentage`
- `template_library_reasoning`
- `template_name`
- `template_match_percentage`
- `template_confidence_percentage`
- `template_reasoning`

---

## Implementation Notes

- Treat `Family` as **Template Library** in the prompts and downstream output.
- Deduplicate candidate lists before passing them to the model.
- Pass clean OCR text for a single page at a time.
- If page images are available, the same prompts can be used with multimodal models by attaching the page image in addition to OCR text.
- For best consistency, use low temperature and enforce JSON response parsing.
