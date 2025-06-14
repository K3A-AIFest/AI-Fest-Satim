"""
Use case processing handlers for FastAPI endpoints.

This module contains handler functions for use case processing endpoints including
KPI analysis, deployment analysis, use case judgment, and complete processing.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, UploadFile
from .models import (
    UseCaseRequest,
    KPIAnalysisResponse,
    DeploymentAnalysisResponse,
    UseCaseJudgmentResponse,
    CompleteUseCaseProcessingResponse,
    FileUploadResponse
)
from .file_utils import extract_text_from_file, validate_file_size, validate_file_type
from pipelines.use_case_processor import analyze_use_case_kpis, analyze_deployment, judge_use_case, process_use_case


async def handle_analyze_use_case_kpis(request: UseCaseRequest) -> KPIAnalysisResponse:
    """
    Handle use case KPI analysis request.
    
    Args:
        request: Use case request
        
    Returns:
        KPIAnalysisResponse: Results of KPI analysis
        
    Raises:
        HTTPException: If KPI analysis fails
    """
    try:
        results = analyze_use_case_kpis(request.use_case_content, request.standards, request.policies)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing use case KPIs: {str(e)}")


async def handle_analyze_use_case_kpis_file(
    file: UploadFile,
    standards: Optional[List[str]] = None,
    policies: Optional[List[str]] = None
) -> KPIAnalysisResponse:
    """
    Handle use case KPI analysis request with file upload.
    
    Args:
        file: Uploaded use case file (DOCX or PDF)
        standards: List of standards to evaluate against
        policies: List of policies to evaluate against
        
    Returns:
        KPIAnalysisResponse: Results of KPI analysis
        
    Raises:
        HTTPException: If file processing or KPI analysis fails
    """
    try:
        # Validate file
        validate_file_size(file)
        validate_file_type(file)
        
        # Extract text from file
        use_case_content = await extract_text_from_file(file)
        
        if not use_case_content.strip():
            raise HTTPException(status_code=400, detail="No text content found in the uploaded file")
        
        # Set default standards if none provided
        if standards is None:
            standards = ["ISO 27001", "NIST", "GDPR"]
        
        # Process the use case
        results = analyze_use_case_kpis(use_case_content, standards, policies)
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file for use case KPI analysis: {str(e)}")


async def handle_analyze_deployment(request: UseCaseRequest) -> DeploymentAnalysisResponse:
    """
    Handle deployment analysis request.
    
    Args:
        request: Use case request
        
    Returns:
        DeploymentAnalysisResponse: Results of deployment analysis
        
    Raises:
        HTTPException: If deployment analysis fails
    """
    try:
        results = analyze_deployment(request.use_case_content, request.standards, request.policies)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing deployment aspects: {str(e)}")


async def handle_analyze_deployment_file(
    file: UploadFile,
    standards: Optional[List[str]] = None,
    policies: Optional[List[str]] = None
) -> DeploymentAnalysisResponse:
    """
    Handle deployment analysis request with file upload.
    
    Args:
        file: Uploaded use case file (DOCX or PDF)
        standards: List of standards to evaluate against
        policies: List of policies to evaluate against
        
    Returns:
        DeploymentAnalysisResponse: Results of deployment analysis
        
    Raises:
        HTTPException: If file processing or deployment analysis fails
    """
    try:
        # Validate file
        validate_file_size(file)
        validate_file_type(file)
        
        # Extract text from file
        use_case_content = await extract_text_from_file(file)
        
        if not use_case_content.strip():
            raise HTTPException(status_code=400, detail="No text content found in the uploaded file")
        
        # Set default standards if none provided
        if standards is None:
            standards = ["ISO 27001", "NIST", "GDPR"]
        
        # Process the use case
        results = analyze_deployment(use_case_content, standards, policies)
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file for deployment analysis: {str(e)}")


async def handle_judge_use_case(request: UseCaseRequest) -> UseCaseJudgmentResponse:
    """
    Handle use case judgment request.
    
    Args:
        request: Use case request
        
    Returns:
        UseCaseJudgmentResponse: Results of use case judgment
        
    Raises:
        HTTPException: If use case judgment fails
    """
    try:
        results = judge_use_case(request.use_case_content, request.standards, request.policies)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error judging use case: {str(e)}")


async def handle_judge_use_case_file(
    file: UploadFile,
    standards: Optional[List[str]] = None,
    policies: Optional[List[str]] = None
) -> UseCaseJudgmentResponse:
    """
    Handle use case judgment request with file upload.
    
    Args:
        file: Uploaded use case file (DOCX or PDF)
        standards: List of standards to evaluate against
        policies: List of policies to evaluate against
        
    Returns:
        UseCaseJudgmentResponse: Results of use case judgment
        
    Raises:
        HTTPException: If file processing or use case judgment fails
    """
    try:
        # Validate file
        validate_file_size(file)
        validate_file_type(file)
        
        # Extract text from file
        use_case_content = await extract_text_from_file(file)
        
        if not use_case_content.strip():
            raise HTTPException(status_code=400, detail="No text content found in the uploaded file")
        
        # Set default standards if none provided
        if standards is None:
            standards = ["ISO 27001", "NIST", "GDPR"]
        
        # Process the use case
        results = judge_use_case(use_case_content, standards, policies)
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file for use case judgment: {str(e)}")


async def handle_process_use_case(request: UseCaseRequest) -> CompleteUseCaseProcessingResponse:
    """
    Handle complete use case processing request.
    
    Args:
        request: Use case request
        
    Returns:
        CompleteUseCaseProcessingResponse: Results of complete processing
        
    Raises:
        HTTPException: If use case processing fails
    """
    try:
        results = process_use_case(request.use_case_content, request.standards, request.policies)
        
        # Add processed_at timestamp
        results["processed_at"] = datetime.utcnow().isoformat() + "Z"
        
        return CompleteUseCaseProcessingResponse(**results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing use case: {str(e)}")


async def handle_process_use_case_file(
    file: UploadFile,
    standards: Optional[List[str]] = None,
    policies: Optional[List[str]] = None
) -> CompleteUseCaseProcessingResponse:
    """
    Handle complete use case processing request with file upload.
    
    Args:
        file: Uploaded use case file (DOCX or PDF)
        standards: List of standards to evaluate against
        policies: List of policies to evaluate against
        
    Returns:
        CompleteUseCaseProcessingResponse: Results of complete processing
        
    Raises:
        HTTPException: If file processing or use case processing fails
    """
    try:
        # Validate file
        validate_file_size(file)
        validate_file_type(file)
        
        # Extract text from file
        use_case_content = await extract_text_from_file(file)
        
        if not use_case_content.strip():
            raise HTTPException(status_code=400, detail="No text content found in the uploaded file")
        
        # Set default standards if none provided
        if standards is None:
            standards = ["ISO 27001", "NIST", "GDPR"]
        
        # Create request object and delegate to text handler
        request = UseCaseRequest(
            use_case_content=use_case_content,
            standards=standards,
            policies=policies
        )
        
        return await handle_process_use_case(request)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file for use case processing: {str(e)}")
