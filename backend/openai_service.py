"""
OpenAI Integration Service for Drug Repurposing Analysis
"""

# Copyright (c) 2025 OncoPurpose (trovesx)
# All Rights Reserved.
# For licensing info, see LICENSE or contact oncopurpose@trovesx.com

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
        
        Args:
            drug_name: Name of the drug to analyze
            cancer_type: Type of cancer for repurposing
            molecular_target: Optional molecular target
            current_indication: Current approved indication
            analysis_mode: 'fast' or 'deep' analysis
            
        Returns:
            Dictionary containing analysis results
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
        else:  # deep analysis
            base_prompt += """
Provide a comprehensive deep analysis including:

1. **Confidence Score** (0-100): Overall confidence in repurposing potential with rationale
2. **Detailed Mechanism**: In-depth explanation of molecular mechanisms
3. **Clinical Evidence**: 
   - Preclinical studies
   - Clinical trials (if any)
   - Case reports
4. **Molecular Pathways**: Specific pathways affected
5. **Safety & Toxicity**:
   - Known adverse effects
   - Drug interactions
   - Contraindications
6. **Biomarkers**: Potential predictive biomarkers
7. **Market Analysis**:
   - Patient population size
   - Competitive landscape
   - Patent status considerations
8. **Development Roadmap**: Proposed clinical development path
9. **Regulatory Considerations**: FDA pathway and requirements
10. **Risk Assessment**: Key challenges and mitigation strategies

Format your response as JSON with these exact keys:
{
  "confidence_score": <number>,
  "confidence_rationale": "<string>",
  "drug_name": "<string>",
  "cancer_type": "<string>",
  "mechanism_of_action": "<string>",
  "molecular_pathways": ["<string>", "<string>"],
  "clinical_evidence": {
    "preclinical": "<string>",
    "clinical_trials": "<string>",
    "case_reports": "<string>"
  },
  "biomarkers": ["<string>", "<string>"],
  "safety_profile": {
    "adverse_effects": "<string>",
    "drug_interactions": "<string>",
    "contraindications": "<string>"
  },
  "market_analysis": {
    "patient_population": "<string>",
    "market_size_estimate": "<string>",
    "competitive_landscape": "<string>",
    "patent_status": "<string>"
  },
  "development_roadmap": {
    "phase_1": "<string>",
    "phase_2": "<string>",
    "phase_3": "<string>",
    "estimated_timeline": "<string>"
  },
  "regulatory_pathway": "<string>",
  "risk_assessment": {
    "key_challenges": ["<string>", "<string>"],
    "mitigation_strategies": ["<string>", "<string>"]
  },
  "recommendation": "<string>",
  "next_steps": ["<string>", "<string>", "<string>"]
}
"""
        
        return base_prompt
    
    async def generate_drug_summary(self, drug_name: str) -> Dict[str, Any]:
        """Generate a brief summary of a drug"""
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        
        try:
            prompt = f"""
Provide a brief summary of the drug **{drug_name}** including:
- Drug class
- Mechanism of action
- Approved indications
- Common side effects

Format as JSON:
{{
  "drug_name": "<string>",
  "drug_class": "<string>",
  "mechanism": "<string>",
  "indications": ["<string>"],
  "side_effects": ["<string>"]
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a pharmacology expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error generating drug summary: {e}")
            raise


# Global service instance
_service_instance: Optional[OpenAIService] = None


def get_openai_service(settings: Settings) -> OpenAIService:
    """Get or create OpenAI service instance"""
    global _service_instance
    
    if _service_instance is None:
        _service_instance = OpenAIService(settings)
    
    return _service_instance
