"""
Test script for policy evaluation endpoint.

This script tests the /api/v1/evaluate-policy endpoint by:
1. Fetching a real policy from the vector database
2. Sending it to the endpoint
3. Saving the output to a JSON file
"""
import os
import json
import asyncio
import httpx
from datetime import datetime
from tools.vector_db import fetch_relevant_policies


async def test_policy_evaluation():
    """Test the policy evaluation endpoint using a real policy from the vector database."""
    
    # 1. Fetch a policy from the vector database
    print("Fetching policy from vector database...")
    
    # Using the Information Security Policy as our search query
    query = "Information Security Policy"
    
    # Fetch the policy content from the vector database
    policy_chunks = fetch_relevant_policies(query, top_k=20)
    
    # Extract the most relevant chunk and policy name
    if not policy_chunks:
        print("Error: No policy found in the vector database")
        return
    
    # Get the policy name from metadata
    policy_name = policy_chunks[0].get("metadata", {}).get("file_name", "Unknown Policy")
    print(f"Using policy: {policy_name}")
    
    # Combine all chunks from the same policy into a single document
    full_policy_content = "\n\n".join([chunk["content"] for chunk in policy_chunks])
    
    # 2. Send the policy to the evaluate-policy endpoint
    print("Sending policy to evaluation endpoint...")
    
    # Prepare the request payload
    payload = {
        "policy_content": full_policy_content,
        "standards": ["ISO 27001", "NIST"],  # You can customize this list
        "chunk_size": 1000,
        "speed": "deep"  # or "fast" for quicker results
    }
    
    # Make the API call
    async with httpx.AsyncClient(timeout=300.0) as client:  # 5-minute timeout
        try:
            response = await client.post(
                "http://localhost:8000/api/v1/evaluate-policy",
                json=payload
            )
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
        except httpx.HTTPError as e:
            print(f"Error making API request: {e}")
            return
    
    # 3. Save the output to a JSON file
    print("Saving response to file...")
    
    # Create a timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    policy_filename = policy_name.replace(" ", "_").replace(".docx", "").replace(".pdf", "")
    output_filename = f"evaluation_result_{policy_filename}_{timestamp}.json"
    
    # Parse and format the JSON response
    try:
        result_data = response.json()
        
        # Add metadata for context
        result_data["test_metadata"] = {
            "timestamp": timestamp,
            "policy_name": policy_name,
            "endpoint": "/api/v1/evaluate-policy",
            "standards_used": payload["standards"],
            "speed": payload["speed"]
        }
        
        # Write to file with pretty formatting
        with open(output_filename, "w") as f:
            json.dump(result_data, f, indent=2)
        
        print(f"Evaluation results saved to: {output_filename}")
        print(f"Policy evaluated: {policy_name}")
        
        # Print a summary of the results
        chunks_evaluated = len(result_data.get("results", {}).get("gap_analysis", []))
        print(f"Number of chunks evaluated: {chunks_evaluated}")
        print("Test completed successfully.")
        
    except Exception as e:
        print(f"Error processing response: {e}")
        # Save raw response in case of error
        with open(f"raw_response_{timestamp}.json", "w") as f:
            f.write(response.text)


if __name__ == "__main__":
    asyncio.run(test_policy_evaluation())
