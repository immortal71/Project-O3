"""
DrugBank API integration service
"""

import asyncio
from typing import Dict, List, Optional

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.logging import get_struct_logger
from app.models.drug import Drug, SafetyProfile

logger = get_struct_logger(__name__)


class DrugBankService:
    """Service for interacting with DrugBank API"""
    
    BASE_URL = "https://go.drugbank.com/api"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiter = asyncio.Semaphore(2)  # Max 2 concurrent requests
        self.api_key = settings.DRUGBANK_API_KEY
    
    async def __aenter__(self):
        """Async context manager entry"""
        if not self.api_key:
            raise ValueError("DrugBank API key is required")
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                "User-Agent": "OncoPurpose/1.0",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_drug_details(self, drugbank_id: str) -> Optional[Dict]:
        """Get detailed drug information"""
        
        async with self.rate_limiter:
            try:
                url = f"{self.BASE_URL}/drugs/{drugbank_id}"
                
                async with self.session.get(url) as response:
                    if response.status != 200:
                        logger.error(
                            "DrugBank API request failed",
                            extra={
                                "status": response.status,
                                "drugbank_id": drugbank_id,
                            },
                        )
                        return None
                    
                    drug_data = await response.json()
                    return self._parse_drug_data(drug_data)
                    
            except Exception as e:
                logger.error(
                    "Error getting drug details from DrugBank",
                    extra={"error": str(e), "drugbank_id": drugbank_id},
                )
                return None
    
    def _parse_drug_data(self, drug_data: Dict) -> Dict:
        """Parse drug data from DrugBank response"""
        
        # Extract basic information
        drug_name = drug_data.get("name", "")
        drugbank_id = drug_data.get("drugbank_id", "")
        
        # Extract chemical properties
        properties = drug_data.get("properties", {})
        molecular_weight = properties.get("molecular_weight")
        smiles = drug_data.get("smiles", "")
        
        # Extract approval information
        groups = drug_data.get("groups", [])
        approval_status = "Approved" if "approved" in groups else "Not Approved"
        
        # Extract manufacturer
        manufacturer = ""
        if drug_data.get("manufacturer"):
            manufacturer = drug_data["manufacturer"].get("name", "")
        
        # Extract mechanism of action
        mechanism = ""
        mechanisms = drug_data.get("mechanisms_of_action", [])
        if mechanisms:
            mechanism = mechanisms[0].get("mechanism", "")
        
        # Extract drug class
        drug_class = ""
        classifications = drug_data.get("drug_classifications", [])
        if classifications:
            drug_class = classifications[0].get("classification", "")
        
        # Extract safety information
        adverse_events = []
        for ae in drug_data.get("adverse_effects", []):
            if "event" in ae and "frequency" in ae:
                adverse_events.append({
                    "event": ae["event"],
                    "frequency": ae["frequency"],
                })
        
        contraindications = drug_data.get("contraindications", [])
        drug_interactions = []
        for interaction in drug_data.get("drug_interactions", []):
            if "drug" in interaction and "description" in interaction:
                drug_interactions.append(
                    f"{interaction['drug']}: {interaction['description']}"
                )
        
        return {
            "drug_name": drug_name,
            "drugbank_id": drugbank_id,
            "molecular_weight": molecular_weight,
            "chemical_structure": smiles,
            "approval_status": approval_status,
            "manufacturer": manufacturer,
            "mechanism_of_action": mechanism,
            "drug_class": drug_class,
            "adverse_events": adverse_events,
            "contraindications": contraindications,
            "drug_interactions": drug_interactions,
        }
    
    async def search_drugs(self, query: str, max_results: int = 20) -> List[Dict]:
        """Search for drugs in DrugBank"""
        
        async with self.rate_limiter:
            try:
                params = {
                    "q": query,
                    "limit": max_results,
                }
                
                url = f"{self.BASE_URL}/drugs"
                async with self.session.get(url, params=params) as response:
                    if response.status != 200:
                        logger.error(
                            "DrugBank search failed",
                            extra={
                                "status": response.status,
                                "query": query,
                            },
                        )
                        return []
                    
                    data = await response.json()
                    
                    drugs = []
                    for drug_info in data.get("drugs", []):
                        parsed_drug = self._parse_drug_data(drug_info)
                        if parsed_drug:
                            drugs.append(parsed_drug)
                    
                    return drugs
                    
            except Exception as e:
                logger.error(
                    "Error searching DrugBank",
                    extra={"error": str(e), "query": query},
                )
                return []
    
    async def sync_drug_to_database(
        self,
        db: AsyncSession,
        drug_data: Dict,
    ) -> bool:
        """Sync drug data to database"""
        
        try:
            # Check if drug already exists
            existing = await db.execute(
                select(Drug).where(
                    Drug.drugbank_id == drug_data["drugbank_id"]
                )
            )
            
            if existing.scalar_one_or_none():
                # Update existing drug
                drug = existing.scalar_one_or_none()
                for key, value in drug_data.items():
                    if key not in ["adverse_events", "contraindications", "drug_interactions"]:
                        setattr(drug, key, value)
            else:
                # Create new drug
                drug = Drug(
                    drug_name=drug_data["drug_name"],
                    drugbank_id=drug_data["drugbank_id"],
                    molecular_weight=drug_data.get("molecular_weight"),
                    chemical_structure=drug_data.get("chemical_structure"),
                    primary_indication="",  # Will be updated later
                    approval_status=drug_data["approval_status"],
                    manufacturer=drug_data.get("manufacturer"),
                    mechanism_of_action=drug_data.get("mechanism_of_action"),
                    drug_class=drug_data.get("drug_class"),
                )
                db.add(drug)
                await db.flush()  # Get the ID
            
            # Create safety profile
            if any([drug_data.get("adverse_events"), drug_data.get("contraindications"), drug_data.get("drug_interactions")]):
                safety_profile = SafetyProfile(
                    drug_id=drug.id,
                    adverse_events=drug_data.get("adverse_events"),
                    contraindications=drug_data.get("contraindications"),
                    drug_interactions=drug_data.get("drug_interactions"),
                )
                db.add(safety_profile)
            
            await db.commit()
            logger.info(
                "Drug synced to database",
                extra={"drugbank_id": drug_data["drugbank_id"]},
            )
            
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(
                "Error syncing drug to database",
                extra={"error": str(e), "drugbank_id": drug_data.get("drugbank_id")},
            )
            return False
    
    async def sync_all_drugs(self, db: AsyncSession) -> int:
        """Sync all drugs from DrugBank to database"""
        
        if not self.api_key:
            logger.warning("DrugBank API key not configured, skipping sync")
            return 0
        
        synced_count = 0
        
        try:
            # Get all approved drugs
            params = {
                "q": "approved",
                "limit": 1000,  # Adjust based on API limits
            }
            
            url = f"{self.BASE_URL}/drugs"
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for drug_info in data.get("drugs", []):
                        # Get detailed information
                        detailed_data = await self.get_drug_details(
                            drug_info.get("drugbank_id", "")
                        )
                        
                        if detailed_data:
                            success = await self.sync_drug_to_database(db, detailed_data)
                            if success:
                                synced_count += 1
                    
                    logger.info(
                        "Drug sync completed",
                        extra={"synced_count": synced_count},
                    )
        
        except Exception as e:
            logger.error(
                "Error syncing all drugs",
                extra={"error": str(e)},
            )
        
        return synced_count


# Global DrugBank service instance
drugbank_service = DrugBankService()