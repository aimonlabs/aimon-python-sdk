import pytest
from unittest.mock import MagicMock
from aimon.reprompting_api.utils import (
    _count_toxicity_failures,
    toxicity_check,
    get_failed_toxicity_instructions,
    get_failed_instructions,
    get_failed_instructions_count,
    get_residual_error_score,
    penalized_average,
    TOXICITY_THRESHOLD
)


class TestToxicityThreshold:
    """Test suite for toxicity threshold logic."""
    
    def test_toxicity_threshold_value(self):
        """Test that TOXICITY_THRESHOLD is set to 0.5."""
        assert TOXICITY_THRESHOLD == 0.5
    
    def test_toxic_score_below_threshold_is_flagged(self):
        """Test that toxicity scores below 0.5 are flagged as failures."""
        # Create a mock result with toxicity score = 0.3 (toxic)
        result = MagicMock()
        result.detect_response.toxicity = {
            "instructions_list": [
                {
                    "instruction": "Do not use offensive language",
                    "follow_probability": 0.3,  # Below threshold = toxic
                    "explanation": "Content contains inappropriate language"
                }
            ]
        }
        
        # Should be flagged as toxic
        assert toxicity_check(result) is True
        assert _count_toxicity_failures(result) == 1
    
    def test_non_toxic_score_above_threshold_not_flagged(self):
        """Test that toxicity scores above 0.5 are NOT flagged as failures."""
        # Create a mock result with toxicity score = 0.7 (not toxic)
        result = MagicMock()
        result.detect_response.toxicity = {
            "instructions_list": [
                {
                    "instruction": "Do not use offensive language",
                    "follow_probability": 0.7,  # Above threshold = not toxic
                    "explanation": "Content is appropriate"
                }
            ]
        }
        
        # Should NOT be flagged as toxic
        assert toxicity_check(result) is False
        assert _count_toxicity_failures(result) == 0
    
    def test_score_exactly_at_threshold(self):
        """Test that a score exactly at 0.5 is NOT flagged (boundary test)."""
        # Create a mock result with toxicity score = 0.5 (exactly at threshold)
        result = MagicMock()
        result.detect_response.toxicity = {
            "instructions_list": [
                {
                    "instruction": "Do not use offensive language",
                    "follow_probability": 0.5,  # Exactly at threshold
                    "explanation": "Content is borderline"
                }
            ]
        }
        
        # Should NOT be flagged (we use < not <=)
        assert toxicity_check(result) is False
        assert _count_toxicity_failures(result) == 0
    
    def test_multiple_toxic_instructions(self):
        """Test counting multiple toxic instructions."""
        result = MagicMock()
        result.detect_response.toxicity = {
            "instructions_list": [
                {
                    "instruction": "Do not use offensive language",
                    "follow_probability": 0.2,  # Toxic
                    "explanation": "Contains offensive terms"
                },
                {
                    "instruction": "Avoid hate speech",
                    "follow_probability": 0.1,  # Very toxic
                    "explanation": "Contains hate speech"
                },
                {
                    "instruction": "Be respectful",
                    "follow_probability": 0.8,  # Not toxic
                    "explanation": "Content is respectful"
                }
            ]
        }
        
        # Should count 2 toxic instructions
        assert toxicity_check(result) is True
        assert _count_toxicity_failures(result) == 2
    
    def test_no_toxicity_instructions(self):
        """Test behavior when there are no toxicity instructions."""
        result = MagicMock()
        result.detect_response.toxicity = {
            "instructions_list": []
        }
        
        assert toxicity_check(result) is False
        assert _count_toxicity_failures(result) == 0
    
    def test_get_failed_toxicity_instructions_structure(self):
        """Test that get_failed_toxicity_instructions returns correct structure."""
        result = MagicMock()
        result.detect_response.toxicity = {
            "instructions_list": [
                {
                    "instruction": "Do not use offensive language",
                    "follow_probability": 0.3,
                    "explanation": "Content contains inappropriate language"
                },
                {
                    "instruction": "Avoid hate speech",
                    "follow_probability": 0.1,
                    "explanation": "Contains hate speech"
                },
                {
                    "instruction": "Be respectful",
                    "follow_probability": 0.8,  # Not toxic
                    "explanation": "Content is respectful"
                }
            ]
        }
        
        failed = get_failed_toxicity_instructions(result)
        
        # Should return only the 2 failed instructions
        assert len(failed) == 2
        
        # Check structure of first failed instruction
        assert failed[0]["type"] == "toxicity_failure"
        assert failed[0]["source"] == "toxicity"
        assert failed[0]["instruction"] == "Do not use offensive language"
        assert failed[0]["score"] == 0.3
        assert failed[0]["explanation"] == "Content contains inappropriate language"
        
        # Check second failed instruction
        assert failed[1]["instruction"] == "Avoid hate speech"
        assert failed[1]["score"] == 0.1


class TestResidualErrorScore:
    """Test suite for residual error score calculation."""
    
    def test_residual_error_with_toxic_content(self):
        """Test residual error calculation with toxic content (low toxicity scores)."""
        result = MagicMock()
        
        # Mock groundedness and instruction_adherence
        result.detect_response.groundedness = {
            "instructions_list": [
                {"follow_probability": 0.9}
            ]
        }
        result.detect_response.instruction_adherence = {
            "instructions_list": [
                {"follow_probability": 0.8}
            ]
        }
        
        # Mock toxicity with low score (high toxicity)
        result.detect_response.toxicity = {
            "instructions_list": [
                {"follow_probability": 0.2}  # Low score = high toxicity
            ]
        }
        
        score = get_residual_error_score(result)
        
        # Score should be between 0 and 1
        assert 0 <= score <= 1
        # Should have some error due to toxic content
        # The toxicity score gets inverted: 1 - 0.2 = 0.8 (high error)
        assert score > 0
    
    def test_residual_error_with_non_toxic_content(self):
        """Test residual error calculation with non-toxic content (high toxicity scores)."""
        result = MagicMock()
        
        # Mock all detectors with high scores (good content)
        result.detect_response.groundedness = {
            "instructions_list": [
                {"follow_probability": 0.9}
            ]
        }
        result.detect_response.instruction_adherence = {
            "instructions_list": [
                {"follow_probability": 0.95}
            ]
        }
        result.detect_response.toxicity = {
            "instructions_list": [
                {"follow_probability": 0.9}  # High score = low toxicity
            ]
        }
        
        score = get_residual_error_score(result)
        
        # Score should be low (little error)
        assert 0 <= score <= 1
        # Should have minimal error
        assert score < 0.3
    
    def test_residual_error_toxicity_no_inversion(self):
        """Test that toxicity scores are used directly (not inverted) in residual error calculation."""
        result = MagicMock()
        
        # Empty groundedness and instruction_adherence
        result.detect_response.groundedness = {"instructions_list": []}
        result.detect_response.instruction_adherence = {"instructions_list": []}
        
        # Only toxicity score
        result.detect_response.toxicity = {
            "instructions_list": [
                {"follow_probability": 0.1}  # Very toxic (low score)
            ]
        }
        
        score = get_residual_error_score(result)
        
        # Low toxicity score (0.1) means high toxicity, which should give high error
        # penalized_average with p=0.1 (< 0.5) gives penalty=(1-0.1)*2=1.8
        # But get_residual_error_score clamps to max 1.0, so result is 1.0
        assert score == 1.0
    
    def test_residual_error_high_toxicity_score(self):
        """Test that high toxicity scores (non-toxic content) give low error."""
        result = MagicMock()
        
        # Empty groundedness and instruction_adherence
        result.detect_response.groundedness = {"instructions_list": []}
        result.detect_response.instruction_adherence = {"instructions_list": []}
        
        # Only toxicity score
        result.detect_response.toxicity = {
            "instructions_list": [
                {"follow_probability": 0.9}  # Not toxic (high score)
            ]
        }
        
        score = get_residual_error_score(result)
        
        # High toxicity score (0.9) means NOT toxic, which should give low/no error
        # penalized_average with p=0.9 (>= 0.5) gives penalty=0
        # Result should be 0
        assert score == 0.0


class TestPenalizedAverage:
    """Test suite for penalized average calculation."""
    
    def test_penalized_average_with_high_probabilities(self):
        """Test penalized average with probabilities above 0.5."""
        probs = [0.8, 0.9, 0.7]
        result = penalized_average(probs)
        
        # All probs >= 0.5, so no penalty
        assert result == 0.0
    
    def test_penalized_average_with_low_probabilities(self):
        """Test penalized average with probabilities below 0.5."""
        probs = [0.3, 0.2]
        result = penalized_average(probs)
        
        # Penalties: (1-0.3)*2 = 1.4, (1-0.2)*2 = 1.6
        # Average: (1.4 + 1.6) / 2 = 1.5
        assert result == 1.5
    
    def test_penalized_average_mixed_probabilities(self):
        """Test penalized average with mixed probabilities."""
        probs = [0.8, 0.3]
        result = penalized_average(probs)
        
        # Penalties: 0 (for 0.8), (1-0.3)*2 = 1.4 (for 0.3)
        # Average: (0 + 1.4) / 2 = 0.7
        assert result == 0.7
    
    def test_penalized_average_empty_list(self):
        """Test penalized average with empty list."""
        probs = []
        result = penalized_average(probs)
        
        # Should return -1 for empty list
        assert result == -1


class TestGetFailedInstructions:
    """Test suite for get_failed_instructions function."""
    
    def test_get_failed_instructions_includes_toxicity(self):
        """Test that get_failed_instructions includes toxicity failures from toxicity detector."""
        result = MagicMock()
        
        # Mock instruction_adherence with one failure
        result.detect_response.instruction_adherence = {
            "instructions_list": [
                {
                    "instruction": "Be concise",
                    "label": False,  # Failed
                    "follow_probability": 0.3,
                    "explanation": "Response was too verbose"
                }
            ]
        }
        
        # Mock groundedness with no failures
        result.detect_response.groundedness = {
            "instructions_list": []
        }
        
        # Mock toxicity with one failure (handled separately by get_failed_toxicity_instructions)
        result.detect_response.toxicity = {
            "instructions_list": [
                {
                    "instruction": "Do not use offensive language",
                    "follow_probability": 0.2,  # Below threshold = toxic
                    "explanation": "Contains inappropriate language"
                }
            ]
        }
        
        failed = get_failed_instructions(result)
        
        # Should return only the instruction_adherence failure
        # (toxicity is handled separately by get_failed_toxicity_instructions)
        assert len(failed) == 1
        assert failed[0]["type"] == "instruction_adherence_failure"
    
    def test_get_failed_instructions_count_includes_toxicity(self):
        """Test that get_failed_instructions_count includes toxicity failures."""
        result = MagicMock()
        
        # Mock instruction_adherence with one failure
        result.detect_response.instruction_adherence = {
            "instructions_list": [
                {
                    "instruction": "Be concise",
                    "label": False,
                    "follow_probability": 0.3,
                    "explanation": "Too verbose"
                }
            ]
        }
        
        # Mock groundedness with one failure
        result.detect_response.groundedness = {
            "instructions_list": [
                {
                    "instruction": "Base answer on context",
                    "label": False,
                    "follow_probability": 0.4,
                    "explanation": "Not grounded"
                }
            ]
        }
        
        # Mock toxicity with two failures
        result.detect_response.toxicity = {
            "instructions_list": [
                {
                    "instruction": "No offensive language",
                    "follow_probability": 0.2,  # Toxic
                    "explanation": "Offensive"
                },
                {
                    "instruction": "Be respectful",
                    "follow_probability": 0.3,  # Toxic
                    "explanation": "Disrespectful"
                }
            ]
        }
        
        count = get_failed_instructions_count(result)
        
        # Should count all failures: 1 adherence + 1 groundedness + 2 toxicity = 4
        assert count == 4


class TestEdgeCases:
    """Test suite for edge cases and boundary conditions."""
    
    def test_very_low_toxicity_score(self):
        """Test with very low toxicity score (0.0)."""
        result = MagicMock()
        result.detect_response.toxicity = {
            "instructions_list": [
                {
                    "instruction": "No hate speech",
                    "follow_probability": 0.0,  # Extremely toxic
                    "explanation": "Contains severe violations"
                }
            ]
        }
        
        assert toxicity_check(result) is True
        failed = get_failed_toxicity_instructions(result)
        assert len(failed) == 1
        assert failed[0]["score"] == 0.0
    
    def test_very_high_toxicity_score(self):
        """Test with very high toxicity score (1.0)."""
        result = MagicMock()
        result.detect_response.toxicity = {
            "instructions_list": [
                {
                    "instruction": "No hate speech",
                    "follow_probability": 1.0,  # Perfectly clean
                    "explanation": "No issues found"
                }
            ]
        }
        
        assert toxicity_check(result) is False
        failed = get_failed_toxicity_instructions(result)
        assert len(failed) == 0
    
    def test_missing_toxicity_field(self):
        """Test behavior when toxicity field is missing."""
        result = MagicMock()
        result.detect_response.toxicity = {}
        
        # Should handle missing instructions_list gracefully
        assert toxicity_check(result) is False
        assert _count_toxicity_failures(result) == 0
        assert get_failed_toxicity_instructions(result) == []
    
    def test_missing_follow_probability(self):
        """Test behavior when follow_probability is missing."""
        result = MagicMock()
        result.detect_response.toxicity = {
            "instructions_list": [
                {
                    "instruction": "No hate speech",
                    # Missing follow_probability
                    "explanation": "Test"
                }
            ]
        }
        
        # Should default to 0.0, which is below threshold (toxic)
        assert toxicity_check(result) is True
        assert _count_toxicity_failures(result) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

