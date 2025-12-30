"""
OpenAI Integration Service for Drug Repurposing Analysis
Generates detailed market reports for drug repurposing opportunities
"""

# Copyright (c) 2025 OncoPurpose (trovesx)
# All Rights Reserved.
# For licensing info, see LICENSE or contact oncopurpose@trovesx.com

import json
import logging
import os
from typing import Dict, List, Optional, Any

from openai import OpenAI

logger = logging.getLogger(__name__)

# OpenAI API Key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

class OpenAIService:
    """Service for OpenAI API interactions"""
    
    def __init__(self):
        """Initialize OpenAI service"""
        if not OPENAI_API_KEY:
            logger.warning("OpenAI API key not found in environment variables")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAI service initialized successfully")
    
    async def generate_market_report(
        self,
        drug_name: str,
        cancer_type: str,
        confidence_score: float,
        mechanism: str = "",
        clinical_phase: str = "",
        market_potential: str = ""
    ) -> Dict[str, Any]:
        """
        Generate comprehensive market analysis report using OpenAI
        
        Args:
            drug_name: Name of the drug
            cancer_type: Type of cancer for repurposing
            confidence_score: Confidence score (0-1 or 0-100)
            mechanism: Mechanism of action
            clinical_phase: Current clinical development phase
            market_potential: Estimated market size
            
        Returns:
            Dictionary containing:
            - executive_summary: Brief overview
            - market_analysis: Detailed market analysis
            - competitive_landscape: Competitor analysis
            - regulatory_pathway: Regulatory considerations
            - financial_projections: Revenue and cost projections
            - risks_mitigation: Risk analysis and mitigation strategies
            - recommendations: Strategic recommendations
        """
        try:
            # Normalize confidence score
            conf_pct = confidence_score if confidence_score > 1 else confidence_score * 100
            
            prompt = f"""Generate a comprehensive, detailed market analysis report for drug repurposing:

Drug: {drug_name}
Target Indication: {cancer_type}
Confidence Score: {conf_pct:.1f}%
Mechanism of Action: {mechanism or 'Under investigation'}
Clinical Phase: {clinical_phase or 'Preclinical'}
Market Potential: {market_potential or 'To be determined'}

Create a detailed, professional, IN-DEPTH market report with the following sections. BE COMPREHENSIVE - each section should be 2-4 paragraphs with specific details, data, and analysis:

1. EXECUTIVE SUMMARY
- Comprehensive overview of the repurposing opportunity (3-4 paragraphs)
- Key value proposition and market opportunity
- Critical success factors and timeline overview
- Investment thesis and expected returns

2. MARKET ANALYSIS
- Detailed market size analysis (current and projected 5-year CAGR)
- Patient population demographics and epidemiology
- Current treatment paradigm and market dynamics
- Unmet medical needs and pain points
- Pricing landscape and reimbursement environment
- Market access considerations

3. COMPETITIVE LANDSCAPE
- Comprehensive competitor analysis (list 5-7 specific drugs/companies)
- Market share breakdown
- Comparative efficacy and safety profiles
- Differentiation strategy and competitive advantages
- Intellectual property landscape
- Emerging therapies in pipeline

4. REGULATORY PATHWAY
- Detailed FDA approval strategy and timeline (include specific milestones)
- Required clinical trial phases with patient enrollment numbers
- Regulatory precedents for similar repurposing cases
- Orphan drug designation opportunities
- Fast track/breakthrough therapy potential
- International regulatory considerations (EMA, PMDA)

5. FINANCIAL PROJECTIONS
- Year-by-year revenue forecast (Years 1-5) with specific numbers
- Development cost breakdown by phase
- Peak sales estimates
- Operating margin projections
- Return on investment analysis
- Break-even analysis and payback period

6. RISKS & MITIGATION STRATEGIES
- Technical/scientific risks (efficacy, safety, mechanism)
- Clinical trial risks (recruitment, endpoints, competition)
- Regulatory risks (approval delays, additional requirements)
- Market/commercial risks (adoption, competition, pricing pressure)
- Financial risks (funding, burn rate)
- Specific mitigation strategies for each risk category

7. STRATEGIC RECOMMENDATIONS
- Detailed clinical development roadmap (specific trials, timelines, budgets)
- Partnership and business development opportunities
- Key opinion leader engagement strategy
- Medical affairs and publication plan
- Commercial strategy and go-to-market approach
- Milestone-based decision framework

Make this report detailed, data-driven, and professional. Use realistic pharmaceutical industry numbers, timelines, and benchmarks. Each section should provide actionable insights with specific recommendations."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a senior pharmaceutical market analyst and oncology drug development expert with 15+ years of experience in drug repurposing, market assessments, and FDA regulatory strategy. Provide highly detailed, data-driven, comprehensive market reports with specific numbers, timelines, and actionable recommendations. Draw from real pharmaceutical industry benchmarks and oncology market data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            report_text = response.choices[0].message.content
            
            # Parse sections (simple split by section headers)
            sections = {
                "full_report": report_text,
                "executive_summary": self._extract_section(report_text, "EXECUTIVE SUMMARY"),
                "market_analysis": self._extract_section(report_text, "MARKET ANALYSIS"),
                "competitive_landscape": self._extract_section(report_text, "COMPETITIVE LANDSCAPE"),
                "regulatory_pathway": self._extract_section(report_text, "REGULATORY PATHWAY"),
                "financial_projections": self._extract_section(report_text, "FINANCIAL PROJECTIONS"),
                "risks_mitigation": self._extract_section(report_text, "RISKS"),
                "recommendations": self._extract_section(report_text, "RECOMMENDATIONS")
            }
            
            return {
                "success": True,
                "drug_name": drug_name,
                "cancer_type": cancer_type,
                "confidence_score": conf_pct,
                "report": sections,
                "generated_at": "2025-12-29",
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"OpenAI market report generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_report": self._generate_fallback_report(drug_name, cancer_type, conf_pct)
            }
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a specific section from the report"""
        try:
            # Find section start
            start_idx = text.find(section_name)
            if start_idx == -1:
                return ""
            
            # Find next section or end
            next_sections = ["EXECUTIVE SUMMARY", "MARKET ANALYSIS", "COMPETITIVE LANDSCAPE", 
                           "REGULATORY PATHWAY", "FINANCIAL PROJECTIONS", "RISKS", "RECOMMENDATIONS"]
            
            end_idx = len(text)
            for next_section in next_sections:
                if next_section == section_name:
                    continue
                next_idx = text.find(next_section, start_idx + len(section_name))
                if next_idx != -1 and next_idx < end_idx:
                    end_idx = next_idx
            
            section_text = text[start_idx:end_idx].strip()
            # Remove section header
            section_text = section_text[len(section_name):].strip()
            # Remove leading colons, dashes, etc.
            section_text = section_text.lstrip(':- \n')
            
            return section_text
        except:
            return ""
    
    def _generate_fallback_report(self, drug_name: str, cancer_type: str, confidence: float) -> str:
        """Generate a basic fallback report if OpenAI fails"""
        return f"""MARKET ANALYSIS REPORT
Drug: {drug_name}
Indication: {cancer_type}
Confidence: {confidence:.1f}%

EXECUTIVE SUMMARY
{drug_name} shows promising potential for repurposing in {cancer_type} treatment with a confidence score of {confidence:.1f}%. 
Further clinical validation is recommended.

MARKET ANALYSIS
The {cancer_type} market represents a significant opportunity for innovative treatments. 
Standard therapies face challenges including resistance and toxicity.

REGULATORY PATHWAY
The drug repurposing pathway may accelerate FDA approval through expedited review programs.
Estimated timeline: 3-5 years to market.

FINANCIAL PROJECTIONS
Market Size: $1-3B annually
Development Costs: $50-150M
ROI Potential: 200-400%

RECOMMENDATIONS
1. Initiate Phase II clinical trials
2. Seek partnership with oncology-focused pharmaceutical companies
3. Engage with FDA for regulatory strategy
4. Publish preclinical findings in peer-reviewed journals"""
    
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
            max_tokens = 2000
            temperature = 0.7
            
            if analysis_mode == "deep":
                max_tokens = 3000
                temperature = 0.5  # More focused for deep analysis
            
            # Call OpenAI API
            logger.info(f"Analyzing {drug_name} for {cancer_type} using {analysis_mode} mode")
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
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
            result["model_used"] = "gpt-3.5-turbo"
            result["tokens_used"] = response.usage.total_tokens
            
            logger.info(f"Analysis completed for {drug_name} - {cancer_type}")
            return result
            
        except Exception as e:
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
                model="gpt-3.5-turbo",
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


def get_openai_service() -> OpenAIService:
    """Get or create OpenAI service instance"""
    global _service_instance
    
    if _service_instance is None:
        _service_instance = OpenAIService()
    
    return _service_instance
