# Medical Document AI Prompts

This directory contains production-ready system prompts for medical document analysis using Claude AI.

## Prompt Files

### classification.md
**Purpose:** Classifies medical documents into exactly one of 5 types  
**Output:** JSON with `document_type`, `confidence`, `rationale`, and `evidence` array  
**Types:**
- COMPLETE BLOOD COUNT (CBC)
- BASIC METABOLIC PANEL (BMP)
- X-RAY
- CT (Computed Tomography)
- CLINICAL NOTE

### codes.md
**Purpose:** Extracts ICD-10 diagnostic codes from medical documents  
**Output:** JSON with `codes` array containing code, description, confidence, and evidence  
**Policy:** No hallucinations - only codes explicitly supported by document evidence

### summary.md
**Purpose:** Generates provider-facing clinical summaries  
**Output:** JSON with `summary`, `confidence`, and `evidence` array  
**Tone:** Clinical, professional, provider-focused

## JSON Contracts

All prompts enforce strict JSON-only responses with the following structure:

```json
// Classification
{
  "document_type": "COMPLETE BLOOD COUNT",
  "confidence": 0.95,
  "rationale": "Brief justification",
  "evidence": ["exact quote 1", "exact quote 2"]
}

// Codes
{
  "codes": [
    {
      "code": "D64.9",
      "description": "Anemia, unspecified",
      "confidence": 0.85,
      "evidence": ["supporting text from document"]
    }
  ]
}

// Summary
{
  "summary": "3-6 sentences of clinical summary",
  "confidence": 0.90,
  "evidence": ["key finding 1", "key finding 2"]
}
```

## Confidence & Evidence Policy

**Confidence Scores:**
- ≥0.8: High confidence - well-supported by clear evidence
- 0.5-0.79: Medium confidence - some supporting evidence, may need review
- <0.5: Low confidence - uncertain, flag for manual review

**Evidence Requirements:**
- Must be exact quotes from source document
- Include line/section references when possible
- Multiple evidence points increase confidence
- No paraphrasing or interpretation in evidence quotes

## Adding Few-Shot Examples

To improve prompt performance, add 1-3 few-shot examples directly in the prompt file:

```markdown
## Examples

Example 1:
Document: "COMPLETE BLOOD COUNT\nWBC 12.5 K/uL (H)..."
Expected Output: {"document_type": "COMPLETE BLOOD COUNT", ...}

Example 2:
Document: "BASIC METABOLIC PANEL\nSodium 138 mEq/L..."
Expected Output: {"document_type": "BASIC METABOLIC PANEL", ...}
```

## Using Prompt Improver

When prompt performance degrades or new edge cases emerge:

1. Collect failed examples with ground truth
2. Use Claude's Prompt Improver tool or manual iteration
3. Test with evaluation dataset (see /evals)
4. Update prompt files with improvements
5. Document changes in git commit messages

## ICD-10 Definition

**ICD-10** (International Classification of Diseases, 10th Revision) is a standardized diagnostic coding system maintained by the World Health Organization (WHO). It provides alphanumeric codes for diseases, symptoms, abnormal findings, and external causes of injury.

**Format:** Code ranges from A00-Z99 (e.g., D64.9, E87.5, I51.7)  
**Usage:** Medical billing, epidemiology, health statistics, clinical documentation

**Important:** Only extract codes when diagnosis is explicitly supported by document evidence. Avoid speculative coding based on symptoms alone.

## Advanced Features

### Prompt Caching (Anthropic)
- Cache long system prompts to reduce latency and cost
- Enabled via `cache_control` parameter in API calls
- Useful for prompts >1024 tokens that are reused frequently

### Extended Thinking (Claude)
- Enable for complex cases requiring multi-step reasoning
- Useful for ambiguous documents or edge cases
- May increase latency but improves accuracy

See `app/services/anthropic_client.py` for implementation details.
