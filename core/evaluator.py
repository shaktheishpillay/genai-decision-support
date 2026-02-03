"""
Core evaluation logic
"""

import json
from typing import Dict, Any
from core.llm import LLMClient
from core.prompts import EVALUATION_SYSTEM_PROMPT, EVALUATION_USER_PROMPT, POLICY_MODES


class DecisionEvaluator:
    def __init__(self):
        self.llm = LLMClient()
    
    def evaluate(self, ai_output: str, task_context: str, policy_mode: str = "balanced") -> Dict[str, Any]:
        """
        Evaluate an AI output and return a structured decision
        
        Args:
            ai_output: The AI-generated content to evaluate
            task_context: Description of what the AI was trying to do
            policy_mode: "strict", "balanced", or "relaxed"
        
        Returns:
            Dictionary with decision, confidence, risk_flags, etc.
        """
        
        # Build the prompt
        user_prompt = EVALUATION_USER_PROMPT.format(
            policy_mode=POLICY_MODES.get(policy_mode, POLICY_MODES["balanced"]),
            ai_output=ai_output,
            task_context=task_context
        )
        
        # Get evaluation from LLM
        try:
            response = self.llm.generate(
                system_prompt=EVALUATION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.2  # Low temperature for consistent decisions
            )
            
            # Parse JSON response
            # Sometimes the model wraps JSON in markdown code blocks, so we clean it
            cleaned_response = response.strip()
            if cleaned_response.startswith("```"):
                # Remove markdown code blocks
                cleaned_response = cleaned_response.split("```")[1]
                if cleaned_response.startswith("json"):
                    cleaned_response = cleaned_response[4:]
                cleaned_response = cleaned_response.strip()
            
            decision_data = json.loads(cleaned_response)
            
            # Validate the response has required fields
            required_fields = ["decision", "confidence", "risk_flags", "explanation", "recommended_action"]
            for field in required_fields:
                if field not in decision_data:
                    raise ValueError(f"Missing required field: {field}")
            
            return decision_data
        
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return a safe default
            return {
                "decision": "REVIEW_REQUIRED",
                "confidence": 0.0,
                "risk_flags": ["evaluation_error"],
                "explanation": f"Failed to parse evaluation response: {str(e)}",
                "recommended_action": "Manual review required due to evaluation error"
            }
        
        except Exception as e:
            return {
                "decision": "REVIEW_REQUIRED",
                "confidence": 0.0,
                "risk_flags": ["system_error"],
                "explanation": f"Evaluation error: {str(e)}",
                "recommended_action": "Manual review required due to system error"
            }