"""Confidence scoring utilities."""

from src.constants import (
    BASE_CONFIDENCE,
    CONFIDENCE_LONG_ANSWER_THRESHOLD,
    CONFIDENCE_SHORT_ANSWER_THRESHOLD,
    CONFIDENCE_MIN_CHUNKS_THRESHOLD,
    CONFIDENCE_BOOST_LONG,
    CONFIDENCE_PENALTY_SHORT,
    CONFIDENCE_BOOST_MANY_CHUNKS,
    CONFIDENCE_PENALTY_FEW_CHUNKS,
    CONFIDENCE_PENALTY_UNCERTAINTY,
    UNCERTAINTY_PHRASES
)


def estimate_confidence(answer: str, num_chunks: int) -> float:
    """
    Estimate confidence score based on heuristics.
    
    Args:
        answer: Generated answer text.
        num_chunks: Number of retrieved chunks.
        
    Returns:
        Confidence score between 0.0 and 1.0.
    """
    confidence = BASE_CONFIDENCE
    
    # Adjust based on answer length
    confidence += _get_length_adjustment(answer)
    
    # Adjust based on number of chunks
    confidence += _get_chunk_count_adjustment(num_chunks)
    
    # Check for uncertainty phrases
    if _contains_uncertainty(answer):
        confidence -= CONFIDENCE_PENALTY_UNCERTAINTY
    
    # Clamp to [0.0, 1.0]
    return max(0.0, min(1.0, confidence))


def _get_length_adjustment(answer: str) -> float:
    """Get confidence adjustment based on answer length."""
    answer_length = len(answer)
    
    if answer_length > CONFIDENCE_LONG_ANSWER_THRESHOLD:
        return CONFIDENCE_BOOST_LONG
    elif answer_length < CONFIDENCE_SHORT_ANSWER_THRESHOLD:
        return -CONFIDENCE_PENALTY_SHORT
    
    return 0.0


def _get_chunk_count_adjustment(num_chunks: int) -> float:
    """Get confidence adjustment based on number of chunks."""
    if num_chunks >= CONFIDENCE_MIN_CHUNKS_THRESHOLD:
        return CONFIDENCE_BOOST_MANY_CHUNKS
    elif num_chunks == 1:
        return -CONFIDENCE_PENALTY_FEW_CHUNKS
    
    return 0.0


def _contains_uncertainty(answer: str) -> bool:
    """Check if answer contains uncertainty phrases."""
    answer_lower = answer.lower()
    return any(phrase in answer_lower for phrase in UNCERTAINTY_PHRASES)
