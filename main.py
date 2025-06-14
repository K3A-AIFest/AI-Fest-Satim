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
@app.post("/api/v1/evaluate-policy", tags=["Policy Evaluation"])
async def evaluate_policy(request: PolicyEvaluationRequest):
    """
    Perform a comprehensive evaluation of a policy against standards.
    
    This endpoint combines gap identification, compliance checking, and policy enhancement
    into a single comprehensive evaluation.
    """
    try:
        gap_results = identify_gaps(request.policy, request.standards)
        compliance_results = check_compliance(request.policy, request.standards)
        enhancement_results = enhance_policy(request.policy, request.standards)
        
        return {
            "gaps": gap_results,
            "compliance": compliance_results,
            "enhancements": enhancement_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in policy evaluation: {str(e)}")

# Serve the application
if __name__ == "__main__":
    import uvicorn
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8000))
    # Run the server
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info", reload=True)
