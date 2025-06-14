# Frontend Integration Guide: Key API Endpoints

This document provides detailed information about the two primary API endpoints that the frontend needs to consume for the GRC Assistant application. These endpoints are core to the application's functionality and handle policy evaluation and use case processing.

## Base URL
```
http://localhost:8000
```



## 1. Policy Evaluation Endpoint

The Policy Evaluation endpoint analyzes organizational policies against regulatory standards, identifies compliance gaps, assesses alignment with standards, and provides enhancement recommendations.

### Request Endpoint
**POST** `/policies/evaluate`

### Request Parameters

```json
{
  "policy_content": "Full text content of the policy to evaluate",
  "standards": ["ISO 27001", "GDPR", "PCI-DSS"],  // Optional - specific standards to check against
  "chunk_size": 1000  // Optional - size of text chunks for processing
}
```

### Response Structure

```json
{
  "results": [
    {
      "chunk_content": "Original policy text segment",
      "gap_analysis": {
        "classification": "MISSING | PARTIAL | COMPLIANT",
        "gaps": [
          "Policy does not specify the types of information system accounts to be used (AC-2a).",
          "Policy does not require the assignment of account managers (AC-2b)."
          // Additional gaps identified
        ],
        "rationale": "Detailed explanation of the gap analysis results",
        "references": [
          "NIST SP 800-53 AC-2a",
          "NIST SP 800-53 AC-2b"
          // Additional reference identifiers
        ]
      },
      "compliance_assessment": {
        "classification": "MISSING | PARTIAL | COMPLIANT",
        "issues": [
          "The policy does not identify and select types of information system accounts (AC-2 a).",
          // Additional compliance issues
        ],
        "rationale": "Detailed explanation of compliance assessment",
        "references": [
          "NIST SP 800-53 AC-2 a",
          // Additional reference identifiers
        ]
      },
      "enhancement": {
        "classification": "MISSING | PARTIAL | COMPLIANT",
        "enhanced_version": "Enhanced policy text that addresses identified gaps",
        "changes": [
          "Added section 1 to require identification and selection of information system account types (AC-2 a).",
          // Additional changes made
        ],
        "rationale": "Explanation of why the enhancements address the gaps"
      }
    }
    // Additional policy chunks with their respective analyses
  ],
  "summary": {
    "total_chunks": 5,
    "compliant_chunks": 1,
    "partial_chunks": 2,
    "missing_chunks": 2,
    "overall_compliance_score": 45,
    "top_gaps": [
      "Account Management (AC-2)",
      "Access Enforcement (AC-3)"
      // Most common gaps identified
    ]
  },
  "processed_at": "2025-06-14T10:30:00Z"
}
```

### Usage Notes

- The policy evaluation process splits the policy into manageable chunks for analysis
- Each chunk is evaluated independently against relevant standards
- The response includes the original chunk text, gap analysis, compliance assessment, and enhancement suggestions
- For each evaluation, the classification can be 'MISSING', 'PARTIAL', or 'COMPLIANT'
- References link directly to the specific control or requirement in the standard

### Frontend Implementation Tips

1. **Progress Indication**: This endpoint may take time to process large policies. Implement a progress indicator.
2. **Chunk Navigation**: Create an easy way to navigate between different policy chunks.
3. **Highlighting**: Highlight gaps directly in the policy text.
4. **Side-by-Side View**: Show the original and enhanced policy versions side by side.
5. **Filtering**: Allow filtering by compliance classification and standard references.
6. **Export Options**: Provide PDF and Word export options for the evaluation results.

---

## 2. Use Case Processor Endpoint

The Use Case Processor endpoint evaluates security use cases against organizational policies and industry standards, providing comprehensive analysis of effectiveness, deployment feasibility, and alignment with security requirements.

### Request Endpoint
**POST** `/use-cases/process`

### Request Parameters

```json
{
  "use_case_content": "Full text content of the security use case to evaluate",
  "standards": ["ISO 27001", "GDPR", "PCI-DSS"],  // Optional - specific standards to evaluate against
  "policies": ["Access Control Policy", "Information Security Policy"]  // Optional - specific policies to evaluate against
}
```

### Response Structure

```json
{
  "use_case_content": "Original security use case text",
  "kpi_analysis": {
    "kpi_scores": {
      "vulnerability_management": 10,
      "mttd_estimate": 70,
      "mttr_estimate": 60,
      "security_coverage_score": 80,
      "risk_reduction_percentage": 90,
      "compliance_coverage_percentage": 95,
      "security_control_implementation_score": 90,
      "security_testing_coverage": 30,
      "security_training_effectiveness": 85,
      "incident_response_readiness": 50
    },
    "analysis": {
      "vulnerability_management": "Detailed analysis of vulnerability management aspects",
      "mttd_estimate": "Analysis of mean time to detect",
      // Analysis for each KPI
    },
    "overall_score": 66.0,
    "recommendations": [
      "Implement dedicated security testing for the solution",
      // Additional recommendations
    ]
  },
  "deployment_analysis": {
    "feasibility_score": 85.0,
    "pros": [
      "Significantly enhances the organization's security posture",
      // Additional pros
    ],
    "cons": [
      "Potential for user friction and resistance during adoption",
      // Additional cons
    ],
    "timeline_estimate": "6-8 months",
    "resource_requirements": [
      "Identity management team (2 FTE)",
      // Additional resource requirements
    ],
    "risk_factors": [
      {
        "risk": "User resistance and low adoption rate",
        "severity": "High",
        "mitigation": "Comprehensive user training, clear communication on benefits"
      },
      // Additional risk factors
    ]
  },
  "use_case_judgment": {
    "effectiveness_score": 80.0,
    "alignment_with_standards": [
      {
        "standard": "PCI DSS Requirement 8.2.1",
        "alignment_score": 85,
        "comments": "Analysis of alignment with this standard"
      },
      // Additional standard alignments
    ],
    "alignment_with_policies": [
      {
        "policy": "Corporate Authentication Policy",
        "alignment_score": 85,
        "comments": "Analysis of alignment with this policy"
      },
      // Additional policy alignments
    ],
    "security_impact": "High positive impact. Implementing multi-factor authentication significantly reduces risks...",
    "gaps_identified": [
      "Lack of specific definition for 'critical systems' and 'sensitive operations'",
      // Additional gaps
    ],
    "improvement_suggestions": [
      "Define and list the 'critical systems' and 'sensitive operations' within the scope",
      // Additional improvement suggestions
    ]
  },
  "aggregated_analysis": {
    "overall_assessment": "Overall assessment summary of the use case",
    "overall_score": 82.5,
    "key_findings": [
      "Implementing MFA is a fundamental security control with high potential",
      // Additional key findings
    ],
    "critical_considerations": [
      "User adoption and managing potential friction are high-severity risks",
      // Additional considerations
    ],
    "recommended_next_steps": [
      "Develop detailed plans for user enrollment, onboarding",
      // Additional next steps
    ],
    "stakeholder_considerations": {
      "executive_management": [
        "Understand the high positive security impact and risk reduction potential",
        // Additional considerations for executives
      ],
      "security_team": [
        "Focus on detailed planning for security testing",
        // Additional considerations for security team
      ],
      "operations_team": [
        "Plan for increased load on Help Desk",
        // Additional considerations for operations
      ],
      "compliance": [
        "Verify explicit alignment with specific PCI-DSS requirements",
        // Additional considerations for compliance team
      ]
    }
  },
  "processed_at": "2025-06-14T10:30:00Z"
}
```

### Usage Notes

- The use case is analyzed across multiple dimensions: KPIs, deployment feasibility, security effectiveness, and compliance
- The response includes detailed scores, analysis text, and recommendations for each dimension
- The aggregated analysis provides an executive summary with key findings and next steps
- Stakeholder considerations are included to help different teams understand implications

### Frontend Implementation Tips

1. **Interactive Dashboard**: Create a visual dashboard with key scores and metrics from the analysis
2. **Tabbed Interface**: Organize the detailed analyses into tabs for better navigation
3. **Radar/Spider Charts**: Visualize the KPI scores and other metrics using radar charts
4. **Expandable Sections**: Allow users to expand/collapse detailed analysis sections
5. **Risk Matrix**: Create a visual matrix for displaying risk factors by severity
6. **Stakeholder Views**: Provide filtered views specialized for different stakeholders
7. **PDF Report Generation**: Include one-click generation of comprehensive PDF reports
8. **Comparison Feature**: Allow comparison of multiple use case evaluations side by side

---

## Error Handling

Both endpoints may return the following error responses:

```json
{
  "error": "Bad Request",
  "message": "Invalid request parameters",
  "details": {
    "field": "use_case_content",
    "issue": "Required field missing"
  }
}
```

```json
{
  "error": "Processing Error",
  "message": "The analysis could not be completed",
  "details": {
    "reason": "Content too large",
    "suggestion": "Try splitting the content into smaller segments"
  }
}
```

## Technical Implementation Notes

1. **Batch Processing**: For organizations with many policies or use cases, consider implementing batch processing options
2. **Caching Strategy**: Implement appropriate caching for frequently accessed evaluation results
3. **Versioning**: Store and track versions of evaluations to allow historical comparison
4. **Export Formats**: Support JSON, PDF, DOCX, and CSV export formats for integration with other tools
5. **Feedback Loop**: Include mechanisms for users to provide feedback on evaluation accuracy

