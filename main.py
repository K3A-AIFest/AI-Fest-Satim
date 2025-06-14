"""
FastAPI server for policy evaluation endpoints.

This module provides the API endpoints for:
1. Gap identification - identify missing elements in policies
2. Compliance checking - evaluate compliance of policies against standards
3. Policy enhancement - suggest improvements for policies
"""
import os
import json
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from pipelines.policy_evaluation import identify_gaps, check_compliance, enhance_policy

# Initialize FastAPI app
app = FastAPI(
    title="Policy Evaluation API",
    description="API for evaluating security policies against standards",
    version="1.0.0",
)

# Define request and response models
class PolicyEvaluationRequest(BaseModel):
    """Request model for policy evaluation endpoints."""
    policy: str = Field(..., description="The policy document text to evaluate")
    standards: List[str] = Field(..., description="List of standard documents to evaluate against")

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

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Gap identification endpoint
@app.post("/api/v1/identify-gaps", response_model=GapAnalysisResponse, tags=["Policy Evaluation"])
async def gap_identification(request: PolicyEvaluationRequest):
    """
    Identify gaps in a policy compared to standards.
    
    This endpoint analyzes a policy document to identify missing elements when compared to standards.
    """
    try:
        results = identify_gaps(request.policy, request.standards)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in gap identification: {str(e)}")

# Compliance checking endpoint
@app.post("/api/v1/check-compliance", response_model=ComplianceCheckResponse, tags=["Policy Evaluation"])
async def compliance_checking(request: PolicyEvaluationRequest):
    """
    Check compliance of a policy against standards.
    
    This endpoint evaluates how well a policy complies with the requirements in standards.
    """
    try:
        results = check_compliance(request.policy, request.standards)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in compliance checking: {str(e)}")

# Policy enhancement endpoint
@app.post("/api/v1/enhance-policy", response_model=PolicyEnhancementResponse, tags=["Policy Evaluation"])
async def policy_enhancement(request: PolicyEvaluationRequest):
    """
    Enhance a policy based on standards.
    
    This endpoint suggests improvements for a policy to better align with standards.
    """
    try:
        results = enhance_policy(request.policy, request.standards)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in policy enhancement: {str(e)}")

# Combined evaluation endpoint
@app.post("/api/v1/evaluate-policy", response_model=CombinedEvaluationResponse, tags=["Policy Evaluation"])
async def evaluate_policy(request: PolicyEvaluationRequest):
    """
    Perform a comprehensive evaluation of a policy against standards.
    
    This endpoint combines gap identification, compliance checking, and policy enhancement
    into a single comprehensive evaluation, with results merged by policy chunk.
    """
    try:
        # Get all individual analysis results
        gap_results = identify_gaps(request.policy, request.standards)
        compliance_results = check_compliance(request.policy, request.standards)
        enhancement_results = enhance_policy(request.policy, request.standards)
        
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
            
        return {"results": merged_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in policy evaluation: {str(e)}")

# Serve the application
if __name__ == "__main__":
    import uvicorn
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8000))
    # Run the server
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info", reload=True)
