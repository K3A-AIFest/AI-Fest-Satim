"""
FastAPI server for GRC Assistant API endpoints.

This module provides the API endpoints for:
1. Policy evaluation (gap identification, compliance checking, enhancement)
2. Use case processing (KPI analysis, deployment analysis, judgment)
3. File upload support for DOCX and PDF documents
"""
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

# Import handlers and models
from handlers.models import (
    PolicyEvaluationRequest,
    PolicyEvaluationRequestWithSpeed,
    UseCaseRequest,
    GapAnalysisResponse,
    ComplianceCheckResponse,
    PolicyEnhancementResponse,
    CombinedEvaluationResponse,
    FastAnalysisResponse,
    KPIAnalysisResponse,
    DeploymentAnalysisResponse,
    UseCaseJudgmentResponse,
    CompleteUseCaseProcessingResponse,

)
from handlers.policy_handlers import (
    handle_gap_identification,
    handle_gap_identification_file,
    handle_compliance_checking,
    handle_compliance_checking_file,
    handle_policy_enhancement,
    handle_policy_enhancement_file,
    handle_evaluate_policy,
    handle_evaluate_policy_file,
    handle_fast_analyze_policy,
    handle_fast_analyze_policy_file
)
from handlers.use_case_handlers import (
    handle_analyze_use_case_kpis,
    handle_analyze_use_case_kpis_file,
    handle_analyze_deployment,
    handle_analyze_deployment_file,
    handle_judge_use_case,
    handle_judge_use_case_file,
    handle_process_use_case,
    handle_process_use_case_file
)

# Initialize FastAPI app
app = FastAPI(
    title="GRC Assistant API",
    description="API for evaluating security policies and use cases against standards",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}


# =============================================================================
# POLICY EVALUATION ENDPOINTS
# =============================================================================

# Text-based endpoints
@app.post("/policies/gaps", response_model=GapAnalysisResponse, tags=["Policy Evaluation"])
async def gap_identification(request: PolicyEvaluationRequest):
    """
    Identify gaps in a policy compared to standards.
    
    This endpoint analyzes a policy document to identify missing elements when compared to standards.
    """
    return await handle_gap_identification(request)


@app.post("/policies/compliance", response_model=ComplianceCheckResponse, tags=["Policy Evaluation"])
async def compliance_checking(request: PolicyEvaluationRequest):
    """
    Check compliance of a policy against standards.
    
    This endpoint evaluates how well a policy complies with the requirements in standards.
    """
    return await handle_compliance_checking(request)


@app.post("/policies/enhance", response_model=PolicyEnhancementResponse, tags=["Policy Evaluation"])
async def policy_enhancement(request: PolicyEvaluationRequest):
    """
    Enhance a policy based on standards.
    
    This endpoint suggests improvements for a policy to better align with standards.
    """
    return await handle_policy_enhancement(request)


@app.post("/policies/evaluate", response_model=CombinedEvaluationResponse, tags=["Policy Evaluation"])
async def evaluate_policy(request: PolicyEvaluationRequestWithSpeed):
    """
    Perform a comprehensive evaluation of a policy against standards.
    
    This endpoint combines gap identification, compliance checking, and policy enhancement
    into a single comprehensive evaluation, with results merged by policy chunk.
    
    You can specify a 'speed' parameter with values:
    - 'deep' (default): Thorough analysis with gap identification, compliance checking, and policy enhancement
    - 'fast': Quick analysis focusing only on critical gaps, with larger chunks and sampling for faster results
    """
    return await handle_evaluate_policy(request)


@app.post("/policies/analyze/fast", response_model=FastAnalysisResponse, tags=["Policy Evaluation"])
async def fast_analyze_policy(request: PolicyEvaluationRequest):
    """
    Perform a quick analysis of a policy against standards.
    
    This endpoint provides a faster analysis by:
    1. Processing only representative chunks of the policy
    2. Focusing only on critical gaps rather than full compliance
    3. Using larger chunks to reduce processing time
    
    It's ideal for initial assessment or when time is limited.
    """
    return await handle_fast_analyze_policy(request)


# File upload endpoints
@app.post("/policies/gaps/upload", response_model=GapAnalysisResponse, tags=["Policy Evaluation", "File Upload"])
async def gap_identification_upload(
    file: UploadFile = File(..., description="Policy document file (DOCX or PDF)"),
    standards: Optional[List[str]] = Form(default=None, description="List of standards to evaluate against"),
    chunk_size: Optional[int] = Form(default=1000, description="Size of text chunks for processing")
):
    """
    Identify gaps in a policy document file compared to standards.
    
    Upload a policy document (DOCX or PDF) and get gap analysis results.
    """
    return await handle_gap_identification_file(file, standards, chunk_size)


@app.post("/policies/compliance/upload", response_model=ComplianceCheckResponse, tags=["Policy Evaluation", "File Upload"])
async def compliance_checking_upload(
    file: UploadFile = File(..., description="Policy document file (DOCX or PDF)"),
    standards: Optional[List[str]] = Form(default=None, description="List of standards to evaluate against"),
    chunk_size: Optional[int] = Form(default=1000, description="Size of text chunks for processing")
):
    """
    Check compliance of a policy document file against standards.
    
    Upload a policy document (DOCX or PDF) and get compliance assessment results.
    """
    return await handle_compliance_checking_file(file, standards, chunk_size)


@app.post("/policies/enhance/upload", response_model=PolicyEnhancementResponse, tags=["Policy Evaluation", "File Upload"])
async def policy_enhancement_upload(
    file: UploadFile = File(..., description="Policy document file (DOCX or PDF)"),
    standards: Optional[List[str]] = Form(default=None, description="List of standards to evaluate against"),
    chunk_size: Optional[int] = Form(default=1000, description="Size of text chunks for processing")
):
    """
    Enhance a policy document file based on standards.
    
    Upload a policy document (DOCX or PDF) and get enhancement suggestions.
    """
    return await handle_policy_enhancement_file(file, standards, chunk_size)


@app.post("/policies/evaluate/upload", response_model=CombinedEvaluationResponse, tags=["Policy Evaluation", "File Upload"])
async def evaluate_policy_upload(
    file: UploadFile = File(..., description="Policy document file (DOCX or PDF)"),
    standards: Optional[List[str]] = Form(default=None, description="List of standards to evaluate against"),
    chunk_size: Optional[int] = Form(default=1000, description="Size of text chunks for processing"),
    speed: Optional[str] = Form(default="deep", description="Analysis speed: 'deep' or 'fast'")
):
    """
    Perform a comprehensive evaluation of a policy document file against standards.
    
    Upload a policy document (DOCX or PDF) and get comprehensive evaluation results.
    """
    return await handle_evaluate_policy_file(file, standards, chunk_size, speed)


@app.post("/policies/analyze/fast/upload", response_model=FastAnalysisResponse, tags=["Policy Evaluation", "File Upload"])
async def fast_analyze_policy_upload(
    file: UploadFile = File(..., description="Policy document file (DOCX or PDF)"),
    standards: Optional[List[str]] = Form(default=None, description="List of standards to evaluate against"),
    chunk_size: Optional[int] = Form(default=1000, description="Size of text chunks for processing")
):
    """
    Perform a quick analysis of a policy document file against standards.
    
    Upload a policy document (DOCX or PDF) and get fast analysis results.
    """
    return await handle_fast_analyze_policy_file(file, standards, chunk_size)


# =============================================================================
# USE CASE PROCESSING ENDPOINTS
# =============================================================================

# Text-based endpoints
@app.post("/use-cases/kpis", response_model=KPIAnalysisResponse, tags=["Use Case Processor"])
async def analyze_use_case_kpis_endpoint(request: UseCaseRequest):
    """
    Analyze the security KPIs for a use case.
    
    This endpoint evaluates a security use case against industry standard security KPIs
    and provides scores, analysis, and recommendations for improvement.
    """
    return await handle_analyze_use_case_kpis(request)


@app.post("/use-cases/deployment", response_model=DeploymentAnalysisResponse, tags=["Use Case Processor"])
async def analyze_deployment_endpoint(request: UseCaseRequest):
    """
    Analyze the deployment aspects of a security use case.
    
    This endpoint evaluates the feasibility, pros, cons, timeline, and resource requirements
    for implementing a security use case.
    """
    return await handle_analyze_deployment(request)


@app.post("/use-cases/judge", response_model=UseCaseJudgmentResponse, tags=["Use Case Processor"])
async def judge_use_case_endpoint(request: UseCaseRequest):
    """
    Judge the quality and effectiveness of a security use case.
    
    This endpoint evaluates how well a security use case addresses security requirements
    and aligns with standards and policies.
    """
    return await handle_judge_use_case(request)


@app.post("/use-cases/process", response_model=CompleteUseCaseProcessingResponse, tags=["Use Case Processor"])
async def process_use_case_endpoint(request: UseCaseRequest):
    """
    Process a security use case with comprehensive analysis.
    
    This endpoint combines KPI analysis, deployment analysis, judgment, and aggregated assessment
    into a complete evaluation of a security use case.
    """
    return await handle_process_use_case(request)


# File upload endpoints
@app.post("/use-cases/kpis/upload", response_model=KPIAnalysisResponse, tags=["Use Case Processor", "File Upload"])
async def analyze_use_case_kpis_upload(
    file: UploadFile = File(..., description="Use case document file (DOCX or PDF)"),
    standards: Optional[List[str]] = Form(default=None, description="List of standards to evaluate against"),
    policies: Optional[List[str]] = Form(default=None, description="List of policies to evaluate against")
):
    """
    Analyze the security KPIs for a use case document file.
    
    Upload a use case document (DOCX or PDF) and get KPI analysis results.
    """
    return await handle_analyze_use_case_kpis_file(file, standards, policies)


@app.post("/use-cases/deployment/upload", response_model=DeploymentAnalysisResponse, tags=["Use Case Processor", "File Upload"])
async def analyze_deployment_upload(
    file: UploadFile = File(..., description="Use case document file (DOCX or PDF)"),
    standards: Optional[List[str]] = Form(default=None, description="List of standards to evaluate against"),
    policies: Optional[List[str]] = Form(default=None, description="List of policies to evaluate against")
):
    """
    Analyze the deployment aspects of a use case document file.
    
    Upload a use case document (DOCX or PDF) and get deployment analysis results.
    """
    return await handle_analyze_deployment_file(file, standards, policies)


@app.post("/use-cases/judge/upload", response_model=UseCaseJudgmentResponse, tags=["Use Case Processor", "File Upload"])
async def judge_use_case_upload(
    file: UploadFile = File(..., description="Use case document file (DOCX or PDF)"),
    standards: Optional[List[str]] = Form(default=None, description="List of standards to evaluate against"),
    policies: Optional[List[str]] = Form(default=None, description="List of policies to evaluate against")
):
    """
    Judge the quality and effectiveness of a use case document file.
    
    Upload a use case document (DOCX or PDF) and get use case judgment results.
    """
    return await handle_judge_use_case_file(file, standards, policies)


@app.post("/use-cases/process/upload", response_model=CompleteUseCaseProcessingResponse, tags=["Use Case Processor", "File Upload"])
async def process_use_case_upload(
    file: UploadFile = File(..., description="Use case document file (DOCX or PDF)"),
    standards: Optional[List[str]] = Form(default=None, description="List of standards to evaluate against"),
    policies: Optional[List[str]] = Form(default=None, description="List of policies to evaluate against")
):
    """
    Process a use case document file with comprehensive analysis.
    
    Upload a use case document (DOCX or PDF) and get complete processing results.
    """
    return await handle_process_use_case_file(file, standards, policies)


# =============================================================================
# LEGACY ENDPOINTS (for backward compatibility)
# =============================================================================

@app.post("/api/v1/identify-gaps", response_model=GapAnalysisResponse, tags=["Legacy API"])
async def legacy_gap_identification(request: PolicyEvaluationRequest):
    """Legacy endpoint for gap identification. Use /policies/gaps instead."""
    return await handle_gap_identification(request)


@app.post("/api/v1/check-compliance", response_model=ComplianceCheckResponse, tags=["Legacy API"])
async def legacy_compliance_checking(request: PolicyEvaluationRequest):
    """Legacy endpoint for compliance checking. Use /policies/compliance instead."""
    return await handle_compliance_checking(request)


@app.post("/api/v1/enhance-policy", response_model=PolicyEnhancementResponse, tags=["Legacy API"])
async def legacy_policy_enhancement(request: PolicyEvaluationRequest):
    """Legacy endpoint for policy enhancement. Use /policies/enhance instead."""
    return await handle_policy_enhancement(request)


@app.post("/api/v1/evaluate-policy", response_model=CombinedEvaluationResponse, tags=["Legacy API"])
async def legacy_evaluate_policy(request: PolicyEvaluationRequestWithSpeed):
    """Legacy endpoint for policy evaluation. Use /policies/evaluate instead."""
    return await handle_evaluate_policy(request)


@app.post("/api/v1/fast-analyze", response_model=FastAnalysisResponse, tags=["Legacy API"])
async def legacy_fast_analyze_policy(request: PolicyEvaluationRequest):
    """Legacy endpoint for fast analysis. Use /policies/analyze/fast instead."""
    return await handle_fast_analyze_policy(request)


@app.post("/api/v1/use-case/analyze-kpis", response_model=KPIAnalysisResponse, tags=["Legacy API"])
async def legacy_analyze_use_case_kpis_endpoint(request: UseCaseRequest):
    """Legacy endpoint for use case KPI analysis. Use /use-cases/kpis instead."""
    return await handle_analyze_use_case_kpis(request)


@app.post("/api/v1/use-case/analyze-deployment", response_model=DeploymentAnalysisResponse, tags=["Legacy API"])
async def legacy_analyze_deployment_endpoint(request: UseCaseRequest):
    """Legacy endpoint for deployment analysis. Use /use-cases/deployment instead."""
    return await handle_analyze_deployment(request)


@app.post("/api/v1/use-case/judge", response_model=UseCaseJudgmentResponse, tags=["Legacy API"])
async def legacy_judge_use_case_endpoint(request: UseCaseRequest):
    """Legacy endpoint for use case judgment. Use /use-cases/judge instead."""
    return await handle_judge_use_case(request)


@app.post("/api/v1/use-case/process", response_model=CompleteUseCaseProcessingResponse, tags=["Legacy API"])
async def legacy_process_use_case_endpoint(request: UseCaseRequest):
    """Legacy endpoint for use case processing. Use /use-cases/process instead."""
    return await handle_process_use_case(request)


# Serve the application
if __name__ == "__main__":
    import uvicorn
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8000))
    # Run the server
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info", reload=True)
