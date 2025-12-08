# OpenAI API Integration - Setup Guide

## Overview
OpenAI API has been successfully integrated for drug repurposing analysis. The system uses GPT-4 to analyze drug candidates for specific cancer types.

## Files Created/Modified

### New Files
1. **backend/openai_service.py** - OpenAI integration service
2. **backend/discovery_api.py** - Discovery API endpoints
3. **backend/.env.example** - Environment configuration template

### Modified Files
1. **backend/config.py** - Added OpenAI configuration fields
2. **backend/main.py** - Registered discovery router

## Installation Steps

### 1. Install OpenAI Package
```powershell
cd backend
pip install openai
```

### 2. Configure Environment Variables
Create a `.env` file in the backend directory:

```bash
# Copy from example
cp .env.example .env

# Or on Windows
copy .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7
```

### 3. Get OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key and add to `.env`

**Important:** 
- Never commit your API key to version control
- Keep `.env` in `.gitignore`
- Use environment variables in production

## API Endpoints

### 1. Analyze Drug Repurposing
**POST** `/api/discovery/analyze`

Analyzes drug repurposing potential using OpenAI.

**Request Body:**
```json
{
  "cancer_type": "Non-Small Cell Lung Cancer",
  "drug_name": "Metformin",
  "molecular_target": "AMPK",
  "current_indication": "Type 2 Diabetes",
  "analysis_mode": "fast",
  "confidence_threshold": 70,
  "filters": {
    "clinical_trials": true,
    "preclinical_studies": true,
    "mechanism_based": true,
    "safety_data": true
  }
}
```

**Response (Fast Mode):**
```json
{
  "success": true,
  "analysis_mode": "fast",
  "model_used": "gpt-4",
  "tokens_used": 1234,
  "result": {
    "confidence_score": 75,
    "drug_name": "Metformin",
    "cancer_type": "Non-Small Cell Lung Cancer",
    "mechanism_of_action": "...",
    "evidence_summary": "...",
    "safety_profile": "...",
    "market_opportunity": "...",
    "recommendation": "...",
    "key_findings": ["...", "...", "..."]
  },
  "message": "Analysis completed successfully"
}
```

**Response (Deep Mode):**
```json
{
  "success": true,
  "analysis_mode": "deep",
  "model_used": "gpt-4",
  "tokens_used": 2567,
  "result": {
    "confidence_score": 78,
    "confidence_rationale": "...",
    "drug_name": "Metformin",
    "cancer_type": "Non-Small Cell Lung Cancer",
    "mechanism_of_action": "...",
    "molecular_pathways": ["AMPK activation", "mTOR inhibition"],
    "clinical_evidence": {
      "preclinical": "...",
      "clinical_trials": "...",
      "case_reports": "..."
    },
    "biomarkers": ["AMPK expression", "LKB1 mutation"],
    "safety_profile": {
      "adverse_effects": "...",
      "drug_interactions": "...",
      "contraindications": "..."
    },
    "market_analysis": {
      "patient_population": "...",
      "market_size_estimate": "...",
      "competitive_landscape": "...",
      "patent_status": "..."
    },
    "development_roadmap": {
      "phase_1": "...",
      "phase_2": "...",
      "phase_3": "...",
      "estimated_timeline": "..."
    },
    "regulatory_pathway": "...",
    "risk_assessment": {
      "key_challenges": ["...", "..."],
      "mitigation_strategies": ["...", "..."]
    },
    "recommendation": "...",
    "next_steps": ["...", "...", "..."]
  },
  "message": "Analysis completed successfully"
}
```

### 2. Get Drug Summary
**POST** `/api/discovery/drug-summary`

Get brief drug information.

**Request Body:**
```json
{
  "drug_name": "Metformin"
}
```

**Response:**
```json
{
  "drug_name": "Metformin",
  "drug_class": "Biguanide",
  "mechanism": "AMPK activation, reduces hepatic glucose production",
  "indications": ["Type 2 Diabetes", "PCOS"],
  "side_effects": ["Gastrointestinal upset", "Lactic acidosis (rare)"]
}
```

### 3. Health Check
**GET** `/api/discovery/health`

Check discovery API status.

## Frontend Integration

The frontend (discovery.html) is already configured to call the API:

```javascript
// Analyze button click
async function handleAnalyze() {
  const response = await fetch('http://localhost:8000/api/discovery/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      cancer_type: cancerType,
      drug_name: drugName,
      molecular_target: molecularTarget,
      current_indication: currentIndication,
      analysis_mode: analysisMode,
      confidence_threshold: confidenceThreshold
    })
  });
  
  const data = await response.json();
  // Display results
}
```

## Running the Backend

### Development Mode
```powershell
cd backend
python main.py
```

Server starts at: http://localhost:8000

### Production Mode
```powershell
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing the Integration

### 1. Test with cURL
```bash
curl -X POST http://localhost:8000/api/discovery/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "cancer_type": "Breast Cancer",
    "drug_name": "Aspirin",
    "analysis_mode": "fast",
    "confidence_threshold": 60
  }'
```

### 2. Test in Browser
1. Start backend: `python main.py`
2. Open discovery.html in browser
3. Fill in cancer type and drug name
4. Click "Analyze Drug"
5. View results

### 3. API Documentation
Visit http://localhost:8000/docs for interactive API docs

## Cost Considerations

### OpenAI Pricing (GPT-4)
- Input: $0.03 per 1K tokens
- Output: $0.06 per 1K tokens

### Estimated Costs per Analysis
- **Fast mode**: ~1,500 tokens = $0.05-0.10
- **Deep mode**: ~3,000 tokens = $0.15-0.25

### Monthly Estimates
- 100 analyses/month: $5-10 (fast) or $15-25 (deep)
- 1,000 analyses/month: $50-100 (fast) or $150-250 (deep)

### Cost Optimization Tips
1. Use fast mode for quick scans
2. Cache results for repeated queries
3. Implement rate limiting
4. Set token limits appropriately
5. Monitor usage via OpenAI dashboard

## Error Handling

The API handles these error scenarios:

1. **Missing API Key**: Returns 400 with clear message
2. **API Rate Limit**: Returns 429 with retry advice
3. **Invalid Input**: Returns 400 with validation errors
4. **OpenAI Error**: Returns 500 with generic message
5. **Timeout**: Returns 504 with timeout message

## Security Best Practices

1. **Never expose API key in frontend**
2. **Use environment variables**
3. **Implement rate limiting**
4. **Add authentication for production**
5. **Log API usage for monitoring**
6. **Set spending limits in OpenAI dashboard**

## Next Steps

1. Install OpenAI package: `pip install openai`
2. Add API key to `.env`
3. Start backend server
4. Test analyze button
5. Review results rendering
6. Optimize prompts based on feedback

## Troubleshooting

### "OpenAI API key not configured"
- Check `.env` file exists
- Verify `OPENAI_API_KEY` is set
- Restart backend server

### "Rate limit exceeded"
- Wait and retry
- Upgrade OpenAI plan
- Implement caching

### "Timeout errors"
- Increase timeout in OpenAI client
- Use fast mode instead of deep
- Check network connection

### "Invalid response format"
- Check OpenAI model supports JSON mode
- Verify prompt structure
- Update to latest OpenAI package

## Support

For issues or questions:
1. Check backend logs: Look for error messages
2. Test API directly: Use cURL or Postman
3. Review OpenAI status: https://status.openai.com
4. Check API usage: https://platform.openai.com/usage
