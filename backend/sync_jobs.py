"""
Background jobs for data synchronization
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_struct_logger
from app.db.database import async_session_maker
from app.services.external.clinicaltrials import clinicaltrials_service
from app.services.external.drugbank import drugbank_service
from app.services.external.pubmed import pubmed_service
from app.services.ml.predictor import predictor

logger = get_struct_logger(__name__)


class DataSyncJobs:
    """Background jobs for data synchronization"""
    
    @staticmethod
    async def sync_pubmed_papers(
        drug_names: List[str],
        cancer_types: List[str],
        max_results: int = 50,
    ) -> Dict[str, int]:
        """Sync research papers from PubMed"""
        
        results = {"synced": 0, "failed": 0}
        
        try:
            async with pubmed_service:
                async with async_session_maker() as db:
                    
                    # Create search queries
                    search_queries = []
                    for drug in drug_names:
                        for cancer in cancer_types:
                            search_queries.append(f"{drug} AND {cancer} AND cancer")
                    
                    # Search and sync papers
                    for query in search_queries:
                        try:
                            # Search for papers (last 5 years)
                            date_filter = datetime.now() - timedelta(days=5 * 365)
                            papers = await pubmed_service.search_papers(
                                query=query,
                                max_results=max_results,
                                date_filter=date_filter,
                            )
                            
                            # Sync to database
                            synced_count = await pubmed_service.sync_papers_to_database(
                                db, papers
                            )
                            results["synced"] += synced_count
                            
                            # Small delay to avoid rate limiting
                            await asyncio.sleep(1)
                            
                        except Exception as e:
                            logger.error(
                                "Error syncing papers for query",
                                extra={"error": str(e), "query": query},
                            )
                            results["failed"] += 1
                            continue
                    
                    logger.info(
                        "PubMed sync completed",
                        extra={"results": results},
                    )
                    
        except Exception as e:
            logger.error("PubMed sync job failed", extra={"error": str(e)})
        
        return results
    
    @staticmethod
    async def sync_clinical_trials(
        drug_names: List[str],
        cancer_types: List[str],
        max_results: int = 20,
    ) -> Dict[str, int]:
        """Sync clinical trials from ClinicalTrials.gov"""
        
        results = {"synced": 0, "failed": 0}
        
        try:
            async with clinicaltrials_service:
                async with async_session_maker() as db:
                    
                    # Search and sync trials
                    for drug in drug_names:
                        for cancer in cancer_types:
                            try:
                                # Search for trials
                                trials = await clinicaltrials_service.search_trials(
                                    drug_name=drug,
                                    cancer_type=cancer,
                                    max_results=max_results,
                                )
                                
                                # Get drug ID from database
                                from app.models.drug import Drug
                                
                                drug_result = await db.execute(
                                    select(Drug).where(Drug.drug_name.ilike(f"%{drug}%"))
                                )
                                drug_obj = drug_result.scalar_one_or_none()
                                drug_id = drug_obj.id if drug_obj else None
                                
                                # Get cancer ID from database
                                from app.models.cancer import Cancer
                                
                                cancer_result = await db.execute(
                                    select(Cancer).where(
                                        Cancer.cancer_type.ilike(f"%{cancer}%")
                                    )
                                )
                                cancer_obj = cancer_result.scalar_one_or_none()
                                cancer_id = cancer_obj.id if cancer_obj else None
                                
                                # Sync to database
                                synced_count = await clinicaltrials_service.sync_trials_to_database(
                                    db, trials, drug_id, cancer_id
                                )
                                results["synced"] += synced_count
                                
                                # Small delay to avoid rate limiting
                                await asyncio.sleep(1)
                                
                            except Exception as e:
                                logger.error(
                                    "Error syncing trials",
                                    extra={
                                        "error": str(e),
                                        "drug": drug,
                                        "cancer": cancer,
                                    },
                                )
                                results["failed"] += 1
                                continue
                    
                    logger.info(
                        "Clinical trials sync completed",
                        extra={"results": results},
                    )
                    
        except Exception as e:
            logger.error("Clinical trials sync job failed", extra={"error": str(e)})
        
        return results
    
    @staticmethod
    async def sync_drugbank_data(max_results: int = 100) -> Dict[str, int]:
        """Sync drug data from DrugBank"""
        
        results = {"synced": 0, "failed": 0}
        
        try:
            async with drugbank_service:
                async with async_session_maker() as db:
                    
                    # Sync all drugs
                    synced_count = await drugbank_service.sync_all_drugs(db)
                    results["synced"] = synced_count
                    
                    logger.info(
                        "DrugBank sync completed",
                        extra={"results": results},
                    )
                    
        except Exception as e:
            logger.error("DrugBank sync job failed", extra={"error": str(e)})
        
        return results
    
    @staticmethod
    async def update_predictions() -> Dict[str, int]:
        """Update ML predictions for all drug-cancer pairs"""
        
        results = {"updated": 0, "failed": 0}
        
        try:
            async with async_session_maker() as db:
                
                # Get all drugs and cancers
                from app.models.drug import Drug
                from app.models.cancer import Cancer
                
                drugs = await db.execute(select(Drug))
                cancers = await db.execute(select(Cancer))
                
                drug_list = drugs.scalars().all()
                cancer_list = cancers.scalars().all()
                
                # Generate predictions for all combinations
                for drug in drug_list:
                    for cancer in cancer_list:
                        try:
                            # Make prediction
                            prediction_data = await predictor.predict(db, drug, cancer)
                            
                            # Save to database
                            prediction_id = await predictor.save_prediction(
                                db,
                                drug.id,
                                cancer.id,
                                prediction_data,
                            )
                            
                            if prediction_id:
                                results["updated"] += 1
                            else:
                                results["failed"] += 1
                            
                        except Exception as e:
                            logger.error(
                                "Error updating prediction",
                                extra={
                                    "error": str(e),
                                    "drug_id": drug.id,
                                    "cancer_id": cancer.id,
                                },
                            )
                            results["failed"] += 1
                            continue
                
                logger.info(
                    "Predictions update completed",
                    extra={"results": results},
                )
                
        except Exception as e:
            logger.error("Predictions update job failed", extra={"error": str(e)})
        
        return results
    
    @staticmethod
    async def daily_sync() -> Dict[str, Dict[str, int]]:
        """Run daily synchronization tasks"""
        
        logger.info("Starting daily sync tasks")
        
        # Define sync parameters
        drug_names = ["Metformin", "Aspirin", "Ibuprofen", "Simvastatin"]
        cancer_types = ["Breast Cancer", "Lung Cancer", "Colorectal Cancer", "Prostate Cancer"]
        
        # Run sync tasks in parallel
        tasks = [
            DataSyncJobs.sync_pubmed_papers(drug_names, cancer_types, max_results=25),
            DataSyncJobs.sync_clinical_trials(drug_names, cancer_types, max_results=10),
            DataSyncJobs.update_predictions(),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        final_results = {
            "pubmed": results[0] if not isinstance(results[0], Exception) else {"synced": 0, "failed": 1},
            "clinical_trials": results[1] if not isinstance(results[1], Exception) else {"synced": 0, "failed": 1},
            "predictions": results[2] if not isinstance(results[2], Exception) else {"updated": 0, "failed": 1},
        }
        
        logger.info("Daily sync tasks completed", extra={"results": final_results})
        
        return final_results
    
    @staticmethod
    async def weekly_sync() -> Dict[str, Dict[str, int]]:
        """Run weekly synchronization tasks"""
        
        logger.info("Starting weekly sync tasks")
        
        # Run comprehensive DrugBank sync
        drugbank_results = await DataSyncJobs.sync_drugbank_data(max_results=500)
        
        # Run more extensive PubMed search (last 30 days)
        drug_names = ["Metformin", "Aspirin", "Ibuprofen", "Simvastatin", "Doxycycline"]
        cancer_types = [
            "Breast Cancer",
            "Lung Cancer",
            "Colorectal Cancer",
            "Prostate Cancer",
            "Leukemia",
        ]
        
        pubmed_results = await DataSyncJobs.sync_pubmed_papers(
            drug_names, cancer_types, max_results=100
        )
        
        results = {
            "drugbank": drugbank_results,
            "pubmed": pubmed_results,
        }
        
        logger.info("Weekly sync tasks completed", extra={"results": results})
        
        return results
    
    @staticmethod
    async def monthly_sync() -> Dict[str, any]:
        """Run monthly synchronization tasks"""
        
        logger.info("Starting monthly sync tasks")
        
        # Train ML model with new data
        async with async_session_maker() as db:
            try:
                success = await predictor.train_model(db)
                ml_result = {"trained": success}
            except Exception as e:
                logger.error("ML model training failed", extra={"error": str(e)})
                ml_result = {"trained": False, "error": str(e)}
        
        # Run comprehensive data sync
        sync_results = await DataSyncJobs.weekly_sync()
        
        results = {
            "ml_training": ml_result,
            "data_sync": sync_results,
        }
        
        logger.info("Monthly sync tasks completed", extra={"results": results})
        
        return results