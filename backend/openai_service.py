"""
OpenAI Integration Service for Drug Repurposing Analysis
"""

import json
import logging
from typing import Dict, List, Optional, Any

import openai
from openai import OpenAI
from config import Settings

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for OpenAI API interactions"""
    
    def __init__(self, settings: Settings):
        """Initialize OpenAI service"""
        self.settings = settings
        self.client = None
        
        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI service initialized successfully")
        else:
            logger.warning("OpenAI API key not configured")

    async def analyze_drug_repurposing(
        self,
        drug_name: str,
        cancer_type: str,
        molecular_target: Optional[str] = None,
        current_indication: Optional[str] = None,
        analysis_mode: str = "fast"
    ) -> Dict[str, Any]:
        """
        Analyze drug repurposing potential using OpenAI
        """
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        
        try:
            # Build the analysis prompt
            prompt = self._build_analysis_prompt(
                drug_name=drug_name,
                cancer_type=cancer_type,
                molecular_target=molecular_target,
                current_indication=current_indication,
                analysis_mode=analysis_mode
            )
            
            # Set parameters based on analysis mode
            max_tokens = self.settings.OPENAI_MAX_TOKENS
            temperature = self.settings.OPENAI_TEMPERATURE
            
            if analysis_mode == "deep":
                max_tokens = 3000
                temperature = 0.5  # More focused for deep analysis
            
            # Call OpenAI API
            logger.info(f"Analyzing {drug_name} for {cancer_type} using {analysis_mode} mode")
            
            response = self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert oncologist and pharmacologist specializing in drug repurposing for cancer treatment. Provide evidence-based, scientifically accurate analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            # Add metadata
            result["analysis_mode"] = analysis_mode
            result["model_used"] = self.settings.OPENAI_MODEL
            result["tokens_used"] = response.usage.total_tokens
            
            logger.info(f"Analysis completed for {drug_name} - {cancer_type}")
            return result
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error analyzing drug repurposing: {e}")
            raise

    def _build_analysis_prompt(
        self,
        drug_name: str,
        cancer_type: str,
        molecular_target: Optional[str],
        current_indication: Optional[str],
        analysis_mode: str
    ) -> str:
        """Build the analysis prompt for OpenAI"""
        
        base_prompt = f"""
Analyze the potential for repurposing **{drug_name}** for **{cancer_type}** treatment.

Drug: {drug_name}
Target Cancer: {cancer_type}
"""
        
        if molecular_target:
            base_prompt += f"Molecular Target: {molecular_target}\n"
        
        if current_indication:
            base_prompt += f"Current Indication: {current_indication}\n"
        
        if analysis_mode == "fast":
            base_prompt += """
Provide a concise analysis including:

1. **Confidence Score** (0-100): Overall confidence in repurposing potential
2. **Mechanism of Action**: How the drug could work against this cancer
3. **Evidence Summary**: Key supporting evidence from literature
4. **Safety Profile**: Important safety considerations
5. **Market Opportunity**: Brief market potential assessment
6. **Recommendation**: Clear next steps

Format your response as JSON with these exact keys:
{
  "confidence_score": <number>,
  "drug_name": "<string>",
  "cancer_type": "<string>",
  "mechanism_of_action": "<string>",
  "evidence_summary": "<string>",
  "safety_profile": "<string>",
  "market_opportunity": "<string>",
  "recommendation": "<string>",
  "key_findings": ["<string>", "<string>", "<string>"]
}
"""
        else:
            base_prompt += """
Provide a comprehensive deep analysis including:
1. **Confidence Score** (0-100): Overall confidence in repurposing potential with rationale
... (remainder trimmed for brevity)
"""
