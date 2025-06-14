# Fast vs Deep Analysis in Policy Evaluation API

## Overview

The Policy Evaluation API provides two modes of analysis for security policies:

1. **Deep Analysis** - A comprehensive evaluation that examines every aspect of policy compliance
2. **Fast Analysis** - An optimized approach that provides quick insights for initial assessment

This document outlines the key differences between these two modes, their use cases, and implementation details.

## Key Differences

| Feature | Deep Analysis | Fast Analysis |
|---------|--------------|---------------|
| **Processing Coverage** | Processes every chunk of the policy | Samples representative chunks (first, middle, last, plus random samples) |
| **Chunk Size** | 1,000 characters | 2,000 characters (2x larger) |
| **Evaluation Steps** | Gap analysis + Compliance checking + Policy enhancement | Gap analysis only |
| **Execution Time** | Longer (complete analysis) | Significantly faster (30-70% reduction) |
| **Result Completeness** | Complete with enhancement suggestions | Critical gaps only |
| **API Endpoints** | `/api/v1/evaluate-policy` with `speed="deep"` | `/api/v1/fast-analyze` or `/api/v1/evaluate-policy` with `speed="fast"` |

## Technical Implementation

### Fast Analysis Optimizations

The fast analysis mode incorporates several optimizations:

1. **Larger Chunk Sizes**
   - Deep: Uses 1,000-character chunks
   - Fast: Uses 2,000-character chunks, reducing the number of processing units by half

2. **Chunk Sampling**
   - Deep: Processes all policy chunks
   - Fast: Intelligently samples representative chunks:
     - Always includes the first and last chunks
     - Includes the middle chunk
     - Adds up to 2 random samples from the remaining chunks
     - If policy has ≤ 5 chunks, processes all chunks

3. **Focused Processing**
   - Deep: Performs gap analysis, compliance checking, and policy enhancement
   - Fast: Performs only gap analysis (most critical aspect)

4. **Result Structure**
   - Both modes return a structured format, but fast analysis includes a `speed="fast"` indicator
   - Fast analysis returns empty placeholders for compliance and enhancement data when using the combined endpoint

## When to Use Each Mode

### Use Deep Analysis When:

- Performing thorough policy reviews
- Preparing for compliance audits
- Needing detailed enhancement suggestions
- Having sufficient time for comprehensive analysis
- Conducting final policy validation

### Use Fast Analysis When:

- Performing initial policy assessments
- Needing quick feedback on critical gaps
- Working with very large policy documents
- Conducting preliminary reviews before deeper analysis
- Time constraints require prioritizing speed over completeness

## Performance Implications

The fast analysis mode can provide significant performance improvements:

- Processing time reduction of 30-70% depending on document size
- Resource utilization reduction
- API response time improvement

This is achieved through:
- Reducing the number of chunks by sampling (most significant factor)
- Processing fewer chunks due to larger chunk sizes
- Eliminating compliance checking and enhancement generation steps

## API Usage

### Deep Analysis

```http
POST /api/v1/evaluate-policy
Content-Type: application/json

{
  "policy": "Full policy text...",
  "standards": ["Standard 1...", "Standard 2..."],
  "speed": "deep"
}
```

### Fast Analysis

```http
POST /api/v1/fast-analyze
Content-Type: application/json

{
  "policy": "Full policy text...",
  "standards": ["Standard 1...", "Standard 2..."]
}
```

Or using the combined endpoint:

```http
POST /api/v1/evaluate-policy
Content-Type: application/json

{
  "policy": "Full policy text...",
  "standards": ["Standard 1...", "Standard 2..."],
  "speed": "fast"
}
```

## Conclusion

The dual-mode approach provides flexibility in policy evaluation, allowing users to balance thoroughness and speed according to their needs. The fast analysis mode is particularly valuable for initial assessments or when dealing with large policy documents where quick insights are prioritized over comprehensive analysis.

For critical compliance requirements or final policy validation, the deep analysis mode provides the comprehensive evaluation needed to ensure complete policy alignment with standards.
