# Medical Doc AI - Evaluation Dataset

This folder contains evaluation datasets and tools for testing the Medical Doc AI system.

## Dataset Structure

### test-documents.json

A seed dataset with 5 test cases covering each of the 5 document types:

1. **CBC (Complete Blood Count)** - Lab report with blood cell counts
2. **BMP (Basic Metabolic Panel)** - Lab report with electrolytes and kidney function
3. **X-Ray** - Radiographic imaging report
4. **CT** - Computed tomography imaging report
5. **Clinical Note** - Provider progress note

Each case includes:
- `id`: Unique identifier
- `document_text`: Full document text
- `ground_truth`: Expected classification type, ICD-10 codes, and key findings

## Quick Smoke Tests

### Test Classification Endpoint

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "document_text": "COMPLETE BLOOD COUNT\nWBC 12.5 K/uL (H)\nHemoglobin 9.2 g/dL (L)\nPlatelets 245 K/uL"
  }'
```

Expected: `document_type: "COMPLETE BLOOD COUNT"` with high confidence

### Test Code Extraction

```bash
curl -X POST http://localhost:8000/extract-codes \
  -H "Content-Type: application/json" \
  -d '{
    "document_text": "Hemoglobin 9.2 g/dL - consistent with anemia",
    "document_type": "COMPLETE BLOOD COUNT"
  }'
```

Expected: ICD-10 code D64.9 (Anemia, unspecified)

### Test Summary Generation

```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "document_text": "Potassium 6.1 mEq/L (H) - Hyperkalemia requiring urgent treatment",
    "document_type": "BASIC METABOLIC PANEL"
  }'
```

Expected: Clinical summary mentioning hyperkalemia and urgent intervention

### Test Full Pipeline

```bash
curl -X POST http://localhost:8000/documents \
  -F "file=@test-cbc.pdf" \
  -F "run_pipeline=true"
```

Expected: Complete results with classification, codes, and summary

## Running Systematic Evaluations

### Manual Testing

1. Start the backend server
2. Use the test cases from `test-documents.json`
3. Compare results against ground truth
4. Document any discrepancies

### Future: Automated Evaluation

This directory is set up to integrate with Claude Eval Tool for systematic prompt evaluation:

1. Convert test cases to Claude Eval format
2. Run evaluations across prompt iterations
3. Track performance metrics (accuracy, precision, recall)
4. Store results in `results/` directory

### Adding New Test Cases

When you encounter edge cases or failure modes:

1. Document the case in `test-documents.json`
2. Include ground truth expectations
3. Note any special considerations
4. Run tests to verify fixes
5. Update prompts in `backend-fastapi/app/services/prompts/` as needed

## Performance Metrics to Track

- **Classification Accuracy:** % of documents correctly classified
- **Code Precision:** % of extracted codes that are correct
- **Code Recall:** % of correct codes that were extracted
- **Summary Quality:** Subjective assessment of clinical utility

## Known Limitations

Current stub mode limitations:
- Simple keyword matching for classification
- Limited code extraction patterns
- Generic summaries for edge cases

These will improve when using real Claude API (`USE_CLAUDE_REAL=true`)

## Expanding the Dataset

To create a comprehensive evaluation set:

1. Collect diverse real-world examples (de-identified)
2. Include edge cases: ambiguous documents, multi-type docs, poor quality scans
3. Cover rare document types and unusual presentations
4. Test with different medical specialties
5. Validate with healthcare providers

## Integration with Claude Eval Tool

Future enhancement: Use Anthropic's evaluation tools for:
- Systematic prompt testing
- A/B testing prompt variations
- Performance regression detection
- Automated quality monitoring

See [Claude Eval Documentation](https://docs.anthropic.com/) for setup instructions.
