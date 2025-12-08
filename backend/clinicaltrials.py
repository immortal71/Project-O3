"""
ClinicalTrials.gov API integration service
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.logging import get_struct_logger
from app.models.business import ClinicalTrial

logger = get_struct_logger(__name__)


class ClinicalTrialsService:
    """Service for interacting with ClinicalTrials.gov API"""
    
    BASE_URL = "https://clinicaltrials.gov/api"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiter = asyncio.Semaphore(5)  # Max 5 concurrent requests
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "OncoPurpose/1.0"},
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def search_trials(
        self,
        drug_name: str,
        cancer_type: Optional[str] = None,
        status_filter: Optional[str] = None,
        max_results: int = 50,
    ) -> List[Dict]:
        """Search for clinical trials"""
        
        async with self.rate_limiter:
            try:
                # Build search query
                search_terms = [f'"{drug_name}"']
                
                if cancer_type:
                    search_terms.append(f'"{cancer_type}"')
                
                query = " AND ".join(search_terms)
                
                params = {
                    "expr": query,
                    "fmt": "json",
                    "max_rnk": max_results,
                }
                
                if status_filter:
                    params["filter.overall_status"] = status_filter
                
                # Execute search
                search_url = f"{self.BASE_URL}/v2/studies"
                async with self.session.get(search_url, params=params) as response:
                    if response.status != 200:
                        logger.error(
                            "ClinicalTrials.gov search failed",
                            extra={
                                "status": response.status,
                                "drug_name": drug_name,
                                "cancer_type": cancer_type,
                            },
                        )
                        return []
                    
                    data = await response.json()
                    
                    # Parse results
                    trials = []
                    for study in data.get("studies", []):
                        trial_data = self._parse_trial_data(study)
                        if trial_data:
                            trials.append(trial_data)
                    
                    return trials
                    
            except Exception as e:
                logger.error(
                    "Error searching ClinicalTrials.gov",
                    extra={
                        "error": str(e),
                        "drug_name": drug_name,
                        "cancer_type": cancer_type,
                    },
                )
                return []
    
    def _parse_trial_data(self, study_data: Dict) -> Optional[Dict]:
        """Parse trial data from ClinicalTrials.gov response"""
        
        try:
            protocol = study_data.get("protocolSection", {})
            identification = protocol.get("identificationModule", {})
            status = protocol.get("statusModule", {})
            design = protocol.get("designModule", {})
            
            # Extract basic information
            nct_id = identification.get("nctId", "")
            title = identification.get("briefTitle", "")
            
            if not nct_id or not title:
                return None
            
            # Extract status
            overall_status = status.get("overallStatus", "")
            
            # Extract phase
            phase = ""
            if design.get("phases"):
                phase = design["phases"][0].get("phase", "")
            
            # Extract sponsor
            sponsor = ""
            if identification.get("sponsor"):
                sponsor = identification["sponsor"].get("name", "")
            
            # Extract dates
            start_date = None
            if status.get("startDateStruct"):
                date_struct = status["startDateStruct"]
                try:
                    start_date = datetime(
                        date_struct.get("year", 2000),
                        date_struct.get("month", 1),
                        date_struct.get("day", 1),
                    )
                except (ValueError, TypeError):
                    pass
            
            completion_date = None
            if status.get("completionDateStruct"):
                date_struct = status["completionDateStruct"]
                try:
                    completion_date = datetime(
                        date_struct.get("year", 2000),
                        date_struct.get("month", 1),
                        date_struct.get("day", 1),
                    )
                except (ValueError, TypeError):
                    pass
            
            # Extract enrollment
            enrollment_count = 0
            if design.get("enrollmentInfo"):
                enrollment_count = design["enrollmentInfo"].get("count", 0)
            
            # Extract primary outcome
            primary_outcome = ""
            outcomes = protocol.get("outcomesModule", {})
            if outcomes.get("primaryOutcomes"):
                primary_outcome = outcomes["primaryOutcomes"][0].get("measure", "")
            
            return {
                "nct_id": nct_id,
                "title": title,
                "status": overall_status,
                "phase": phase,
                "sponsor": sponsor,
                "start_date": start_date,
                "completion_date": completion_date,
                "enrollment_count": enrollment_count,
                "primary_outcome": primary_outcome,
                "trial_url": f"https://clinicaltrials.gov/study/{nct_id}",
            }
            
        except Exception as e:
            logger.error(
                "Error parsing trial data",
                extra={"error": str(e), "nct_id": study_data.get("protocolSection", {}).get("identificationModule", {}).get("nctId")},
            )
            return None
    
    async def get_trial_details(self, nct_id: str) -> Optional[Dict]:
        """Get detailed information for a specific trial"""
        
        try:
            params = {
                "expr": f"{nct_id}",
                "fmt": "json",
            }
            
            url = f"{self.BASE_URL}/v2/studies"
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("studies"):
                        return self._parse_trial_data(data["studies"][0])
                
        except Exception as e:
            logger.error(
                "Error getting trial details",
                extra={"error": str(e), "nct_id": nct_id},
            )
        
        return None
    
    async def sync_trials_to_database(
        self,
        db: AsyncSession,
        trials: List[Dict],
        drug_id: Optional[str] = None,
        cancer_id: Optional[str] = None,
    ) -> int:
        """Sync trials to database"""
        
        synced_count = 0
        
        for trial_data in trials:
            try:
                # Check if trial already exists
                existing = await db.execute(
                    select(ClinicalTrial).where(
                        ClinicalTrial.nct_id == trial_data["nct_id"]
                    )
                )
                
                if existing.scalar_one_or_none():
                    continue
                
                # Create new trial record
                trial = ClinicalTrial(
                    nct_id=trial_data["nct_id"],
                    drug_id=drug_id,
                    cancer_id=cancer_id,
                    title=trial_data["title"],
                    status=trial_data["status"],
                    phase=trial_data["phase"],
                    sponsor=trial_data["sponsor"],
                    start_date=trial_data["start_date"],
                    completion_date=trial_data["completion_date"],
                    enrollment_count=trial_data["enrollment_count"],
                    primary_outcome=trial_data["primary_outcome"],
                    trial_url=trial_data["trial_url"],
                )
                
                db.add(trial)
                synced_count += 1
                
            except Exception as e:
                logger.error(
                    "Error syncing trial to database",
                    extra={
                        "error": str(e),
                        "nct_id": trial_data.get("nct_id"),
                    },
                )
                continue
        
        if synced_count > 0:
            await db.commit()
            logger.info(
                "Clinical trials synced to database",
                extra={"synced_count": synced_count},
            )
        
        return synced_count


# Global ClinicalTrials service instance
clinicaltrials_service = ClinicalTrialsService()