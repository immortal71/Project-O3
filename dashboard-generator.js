/**
 * Dashboard Image Generator
 * Triggers backend API to generate hero dashboard image using Google Imagen
 * Saves generated outputs to database
 */

// Import configuration (if available, otherwise use defaults)
const CONFIG = typeof window !== 'undefined' && window.CONFIG ? window.CONFIG : {
    API_BASE_URL: 'http://localhost:8000',
    ENDPOINTS: {
        IMAGE_GENERATE: '/api/images/generate-quick',
        IMAGE_DASHBOARD: '/api/images/dashboard-preview',
        DB_SAVE_OUTPUT: '/api/v1/db/output'
    },
    USE_DATABASE: true
};

const API_BASE_URL = CONFIG.API_BASE_URL;

/**
 * Save generated image to database
 */
async function saveImageToDatabase(imageData) {
    if (!CONFIG.USE_DATABASE) {
        console.log('Database not enabled, skipping save');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${CONFIG.ENDPOINTS.DB_SAVE_OUTPUT}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                output_type: 'dashboard_image',
                file_path: imageData.url,
                input_parameters: {
                    generation_time: new Date().toISOString(),
                    method: 'google_imagen'
                },
                output_data: {
                    success: imageData.success,
                    size: imageData.size || 'unknown'
                },
                status: 'completed'
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('✅ Image saved to database:', result.id);
            return result;
        }
    } catch (error) {
        console.warn('Could not save to database:', error);
    }
}

/**
 * Generate dashboard preview image
 */
async function generateDashboardImage() {
    const generateBtn = document.getElementById('generate-dashboard-btn');
    const statusDiv = document.getElementById('generation-status');
    const dashboardCard = document.getElementById('dashboard-preview-card');
    
    if (generateBtn) {
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';
    }
    
    if (statusDiv) {
        statusDiv.innerHTML = '<p class="text-sm" style="color: #14b8a6;">⏳ Generating dashboard image with Google Imagen...</p>';
    }
    
    try {
        // Call the backend API to generate image
        const response = await fetch(`${API_BASE_URL}${CONFIG.ENDPOINTS.IMAGE_GENERATE}`, {
            method: 'POST',
            headers: {
        /*
         * Copyright (c) 2025 OncoPurpose (trovesx)
         * All Rights Reserved.
         * For licensing info, see LICENSE or contact oncopurpose@trovesx.com
         */
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Save to database
            await saveImageToDatabase(result);
            
            // Update the dashboard card with the generated image
            if (dashboardCard) {
                dashboardCard.innerHTML = `
                    <img 
                        src="${API_BASE_URL}${result.url}?t=${Date.now()}" 
                        alt="OncoPurpose Dashboard Preview" 
                        class="w-full h-auto rounded-xl"
                        style="box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);"
                    />
                `;
            }
            
            if (statusDiv) {
                statusDiv.innerHTML = '<p class="text-sm" style="color: #10b981;">✓ Dashboard image generated successfully!</p>';
            }
            
            if (generateBtn) {
                generateBtn.textContent = '✓ Generated';
                setTimeout(() => {
                    generateBtn.disabled = false;
                    generateBtn.textContent = 'Regenerate Dashboard';
                }, 2000);
            }
        }
        
    } catch (error) {
        console.error('Failed to generate dashboard image:', error);
        
        if (statusDiv) {
            statusDiv.innerHTML = `
                <p class="text-sm" style="color: #ef4444;">
                    ✗ Failed to generate image. Please check:
                    <br>• Backend server is running on port 8000
                    <br>• Google API key is valid
                    <br>• Error: ${error.message}
                </p>
            `;
        }
        
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.textContent = 'Try Again';
        }
    }
}

/**
 * Check if generated image exists and load it
 */
async function loadExistingDashboardImage() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/images/dashboard-preview`);
        
        if (response.ok) {
            const dashboardCard = document.getElementById('dashboard-preview-card');
            if (dashboardCard) {
                dashboardCard.innerHTML = `
                    <img 
                        src="${API_BASE_URL}/api/images/dashboard-preview?t=${Date.now()}" 
                        alt="OncoPurpose Dashboard Preview" 
                        class="w-full h-auto rounded-xl"
                        style="box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);"
                    />
                `;
            }
        }
    } catch (error) {
        console.log('No existing dashboard image found');
    }
}

// Auto-load existing image on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadExistingDashboardImage);
} else {
    loadExistingDashboardImage();
}

// Export for use in other scripts
window.generateDashboardImage = generateDashboardImage;
