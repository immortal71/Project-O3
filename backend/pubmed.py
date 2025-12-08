"""
PubMed API integration service
"""

# Copyright (c) 2025 OncoPurpose (trovesx)
# All Rights Reserved.
# For licensing info, see LICENSE or contact oncopurpose@trovesx.com

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.logging import get_struct_logger
from app.models.research import ResearchPaper

logger = get_struct_logger(__name__)


class PubMedService:
    """Service for interacting with PubMed API"""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiter = asyncio.Semaphore(3)  # Max 3 concurrent requests
    
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
    
    async def search_papers(
        self,
        query: str,
        max_results: int = 100,
        date_filter: Optional[datetime] = None,
    ) -> List[Dict]:
        """Search for papers in PubMed"""
        
        async with self.rate_limiter:
            try:
                # Build search query
                search_params = {
                    "db": "pubmed",
                    "term": query,
                    "retmax": max_results,
                    "retmode": "json",
                    "sort": "relevance",
                }
                
                if date_filter:
                    # Add date filter (last 5 years by default)
                    date_str = date_filter.strftime("%Y/%m/%d")
                    search_params["mindate"] = date_str
                
                # Execute search
                search_url = f"{self.BASE_URL}/esearch.fcgi"
                async with self.session.get(search_url, params=search_params) as response:
                    if response.status != 200:
                        logger.error(
                            "PubMed search failed",
                            extra={"status": response.status, "query": query},
                        )
                        return []
                    
                    search_data = await response.json()
                    
                    # Extract PMIDs
                    pmids = search_data.get("esearchresult", {}).get("idlist", [])
                    
                    if not pmids:
                        return []
                    
                    # Fetch detailed information for papers
                    return await self.fetch_paper_details(pmids)
                    
            except Exception as e:
                logger.error(
                    "Error searching PubMed",
                    extra={"error": str(e), "query": query},
                )
                return []
    
    async def fetch_paper_details(self, pmids: List[str]) -> List[Dict]:
        """Fetch detailed information for papers"""
        
        if not pmids:
            return []
        
        try:
            # Fetch details in batches to avoid URL length limits
            batch_size = 100
            all_papers = []
            
            for i in range(0, len(pmids), batch_size):
                batch_pmids = pmids[i:i + batch_size]
                batch_papers = await self._fetch_paper_batch(batch_pmids)
                all_papers.extend(batch_papers)
            
            return all_papers
            
        except Exception as e:
            logger.error(
                "Error fetching paper details",
                extra={"error": str(e), "pmid_count": len(pmids)},
            )
            return []
    
    async def _fetch_paper_batch(self, pmids: List[str]) -> List[Dict]:
        """Fetch details for a batch of papers"""
        
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "json",
            "rettype": "abstract",
        }
        
        fetch_url = f"{self.BASE_URL}/efetch.fcgi"
        
        async with self.session.get(fetch_url, params=fetch_params) as response:
            if response.status != 200:
                logger.error(
                    "PubMed fetch failed",
                    extra={"status": response.status, "pmid_count": len(pmids)},
                )
                return []
            
            data = await response.json()
            
            papers = []
            for paper_data in data.get("result", {}).get("uids", []):
                paper_info = data["result"].get(paper_data, {})
                if paper_info:
                    papers.append(self._parse_paper_data(paper_info))
            
            return papers
    
    def _parse_paper_data(self, paper_info: Dict) -> Dict:
        """Parse paper data from PubMed response"""
        
        # Extract authors
        authors = []
        for author in paper_info.get("authors", []):
            if "name" in author:
                authors.append(author["name"])
        
        # Extract publication date
        pub_date = None
        if "pubdate" in paper_info:
            try:
                pub_date = datetime.strptime(paper_info["pubdate"], "%Y %b %d")
            except ValueError:
                try:
                    pub_date = datetime.strptime(paper_info["pubdate"], "%Y %b")
                except ValueError:
                    try:
                        pub_date = datetime.strptime(paper_info["pubdate"], "%Y")
                    except ValueError:
                        pass
        
        return {
            "pubmed_id": paper_info.get("uid", ""),
            "title": paper_info.get("title", ""),
            "authors": authors,
            "journal": paper_info.get("source", ""),
            "publication_date": pub_date,
            "doi": paper_info.get("articleids", [{}])[0].get("value", "")
            if paper_info.get("articleids")
            else "",
            "abstract": paper_info.get("abstract", ""),
            "citation_count": paper_info.get("pmcrefcount", 0),
        }
    
    async def get_citation_count(self, pmid: str) -> int:
        """Get citation count for a paper"""
        
        try:
            params = {
                "db": "pubmed",
                "linkname": "pubmed_pubmed_citedin",
                "id": pmid,
                "retmode": "json",
            }
            
            url = f"{self.BASE_URL}/elink.fcgi"
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return len(data.get("linksets", [{}])[0].get("linksetdbs", [{}])[0].get("links", []))
                
        except Exception as e:
            logger.error(
                "Error getting citation count",
                extra={"error": str(e), "pmid": pmid},
            )
        
        return 0
    
    async def sync_papers_to_database(
        self,
        db: AsyncSession,
        papers: List[Dict],
        drug_id: Optional[str] = None,
    ) -> int:
        """Sync papers to database"""
        
        synced_count = 0
        
        for paper_data in papers:
            try:
                # Check if paper already exists
                existing = await db.execute(
                    select(ResearchPaper).where(
                        ResearchPaper.pubmed_id == paper_data["pubmed_id"]
                    )
                )
                
                if existing.scalar_one_or_none():
                    continue
                
                # Create new paper record
                paper = ResearchPaper(
                    pubmed_id=paper_data["pubmed_id"],
                    title=paper_data["title"],
                    authors=paper_data["authors"],
                    journal=paper_data["journal"],
                    publication_date=paper_data["publication_date"],
                    doi=paper_data["doi"],
                    abstract=paper_data["abstract"],
                    citation_count=paper_data.get("citation_count", 0),
                )
                
                db.add(paper)
                synced_count += 1
                
            except Exception as e:
                logger.error(
                    "Error syncing paper to database",
                    extra={"error": str(e), "pubmed_id": paper_data.get("pubmed_id")},
                )
                continue
        
        if synced_count > 0:
            await db.commit()
            logger.info(
                "Papers synced to database",
                extra={"synced_count": synced_count},
            )
        
        return synced_count


# Global PubMed service instance
pubmed_service = PubMedService()