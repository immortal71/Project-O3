"""
Database initialization and seed data
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_struct_logger
from app.models.base import Base
from app.models.cancer import Cancer
from app.models.drug import Drug
from app.models.user import User

logger = get_struct_logger(__name__)


async def init_db() -> None:
    """Initialize database with seed data"""
    
    # This function is called during application startup
    # In production, migrations should be used instead
    
    logger.info("Initializing database")
    
    # Check if we should seed data (only in development)
    if settings.is_development:
        await seed_development_data()
    
    logger.info("Database initialization complete")


async def seed_development_data() -> None:
    """Seed development data"""
    
    from app.db.database import async_session_maker
    from app.core.security import get_password_hash
    
    async with async_session_maker() as session:
        try:
            # Check if data already exists
            user_count = await session.execute("SELECT COUNT(*) FROM users")
            if user_count.scalar() > 0:
                logger.info("Database already contains data, skipping seed")
                return
            
            # Create admin user
            admin_user = User(
                email="admin@oncopardigm.com",
                password_hash=get_password_hash("admin123"),
                full_name="System Administrator",
                company_name="OncoPurpose",
                role="admin",
                subscription_tier="enterprise",
                is_active=True,
            )
            session.add(admin_user)
            
            # Create test researcher
            test_user = User(
                email="researcher@pharmacorp.com",
                password_hash=get_password_hash("test123"),
                full_name="Dr. Sarah Chen",
                company_name="PharmaCorp International",
                role="researcher",
                subscription_tier="professional",
                is_active=True,
            )
            session.add(test_user)
            
            # Seed cancer types
            cancer_data = [
                {
                    "cancer_type": "Breast Cancer",
                    "cancer_subtype": "Triple-negative",
                    "icd_code": "C50.9",
                    "prevalence_global": 2100000,
                    "prevalence_us": 280000,
                    "mortality_rate": 15.4,
                    "five_year_survival_rate": 90.3,
                    "standard_treatments": [
                        "Surgery",
                        "Chemotherapy",
                        "Radiation therapy",
                        "Hormone therapy",
                    ],
                    "biomarkers": ["ER", "PR", "HER2"],
                },
                {
                    "cancer_type": "Lung Cancer",
                    "cancer_subtype": "Non-small cell",
                    "icd_code": "C34.9",
                    "prevalence_global": 2200000,
                    "prevalence_us": 235000,
                    "mortality_rate": 47.2,
                    "five_year_survival_rate": 25.4,
                    "standard_treatments": [
                        "Surgery",
                        "Chemotherapy",
                        "Radiation therapy",
                        "Targeted therapy",
                    ],
                    "biomarkers": ["EGFR", "ALK", "ROS1", "PD-L1"],
                },
                {
                    "cancer_type": "Colorectal Cancer",
                    "cancer_subtype": "Adenocarcinoma",
                    "icd_code": "C18.9",
                    "prevalence_global": 1900000,
                    "prevalence_us": 150000,
                    "mortality_rate": 32.1,
                    "five_year_survival_rate": 65.1,
                    "standard_treatments": [
                        "Surgery",
                        "Chemotherapy",
                        "Radiation therapy",
                        "Targeted therapy",
                    ],
                    "biomarkers": ["KRAS", "NRAS", "BRAF", "MSI"],
                },
                {
                    "cancer_type": "Prostate Cancer",
                    "cancer_subtype": "Adenocarcinoma",
                    "icd_code": "C61",
                    "prevalence_global": 1400000,
                    "prevalence_us": 175000,
                    "mortality_rate": 18.9,
                    "five_year_survival_rate": 98.2,
                    "standard_treatments": [
                        "Surgery",
                        "Radiation therapy",
                        "Hormone therapy",
                        "Chemotherapy",
                    ],
                    "biomarkers": ["PSA", "Gleason score"],
                },
            ]
            
            for cancer_info in cancer_data:
                cancer = Cancer(**cancer_info)
                session.add(cancer)
            
            # Seed drugs
            drug_data = [
                {
                    "drug_name": "Metformin",
                    "drugbank_id": "DB00331",
                    "pubchem_id": "4091",
                    "primary_indication": "Type 2 Diabetes Mellitus",
                    "approval_status": "FDA Approved",
                    "manufacturer": "Generic",
                    "mechanism_of_action": "AMPK activation, mTOR inhibition",
                    "drug_class": "Biguanide",
                },
                {
                    "drug_name": "Aspirin",
                    "drugbank_id": "DB00945",
                    "pubchem_id": "2244",
                    "primary_indication": "Pain, Inflammation, Cardiovascular protection",
                    "approval_status": "FDA Approved",
                    "manufacturer": "Generic",
                    "mechanism_of_action": "COX-1/2 inhibition",
                    "drug_class": "NSAID",
                },
                {
                    "drug_name": "Ibuprofen",
                    "drugbank_id": "DB01050",
                    "pubchem_id": "3672",
                    "primary_indication": "Pain, Inflammation",
                    "approval_status": "FDA Approved",
                    "manufacturer": "Generic",
                    "mechanism_of_action": "COX-2 inhibition",
                    "drug_class": "NSAID",
                },
                {
                    "drug_name": "Simvastatin",
                    "drugbank_id": "DB00641",
                    "pubchem_id": "54454",
                    "primary_indication": "Hyperlipidemia",
                    "approval_status": "FDA Approved",
                    "manufacturer": "Generic",
                    "mechanism_of_action": "HMG-CoA reductase inhibition",
                    "drug_class": "Statin",
                },
            ]
            
            for drug_info in drug_data:
                drug = Drug(**drug_info)
                session.add(drug)
            
            await session.commit()
            logger.info("Development data seeded successfully")
            
        except Exception as e:
            await session.rollback()
            logger.error("Error seeding development data", extra={"error": str(e)})
            raise


def get_db_url() -> str:
    """Get database URL for migrations"""
    return settings.DATABASE_URL


if __name__ == "__main__":
    import asyncio
    
    async def main():
        await seed_development_data()
    
    asyncio.run(main())