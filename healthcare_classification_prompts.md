# Healthcare Document Classification Prompts for Docs Ontology

This file provides a ready-to-use three-step prompt set for healthcare document classification based on the Docs Ontology configuration.

## Purpose

Classify a single healthcare document page using the ontology fields supplied in configuration.

The prompt flow uses this operational hierarchy:

1. **Group**
2. **SubGroup**
3. **Exact ontology row**

The final row is selected from the filtered candidate rows and includes:

- `Group`
- `SubGroup`
- `Speciality`
- `DocumentType`
- `In-Out`
- `BodyPart`
- `SNOMEDCT`
- `LOINCID`
- `Source`

This approach keeps the workflow at three prompts while still supporting the richer ontology you provided.

## Expected Configuration Input

The source Excel file should contain these columns:

- `Group`
- `SubGroup`
- `Speciality`
- `DocumentType`
- `In-Out`
- `BodyPart`
- `SNOMEDCT`
- `LOINCID`
- `Source`

### Recommended Preprocessing

Before sending ontology rows to the model:

1. Add a stable unique identifier for each row, such as `row_id`.
2. Preserve blank values as empty strings rather than dropping columns.
3. Deduplicate exact duplicate rows if they exist.
4. Normalize whitespace only; do not rename values.

## Recommended Orchestration Rules

1. Load the ontology Excel file into memory.
2. Assign a stable `row_id` to each ontology row.
3. Run **Prompt 1** with all unique `Group` values plus `Other`.
4. If Prompt 1 returns `Other`, stop.
5. Run **Prompt 2** with all unique `SubGroup` values for the selected `Group` plus `Other`.
6. If Prompt 2 returns `Other`, stop.
7. Filter ontology rows to the selected `Group` and `SubGroup`.
8. Run **Prompt 3** using the filtered ontology rows.
9. Set **Healthcare Classification** to the final selected ontology row.

## Shared System Prompt

Use this same system prompt for all three steps.

```text
You are a healthcare document classification engine.

Your job is to classify a single document page using only the predefined Docs Ontology values provided in the prompt input.

Rules:
1. Use only the supplied candidate values and ontology rows. Do not invent labels, aliases, or normalized replacements.
2. Evaluate the page exactly as provided.
3. Base decisions on explicit evidence from the page such as titles, headers, specialty names, form labels, report sections, procedure names, ordering language, imaging modality names, note types, and payer or legal wording.
4. When choosing among similar candidates, prefer the option best supported by explicit evidence on the page.
5. If the evidence is weak, ambiguous, conflicting, or does not reasonably fit any candidate at Prompt 1 or Prompt 2, choose "Other".
6. Match Percentage is how strongly the page aligns to the selected candidate among the options shown.
7. Confidence Percentage is how certain you are based on the visible page evidence.
8. Percentages must be integers from 0 to 100.
9. Reasoning must be concise, factual, and grounded in page evidence.
10. Return valid JSON only. Do not include markdown, commentary, or code fences.
11. Preserve exact spelling, capitalization, punctuation, and spacing from the provided candidate values.
12. Blank ontology fields are meaningful and should not be filled in unless they are explicitly present in the selected candidate row.
```

---

## Prompt 1: Group Classification

### User Prompt Template

```text
Classify the following healthcare document page into the best matching Group from the Docs Ontology.

Candidate Group values:
{{GROUP_OPTIONS_WITH_OTHER}}

Document page content:
{{DOCUMENT_PAGE_TEXT}}

Return JSON in exactly this format:
{
  "group": "<selected group or Other>",
  "match_percentage": <integer 0-100>,
  "confidence_percentage": <integer 0-100>,
  "reasoning": "<concise evidence-based explanation>"
}

Selection guidance:
- Compare the page against all provided Group values.
- Choose the single best Group.
- If no Group is a reasonable fit, return "Other".
- Do not return any fields other than the four fields above.
```

### Expected Output Example

```json
{
  "group": "Clinical Notes",
  "match_percentage": 90,
  "confidence_percentage": 87,
  "reasoning": "The page is a narrative clinician-authored note with history, assessment, and plan content rather than an order, imaging study, consent, or financial document."
}
```

---

## Prompt 2: SubGroup Classification

Run this prompt only when Prompt 1 does **not** return `Other`.

### User Prompt Template

```text
Classify the following healthcare document page into the best matching SubGroup within the selected Group.

Selected Group:
{{SELECTED_GROUP}}

Candidate SubGroup values:
{{SUBGROUP_OPTIONS_WITH_OTHER}}

Document page content:
{{DOCUMENT_PAGE_TEXT}}

Return JSON in exactly this format:
{
  "subgroup": "<selected subgroup or Other>",
  "match_percentage": <integer 0-100>,
  "confidence_percentage": <integer 0-100>,
  "reasoning": "<concise evidence-based explanation>"
}

Selection guidance:
- Evaluate only the SubGroup values provided for the selected Group.
- Choose the single best SubGroup.
- If none is a reasonable fit, return "Other".
- Do not return any fields other than the four fields above.
```

### Expected Output Example

```json
{
  "subgroup": "Progress Note",
  "match_percentage": 92,
  "confidence_percentage": 90,
  "reasoning": "The page contains a dated follow-up clinical narrative with interval status, assessment, and plan, which is most consistent with a progress note."
}
```

---

## Prompt 3: Exact Ontology Row Classification

Run this prompt only when Prompt 2 does **not** return `Other`.

### Prompt Intent

This step selects the exact ontology row, not just a `DocumentType` label. This is important because the same or similar document types may differ by `Speciality`, `In-Out`, `BodyPart`, or coding metadata.

### User Prompt Template

```text
Classify the following healthcare document page to the single best matching Docs Ontology row within the selected Group and SubGroup.

Selected Group:
{{SELECTED_GROUP}}

Selected SubGroup:
{{SELECTED_SUBGROUP}}

Candidate ontology rows:
{{FILTERED_ONTOLOGY_ROWS_WITH_ROW_ID}}

Document page content:
{{DOCUMENT_PAGE_TEXT}}

Return JSON in exactly this format:
{
  "row_id": "<selected row id>",
  "group": "<selected Group>",
  "subgroup": "<selected SubGroup>",
  "speciality": "<selected Speciality>",
  "document_type": "<selected DocumentType>",
  "in_out": "<selected In-Out>",
  "body_part": "<selected BodyPart>",
  "snomed_ct": "<selected SNOMEDCT>",
  "loinc_id": "<selected LOINCID>",
  "source": "<selected Source>",
  "match_percentage": <integer 0-100>,
  "confidence_percentage": <integer 0-100>,
  "reasoning": "<concise evidence-based explanation>"
}

Selection guidance:
- Choose exactly one ontology row from the candidate list.
- Match all returned field values exactly to the selected candidate row.
- Use Speciality, In-Out, BodyPart, SNOMEDCT, LOINCID, and Source as tie-breakers when the DocumentType names are similar.
- Prefer rows with explicit evidence in the page, such as specialty names, inpatient or outpatient context, modality names, note headers, procedure names, anatomical references, or coding cues.
- Do not invent missing values.
- Do not return any fields other than the thirteen fields above.
```

### Expected Output Example

```json
{
  "row_id": "R0108",
  "group": "Clinical Notes",
  "subgroup": "Progress Note",
  "speciality": "Family practice",
  "document_type": "Progress note",
  "in_out": "",
  "body_part": "",
  "snomed_ct": "419772000",
  "loinc_id": "11506-3",
  "source": "LOINC",
  "match_percentage": 94,
  "confidence_percentage": 91,
  "reasoning": "The page is a general follow-up clinical progress note and does not show a narrower specialty, modality, or inpatient/outpatient qualifier that would support a more specific progress-note row."
}
```

---

## Stop Logic

Use the following control logic outside the prompt.

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

- `Healthcare Classification` = `Group > SubGroup > Speciality > DocumentType`

If you prefer a shorter display value, use:

- `Healthcare Classification` = `DocumentType`

Recommended structured fields to store:

- `group`
- `subgroup`
- `speciality`
- `document_type`
- `in_out`
- `body_part`
- `snomed_ct`
- `loinc_id`
- `source`
- `row_id`
- `group_match_percentage`
- `group_confidence_percentage`
- `group_reasoning`
- `subgroup_match_percentage`
- `subgroup_confidence_percentage`
- `subgroup_reasoning`
- `final_match_percentage`
- `final_confidence_percentage`
- `final_reasoning`

---

## Suggested Candidate Row Format for Prompt 3

Pass filtered rows in a compact but explicit format like this:

```text
[
  {
    "row_id": "R0108",
    "Group": "Clinical Notes",
    "SubGroup": "Progress Note",
    "Speciality": "Family practice",
    "DocumentType": "Progress note",
    "In-Out": "",
    "BodyPart": "",
    "SNOMEDCT": "419772000",
    "LOINCID": "11506-3",
    "Source": "LOINC"
  },
  {
    "row_id": "R0109",
    "Group": "Clinical Notes",
    "SubGroup": "Progress Note",
    "Speciality": "Family practice",
    "DocumentType": "Attending Hospital Progress note",
    "In-Out": "Hospital",
    "BodyPart": "",
    "SNOMEDCT": "419772000",
    "LOINCID": "100550-3",
    "Source": "LOINC"
  }
]
```

---

## Implementation Notes

- Use `Group` and `SubGroup` as the first two prompt levels.
- Use the final prompt to pick the exact ontology row rather than only `DocumentType`.
- `Speciality` is not a separate prompt level; it is part of the row-level decision at Prompt 3.
- Blank values in `In-Out`, `BodyPart`, `SNOMEDCT`, or `LOINCID` are valid and should remain blank if the selected row is blank.
- Pass a single page of OCR text at a time.
- If page images are available, use the same prompts with a multimodal model and include the page image as additional input.
- For best consistency, use low temperature and enforce strict JSON schema parsing.
