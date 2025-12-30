"""
Direct test of library API functionality
"""
import json
import os

# Change to backend directory
os.chdir(r"C:\Users\HUAWEI\Downloads\project 03\Project-O3\backend")

# Import library_api functions
from library_api import load_papers

# Test loading papers
data = load_papers()
papers = data.get('papers', [])

print(f"✅ Loaded {len(papers)} research papers")
print(f"\n📊 First paper sample:")
if papers:
    first_paper = papers[0]
    print(f"   PMID: {first_paper.get('pmid')}")
    print(f"   Title: {first_paper.get('title', 'N/A')[:80]}...")
    print(f"   Authors: {first_paper.get('author_string', 'N/A')[:50]}...")
    print(f"   Year: {first_paper.get('year')}")
    print(f"   Cancer Types: {first_paper.get('cancer_types', [])}")
    print(f"   Study Type: {first_paper.get('study_type', 'N/A')}")

# Test cancer type distribution
cancer_types = {}
for paper in papers:
    for cancer in paper.get('cancer_types', []):
        cancer_types[cancer] = cancer_types.get(cancer, 0) + 1

print(f"\n📈 Cancer Type Distribution (top 5):")
sorted_types = sorted(cancer_types.items(), key=lambda x: x[1], reverse=True)[:5]
for cancer_type, count in sorted_types:
    print(f"   {cancer_type}: {count} papers")

# Test study type distribution
study_types = {}
for paper in papers:
    st = paper.get('study_type', 'Unknown')
    study_types[st] = study_types.get(st, 0) + 1

print(f"\n📚 Study Type Distribution:")
sorted_studies = sorted(study_types.items(), key=lambda x: x[1], reverse=True)
for study_type, count in sorted_studies:
    print(f"   {study_type}: {count} papers")

# Test year distribution
years = {}
for paper in papers:
    year = paper.get('year', 0)
    years[year] = years.get(year, 0) + 1

print(f"\n📅 Year Distribution (recent years):")
sorted_years = sorted(years.items(), key=lambda x: x[0], reverse=True)[:10]
for year, count in sorted_years:
    print(f"   {year}: {count} papers")

print(f"\n✅ Library API data loading test successful!")
