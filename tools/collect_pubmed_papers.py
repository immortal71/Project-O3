"""
Download 500+ cancer drug repurposing research papers from PubMed
Collects papers with full metadata for the research library
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

# PubMed API endpoints
ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

# Search queries for drug repurposing in cancer
QUERIES = [
    "drug repurposing cancer",
    "drug repositioning oncology",
    "repurposed drugs cancer treatment",
    "off-label cancer therapy",
    "drug repurposing breast cancer",
    "drug repurposing lung cancer",
    "drug repurposing colorectal cancer",
    "metformin cancer",
    "aspirin cancer prevention",
    "statins cancer",
    "thalidomide multiple myeloma",
    "drug repurposing clinical trials cancer"
]


def search_pubmed(query, max_results=100, year_from=2015):
    """Search PubMed for papers"""
    print(f"🔍 Searching: {query}")
    
    params = {
        'db': 'pubmed',
        'term': f'{query} AND ({year_from}[PDAT] : 3000[PDAT])',
        'retmax': max_results,
        'retmode': 'json',
        'sort': 'relevance'
    }
    
    try:
        response = requests.get(ESEARCH_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            pmids = data.get('esearchresult', {}).get('idlist', [])
            print(f"  Found {len(pmids)} papers")
            return pmids
        else:
            print(f"  ❌ Search failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return []


def fetch_paper_details(pmids, batch_size=50):
    """Fetch detailed information for papers"""
    papers = []
    
    for i in range(0, len(pmids), batch_size):
        batch = pmids[i:i+batch_size]
        print(f"  📥 Fetching details for papers {i+1}-{min(i+batch_size, len(pmids))}")
        
        params = {
            'db': 'pubmed',
            'id': ','.join(batch),
            'retmode': 'xml'
        }
        
        try:
            response = requests.get(EFETCH_URL, params=params)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                for article in root.findall('.//PubmedArticle'):
                    try:
                        paper = extract_paper_info(article)
                        if paper:
                            papers.append(paper)
                    except Exception as e:
                        print(f"    ⚠️  Error extracting paper: {e}")
                        continue
            
            time.sleep(0.4)  # Rate limiting (3 requests per second)
            
        except Exception as e:
            print(f"    ❌ Batch fetch error: {e}")
            continue
    
    return papers


def extract_paper_info(article_xml):
    """Extract paper information from XML"""
    try:
        medline = article_xml.find('.//MedlineCitation')
        article = medline.find('.//Article')
        
        # PMID
        pmid = medline.find('.//PMID').text if medline.find('.//PMID') is not None else None
        
        # Title
        title_elem = article.find('.//ArticleTitle')
        title = title_elem.text if title_elem is not None else "No title"
        
        # Authors
        authors = []
        author_list = article.find('.//AuthorList')
        if author_list is not None:
            for author in author_list.findall('.//Author')[:5]:  # First 5 authors
                last_name = author.find('.//LastName')
                fore_name = author.find('.//ForeName')
                if last_name is not None:
                    author_name = last_name.text
                    if fore_name is not None:
                        author_name = f"{fore_name.text} {author_name}"
                    authors.append(author_name)
        
        # Abstract
        abstract_texts = article.findall('.//AbstractText')
        abstract = " ".join([a.text for a in abstract_texts if a.text]) if abstract_texts else "No abstract available"
        if len(abstract) > 1000:
            abstract = abstract[:1000] + "..."
        
        # Journal
        journal = article.find('.//Journal')
        journal_title = journal.find('.//Title').text if journal and journal.find('.//Title') is not None else "Unknown Journal"
        
        # Publication date
        pub_date = medline.find('.//PubDate')
        year = pub_date.find('.//Year').text if pub_date and pub_date.find('.//Year') is not None else "2024"
        month = pub_date.find('.//Month').text if pub_date and pub_date.find('.//Month') is not None else "01"
        
        try:
            if month.isdigit():
                month_num = month
            else:
                month_map = {
                    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                }
                month_num = month_map.get(month[:3], '01')
        except:
            month_num = '01'
        
        pub_date_str = f"{year}-{month_num}-01"
        
        # Keywords/MeSH terms
        keywords = []
        mesh_list = medline.find('.//MeshHeadingList')
        if mesh_list is not None:
            for mesh in mesh_list.findall('.//DescriptorName')[:10]:
                if mesh.text:
                    keywords.append(mesh.text)
        
        # Detect cancer type
        cancer_types = detect_cancer_types(title + " " + abstract)
        
        # Detect study type
        study_type = detect_study_type(title + " " + abstract)
        
        return {
            'pmid': pmid,
            'title': title,
            'authors': authors,
            'author_string': ', '.join(authors) if authors else 'Unknown',
            'abstract': abstract,
            'journal': journal_title,
            'publication_date': pub_date_str,
            'year': int(year) if year.isdigit() else 2024,
            'keywords': keywords,
            'cancer_types': cancer_types,
            'study_type': study_type,
            'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            'citations': None,  # Would need additional API call
            'doi': None  # Would need additional parsing
        }
    
    except Exception as e:
        print(f"      Error extracting paper: {e}")
        return None


def detect_cancer_types(text):
    """Detect cancer types mentioned in text"""
    text_lower = text.lower()
    cancer_types = []
    
    cancer_keywords = {
        'Breast Cancer': ['breast cancer', 'breast carcinoma'],
        'Lung Cancer': ['lung cancer', 'nsclc', 'small cell lung'],
        'Colorectal Cancer': ['colorectal', 'colon cancer', 'rectal cancer'],
        'Prostate Cancer': ['prostate cancer', 'prostate carcinoma'],
        'Pancreatic Cancer': ['pancreatic cancer', 'pancreas cancer'],
        'Ovarian Cancer': ['ovarian cancer', 'ovary cancer'],
        'Leukemia': ['leukemia', 'leukaemia', 'aml', 'cml', 'all'],
        'Lymphoma': ['lymphoma', 'hodgkin', 'non-hodgkin'],
        'Melanoma': ['melanoma', 'skin cancer'],
        'Liver Cancer': ['hepatocellular', 'liver cancer'],
        'Glioblastoma': ['glioblastoma', 'brain tumor', 'brain cancer']
    }
    
    for cancer_type, keywords in cancer_keywords.items():
        if any(kw in text_lower for kw in keywords):
            cancer_types.append(cancer_type)
    
    return cancer_types if cancer_types else ['General Oncology']


def detect_study_type(text):
    """Detect study type from text"""
    text_lower = text.lower()
    
    if 'phase iii' in text_lower or 'phase 3' in text_lower:
        return 'Clinical Trial - Phase III'
    elif 'phase ii' in text_lower or 'phase 2' in text_lower:
        return 'Clinical Trial - Phase II'
    elif 'phase i' in text_lower or 'phase 1' in text_lower:
        return 'Clinical Trial - Phase I'
    elif 'clinical trial' in text_lower or 'randomized' in text_lower:
        return 'Clinical Trial'
    elif 'meta-analysis' in text_lower or 'systematic review' in text_lower:
        return 'Meta-Analysis'
    elif 'case report' in text_lower:
        return 'Case Report'
    elif 'review' in text_lower:
        return 'Review Article'
    else:
        return 'Research Article'


def main():
    print("=" * 70)
    print("📚 PUBMED RESEARCH PAPER COLLECTOR")
    print("=" * 70)
    print("\nTarget: 500+ papers on cancer drug repurposing\n")
    
    all_papers = []
    seen_pmids = set()
    
    # Collect papers from multiple queries
    for query in QUERIES:
        pmids = search_pubmed(query, max_results=80)
        
        # Filter out duplicates
        new_pmids = [pmid for pmid in pmids if pmid not in seen_pmids]
        seen_pmids.update(new_pmids)
        
        if new_pmids:
            papers = fetch_paper_details(new_pmids)
            all_papers.extend(papers)
            print(f"  ✅ Collected {len(papers)} unique papers")
        
        print(f"  📊 Total so far: {len(all_papers)} papers\n")
        time.sleep(1)  # Be nice to PubMed
        
        # Stop if we have enough
        if len(all_papers) >= 500:
            print(f"🎯 Target reached: {len(all_papers)} papers")
            break
    
    # Save to file
    output_dir = Path(__file__).parent.parent / 'data' / 'research_papers'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'pubmed_papers.json'
    
    output_data = {
        'metadata': {
            'collected_at': datetime.now().isoformat(),
            'total_papers': len(all_papers),
            'queries_used': QUERIES,
            'source': 'PubMed'
        },
        'papers': all_papers
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 70)
    print("✅ COLLECTION COMPLETE")
    print("=" * 70)
    print(f"📄 Total papers: {len(all_papers)}")
    print(f"💾 Saved to: {output_file}")
    
    # Statistics
    cancer_type_counts = {}
    study_type_counts = {}
    year_counts = {}
    
    for paper in all_papers:
        for cancer in paper.get('cancer_types', []):
            cancer_type_counts[cancer] = cancer_type_counts.get(cancer, 0) + 1
        
        study_type = paper.get('study_type', 'Unknown')
        study_type_counts[study_type] = study_type_counts.get(study_type, 0) + 1
        
        year = paper.get('year', 2024)
        year_counts[year] = year_counts.get(year, 0) + 1
    
    print("\n📊 Statistics:")
    print(f"  Top cancer types: {sorted(cancer_type_counts.items(), key=lambda x: x[1], reverse=True)[:5]}")
    print(f"  Study types: {sorted(study_type_counts.items(), key=lambda x: x[1], reverse=True)[:3]}")
    print(f"  Year range: {min(year_counts.keys())} - {max(year_counts.keys())}")
    print("=" * 70)


if __name__ == '__main__':
    main()
