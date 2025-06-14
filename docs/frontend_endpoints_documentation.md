# Frontend Integration Guide: Key API Endpoints

This document provides detailed information about the API endpoints that the frontend needs to consume for the GRC Assistant application. These endpoints handle policy evaluation and use case processing with support for both text input and file uploads (DOCX and PDF).

## Base URL
```
http://localhost:8000
```

## New Features in API v2.0

### 🆕 File Upload Support
- **DOCX files**: Full text extraction from Word documents including tables
- **PDF files**: Text extraction from PDF documents
- **File validation**: Automatic file size and type validation
- **Error handling**: Comprehensive error messages for unsupported formats

### 🆕 Improved Response Structure
- **Summary statistics**: Overall compliance scores and key findings
- **Timestamp tracking**: Processing timestamps for audit trails
- **Enhanced error responses**: Detailed error information with suggestions

### 🆕 Backward Compatibility
- Legacy endpoints (`/api/v1/*`) are maintained for existing integrations
- New simplified endpoints (`/policies/*`, `/use-cases/*`) for better organization



## 1. Policy Evaluation Endpoints

The Policy Evaluation endpoints analyze organizational policies against regulatory standards, identify compliance gaps, assess alignment with standards, and provide enhancement recommendations. Each endpoint supports both text input and file upload (DOCX/PDF).

### 1.1 Comprehensive Policy Evaluation

#### Text Input Endpoint
**POST** `/policies/evaluate`

#### File Upload Endpoint
**POST** `/policies/evaluate/upload`

### Request Parameters (Text Input)

```json
{
  "policy_content": "Full text content of the policy to evaluate",
  "standards": ["ISO 27001", "GDPR", "PCI-DSS"],  // Optional - defaults to ["ISO 27001", "NIST", "GDPR"]
  "chunk_size": 1000,  // Optional - size of text chunks for processing
  "speed": "deep"  // Optional - "deep" (default) or "fast"
}
```

### Request Parameters (File Upload)

```javascript
// Form data for file upload
const formData = new FormData();
formData.append('file', policyFile);  // DOCX or PDF file
formData.append('standards', JSON.stringify(["ISO 27001", "GDPR"]));  // Optional
formData.append('chunk_size', '1000');  // Optional
formData.append('speed', 'deep');  // Optional
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
        ],
        "rationale": "Detailed explanation of the gap analysis results",
        "references": [
          "NIST SP 800-53 AC-2a",
          "NIST SP 800-53 AC-2b"
        ]
      },
      "compliance_assessment": {
        "classification": "MISSING | PARTIAL | COMPLIANT",
        "issues": [
          "The policy does not identify and select types of information system accounts (AC-2 a)."
        ],
        "rationale": "Detailed explanation of compliance assessment",
        "references": [
          "NIST SP 800-53 AC-2 a"
        ]
      },
      "enhancement": {
        "classification": "MISSING | PARTIAL | COMPLIANT",
        "enhanced_version": "Enhanced policy text that addresses identified gaps",
        "changes": [
          "Added section 1 to require identification and selection of information system account types (AC-2 a)."
        ],
        "rationale": "Explanation of why the enhancements address the gaps"
      }
    }
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
    ]
  },
  "processed_at": "2025-06-14T10:30:00Z"
}
```

### 1.2 Individual Analysis Endpoints

#### Gap Analysis
- **Text**: `POST /policies/gaps`
- **File Upload**: `POST /policies/gaps/upload`

#### Compliance Assessment
- **Text**: `POST /policies/compliance`
- **File Upload**: `POST /policies/compliance/upload`

#### Policy Enhancement
- **Text**: `POST /policies/enhance`
- **File Upload**: `POST /policies/enhance/upload`

#### Fast Analysis
- **Text**: `POST /policies/analyze/fast`
- **File Upload**: `POST /policies/analyze/fast/upload`

### File Upload Implementation Example

```javascript
// React/JavaScript example for file upload
const uploadPolicyFile = async (file, options = {}) => {
  const formData = new FormData();
  formData.append('file', file);
  
  // Optional parameters
  if (options.standards) {
    formData.append('standards', JSON.stringify(options.standards));
  }
  if (options.chunk_size) {
    formData.append('chunk_size', options.chunk_size.toString());
  }
  if (options.speed) {
    formData.append('speed', options.speed);
  }
  
  try {
    const response = await fetch('/policies/evaluate/upload', {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error uploading policy file:', error);
    throw error;
  }
};
```

---

## 2. Use Case Processor Endpoints

The Use Case Processor endpoints evaluate security use cases against organizational policies and industry standards, providing comprehensive analysis of effectiveness, deployment feasibility, and alignment with security requirements. Each endpoint supports both text input and file upload (DOCX/PDF).

### 2.1 Complete Use Case Processing

#### Text Input Endpoint
**POST** `/use-cases/process`

#### File Upload Endpoint
**POST** `/use-cases/process/upload`

### Request Parameters (Text Input)

```json
{
  "use_case_content": "Full text content of the security use case to evaluate",
  "standards": ["ISO 27001", "GDPR", "PCI-DSS"],  // Optional - defaults to ["ISO 27001", "NIST", "GDPR"]
  "policies": ["Access Control Policy", "Information Security Policy"]  // Optional - specific policies to evaluate against
}
```

### Request Parameters (File Upload)

```javascript
// Form data for file upload
const formData = new FormData();
formData.append('file', useCaseFile);  // DOCX or PDF file
formData.append('standards', JSON.stringify(["ISO 27001", "GDPR"]));  // Optional
formData.append('policies', JSON.stringify(["Access Control Policy"]));  // Optional
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
      "mttd_estimate": "Analysis of mean time to detect"
    },
    "overall_score": 66.0,
    "recommendations": [
      "Implement dedicated security testing for the solution"
    ]
  },
  "deployment_analysis": {
    "feasibility_score": 85.0,
    "pros": [
      "Significantly enhances the organization's security posture"
    ],
    "cons": [
      "Potential for user friction and resistance during adoption"
    ],
    "timeline_estimate": "6-8 months",
    "resource_requirements": [
      "Identity management team (2 FTE)"
    ],
    "risk_factors": [
      {
        "risk": "User resistance and low adoption rate",
        "severity": "High",
        "mitigation": "Comprehensive user training, clear communication on benefits"
      }
    ]
  },
  "use_case_judgment": {
    "effectiveness_score": 80.0,
    "alignment_with_standards": [
      {
        "standard": "PCI DSS Requirement 8.2.1",
        "alignment_score": 85,
        "comments": "Analysis of alignment with this standard"
      }
    ],
    "alignment_with_policies": [
      {
        "policy": "Corporate Authentication Policy",
        "alignment_score": 85,
        "comments": "Analysis of alignment with this policy"
      }
    ],
    "security_impact": "High positive impact. Implementing multi-factor authentication significantly reduces risks...",
    "gaps_identified": [
      "Lack of specific definition for 'critical systems' and 'sensitive operations'"
    ],
    "improvement_suggestions": [
      "Define and list the 'critical systems' and 'sensitive operations' within the scope"
    ]
  },
  "aggregated_analysis": {
    "overall_assessment": "Overall assessment summary of the use case",
    "overall_score": 82.5,
    "key_findings": [
      "Implementing MFA is a fundamental security control with high potential"
    ],
    "critical_considerations": [
      "User adoption and managing potential friction are high-severity risks"
    ],
    "recommended_next_steps": [
      "Develop detailed plans for user enrollment, onboarding"
    ],
    "stakeholder_considerations": {
      "executive_management": [
        "Understand the high positive security impact and risk reduction potential"
      ],
      "security_team": [
        "Focus on detailed planning for security testing"
      ],
      "operations_team": [
        "Plan for increased load on Help Desk"
      ],
      "compliance": [
        "Verify explicit alignment with specific PCI-DSS requirements"
      ]
    }
  },
  "processed_at": "2025-06-14T10:30:00Z"
}
```

### 2.2 Individual Analysis Endpoints

#### KPI Analysis
- **Text**: `POST /use-cases/kpis`
- **File Upload**: `POST /use-cases/kpis/upload`

#### Deployment Analysis
- **Text**: `POST /use-cases/deployment`
- **File Upload**: `POST /use-cases/deployment/upload`

#### Use Case Judgment
- **Text**: `POST /use-cases/judge`
- **File Upload**: `POST /use-cases/judge/upload`

### File Upload Implementation Example

```javascript
// React/JavaScript example for use case file upload
const uploadUseCaseFile = async (file, options = {}) => {
  const formData = new FormData();
  formData.append('file', file);
  
  // Optional parameters
  if (options.standards) {
    formData.append('standards', JSON.stringify(options.standards));
  }
  if (options.policies) {
    formData.append('policies', JSON.stringify(options.policies));
  }
  
  try {
    const response = await fetch('/use-cases/process/upload', {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error uploading use case file:', error);
    throw error;
  }
};
```

---

## 3. File Upload Features

### 3.1 Supported File Types
- **DOCX**: Microsoft Word documents with full text and table extraction
- **PDF**: Portable Document Format files with text extraction
- **Size Limit**: 10MB maximum file size (configurable)

### 3.2 File Validation
The API automatically validates uploaded files for:
- File size (max 10MB by default)
- File type (DOCX/PDF only)
- Content extraction (ensures file contains readable text)

### 3.3 File Upload Response Structure
All file upload endpoints return the same analysis results as their text counterparts, with no difference in response format.

### 3.4 Error Handling for File Uploads

```json
// File too large
{
  "error": "Request Entity Too Large",
  "message": "File size (15.2MB) exceeds maximum allowed size (10MB)",
  "details": {
    "field": "file",
    "max_size_mb": 10,
    "actual_size_mb": 15.2
  }
}

// Unsupported file type
{
  "error": "Bad Request",
  "message": "Unsupported file type: .txt. Supported types: .docx, .pdf",
  "details": {
    "field": "file",
    "supported_types": [".docx", ".pdf"]
  }
}

// No text content found
{
  "error": "Bad Request",
  "message": "No text content found in the uploaded file",
  "details": {
    "field": "file",
    "suggestion": "Ensure the file contains readable text content"
  }
}

// File processing error
{
  "error": "Processing Error",
  "message": "Error extracting text from PDF file: PDF may be corrupted",
  "details": {
    "field": "file",
    "file_type": "pdf",
    "suggestion": "Try uploading a different version of the file"
  }
}
```

---

## 4. Legacy API Endpoints (Backward Compatibility)

All previous API endpoints (`/api/v1/*`) remain functional for backward compatibility:

- `POST /api/v1/identify-gaps` → Use `POST /policies/gaps`
- `POST /api/v1/check-compliance` → Use `POST /policies/compliance`
- `POST /api/v1/enhance-policy` → Use `POST /policies/enhance`
- `POST /api/v1/evaluate-policy` → Use `POST /policies/evaluate`
- `POST /api/v1/fast-analyze` → Use `POST /policies/analyze/fast`
- `POST /api/v1/use-case/analyze-kpis` → Use `POST /use-cases/kpis`
- `POST /api/v1/use-case/analyze-deployment` → Use `POST /use-cases/deployment`
- `POST /api/v1/use-case/judge` → Use `POST /use-cases/judge`
- `POST /api/v1/use-case/process` → Use `POST /use-cases/process`

**Note**: Legacy endpoints only support text input, not file uploads.

---

## Error Handling

Both text and file upload endpoints may return the following error responses:

```json
{
  "error": "Bad Request",
  "message": "Invalid request parameters",
  "details": {
    "field": "policy_content",
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

## Frontend Implementation Guidelines

### 1. File Upload UI Components

```jsx
// React component example for file upload
import React, { useState } from 'react';

const PolicyUploader = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState(null);

  const handleFileUpload = async (event) => {
    const selectedFile = event.target.files[0];
    
    if (!selectedFile) return;
    
    // Validate file type
    const allowedTypes = ['.docx', '.pdf'];
    const fileExtension = selectedFile.name.substring(selectedFile.name.lastIndexOf('.')).toLowerCase();
    
    if (!allowedTypes.includes(fileExtension)) {
      alert('Please select a DOCX or PDF file');
      return;
    }
    
    // Validate file size (10MB limit)
    if (selectedFile.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB');
      return;
    }
    
    setFile(selectedFile);
    setUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('standards', JSON.stringify(['ISO 27001', 'GDPR']));
      
      const response = await fetch('/policies/evaluate/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Upload failed');
      }
      
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Upload error:', error);
      alert(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        accept=".docx,.pdf"
        onChange={handleFileUpload}
        disabled={uploading}
      />
      {uploading && <div>Processing file...</div>}
      {results && <div>Analysis complete!</div>}
    </div>
  );
};
```

### 2. Progress Indicators
- Implement progress bars for file uploads
- Show processing status for long-running analyses
- Provide estimated completion times

### 3. Error Handling
- Display user-friendly error messages
- Provide suggestions for common issues
- Implement retry mechanisms for transient failures

### 4. Response Visualization
- Create interactive charts for KPI scores
- Implement expandable sections for detailed analysis
- Add export functionality for reports

### 5. Performance Optimization
- Implement result caching for frequently analyzed documents
- Use pagination for large result sets
- Add search and filtering capabilities

---

## Technical Implementation Notes

1. **Batch Processing**: For organizations with many policies or use cases, consider implementing batch processing options
2. **Caching Strategy**: Implement appropriate caching for frequently accessed evaluation results
3. **Versioning**: Store and track versions of evaluations to allow historical comparison
4. **Export Formats**: Support JSON, PDF, DOCX, and CSV export formats for integration with other tools
5. **Feedback Loop**: Include mechanisms for users to provide feedback on evaluation accuracy
6. **File Storage**: Consider temporary file storage for large uploads and background processing
7. **Rate Limiting**: Implement rate limiting to prevent API abuse
8. **Authentication**: Add proper authentication and authorization for production deployments

