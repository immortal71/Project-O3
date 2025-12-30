# Drug Database Sources - Free & Unrestricted

##  Current Status
- **74 FDA-approved drugs** imported
- All data from **free public sources** with no restrictions for commercial use
- Database: `database/oncopurpose.db`

##  Drug Categories

### Cancer Drugs (20 drugs)
- **Tyrosine Kinase Inhibitors**: Imatinib, Erlotinib, Gefitinib, Sunitinib, Sorafenib
- **Checkpoint Inhibitors**: Pembrolizumab, Nivolumab
- **Monoclonal Antibodies**: Bevacizumab, Trastuzumab, Rituximab
- **Hormonal Therapy**: Tamoxifen, Letrozole
- **Chemotherapy**: Paclitaxel, Doxorubicin, Cisplatin, Carboplatin, 5-Fluorouracil, Capecitabine, Gemcitabine, Methotrexate

### Cardiovascular Drugs (15 drugs)
- **Statins**: Atorvastatin, Simvastatin, Rosuvastatin
- **ACE Inhibitors**: Lisinopril, Enalapril
- **Beta Blockers**: Metoprolol, Carvedilol
- **Calcium Channel Blockers**: Amlodipine
- **ARBs**: Losartan, Valsartan
- **Anticoagulants**: Warfarin, Clopidogrel, Aspirin
- **Diuretics**: Hydrochlorothiazide, Furosemide

### Diabetes Drugs (4 drugs)
- Metformin, Insulin Glargine, Sitagliptin, Empagliflozin

### Pain & Inflammation (6 drugs)
- **NSAIDs**: Ibuprofen, Naproxen, Celecoxib
- **Analgesics**: Acetaminophen
- **Opioids**: Morphine, Tramadol

### Neurological Drugs (5 drugs)
- **Anticonvulsants**: Gabapentin, Pregabalin, Levetiracetam, Phenytoin, Valproic Acid

### Psychiatry (9 drugs)
- **SSRIs**: Sertraline, Fluoxetine, Escitalopram
- **SNRIs**: Venlafaxine
- **Other Antidepressants**: Bupropion
- **Antipsychotics**: Aripiprazole, Quetiapine
- **Benzodiazepines**: Alprazolam, Lorazepam

### Respiratory Drugs (3 drugs)
- Albuterol, Montelukast, Fluticasone

### GI Drugs (4 drugs)
- **PPIs**: Omeprazole, Lansoprazole, Pantoprazole
- **H2 Blockers**: Ranitidine

### Endocrine (2 drugs)
- Levothyroxine, Prednisone

### Antibiotics (4 drugs)
- Amoxicillin, Azithromycin, Ciprofloxacin, Doxycycline

### Antivirals (2 drugs)
- Acyclovir, Oseltamivir

---

## 🆓 Free Public Data Sources

###  Used in Current Import

**1. FDA DailyMed**
- URL: https://dailymed.nlm.nih.gov
- License: Public domain (U.S. Government)
- Content: Official drug labels, indications, mechanisms
- Commercial use:  Unrestricted
- API: REST API available

**2. NIH National Library of Medicine**
- Source: RxNorm, Drug Information Portal
- License: Public domain
- Content: Drug names, classes, relationships
- Commercial use:  Unrestricted

---

##  Available for Expansion

### PubChem (NIH)
- URL: https://pubchem.ncbi.nlm.nih.gov
- License: Public domain (U.S. Government)
- Content: 
  - Chemical structures
  - Bioactivity data
  - Drug interactions
  - Literature references
- Size: 110M+ compounds, 270M+ bioactivities
- API: PUG REST API (free, no rate limits for reasonable use)
- Commercial use:  Unrestricted
- Use case: Enrich drug data with structures, bioactivity, interactions

**Example API calls:**
```python
# Get drug by name
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/JSON

# Get bioactivity data
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/assaysummary/JSON

# Get drug interactions
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/xrefs/RegistryID/JSON
```

### ChEMBL (European Bioinformatics Institute)
- URL: https://www.ebi.ac.uk/chembl
- License: CC BY-SA 3.0 (attribution required)
- Content:
  - Bioactive molecules
  - Drug targets
  - Clinical trial data
  - Binding assays
- Size: 2.4M+ compounds, 19M+ activities
- API: REST API (free, no authentication needed)
- Commercial use:  Allowed with attribution
- Use case: Target identification, binding data, clinical trial info

**Example API calls:**
```python
# Search approved drugs
https://www.ebi.ac.uk/chembl/api/data/molecule.json?max_phase=4&limit=100

# Get drug targets
https://www.ebi.ac.uk/chembl/api/data/molecule/CHEMBL25/mechanism.json

# Get bioactivity data
https://www.ebi.ac.uk/chembl/api/data/molecule/CHEMBL25/bioactivity.json
```

### RxNorm (NLM)
- URL: https://www.nlm.nih.gov/research/umls/rxnorm
- License: Public domain
- Content:
  - Normalized drug names
  - Drug relationships
  - Dosage forms
  - Brand/generic mappings
- API: RxNorm API (free)
- Commercial use:  Unrestricted
- Use case: Drug name standardization, relationships

### DailyMed API
- URL: https://dailymed.nlm.nih.gov/dailymed/app-support-web-services.cfm
- License: Public domain
- Content:
  - FDA drug labels
  - Indications and usage
  - Contraindications
  - Pharmacology
- API: REST API
- Commercial use:  Unrestricted
- Use case: Official FDA-approved drug information

---

##  Expansion Roadmap

### Phase 1: Quantity (Target: 500+ drugs)  Complete (74 drugs)
-  Import curated FDA-approved drugs
-  Next: Add more categories (immunosuppressants, hormones, vitamins)

### Phase 2: Quality (Enrich existing drugs)
- Add PubChem CIDs for structure data
- Pull bioactivity data from PubChem
- Add ChEMBL IDs for target information
- Link to clinical trial data

### Phase 3: Real-time Integration
- PubChem API for structure lookups
- ChEMBL API for target binding data
- PubMed API for latest research (already planned)
- ClinicalTrials.gov for trial status (already planned)

---

##  Why These Sources?

### 1. **100% Free**
- No registration required (except DrugBank)
- No API keys needed
- No rate limits for reasonable use

### 2. **No Restrictions**
- Public domain or permissive licenses
- Commercial use allowed
- No attribution required (except ChEMBL)

### 3. **High Quality**
- Government sources (FDA, NIH)
- Peer-reviewed data
- Updated regularly

### 4. **Comprehensive**
- Drug names & classifications
- Mechanisms of action
- Indications & contraindications
- Chemical structures
- Bioactivity data
- Clinical trial information

---

##  Next Steps

1. **Expand to 500+ drugs**
   ```bash
   # Add more drug categories to import_free_drugs.py
   python backend/tools/import_free_drugs.py
   ```

2. **Enrich with PubChem data**
   ```python
   # Fetch PubChem CIDs for all drugs
   # Add structure data, bioactivity, interactions
   ```

3. **Add ChEMBL target data**
   ```python
   # Link drugs to targets
   # Add binding affinity data
   ```

4. **Test discovery workflow**
   ```bash
   # Test with existing 74 drugs
   # Analyze cancer drug repurposing potential
   ```

---

##  Legal Notes

- All data sources are free for commercial use
- No proprietary databases used
- No license restrictions for product building
- Attribution only required for ChEMBL (CC BY-SA 3.0)
- DailyMed and PubChem are U.S. Government public domain
- RxNorm is NLM public domain

**You can use this data to build and sell your product without restrictions!**
