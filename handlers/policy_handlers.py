"""
Policy evaluation handlers for FastAPI endpoints.

This module contains handler functions for policy evaluation endpoints including
gap identification, compliance checking, policy enhancement, and combined evaluation.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, UploadFile, Form
from .models import (
    PolicyEvaluationRequest, 
    PolicyEvaluationRequestWithSpeed,
    GapAnalysisResponse,
    ComplianceCheckResponse, 
    PolicyEnhancementResponse,
    CombinedEvaluationResponse,
    FastAnalysisResponse,
    FileUploadResponse
)
from .file_utils import extract_text_from_file, validate_file_size, validate_file_type
from pipelines.policy_evaluation import identify_gaps, check_compliance, enhance_policy, fast_policy_evaluation


async def handle_gap_identification(request: PolicyEvaluationRequest) -> GapAnalysisResponse:
    """
    Handle gap identification request.
    
    Args:
        request: Policy evaluation request
        
    Returns:
        GapAnalysisResponse: Results of gap identification
        
    Raises:
        HTTPException: If gap identification fails
    """
    try:
        results = identify_gaps(request.policy_content, request.standards)
        return GapAnalysisResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in gap identification: {str(e)}")


async def handle_gap_identification_file(
    file: UploadFile,
    standards: Optional[List[str]] = None,
    chunk_size: Optional[int] = 1000
) -> GapAnalysisResponse:
    """
    Handle gap identification request with file upload.
    
    Args:
        file: Uploaded policy file (DOCX or PDF)
        standards: List of standards to evaluate against
        chunk_size: Size of text chunks for processing
        
    Returns:
        GapAnalysisResponse: Results of gap identification
        
    Raises:
        HTTPException: If file processing or gap identification fails
    """
    try:
        # Validate file
        validate_file_size(file)
        validate_file_type(file)
        
        # Extract text from file
        policy_content = await extract_text_from_file(file)
        
        if not policy_content.strip():
            raise HTTPException(status_code=400, detail="No text content found in the uploaded file")
        
        # Set default standards if none provided
        if standards is None:
            standards = ["ISO 27001", "NIST", "GDPR"]
        
        # Process the policy
        results = identify_gaps(policy_content, standards)
        return GapAnalysisResponse(results=results)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file for gap identification: {str(e)}")


async def handle_compliance_checking(request: PolicyEvaluationRequest) -> ComplianceCheckResponse:
    """
    Handle compliance checking request.
    
    Args:
        request: Policy evaluation request
        
    Returns:
        ComplianceCheckResponse: Results of compliance checking
        
    Raises:
        HTTPException: If compliance checking fails
    """
    try:
        results = check_compliance(request.policy_content, request.standards)
        return ComplianceCheckResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in compliance checking: {str(e)}")


async def handle_compliance_checking_file(
    file: UploadFile,
    standards: Optional[List[str]] = None,
    chunk_size: Optional[int] = 1000
) -> ComplianceCheckResponse:
    """
    Handle compliance checking request with file upload.
    
    Args:
        file: Uploaded policy file (DOCX or PDF)
        standards: List of standards to evaluate against
        chunk_size: Size of text chunks for processing
        
    Returns:
        ComplianceCheckResponse: Results of compliance checking
        
    Raises:
        HTTPException: If file processing or compliance checking fails
    """
    try:
        # Validate file
        validate_file_size(file)
        validate_file_type(file)
        
        # Extract text from file
        policy_content = await extract_text_from_file(file)
        
        if not policy_content.strip():
            raise HTTPException(status_code=400, detail="No text content found in the uploaded file")
        
        # Set default standards if none provided
        if standards is None:
            standards = ["ISO 27001", "NIST", "GDPR"]
        
        # Process the policy
        results = check_compliance(policy_content, standards)
        return ComplianceCheckResponse(results=results)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file for compliance checking: {str(e)}")


async def handle_policy_enhancement(request: PolicyEvaluationRequest) -> PolicyEnhancementResponse:
    """
    Handle policy enhancement request.
    
    Args:
        request: Policy evaluation request
        
    Returns:
        PolicyEnhancementResponse: Results of policy enhancement
        
    Raises:
        HTTPException: If policy enhancement fails
    """
    try:
        results = enhance_policy(request.policy_content, request.standards)
        return PolicyEnhancementResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in policy enhancement: {str(e)}")


async def handle_policy_enhancement_file(
    file: UploadFile,
    standards: Optional[List[str]] = None,
    chunk_size: Optional[int] = 1000
) -> PolicyEnhancementResponse:
    """
    Handle policy enhancement request with file upload.
    
    Args:
        file: Uploaded policy file (DOCX or PDF)
        standards: List of standards to evaluate against
        chunk_size: Size of text chunks for processing
        
    Returns:
        PolicyEnhancementResponse: Results of policy enhancement
        
    Raises:
        HTTPException: If file processing or policy enhancement fails
    """
    try:
        # Validate file
        validate_file_size(file)
        validate_file_type(file)
        
        # Extract text from file
        policy_content = await extract_text_from_file(file)
        
        if not policy_content.strip():
            raise HTTPException(status_code=400, detail="No text content found in the uploaded file")
        
        # Set default standards if none provided
        if standards is None:
            standards = ["ISO 27001", "NIST", "GDPR"]
        
        # Process the policy
        results = enhance_policy(policy_content, standards)
        return PolicyEnhancementResponse(results=results)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file for policy enhancement: {str(e)}")


async def handle_evaluate_policy(request: PolicyEvaluationRequestWithSpeed) -> CombinedEvaluationResponse:
    """
    Handle comprehensive policy evaluation request.
    
    Args:
        request: Policy evaluation request with speed option
        
    Returns:
        CombinedEvaluationResponse: Results of comprehensive evaluation
        
    Raises:
        HTTPException: If policy evaluation fails
    """
    try:
        # Check if fast mode is requested
        speed = getattr(request, 'speed', 'deep')
        
        if speed == 'fast':
            # For fast mode, only perform gap analysis
            gap_results = fast_policy_evaluation(request.policy_content, request.standards)
            compliance_results = []
            enhancement_results = []
        else:
            # Regular deep analysis
            gap_results = identify_gaps(request.policy_content, request.standards)
            compliance_results = check_compliance(request.policy_content, request.standards)
            enhancement_results = enhance_policy(request.policy_content, request.standards)
        
        # Create a merged view by chunk
        merged_results = []
        
        # Use original_content as the unique identifier for each chunk
        for gap_item in gap_results:
            chunk_content = gap_item["original_content"]
            
            # Find matching compliance and enhancement items
            compliance_item = next(
                (item for item in compliance_results if item["original_content"] == chunk_content),
                None
            )
            
            enhancement_item = next(
                (item for item in enhancement_results if item["original_content"] == chunk_content),
                None
            )
            
            # Create consolidated result for this chunk
            consolidated_result = {
                "chunk_content": chunk_content,
                "gap_analysis": {
                    "classification": gap_item.get("classification", "UNKNOWN"),
                    "gaps": gap_item.get("gaps", []),
                    "rationale": gap_item.get("rationale", ""),
                    "references": gap_item.get("references", [])
                },
                "compliance_assessment": {
                    "classification": compliance_item.get("classification", "UNKNOWN") if compliance_item else "UNKNOWN",
                    "issues": compliance_item.get("issues", []) if compliance_item else [],
                    "rationale": compliance_item.get("rationale", "") if compliance_item else "",
                    "references": compliance_item.get("references", []) if compliance_item else []
                },
                "enhancement": {
                    "classification": enhancement_item.get("classification", "UNKNOWN") if enhancement_item else "UNKNOWN",
                    "enhanced_version": enhancement_item.get("enhanced_version", "") if enhancement_item else "",
                    "changes": enhancement_item.get("changes", []) if enhancement_item else [],
                    "rationale": enhancement_item.get("rationale", "") if enhancement_item else ""
                }
            }
            
            merged_results.append(consolidated_result)
        
        # Create summary statistics
        total_chunks = len(merged_results)
        compliant_chunks = sum(1 for r in merged_results if r["gap_analysis"]["classification"] == "COMPLIANT")
        partial_chunks = sum(1 for r in merged_results if r["gap_analysis"]["classification"] == "PARTIAL")
        missing_chunks = sum(1 for r in merged_results if r["gap_analysis"]["classification"] == "MISSING")
        
        # Calculate overall compliance score
        overall_compliance_score = (compliant_chunks * 100 + partial_chunks * 50) / total_chunks if total_chunks > 0 else 0
        
        # Extract top gaps
        all_gaps = []
        for result in merged_results:
            all_gaps.extend(result["gap_analysis"]["gaps"])
        
        # Simple approach to find most common gaps (could be improved with NLP)
        gap_frequency = {}
        for gap in all_gaps:
            key_words = gap.split()[:3]  # Use first 3 words as key
            key = " ".join(key_words)
            gap_frequency[key] = gap_frequency.get(key, 0) + 1
        
        top_gaps = sorted(gap_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
        top_gaps = [gap[0] for gap in top_gaps]
        
        summary = {
            "total_chunks": total_chunks,
            "compliant_chunks": compliant_chunks,
            "partial_chunks": partial_chunks,
            "missing_chunks": missing_chunks,
            "overall_compliance_score": round(overall_compliance_score, 1),
            "top_gaps": top_gaps
        }
        
        return CombinedEvaluationResponse(
            results=merged_results,
            summary=summary,
            processed_at=datetime.utcnow().isoformat() + "Z"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in policy evaluation: {str(e)}")


async def handle_evaluate_policy_file(
    file: UploadFile,
    standards: Optional[List[str]] = None,
    chunk_size: Optional[int] = 1000,
    speed: Optional[str] = "deep"
) -> CombinedEvaluationResponse:
    """
    Handle comprehensive policy evaluation request with file upload.
    
    Args:
        file: Uploaded policy file (DOCX or PDF)
        standards: List of standards to evaluate against
        chunk_size: Size of text chunks for processing
        speed: Analysis speed mode ('deep' or 'fast')
        
    Returns:
        CombinedEvaluationResponse: Results of comprehensive evaluation
        
    Raises:
        HTTPException: If file processing or policy evaluation fails
    """
    try:
        # Validate file
        validate_file_size(file)
        validate_file_type(file)
        
        # Extract text from file
        policy_content = await extract_text_from_file(file)
        
        if not policy_content.strip():
            raise HTTPException(status_code=400, detail="No text content found in the uploaded file")
        
        # Set default standards if none provided
        if standards is None:
            standards = ["ISO 27001", "NIST", "GDPR"]
        
        # Create request object and delegate to text handler
        request = PolicyEvaluationRequestWithSpeed(
            policy_content=policy_content,
            standards=standards,
            chunk_size=chunk_size,
            speed=speed
        )
        
        return await handle_evaluate_policy(request)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file for policy evaluation: {str(e)}")


async def handle_fast_analyze_policy(request: PolicyEvaluationRequest) -> FastAnalysisResponse:
    """
    Handle fast policy analysis request.
    
    Args:
        request: Policy evaluation request
        
    Returns:
        FastAnalysisResponse: Results of fast analysis
        
    Raises:
        HTTPException: If fast analysis fails
    """
    try:
        results = fast_policy_evaluation(request.policy_content, request.standards)
        return FastAnalysisResponse(results=results, speed="fast")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in fast policy analysis: {str(e)}")


async def handle_fast_analyze_policy_file(
    file: UploadFile,
    standards: Optional[List[str]] = None,
    chunk_size: Optional[int] = 1000
) -> FastAnalysisResponse:
    """
    Handle fast policy analysis request with file upload.
    
    Args:
        file: Uploaded policy file (DOCX or PDF)
        standards: List of standards to evaluate against
        chunk_size: Size of text chunks for processing
        
    Returns:
        FastAnalysisResponse: Results of fast analysis
        
    Raises:
        HTTPException: If file processing or fast analysis fails
    """
    try:
        # Validate file
        validate_file_size(file)
        validate_file_type(file)
        
        # Extract text from file
        policy_content = await extract_text_from_file(file)
        
        if not policy_content.strip():
            raise HTTPException(status_code=400, detail="No text content found in the uploaded file")
        
        # Set default standards if none provided
        if standards is None:
            standards = ["ISO 27001", "NIST", "GDPR"]
        
        # Process the policy
        results = fast_policy_evaluation(policy_content, standards)
        return FastAnalysisResponse(results=results, speed="fast")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file for fast policy analysis: {str(e)}")
