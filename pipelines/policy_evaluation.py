"""
Policy evaluation orchestrator that coordinates the workflow between expert agents.

This module contains the main pipeline for policy evaluation against standards:
1. Split policies into chunks
2. For each chunk, run gap analysis
3. For each chunk, run compliance check
4. For each chunk, generate enhancement recommendations
5. Combine results into a structured output
"""
import json
from typing import List, Dict, Any, Optional
from agents.expert_agents import GapCheckerAgent, ComplianceCheckerAgent, PolicyEnhancerAgent
from tools.vector_db import fetch_relevant_policies, fetch_relevant_standards, rewrite_query
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PolicyEvaluationPipeline:
    """
    Orchestrates the policy evaluation process using expert agents.
    """
    
    def __init__(self):
        """
        Initialize the pipeline with expert agents.
        """
        self.gap_checker = GapCheckerAgent()
        self.compliance_checker = ComplianceCheckerAgent()
        self.policy_enhancer = PolicyEnhancerAgent()
        logger.info("Policy evaluation pipeline initialized with expert agents")
    
    def chunk_policy(self, policy_content: str, chunk_size: int = 1000) -> List[str]:
        """
        Split a policy document into manageable chunks for evaluation.
        
        Args:
            policy_content: Full policy document text
            chunk_size: Approximate size of each chunk in characters
            
        Returns:
            List of policy chunks
        """
        # Simple chunking by paragraphs first
        paragraphs = policy_content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        logger.info(f"Split policy into {len(chunks)} chunks")
        return chunks
    
    def get_relevant_standards(self, policy_chunk: str) -> List[str]:
        """
        Retrieve standards relevant to a policy chunk.
        
        Args:
            policy_chunk: A section of a policy document
            
        Returns:
            List of relevant standard sections
        """
        # Rewrite the query to better match the standards
        enhanced_query = rewrite_query(policy_chunk)
        
        # Fetch relevant standards
        standards_results = fetch_relevant_standards(enhanced_query, top_k=5)
        
        # Extract the content
        standards = [result["content"] for result in standards_results]
        
        return standards
    
    def evaluate_policy_chunk(self, policy_chunk: str, standards: List[str]) -> Dict[str, Any]:
        """
        Evaluate a single policy chunk against standards.
        
        Args:
            policy_chunk: A section of a policy document
            standards: List of relevant standard sections
            
        Returns:
            Evaluation results including gap analysis, compliance check, and enhancement suggestions
        """
        logger.info("Starting policy chunk evaluation")
        
        # Step 1: Identify gaps
        logger.info("Performing gap analysis")
        gap_analysis = self.gap_checker.analyze_gaps(policy_chunk, standards)
        
        # Step 2: Check compliance
        logger.info("Checking compliance")
        compliance_assessment = self.compliance_checker.check_compliance(policy_chunk, standards)
        
        # Step 3: Suggest enhancements
        logger.info("Generating enhancement suggestions")
        enhancement = self.policy_enhancer.enhance_policy(
            policy_chunk, 
            gap_analysis, 
            compliance_assessment, 
            standards
        )
        
        # Combine results
        result = {
            "chunk_content": policy_chunk,
            "gap_analysis": gap_analysis,
            "compliance_assessment": compliance_assessment,
            "enhancement": enhancement
        }
        
        logger.info("Policy chunk evaluation complete")
        return result
    
    def evaluate_policy(self, policy_content: str, standards_content: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Evaluate an entire policy document against standards.
        
        Args:
            policy_content: Full policy document text
            standards_content: Optional list of specific standards to evaluate against
                             (if None, relevant standards will be retrieved automatically)
            
        Returns:
            List of evaluation results for each policy chunk
        """
        logger.info("Starting policy evaluation")
        
        # Split policy into manageable chunks
        policy_chunks = self.chunk_policy(policy_content)
        
        results = []
        
        # Process each chunk
        for i, chunk in enumerate(policy_chunks):
            logger.info(f"Processing chunk {i+1}/{len(policy_chunks)}")
            
            # Get relevant standards if not provided
            chunk_standards = standards_content if standards_content else self.get_relevant_standards(chunk)
            
            # Evaluate this chunk
            chunk_result = self.evaluate_policy_chunk(chunk, chunk_standards)
            results.append(chunk_result)
        
        logger.info(f"Policy evaluation complete: {len(results)} chunks processed")
        return results
    
    def evaluate_policy_fast(self, policy_content: str, standards_content: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Perform a fast evaluation of a policy document against standards.
        
        This method is optimized for speed by:
        1. Using larger chunks to reduce the number of API calls
        2. Sampling representative chunks rather than processing the entire document
        3. Focusing only on critical gap identification
        
        Args:
            policy_content: Full policy document text
            standards_content: Optional list of specific standards to evaluate against
                             (if None, relevant standards will be retrieved automatically)
            
        Returns:
            List of fast evaluation results for representative policy chunks
        """
        logger.info("Starting fast policy evaluation")
        
        # Split policy into larger chunks for faster processing
        # Using 2x the size of normal chunks to reduce processing time
        policy_chunks = self.chunk_policy(policy_content, chunk_size=2000)
        
        # If there are many chunks, sample a representative subset
        # Take first, middle, and last chunks plus random samples in between
        if len(policy_chunks) > 5:
            sampled_indices = set()
            # Always include first and last chunks
            sampled_indices.add(0)
            sampled_indices.add(len(policy_chunks) - 1)
            
            # Add middle chunk
            middle_idx = len(policy_chunks) // 2
            sampled_indices.add(middle_idx)
            
            # Add up to 2 more chunks randomly if available
            import random
            remaining_indices = set(range(1, len(policy_chunks) - 1)) - sampled_indices
            additional_samples = min(2, len(remaining_indices))
            if additional_samples > 0 and remaining_indices:
                sampled_indices.update(random.sample(remaining_indices, additional_samples))
            
            # Get the sampled chunks in order
            sampled_chunks = [policy_chunks[i] for i in sorted(sampled_indices)]
            logger.info(f"Sampled {len(sampled_chunks)} chunks out of {len(policy_chunks)} for fast analysis")
            policy_chunks = sampled_chunks
        
        results = []
        
        # Process each chunk
        for i, chunk in enumerate(policy_chunks):
            logger.info(f"Fast processing chunk {i+1}/{len(policy_chunks)}")
            
            # Get relevant standards if not provided
            chunk_standards = standards_content if standards_content else self.get_relevant_standards(chunk)
            
            # Only perform gap analysis for fast mode
            logger.info("Performing quick gap analysis")
            gap_analysis = self.gap_checker.analyze_gaps(chunk, chunk_standards)
            
            # Create simplified result with just gap analysis
            result = {
                "chunk_content": chunk,
                "gap_analysis": gap_analysis,
                "is_fast_analysis": True
            }
            
            results.append(result)
        
        logger.info(f"Fast policy evaluation complete: {len(results)} chunks processed")
        return results


# Functions for the three main tasks

def identify_gaps(policy: str, standards: List[str]) -> List[Dict[str, Any]]:
    """
    Identify gaps in a policy compared to standards.
    
    Args:
        policy: Policy document text
        standards: List of standard documents
        
    Returns:
        List of gap analysis results with a simplified structure:
        - classification: Overall categorization of the chunk
        - original_content: Original policy content that was analyzed
        - gaps: List of specific gaps identified
        - rationale: Explanation of the gap analysis
        - references: Relevant references from standards
    """
    pipeline = PolicyEvaluationPipeline()
    evaluation_results = pipeline.evaluate_policy(policy, standards)
    
    # Extract gap analysis with a cleaner, more structured format
    gap_results = []
    for result in evaluation_results:
        try:
            # The gap_analysis is already a dictionary from the agent
            gap_analysis = result["gap_analysis"]
            
            # Create simplified, structured output
            gap_result = {
                "classification": gap_analysis.get("classification", "UNKNOWN"),
                "original_content": result["chunk_content"],
                "gaps": gap_analysis.get("gaps", []),
                "rationale": gap_analysis.get("rationale", ""),
                "references": gap_analysis.get("references", [])
            }
            
            gap_results.append(gap_result)
        except (KeyError, AttributeError, TypeError) as e:
            logger.error(f"Error processing gap analysis result: {e}")
            gap_results.append({
                "classification": "ERROR",
                "original_content": result["chunk_content"],
                "gaps": [],
                "rationale": f"Error processing result: {str(e)}",
                "references": []
            })
    
    return gap_results

def check_compliance(policy: str, standards: List[str]) -> List[Dict[str, Any]]:
    """
    Check compliance of a policy against standards.
    
    Args:
        policy: Policy document text
        standards: List of standard documents
        
    Returns:
        List of compliance assessments with a simplified structure:
        - classification: Overall compliance status
        - original_content: Original policy content that was analyzed
        - issues: List of identified compliance issues
        - rationale: Explanation of the compliance assessment
        - references: Relevant references from standards
    """
    pipeline = PolicyEvaluationPipeline()
    evaluation_results = pipeline.evaluate_policy(policy, standards)
    
    # Extract compliance assessment with a cleaner, more structured format
    compliance_results = []
    for result in evaluation_results:
        try:
            # The compliance_assessment is already a dictionary from the agent
            compliance_assessment = result["compliance_assessment"]
            
            # Create simplified, structured output
            compliance_result = {
                "classification": compliance_assessment.get("classification", "UNKNOWN"),
                "original_content": result["chunk_content"],
                "issues": compliance_assessment.get("issues", []),
                "rationale": compliance_assessment.get("rationale", ""),
                "references": compliance_assessment.get("references", [])
            }
            
            compliance_results.append(compliance_result)
        except (KeyError, AttributeError, TypeError) as e:
            logger.error(f"Error processing compliance assessment result: {e}")
            compliance_results.append({
                "classification": "ERROR",
                "original_content": result["chunk_content"],
                "issues": [],
                "rationale": f"Error processing result: {str(e)}",
                "references": []
            })
    
    return compliance_results

def enhance_policy(policy: str, standards: List[str]) -> List[Dict[str, Any]]:
    """
    Enhance a policy based on standards.
    
    Args:
        policy: Policy document text
        standards: List of standard documents
        
    Returns:
        List of enhancement results with a simplified structure:
        - classification: Overall assessment category
        - original_content: Original policy content that was analyzed
        - enhanced_version: Improved version of the policy
        - changes: List of specific changes/enhancements made
        - rationale: Explanation of why these enhancements were made
    """
    pipeline = PolicyEvaluationPipeline()
    evaluation_results = pipeline.evaluate_policy(policy, standards)
    
    # Extract enhancement with a cleaner, more structured format
    enhancement_results = []
    for result in evaluation_results:
        try:
            # The enhancement is already a dictionary from the agent
            enhancement = result["enhancement"]
            
            # Create simplified, structured output
            enhancement_result = {
                "classification": enhancement.get("classification", "UNKNOWN"),
                "original_content": result["chunk_content"],
                "enhanced_version": enhancement.get("enhanced_content", ""),
                "changes": enhancement.get("changes", []),
                "rationale": enhancement.get("rationale", "")
            }
            
            enhancement_results.append(enhancement_result)
        except (KeyError, AttributeError, TypeError) as e:
            logger.error(f"Error processing enhancement result: {e}")
            enhancement_results.append({
                "classification": "ERROR",
                "original_content": result["chunk_content"],
                "enhanced_version": result["chunk_content"],
                "changes": [],
                "rationale": f"Error processing result: {str(e)}"
            })
    
    return enhancement_results

def fast_policy_evaluation(policy: str, standards: List[str]) -> List[Dict[str, Any]]:
    """
    Perform a fast evaluation of a policy against standards.
    
    This function provides a simplified and faster analysis using several optimization techniques:
    1. Uses larger chunks (2000 chars vs 1000 chars) to reduce the number of processing units
    2. Samples representative chunks rather than processing the entire document
    3. Focuses only on critical gaps rather than full compliance assessment
    4. Skips the enhancement generation step
    
    This mode is ideal for:
    - Initial quick assessment of a policy
    - Processing very large policy documents
    - When time constraints require rapid feedback
    - Preliminary screening before a deep analysis
    
    Args:
        policy: Policy document text
        standards: List of standard documents
        
    Returns:
        List of gap analysis results with a simplified structure:
        - classification: Overall categorization of the chunk
        - original_content: Original policy content that was analyzed
        - gaps: List of specific gaps identified
        - rationale: Explanation of the gap analysis
        - references: Relevant references from standards
        - speed: Indication this was a fast analysis
    """
    pipeline = PolicyEvaluationPipeline()
    evaluation_results = pipeline.evaluate_policy_fast(policy, standards)
    
    # Extract gap analysis with a cleaner, more structured format
    gap_results = []
    for result in evaluation_results:
        try:
            # The gap_analysis is already a dictionary from the agent
            gap_analysis = result["gap_analysis"]
            
            # Create simplified, structured output
            gap_result = {
                "classification": gap_analysis.get("classification", "UNKNOWN"),
                "original_content": result["chunk_content"],
                "gaps": gap_analysis.get("gaps", []),
                "rationale": gap_analysis.get("rationale", ""),
                "references": gap_analysis.get("references", []),
                "speed": "fast"
            }
            
            gap_results.append(gap_result)
        except (KeyError, AttributeError, TypeError) as e:
            logger.error(f"Error processing fast analysis result: {e}")
            gap_results.append({
                "classification": "ERROR",
                "original_content": result["chunk_content"],
                "gaps": [],
                "rationale": f"Error processing result: {str(e)}",
                "references": [],
                "speed": "fast"
            })
    
    return gap_results
