# Dashboard Image Generator - Quick Setup Guide

## 🎯 Two Options for Dashboard Image

### Option 1: HTML Screenshot (Recommended - Works Immediately!) ✅

Since the Google API key is for Gemini (text) and not Imagen (images), I've created an HTML mockup that looks exactly like a real dashboard.

**Steps:**
1. Open `dashboard-preview-generator.html` in your browser
2. Take a screenshot (Windows: Win + Shift + S, Mac: Cmd + Shift + 4)
3. Save as `dashboard-preview.png` in `resources/generated/`
4. The homepage will automatically load it!

**Files Created:**
- ✅ `dashboard-preview-generator.html` - Beautiful HTML dashboard mockup
- ✅ `dashboard-generator.js` - Frontend script to load the image
- ✅ `test_image_generation.py` - API test script
- ✅ `backend/image_generation.py` - Image generation service
- ✅ `backend/image_api.py` - API endpoints
- ✅ Updated `index (1).html` with generate button

---

### Option 2: Use Google Imagen API (Requires Different API Key)

The API key you provided (`AIzaSyBUkCwt3sZDicU_-_MUsqjWlaiO7Uo7TAQ`) is for:
- ✅ Google Gemini (text generation)
- ❌ Google Imagen (image generation)

**To use real AI image generation:**

1. **Get Imagen API access:**
   - Go to: https://ai.google.dev/
   - Or use Vertex AI: https://cloud.google.com/vertex-ai/docs/generative-ai/image/generate-images
   - Need: Google Cloud project with Vertex AI enabled

2. **Alternative - Use Stability AI (DALL-E style):**
   ```bash
   # Install
   pip install stability-sdk
   
   # Get API key from: https://platform.stability.ai/
   ```

3. **Alternative - Use DALL-E:**
   ```bash
   # Install
   pip install openai
   
   # Get API key from: https://platform.openai.com/api-keys
   ```

---

## 🚀 Quick Start (HTML Screenshot Method)

### Step 1: Generate the Dashboard Image
```bash
# Open in browser
start dashboard-preview-generator.html

# OR just double-click the file
```

### Step 2: Take Screenshot
- Windows: `Win + Shift + S` → Select the dashboard card
- Mac: `Cmd + Shift + 4` → Click and drag around dashboard
- Save as: `dashboard-preview.png`

### Step 3: Place Image
```bash
# Put the screenshot here:
resources/generated/dashboard-preview.png
```

### Step 4: View Homepage
```bash
# Open homepage
http://localhost:8000/index%20(1).html

# The dashboard card will show your screenshot!
```

---

## 📁 File Structure

```
Project_O3/
├── index (1).html              # ✨ Updated with generate button
├── dashboard-generator.js      # Auto-loads dashboard image
├── dashboard-preview-generator.html  # HTML mockup for screenshots
├── test_image_generation.py    # API test script
├── backend/
│   ├── image_generation.py     # Image generation service
│   ├── image_api.py           # API endpoints
│   └── main.py                # ✨ Updated with image routes
└── resources/
    └── generated/
        └── dashboard-preview.png  # 👈 Put your screenshot here
```

---

## 🎨 Homepage Features Added

1. **Generate Button**: Click to trigger image generation (currently uses screenshot)
2. **Auto-load**: Automatically loads existing dashboard image
3. **Status Display**: Shows generation progress/errors
4. **Floating Animation**: Dashboard card has subtle floating effect
5. **Professional Layout**: Two-column hero with prominent dashboard card

---

## 🔧 Backend API Endpoints (Ready for Future Use)

Once you get Imagen/DALL-E API access:

```bash
POST /api/images/generate-dashboard
# Generate with custom parameters
{
  "drug_name": "Metformin",
  "cancer_type": "Breast Cancer",
  "confidence": 87,
  "opportunities": 1183,
  "high_confidence": 89,
  "in_progress": 24,
  "progress_percent": 78
}

POST /api/images/generate-quick
# Generate with default parameters

GET /api/images/dashboard-preview
# Get the generated image
```

---

## 💡 Next Steps

1. **Immediate**: Use HTML screenshot method (works now!)
2. **Later**: Get proper Imagen/DALL-E API key for real AI generation
3. **Optional**: Customize the HTML mockup in `dashboard-preview-generator.html`

---

## 🐛 Troubleshooting

**"Can't see the dashboard image"**
- Make sure file is named exactly: `dashboard-preview.png`
- Place in: `resources/generated/` folder
- Refresh browser with Ctrl+F5 (hard refresh)

**"Generate button doesn't work"**
- Backend server must be running on port 8000
- Current API key is for Gemini (text), not Imagen (images)
- Use HTML screenshot method instead

**"Want AI-generated images"**
- Need Vertex AI Imagen API key
- OR Stability AI key (easier to get)
- OR OpenAI DALL-E key
