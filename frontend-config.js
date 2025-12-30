/**
 * OncoPurpose Frontend Configuration
 * Central configuration for API endpoints and settings
 */

// API Configuration
const CONFIG = {
    // API Base URL
    API_BASE_URL: 'http://localhost:8000',
    
    // Endpoints
    ENDPOINTS: {
        // In-memory endpoints (fast, no database required)
        SEARCH: '/api/v1/search',
        DRUG_DETAILS: '/api/v1/drug/',
        HERO_CASES: '/api/v1/hero-cases',
        STATS: '/api/v1/stats',
        ONCOLOGY: '/api/v1/oncology',
        MECHANISM: '/api/v1/mechanism/',
        
        // Database endpoints (persistent storage)
        DB_SEARCH: '/api/v1/db/search',
        DB_DRUG_DETAILS: '/api/v1/db/drug/',
        DB_HERO_CASES: '/api/v1/db/hero-cases',
        DB_STATS: '/api/v1/db/stats',
        DB_ONCOLOGY: '/api/v1/db/oncology',
        DB_MECHANISM: '/api/v1/db/mechanism/',
        DB_SAVE_OUTPUT: '/api/v1/db/output',
        DB_GET_OUTPUTS: '/api/v1/db/outputs',
        
        // Image generation (if available)
        IMAGE_GENERATE: '/api/images/generate-quick',
        IMAGE_DASHBOARD: '/api/images/dashboard-preview',
        
        // Discovery/Analysis
        DISCOVERY_ANALYZE: '/api/discovery/analyze',
        
        // Health check
        HEALTH: '/health'
    },
    
    // Settings
    USE_DATABASE: true,  // Set to false to use only in-memory data
    TIMEOUT: 30000,      // Request timeout in milliseconds
    RETRY_ATTEMPTS: 3,   // Number of retry attempts for failed requests
    
    // UI Settings
    RESULTS_PER_PAGE: 20,
    DEFAULT_CONFIDENCE_THRESHOLD: 0.7
};

/**
 * Make API request with error handling
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${CONFIG.API_BASE_URL}${endpoint}`;
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        timeout: CONFIG.TIMEOUT
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, finalOptions);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API Error [${endpoint}]:`, error);
        throw error;
    }
}

/**
 * Search drugs
 */
async function searchDrugs(query, limit = CONFIG.RESULTS_PER_PAGE, useDatabase = CONFIG.USE_DATABASE) {
    const endpoint = useDatabase ? CONFIG.ENDPOINTS.DB_SEARCH : CONFIG.ENDPOINTS.SEARCH;
    return apiRequest(`${endpoint}?q=${encodeURIComponent(query)}&limit=${limit}`);
}

/**
 * Get drug details
 */
async function getDrugDetails(drugName, useDatabase = CONFIG.USE_DATABASE) {
    const endpoint = useDatabase ? CONFIG.ENDPOINTS.DB_DRUG_DETAILS : CONFIG.ENDPOINTS.DRUG_DETAILS;
    return apiRequest(`${endpoint}${encodeURIComponent(drugName)}`);
}

/**
 * Get hero cases
 */
async function getHeroCases(limit = CONFIG.RESULTS_PER_PAGE, useDatabase = CONFIG.USE_DATABASE) {
    const endpoint = useDatabase ? CONFIG.ENDPOINTS.DB_HERO_CASES : CONFIG.ENDPOINTS.HERO_CASES;
    return apiRequest(`${endpoint}?limit=${limit}`);
}

/**
 * Get statistics
 */
async function getStats(useDatabase = CONFIG.USE_DATABASE) {
    const endpoint = useDatabase ? CONFIG.ENDPOINTS.DB_STATS : CONFIG.ENDPOINTS.STATS;
    return apiRequest(endpoint);
}

/**
 * Save generated output to database
 */
async function saveGeneratedOutput(outputData) {
    if (!CONFIG.USE_DATABASE) {
        console.warn('Database not enabled, output not saved');
        return null;
    }
    
    return apiRequest(CONFIG.ENDPOINTS.DB_SAVE_OUTPUT, {
        method: 'POST',
        body: JSON.stringify(outputData)
    });
}

/**
 * Get generated outputs from database
 */
async function getGeneratedOutputs(filters = {}, limit = CONFIG.RESULTS_PER_PAGE) {
    if (!CONFIG.USE_DATABASE) {
        console.warn('Database not enabled');
        return [];
    }
    
    const params = new URLSearchParams({
        limit: limit.toString(),
        ...filters
    });
    
    return apiRequest(`${CONFIG.ENDPOINTS.DB_GET_OUTPUTS}?${params}`);
}

/**
 * Health check
 */
async function checkHealth() {
    return apiRequest(CONFIG.ENDPOINTS.HEALTH);
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        CONFIG,
        apiRequest,
        searchDrugs,
        getDrugDetails,
        getHeroCases,
        getStats,
        saveGeneratedOutput,
        getGeneratedOutputs,
        checkHealth
    };
}
