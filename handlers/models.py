"""
Request and response models for the API endpoints.

This module defines all Pydantic models used for request and response validation.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# Policy Evaluation Models
class PolicyEvaluationRequest(BaseModel):
    """Request model for policy evaluation endpoints."""
    policy_content: str = Field(..., description="The policy document text to evaluate")
    standards: Optional[List[str]] = Field(default=["ISO 27001", "NIST", "GDPR"], description="List of standard documents to evaluate against")
    chunk_size: Optional[int] = Field(default=1000, description="Size of text chunks for processing")


class PolicyEvaluationRequestWithSpeed(PolicyEvaluationRequest):
    """Request model for policy evaluation with speed option."""
    speed: Optional[str] = Field("deep", description="Analysis speed: 'deep' (thorough analysis) or 'fast' (quick analysis)")


class GapAnalysisResponse(BaseModel):
    """Response model for gap identification."""
    results: List[Dict[str, Any]] = Field(..., description="List of identified gaps with classification and justification")
    

class ComplianceCheckResponse(BaseModel):
    """Response model for compliance checking."""
    results: List[Dict[str, Any]] = Field(..., description="List of compliance assessments with classification and justification")
    

class PolicyEnhancementResponse(BaseModel):
    """Response model for policy enhancement."""
    results: List[Dict[str, Any]] = Field(..., description="List of enhanced policy chunks with justification")


class CombinedEvaluationResponse(BaseModel):
    """Response model for combined policy evaluation."""
    results: List[Dict[str, Any]] = Field(..., description="List of consolidated evaluation results for each policy chunk")
    summary: Optional[Dict[str, Any]] = Field(None, description="Summary statistics and key findings")
    processed_at: str = Field(..., description="Timestamp when the evaluation was processed")


class FastAnalysisResponse(BaseModel):
    """Response model for fast policy analysis."""
    results: List[Dict[str, Any]] = Field(..., description="List of quick gap analysis results with classification")
    speed: str = Field("fast", description="Speed mode used for the analysis")


# Use Case Processor Models
class UseCaseRequest(BaseModel):
    """Request model for use case processor endpoints."""
    use_case_content: str = Field(..., description="The security use case text to analyze")
    standards: Optional[List[str]] = Field(default=["ISO 27001", "NIST", "GDPR"], description="List of standard documents to evaluate against")
    policies: Optional[List[str]] = Field(None, description="Optional list of policy documents to evaluate against")


class KPIAnalysisResponse(BaseModel):
    """Response model for KPI analysis."""
    kpi_scores: Dict[str, float] = Field(..., description="Dictionary of KPI names and their scores")
    analysis: Dict[str, str] = Field(..., description="Dictionary of KPI names and their analysis explanation")
    overall_score: float = Field(..., description="Overall security KPI score between 0 and 100")
    recommendations: List[str] = Field(..., description="List of recommendations to improve KPI scores")


class DeploymentAnalysisResponse(BaseModel):
    """Response model for deployment analysis."""
    feasibility_score: float = Field(..., description="Feasibility score between 0-100")
    pros: List[str] = Field(..., description="List of advantages for deploying the use case")
    cons: List[str] = Field(..., description="List of disadvantages for deploying the use case")
    timeline_estimate: str = Field(..., description="Estimated timeline for deployment")
    resource_requirements: List[str] = Field(..., description="List of resources required for deployment")
    risk_factors: List[Dict[str, Any]] = Field(..., description="List of risk factors with severity and mitigation")


class UseCaseJudgmentResponse(BaseModel):
    """Response model for use case judgment."""
    effectiveness_score: float = Field(..., description="Effectiveness score between 0-100")
    alignment_with_standards: List[Dict[str, Any]] = Field(..., description="Analysis of alignment with standards")
    alignment_with_policies: List[Dict[str, Any]] = Field(..., description="Analysis of alignment with policies")
    security_impact: str = Field(..., description="Overall security impact assessment")
    gaps_identified: List[str] = Field(..., description="List of identified gaps in the use case")
    improvement_suggestions: List[str] = Field(..., description="List of suggestions to improve the use case")


class AggregatedAnalysisResponse(BaseModel):
    """Response model for aggregated analysis."""
    overall_assessment: str = Field(..., description="Overall assessment summary")
    overall_score: float = Field(..., description="Overall score between 0-100")
    key_findings: List[str] = Field(..., description="List of key findings from all analyses")
    critical_considerations: List[str] = Field(..., description="List of critical considerations")
    recommended_next_steps: List[str] = Field(..., description="Recommended next steps")
    stakeholder_considerations: Dict[str, List[str]] = Field(..., description="Considerations for stakeholders")


class CompleteUseCaseProcessingResponse(BaseModel):
    """Response model for complete use case processing."""
    use_case_content: str = Field(..., description="The original use case text that was analyzed")
    kpi_analysis: KPIAnalysisResponse = Field(..., description="Results of KPI analysis")
    deployment_analysis: DeploymentAnalysisResponse = Field(..., description="Results of deployment analysis")
    use_case_judgment: UseCaseJudgmentResponse = Field(..., description="Results of use case judgment")
    aggregated_analysis: AggregatedAnalysisResponse = Field(..., description="Results of aggregated analysis")
    processed_at: str = Field(..., description="Timestamp when the processing was completed")


# File Upload Response Models
class FileUploadResponse(BaseModel):
    """Response model for file upload operations."""
    filename: str = Field(..., description="Name of the uploaded file")
    file_size: int = Field(..., description="Size of the uploaded file in bytes")
    extracted_text_length: int = Field(..., description="Length of the extracted text in characters")
    message: str = Field(..., description="Success message")


# Error Response Models
class ErrorResponse(BaseModel):
    """Response model for error responses."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
