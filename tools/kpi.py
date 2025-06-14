"""
KPI tools for security and financial systems.

This module provides functions to calculate various Key Performance Indicators (KPIs)
related to security and deployment of information systems, especially in banking
and financial transaction contexts.
"""

from typing import Dict, List, Any, Union, Optional
import math
from datetime import datetime, timedelta


def calculate_vulnerability_management_effectiveness(
    total_vulnerabilities: int, 
    addressed_vulnerabilities: int,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Calculate vulnerability management effectiveness KPI.
    
    Args:
        total_vulnerabilities: Total number of identified vulnerabilities
        addressed_vulnerabilities: Number of vulnerabilities that have been addressed
        weights: Optional dictionary of weights for different vulnerability categories
        
    Returns:
        Dictionary with effectiveness score and details
    """
    if total_vulnerabilities == 0:
        return {
            "score": 100.0,
            "percentage": 100.0,
            "details": "No vulnerabilities identified"
        }
    
    basic_percentage = (addressed_vulnerabilities / total_vulnerabilities) * 100
    
    if not weights:
        return {
            "score": basic_percentage,
            "percentage": basic_percentage,
            "details": f"{addressed_vulnerabilities} out of {total_vulnerabilities} vulnerabilities addressed"
        }
    else:
        # Calculate weighted score based on vulnerability categories
        weighted_score = 0
        details = []
        
        for category, weight in weights.items():
            if category in weights:
                category_score = basic_percentage * weight
                weighted_score += category_score
                details.append(f"{category}: {category_score:.2f} (weight: {weight})")
                
        return {
            "score": weighted_score,
            "percentage": basic_percentage,
            "details": details,
            "summary": f"{addressed_vulnerabilities} out of {total_vulnerabilities} vulnerabilities addressed"
        }


def calculate_mean_time_to_detect(
    detection_times_hours: List[float]
) -> Dict[str, Any]:
    """
    Calculate Mean Time to Detect (MTTD) KPI.
    
    Args:
        detection_times_hours: List of detection times in hours for incidents
        
    Returns:
        Dictionary with MTTD score and details
    """
    if not detection_times_hours:
        return {
            "score": 0.0,
            "mttd_hours": 0.0,
            "details": "No detection data available"
        }
    
    mttd = sum(detection_times_hours) / len(detection_times_hours)
    
    # Convert MTTD to a score (lower MTTD is better)
    # Using a scoring function where 0 hours = 100 score, 24 hours = 50 score, 72 hours = 0 score
    score = max(0, 100 - (mttd * 100 / 72)) if mttd <= 72 else 0
    
    return {
        "score": score,
        "mttd_hours": mttd,
        "details": f"Mean Time to Detect: {mttd:.2f} hours"
    }


def calculate_mean_time_to_respond(
    response_times_hours: List[float]
) -> Dict[str, Any]:
    """
    Calculate Mean Time to Respond (MTTR) KPI.
    
    Args:
        response_times_hours: List of response times in hours for incidents
        
    Returns:
        Dictionary with MTTR score and details
    """
    if not response_times_hours:
        return {
            "score": 0.0,
            "mttr_hours": 0.0,
            "details": "No response time data available"
        }
    
    mttr = sum(response_times_hours) / len(response_times_hours)
    
    # Convert MTTR to a score (lower MTTR is better)
    # Using a scoring function where 0 hours = 100 score, 4 hours = 75 score, 24 hours = 0 score
    score = max(0, 100 - (mttr * 100 / 24)) if mttr <= 24 else 0
    
    return {
        "score": score,
        "mttr_hours": mttr,
        "details": f"Mean Time to Respond: {mttr:.2f} hours"
    }


def calculate_security_coverage_score(
    coverage_metrics: Dict[str, Dict[str, Union[float, bool]]]
) -> Dict[str, Any]:
    """
    Calculate Security Coverage Score KPI.
    
    Args:
        coverage_metrics: Dictionary of security coverage areas and their metrics
        
    Returns:
        Dictionary with security coverage score and details
    """
    if not coverage_metrics:
        return {
            "score": 0.0,
            "details": "No security coverage metrics available"
        }
    
    total_score = 0
    details = []
    
    for area, metrics in coverage_metrics.items():
        area_score = metrics.get("score", 0)
        implemented = metrics.get("implemented", False)
        
        if implemented:
            total_score += area_score
            details.append(f"{area}: {area_score:.2f} (Implemented)")
        else:
            details.append(f"{area}: 0.00 (Not Implemented)")
    
    # Normalize score to 0-100 based on number of areas
    normalized_score = total_score / len(coverage_metrics) if coverage_metrics else 0
    
    return {
        "score": normalized_score,
        "details": details,
        "coverage_areas": len(coverage_metrics)
    }


def calculate_risk_reduction_percentage(
    initial_risk_level: float,
    residual_risk_level: float
) -> Dict[str, Any]:
    """
    Calculate Risk Reduction Percentage KPI.
    
    Args:
        initial_risk_level: Initial risk level before controls (0-100)
        residual_risk_level: Residual risk level after controls (0-100)
        
    Returns:
        Dictionary with risk reduction percentage and details
    """
    if initial_risk_level <= 0:
        return {
            "score": 0.0,
            "reduction_percentage": 0.0,
            "details": "Invalid initial risk level"
        }
    
    reduction = initial_risk_level - residual_risk_level
    reduction_percentage = (reduction / initial_risk_level) * 100 if initial_risk_level > 0 else 0
    
    # Score is directly based on the reduction percentage (higher is better)
    score = reduction_percentage
    
    return {
        "score": score,
        "reduction_percentage": reduction_percentage,
        "details": f"Risk reduced from {initial_risk_level:.2f} to {residual_risk_level:.2f} ({reduction_percentage:.2f}%)"
    }


def calculate_compliance_coverage_percentage(
    requirements_covered: int,
    total_requirements: int,
    weighted_categories: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Calculate Compliance Coverage Percentage KPI.
    
    Args:
        requirements_covered: Number of compliance requirements covered
        total_requirements: Total number of applicable compliance requirements
        weighted_categories: Optional dictionary of compliance categories with weights
        
    Returns:
        Dictionary with compliance coverage percentage and details
    """
    if total_requirements == 0:
        return {
            "score": 100.0,
            "coverage_percentage": 100.0,
            "details": "No compliance requirements applicable"
        }
    
    basic_percentage = (requirements_covered / total_requirements) * 100
    
    if not weighted_categories:
        return {
            "score": basic_percentage,
            "coverage_percentage": basic_percentage,
            "details": f"{requirements_covered} out of {total_requirements} requirements covered ({basic_percentage:.2f}%)"
        }
    else:
        # Calculate weighted score based on compliance categories
        weighted_score = 0
        details = []
        
        for category, data in weighted_categories.items():
            weight = data.get("weight", 0)
            cat_covered = data.get("covered", 0)
            cat_total = data.get("total", 0)
            
            if cat_total > 0:
                cat_percentage = (cat_covered / cat_total) * 100
                cat_weighted_score = cat_percentage * weight
                weighted_score += cat_weighted_score
                details.append(f"{category}: {cat_percentage:.2f}% (weight: {weight}, weighted score: {cat_weighted_score:.2f})")
        
        return {
            "score": weighted_score,
            "coverage_percentage": basic_percentage,
            "details": details,
            "summary": f"{requirements_covered} out of {total_requirements} requirements covered ({basic_percentage:.2f}%)"
        }


def calculate_transaction_anomaly_detection_rate(
    detected_anomalies: int,
    total_anomalies: int
) -> Dict[str, Any]:
    """
    Calculate Transaction Anomaly Detection Rate KPI.
    
    Args:
        detected_anomalies: Number of detected anomalous transactions
        total_anomalies: Total number of anomalous transactions (known)
        
    Returns:
        Dictionary with anomaly detection rate and details
    """
    if total_anomalies == 0:
        return {
            "score": 100.0,
            "detection_rate": 100.0,
            "details": "No anomalies present in the dataset"
        }
    
    detection_rate = (detected_anomalies / total_anomalies) * 100
    
    return {
        "score": detection_rate,
        "detection_rate": detection_rate,
        "details": f"{detected_anomalies} out of {total_anomalies} anomalies detected ({detection_rate:.2f}%)"
    }


def calculate_false_positive_rate(
    false_positives: int,
    total_alerts: int
) -> Dict[str, Any]:
    """
    Calculate False Positive Rate KPI for security alerts.
    
    Args:
        false_positives: Number of false positive alerts
        total_alerts: Total number of alerts generated
        
    Returns:
        Dictionary with false positive rate and score (lower is better)
    """
    if total_alerts == 0:
        return {
            "score": 100.0,
            "false_positive_rate": 0.0,
            "details": "No alerts generated"
        }
    
    fp_rate = (false_positives / total_alerts) * 100
    
    # Convert FP rate to a score (lower FP rate is better)
    # 0% false positives = 100 score, 100% false positives = 0 score
    score = 100 - fp_rate
    
    return {
        "score": score,
        "false_positive_rate": fp_rate,
        "details": f"{false_positives} out of {total_alerts} alerts were false positives ({fp_rate:.2f}%)"
    }


def calculate_transaction_security_index(
    encryption_score: float,
    authentication_score: float,
    fraud_detection_score: float,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Calculate a Transaction Security Index for financial transactions.
    
    Args:
        encryption_score: Score for transaction encryption (0-100)
        authentication_score: Score for authentication methods (0-100)
        fraud_detection_score: Score for fraud detection capabilities (0-100)
        weights: Optional dictionary of weights for each component
        
    Returns:
        Dictionary with transaction security index and details
    """
    if not weights:
        weights = {
            "encryption": 0.4,
            "authentication": 0.3,
            "fraud_detection": 0.3
        }
    
    # Calculate weighted score
    weighted_score = (
        encryption_score * weights.get("encryption", 0.4) +
        authentication_score * weights.get("authentication", 0.3) +
        fraud_detection_score * weights.get("fraud_detection", 0.3)
    )
    
    details = [
        f"Encryption: {encryption_score:.2f} (weight: {weights.get('encryption', 0.4)})",
        f"Authentication: {authentication_score:.2f} (weight: {weights.get('authentication', 0.3)})",
        f"Fraud Detection: {fraud_detection_score:.2f} (weight: {weights.get('fraud_detection', 0.3)})"
    ]
    
    return {
        "score": weighted_score,
        "details": details,
        "components": {
            "encryption": encryption_score,
            "authentication": authentication_score,
            "fraud_detection": fraud_detection_score
        }
    }


def calculate_system_availability_percentage(
    downtime_minutes: float,
    period_days: int = 30
) -> Dict[str, Any]:
    """
    Calculate System Availability Percentage KPI.
    
    Args:
        downtime_minutes: Total downtime in minutes during the period
        period_days: Period in days (default: 30)
        
    Returns:
        Dictionary with availability percentage and details
    """
    total_minutes = period_days * 24 * 60
    uptime_minutes = total_minutes - downtime_minutes
    
    availability_percentage = (uptime_minutes / total_minutes) * 100 if total_minutes > 0 else 0
    
    # For financial systems, availability expectations are very high (99.9%+)
    # Convert to a score where 100% = 100, 99.9% = 90, 99% = 40, <99% = drops quickly
    if availability_percentage >= 99.99:
        score = 100
    elif availability_percentage >= 99.9:
        score = 90 + (availability_percentage - 99.9) * 100
    elif availability_percentage >= 99:
        score = 40 + (availability_percentage - 99) * 50
    else:
        score = max(0, availability_percentage - 90) * 4
    
    return {
        "score": score,
        "availability_percentage": availability_percentage,
        "details": f"System availability: {availability_percentage:.4f}% ({downtime_minutes:.2f} minutes downtime in {period_days} days)"
    }


def calculate_security_training_effectiveness(
    pre_training_score: float,
    post_training_score: float,
    completion_rate: float
) -> Dict[str, Any]:
    """
    Calculate Security Training Effectiveness KPI.
    
    Args:
        pre_training_score: Average score before training (0-100)
        post_training_score: Average score after training (0-100)
        completion_rate: Percentage of employees who completed the training
        
    Returns:
        Dictionary with training effectiveness score and details
    """
    if pre_training_score >= post_training_score:
        improvement = 0
    else:
        improvement = ((post_training_score - pre_training_score) / (100 - pre_training_score)) * 100
    
    # Weight improvement by completion rate
    weighted_improvement = improvement * (completion_rate / 100)
    
    # Score is based on both improvement and completion rate
    score = (weighted_improvement * 0.7) + (completion_rate * 0.3)
    
    return {
        "score": score,
        "improvement_percentage": improvement,
        "completion_rate": completion_rate,
        "details": f"Training improved knowledge from {pre_training_score:.2f}% to {post_training_score:.2f}% with {completion_rate:.2f}% completion rate"
    }


def calculate_fraud_detection_efficiency(
    detected_fraud_amount: float,
    total_fraud_amount: float,
    response_time_hours: float
) -> Dict[str, Any]:
    """
    Calculate Fraud Detection Efficiency KPI for banking systems.
    
    Args:
        detected_fraud_amount: Amount of fraud detected in currency units
        total_fraud_amount: Total known fraudulent amount in currency units
        response_time_hours: Average response time to fraud alerts in hours
        
    Returns:
        Dictionary with fraud detection efficiency score and details
    """
    if total_fraud_amount == 0:
        return {
            "score": 100.0,
            "detection_rate": 100.0,
            "details": "No fraud occurred during the period"
        }
    
    detection_rate = (detected_fraud_amount / total_fraud_amount) * 100
    
    # Response time score (lower is better)
    # 0 hours = 100, 1 hour = 90, 24 hours = 0
    response_time_score = max(0, 100 - (response_time_hours * 100 / 24)) if response_time_hours <= 24 else 0
    
    # Combined score (detection rate is more important)
    score = (detection_rate * 0.7) + (response_time_score * 0.3)
    
    return {
        "score": score,
        "detection_rate": detection_rate,
        "response_time_score": response_time_score,
        "details": f"Detected {detected_fraud_amount:.2f} out of {total_fraud_amount:.2f} ({detection_rate:.2f}%) with {response_time_hours:.2f} hours average response time"
    }


def calculate_encryption_strength_score(
    encryption_algorithm: str,
    key_length: int,
    data_in_transit_encrypted: bool,
    data_at_rest_encrypted: bool
) -> Dict[str, Any]:
    """
    Calculate Encryption Strength Score KPI.
    
    Args:
        encryption_algorithm: Name of encryption algorithm used
        key_length: Encryption key length in bits
        data_in_transit_encrypted: Whether data in transit is encrypted
        data_at_rest_encrypted: Whether data at rest is encrypted
        
    Returns:
        Dictionary with encryption strength score and details
    """
    # Score algorithm (algorithm strength matters)
    algorithm_scores = {
        "aes": 100,
        "rsa": 90,
        "ecc": 95,
        "3des": 60,
        "des": 20,
        "blowfish": 70,
        "twofish": 85,
        "chacha20": 90,
        "sha256": 85,
        "sha512": 95,
        "md5": 10
    }
    
    algorithm_lower = encryption_algorithm.lower()
    algorithm_score = algorithm_scores.get(algorithm_lower, 50)
    
    # Score key length (longer is better)
    key_length_score = 0
    if key_length >= 4096:
        key_length_score = 100
    elif key_length >= 2048:
        key_length_score = 90
    elif key_length >= 1024:
        key_length_score = 70
    elif key_length >= 256:
        key_length_score = 60
    elif key_length >= 128:
        key_length_score = 50
    else:
        key_length_score = 30
    
    # Score encryption coverage
    coverage_score = 0
    if data_in_transit_encrypted and data_at_rest_encrypted:
        coverage_score = 100
    elif data_in_transit_encrypted:
        coverage_score = 60
    elif data_at_rest_encrypted:
        coverage_score = 40
    
    # Combined score
    score = (algorithm_score * 0.4) + (key_length_score * 0.3) + (coverage_score * 0.3)
    
    return {
        "score": score,
        "algorithm_score": algorithm_score,
        "key_length_score": key_length_score,
        "coverage_score": coverage_score,
        "details": f"{encryption_algorithm} with {key_length}-bit key, "
                   f"Transit encryption: {'Yes' if data_in_transit_encrypted else 'No'}, "
                   f"Rest encryption: {'Yes' if data_at_rest_encrypted else 'No'}"
    }


def get_kpi_tools() -> List[Dict[str, Any]]:
    """
    Returns all KPI calculation tools for agent binding.
    
    Returns:
        List of all KPI tool definitions
    """
    kpi_tools = [
        calculate_vulnerability_management_effectiveness,
        calculate_mean_time_to_detect,
        calculate_mean_time_to_respond,
        calculate_security_coverage_score,
        calculate_risk_reduction_percentage,
        calculate_compliance_coverage_percentage,
        calculate_transaction_anomaly_detection_rate,
        calculate_false_positive_rate,
        calculate_transaction_security_index,
        calculate_system_availability_percentage,
        calculate_security_training_effectiveness,
        calculate_fraud_detection_efficiency,
        calculate_encryption_strength_score
    ]
    
    return kpi_tools
