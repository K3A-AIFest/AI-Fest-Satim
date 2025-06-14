# API Endpoints Documentation

This document describes the backend API endpoints required for the GRC Assistant frontend application. All endpoints should return JSON responses and follow RESTful conventions.

## Base URL
```
https://api.yourdomain.com/v1
```

## Authentication
All API requests should include authentication headers:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

---

## Dashboard Endpoints

### 1. Get Compliance Score
**GET** `/dashboard/compliance-score`

Returns the overall compliance score for the organization.

**Response:**
```json
{
  "score": 78,
  "total": 100,
  "percentage": 78
}
```

### 2. Get Gap Detection Summary
**GET** `/dashboard/gap-detection`

Returns summary of detected compliance gaps.

**Response:**
```json
{
  "count": 24,
  "critical": 3,
  "high": 7,
  "medium": 10,
  "low": 4
}
```

### 3. Get Use Case Evaluation Summary
**GET** `/dashboard/use-case-evaluation`

Returns summary of use case evaluations.

**Response:**
```json
{
  "count": 15,
  "compliant": 11,
  "nonCompliant": 4,
  "percentage": 73
}
```

### 4. Get Recent Activities
**GET** `/dashboard/activities`

Returns recent system activities.

**Query Parameters:**
- `limit` (optional): Number of activities to return (default: 10)

**Response:**
```json
[
  {
    "id": "act1",
    "type": "gap",
    "title": "New Gap Detected",
    "description": "ISO 27001 control missing in Data Privacy Policy",
    "timestamp": "2025-06-12T09:30:00Z",
    "severity": "critical"
  },
  {
    "id": "act2",
    "type": "use-case",
    "title": "Use Case Evaluation Complete",
    "description": "Cloud Storage Use Case - 78% compliant",
    "timestamp": "2025-06-12T08:15:00Z",
    "severity": "medium"
  }
]
```

### 5. Get Smart Suggestions
**GET** `/dashboard/suggestions`

Returns AI-generated compliance suggestions.

**Response:**
```json
[
  {
    "id": "sug1",
    "title": "Update Data Privacy Policy",
    "description": "Add missing controls for data subject access requests to comply with GDPR",
    "priority": "critical"
  },
  {
    "id": "sug2",
    "title": "Review Cloud Storage Use Case",
    "description": "Address non-compliance issues with data encryption requirements",
    "priority": "high"
  }
]
```

### 6. Get Compliance by Category
**GET** `/dashboard/compliance-by-category`

Returns compliance breakdown by category for charts.

**Response:**
```json
[
  {
    "category": "Data Privacy",
    "score": 85,
    "total": 100,
    "percentage": 85
  },
  {
    "category": "Security",
    "score": 92,
    "total": 100,
    "percentage": 92
  }
]
```

---

## Policies Endpoints

### 7. Get All Policies
**GET** `/policies`

Returns list of all internal policies.

**Query Parameters:**
- `status` (optional): Filter by status (`active`, `draft`, `archived`)
- `page` (optional): Page number for pagination
- `limit` (optional): Number of policies per page

**Response:**
```json
{
  "data": [
    {
      "id": "pol1",
      "name": "Data Privacy Policy",
      "description": "Guidelines for handling personal data and ensuring privacy",
      "lastUpdated": "2025-05-15",
      "status": "active"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 25,
    "totalPages": 3
  }
}
```

### 8. Get Policy by ID
**GET** `/policies/{id}`

Returns details of a specific policy.

**Response:**
```json
{
  "id": "pol1",
  "name": "Data Privacy Policy",
  "description": "Guidelines for handling personal data and ensuring privacy",
  "lastUpdated": "2025-05-15",
  "status": "active",
  "content": "Full policy content here...",
  "version": "1.2"
}
```

### 9. Create Policy
**POST** `/policies`

Creates a new policy.

**Request Body:**
```json
{
  "name": "New Policy Name",
  "description": "Policy description",
  "content": "Full policy content",
  "status": "draft"
}
```

**Response:**
```json
{
  "id": "pol_new_id",
  "name": "New Policy Name",
  "description": "Policy description",
  "lastUpdated": "2025-06-12T10:00:00Z",
  "status": "draft"
}
```

### 10. Update Policy
**PUT** `/policies/{id}`

Updates an existing policy.

**Request Body:**
```json
{
  "name": "Updated Policy Name",
  "description": "Updated description",
  "content": "Updated content",
  "status": "active"
}
```

### 11. Delete Policy
**DELETE** `/policies/{id}`

Deletes a policy.

**Response:**
```json
{
  "message": "Policy deleted successfully"
}
```

---

## Standards Endpoints

### 12. Get All Standards
**GET** `/standards`

Returns list of regulatory standards.

**Response:**
```json
[
  {
    "id": "std1",
    "name": "ISO 27001",
    "description": "Information security management",
    "version": "2022"
  },
  {
    "id": "std2",
    "name": "GDPR",
    "description": "General Data Protection Regulation",
    "version": "2018"
  }
]
```

---

## Gap Analysis Endpoints

### 13. Get All Gaps
**GET** `/gaps`

Returns list of identified compliance gaps.

**Query Parameters:**
- `severity` (optional): Filter by severity (`critical`, `high`, `medium`, `low`)
- `policyId` (optional): Filter by policy ID
- `standardId` (optional): Filter by standard ID

**Response:**
```json
[
  {
    "id": "gap1",
    "policyId": "pol1",
    "policyName": "Data Privacy Policy",
    "standardId": "std2",
    "standardName": "GDPR",
    "control": "Article 17 - Right to erasure",
    "description": "Policy does not address the right to erasure (right to be forgotten)",
    "severity": "critical",
    "suggestedFix": "Add section detailing process for handling data erasure requests"
  }
]
```

### 14. Run Gap Analysis
**POST** `/gaps/analyze`

Runs gap analysis between policies and standards.

**Request Body:**
```json
{
  "policyIds": ["pol1", "pol2"],
  "standardIds": ["std1", "std2"]
}
```

**Response:**
```json
{
  "analysisId": "analysis_123",
  "status": "completed",
  "gaps": [
    {
      "id": "gap_new",
      "policyId": "pol1",
      "policyName": "Data Privacy Policy",
      "standardId": "std2",
      "standardName": "GDPR",
      "control": "Article 17 - Right to erasure",
      "description": "Policy does not address the right to erasure",
      "severity": "critical",
      "suggestedFix": "Add section detailing process for handling data erasure requests"
    }
  ]
}
```

### 15. Get Gap Analysis History
**GET** `/gaps/analysis-history`

Returns previous gap analysis results.

**Response:**
```json
[
  {
    "id": "analysis_123",
    "timestamp": "2025-06-12T10:00:00Z",
    "policies": ["Data Privacy Policy", "Security Policy"],
    "standards": ["GDPR", "ISO 27001"],
    "gapsFound": 5,
    "status": "completed"
  }
]
```

---

## Use Case Evaluation Endpoints

### 16. Get All Use Cases
**GET** `/use-cases`

Returns list of evaluated use cases.

**Response:**
```json
[
  {
    "id": "uc1",
    "name": "Cloud Storage Implementation",
    "description": "Using third-party cloud storage for company documents",
    "policies": ["pol1", "pol2"],
    "complianceScore": 78,
    "issues": [
      {
        "policyId": "pol2",
        "policyName": "Information Security Policy",
        "clause": "Section 4.3 - Data Encryption",
        "description": "Cloud storage does not enforce encryption at rest",
        "severity": "high"
      }
    ]
  }
]
```

### 17. Create Use Case Evaluation
**POST** `/use-cases/evaluate`

Evaluates a new use case against selected policies.

**Request Body:**
```json
{
  "name": "New Use Case",
  "description": "Description of the use case",
  "policyIds": ["pol1", "pol2"],
  "details": "Detailed use case scenario..."
}
```

**Response:**
```json
{
  "id": "uc_new",
  "name": "New Use Case",
  "description": "Description of the use case",
  "policies": ["pol1", "pol2"],
  "complianceScore": 85,
  "issues": [
    {
      "policyId": "pol1",
      "policyName": "Data Privacy Policy",
      "clause": "Section 2.1 - Data Location",
      "description": "Use case may involve data processing outside approved jurisdictions",
      "severity": "medium"
    }
  ]
}
```

### 18. Get Use Case by ID
**GET** `/use-cases/{id}`

Returns details of a specific use case evaluation.

**Response:**
```json
{
  "id": "uc1",
  "name": "Cloud Storage Implementation",
  "description": "Using third-party cloud storage for company documents",
  "policies": ["pol1", "pol2"],
  "complianceScore": 78,
  "issues": [
    {
      "policyId": "pol2",
      "policyName": "Information Security Policy",
      "clause": "Section 4.3 - Data Encryption",
      "description": "Cloud storage does not enforce encryption at rest",
      "severity": "high"
    }
  ],
  "createdAt": "2025-06-10T14:30:00Z",
  "lastUpdated": "2025-06-12T09:15:00Z"
}
```

---

## File Upload Endpoints

### 19. Upload Policy Document
**POST** `/files/upload/policy`

Uploads a policy document for analysis.

**Request:**
- Content-Type: `multipart/form-data`
- Body: Form data with file

**Response:**
```json
{
  "fileId": "file_123",
  "filename": "privacy-policy.pdf",
  "uploadedAt": "2025-06-12T10:00:00Z",
  "status": "uploaded",
  "extractedText": "Policy content extracted from document..."
}
```

---

## Settings Endpoints

### 20. Get User Settings
**GET** `/settings`

Returns user/organization settings.

**Response:**
```json
{
  "notifications": {
    "email": true,
    "dashboard": true,
    "criticalAlerts": true
  },
  "integrations": {
    "apiKey": "***masked***",
    "webhookUrl": "https://example.com/webhook"
  },
  "preferences": {
    "theme": "light",
    "language": "en",
    "timezone": "UTC"
  }
}
```

### 21. Update Settings
**PUT** `/settings`

Updates user/organization settings.

**Request Body:**
```json
{
  "notifications": {
    "email": false,
    "dashboard": true,
    "criticalAlerts": true
  },
  "integrations": {
    "apiKey": "new-api-key",
    "webhookUrl": "https://example.com/new-webhook"
  }
}
```

---

## Error Responses

All endpoints should return appropriate HTTP status codes and error messages:

### 400 Bad Request
```json
{
  "error": "Bad Request",
  "message": "Invalid request parameters",
  "details": {
    "field": "policyId",
    "issue": "Required field missing"
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or missing authentication token"
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
```

---

## Notes for Backend Development

1. **Data Types**: All severity levels should be one of: `"critical"`, `"high"`, `"medium"`, `"low"`
2. **Timestamps**: Use ISO 8601 format (`YYYY-MM-DDTHH:mm:ss.sssZ`)
3. **Pagination**: Implement pagination for list endpoints with `page`, `limit`, `total`, and `totalPages`
4. **File Processing**: Policy documents should be processed to extract text content for analysis
5. **Real-time Updates**: Consider implementing WebSocket connections for real-time notifications
6. **Caching**: Implement appropriate caching strategies for frequently accessed data like compliance scores
7. **Rate Limiting**: Implement rate limiting to prevent API abuse
8. **Logging**: Log all API requests for debugging and analytics
9. **Validation**: Validate all input data according to the TypeScript interfaces
10. **CORS**: Configure CORS settings appropriately for the frontend domain

---

## Frontend Integration Notes

The frontend expects the exact JSON structure as defined above. Any changes to the API response format should be coordinated with frontend updates to maintain compatibility.

Current mock data location: `lib/mock-data.ts`
Type definitions location: `lib/types.ts` 