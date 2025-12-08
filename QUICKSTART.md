# OpenAI Integration - Quick Start

## ✅ What's Been Done

1. **Backend Service Created**
   - `backend/openai_service.py` - OpenAI integration with GPT-4
   - `backend/discovery_api.py` - REST API endpoints
   - `backend/config.py` - Configuration with OpenAI settings
   - `backend/main.py` - Discovery router registered

2. **OpenAI Package Installed**
   - Successfully installed `openai` v2.8.1
   - All dependencies resolved

3. **Frontend Ready**
   - `discovery.html` analyze button configured
   - API call structure in place
   - Loading states implemented
   - Error handling ready

## 🚀 Next Steps

### Step 1: Get OpenAI API Key

1. Visit https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

### Step 2: Configure Environment

1. Create `.env` file in `backend/` directory:
   ```bash
   # Copy from example
   copy .env.example .env
   ```

2. Edit `.env` and add your OpenAI key:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   OPENAI_MODEL=gpt-4
   OPENAI_MAX_TOKENS=2000
   OPENAI_TEMPERATURE=0.7
   ```

3. Add minimal config for development:
   ```
   SECRET_KEY=dev-secret-key-change-in-production
   DATABASE_URL=sqlite:///./oncopurpose.db
   REDIS_URL=redis://localhost:6379/0
   ENVIRONMENT=development
   ```

### Step 3: Start Backend Server

```powershell
cd backend
python main.py
```

Server will start at: http://localhost:8000

### Step 4: Test the Integration

1. Open `discovery.html` in browser
2. Fill in the form:
   - Cancer Type: "Breast Cancer"
   - Drug Name: "Aspirin"
   - Analysis Mode: Fast (toggle off) or Deep (toggle on)
3. Click "Analyze Drug"
4. View results in console and alert

## 📋 API Endpoint

**POST** `/api/discovery/analyze`

**Frontend sends:**
```json
{
  "cancer_type": "Breast Cancer",
  "drug_name": "Aspirin",
  "molecular_target": "COX-2",
  "current_indication": "Pain reliever",
  "analysis_mode": "fast",
  "confidence_threshold": 70
}
```

**Backend returns:**
```json
{
  "success": true,
  "analysis_mode": "fast",
  "model_used": "gpt-4",
  "tokens_used": 1234,
  "result": {
    "confidence_score": 75,
    "drug_name": "Aspirin",
    "cancer_type": "Breast Cancer",
    "mechanism_of_action": "...",
    "evidence_summary": "...",
    "safety_profile": "...",
    "market_opportunity": "...",
    "recommendation": "...",
    "key_findings": ["...", "..."]
  },
  "message": "Analysis completed successfully"
}
```

## 🔍 Testing Without API Key

If you don't have an OpenAI API key yet, you can test with mock data:

1. The API will return an error: "OpenAI API key not configured"
2. This confirms the endpoint is working
3. Once you add the API key, real analysis will work

## 💰 Cost Estimate

- **Fast mode**: ~$0.05-0.10 per analysis
- **Deep mode**: ~$0.15-0.25 per analysis
- **Monthly** (100 analyses): ~$5-25 depending on mode

## 📝 Current Status

✅ Backend service implemented
✅ API endpoints created  
✅ OpenAI package installed
✅ Frontend configured
⏳ Needs: OpenAI API key in .env
⏳ Needs: Backend server running
⏳ Needs: Results rendering in UI

## 🎯 Next Implementation

After getting basic analysis working, we can add:

1. **Results Rendering** - Display analysis in discovery.html
2. **Result Cards** - Format confidence scores, mechanisms, evidence
3. **Export Results** - Download as PDF/CSV
4. **Result History** - Save and view past analyses
5. **Batch Analysis** - Analyze multiple drugs at once

## 🆘 Troubleshooting

**"OpenAI API key not configured"**
→ Add `OPENAI_API_KEY` to `.env` file

**"Failed to fetch"**
→ Backend server not running - run `python main.py`

**"API error: 401"**
→ Invalid API key - check OpenAI dashboard

**"API error: 429"**
→ Rate limit exceeded - wait or upgrade plan

**"Connection refused"**
→ Backend not started or wrong port

## 📞 Support

Check these resources:
- OpenAI Status: https://status.openai.com
- OpenAI Docs: https://platform.openai.com/docs
- Backend logs: Check terminal output
- Frontend logs: Check browser console (F12)

---

**Ready to test!** Just add your OpenAI API key to `.env` and start the backend server.
