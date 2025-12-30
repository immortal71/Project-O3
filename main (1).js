// OncoPurpose - Main JavaScript Functionality
// Professional Oncology Drug Repurposing Platform

/*
 * Copyright (c) 2025 OncoPurpose (trovesx)
 * All Rights Reserved.
 * For licensing info, see LICENSE or contact oncopurpose@trovesx.com
 */

// Global state management
const OncoPurpose = {
    currentUser: {
        name: 'Dr. Sarah Chen',
        role: 'Senior Research Director',
        company: 'PharmaCorp International',
        avatar: 'resources/user avtars/exec2 (1).png'
    },
    
    // Mock data for demonstration
    drugs: [
        {
            id: 1,
            name: 'Metformin',
            currentIndication: 'Type 2 Diabetes',
            newIndication: 'Breast Cancer',
            confidence: 87.3,
            marketSize: '$2.3B',
            phase: 'Phase II',
            patentStatus: 'Active',
            structure: 'resources/drug structure/metformin.png',
            mechanism: 'AMPK activation, mTOR inhibition',
            evidence: '12 clinical trials, 45 research papers',
            timeline: '18-24 months to Phase III'
        },
        {
            id: 2,
            name: 'Ibuprofen',
            currentIndication: 'Pain/Inflammation',
            newIndication: 'Colorectal Cancer',
            confidence: 78.3,
            marketSize: '$1.8B',
            phase: 'Phase I',
            patentStatus: 'Expired',
            structure: 'resources/drug structure/ibuprofen.png',
            mechanism: 'COX-2 inhibition, anti-inflammatory',
            evidence: '8 clinical trials, 32 research papers',
            timeline: '12-18 months to Phase II'
        },
        {
            id: 3,
            name: 'Aspirin',
            currentIndication: 'Cardiovascular',
            newIndication: 'Lung Cancer',
            confidence: 91.7,
            marketSize: '$3.1B',
            phase: 'Phase III',
            patentStatus: 'Expired',
            structure: 'resources/drug structure/aspirin.png',
            mechanism: 'COX-1/2 inhibition, anti-platelet',
            evidence: '15 clinical trials, 67 research papers',
            timeline: '6-12 months to Approval'
        }
    ],
    
    analytics: {
        totalOpportunities: 1247,
        highConfidenceMatches: 83,
        drugsAnalyzed: 3428,
        papersReviewed: 12891,
        topCancerTypes: [
            { name: 'Breast', opportunities: 234, confidence: 78 },
            { name: 'Lung', opportunities: 189, confidence: 82 },
            { name: 'Colorectal', opportunities: 156, confidence: 71 },
            { name: 'Prostate', opportunities: 127, confidence: 75 },
            { name: 'Melanoma', opportunities: 94, confidence: 85 }
        ]
    }
};

// Utility functions
const utils = {
    // Format numbers with commas
    formatNumber: (num) => {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    },
    
    // Animate counter numbers
    animateCounter: (element, start, end, duration = 2000) => {
        const startTime = performance.now();
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const current = Math.floor(start + (end - start) * progress);
            element.textContent = utils.formatNumber(current);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        requestAnimationFrame(animate);
    },
    
    // Show notification toast
    showToast: (message, type = 'success') => {
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full`;
        toast.classList.add(type === 'success' ? 'bg-green-600' : 'bg-red-600');
        toast.innerHTML = `
            <div class="flex items-center text-white">
                <span class="mr-2">${type === 'success' ? '✓' : '✗'}</span>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);
        
        // Animate out and remove
        setTimeout(() => {
            toast.classList.add('translate-x-full');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    },
    
    // Initialize tooltips
    initTooltips: () => {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                const tooltip = document.createElement('div');
                tooltip.className = 'absolute z-50 px-2 py-1 text-sm bg-gray-800 text-white rounded shadow-lg';
                tooltip.textContent = e.target.dataset.tooltip;
                tooltip.style.left = e.pageX + 10 + 'px';
                tooltip.style.top = e.pageY - 30 + 'px';
                tooltip.id = 'tooltip';
                document.body.appendChild(tooltip);
            });
            
            element.addEventListener('mouseleave', () => {
                const tooltip = document.getElementById('tooltip');
                if (tooltip) {
                    document.body.removeChild(tooltip);
                }
            });
        });
    }
};

// Navigation functionality
const navigation = {
    init: () => {
        // Set active navigation state
        const currentPage = window.location.pathname.split('/').pop() || 'index.html';
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href === currentPage || (currentPage === '' && href === 'index.html')) {
                link.classList.add('active');
            }
        });
        
        // Initialize user profile
        navigation.initUserProfile();
        
        // Initialize search functionality
        navigation.initSearch();
    },
    
    initUserProfile: () => {
        const userNameElement = document.getElementById('user-name');
        const userRoleElement = document.getElementById('user-role');
        const userAvatarElement = document.getElementById('user-avatar');
        
        if (userNameElement) userNameElement.textContent = OncoPurpose.currentUser.name;
        if (userRoleElement) userRoleElement.textContent = OncoPurpose.currentUser.role;
        if (userAvatarElement) userAvatarElement.src = OncoPurpose.currentUser.avatar;
    },
    
    initSearch: () => {
        const searchInput = document.getElementById('global-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                const query = e.target.value.toLowerCase();
                // Implement search logic here
                console.log('Searching for:', query);
            });
        }
    }
};

// Dashboard functionality
const dashboard = {
    init: () => {
        if (document.getElementById('dashboard-kpi')) {
            dashboard.initKPIs();
            dashboard.initChart();
            dashboard.initTable();
        }
    },
    
    initKPIs: () => {
        const kpis = [
            { id: 'total-opportunities', value: OncoPurpose.analytics.totalOpportunities },
            { id: 'high-confidence', value: OncoPurpose.analytics.highConfidenceMatches },
            { id: 'drugs-analyzed', value: OncoPurpose.analytics.drugsAnalyzed },
            { id: 'papers-reviewed', value: OncoPurpose.analytics.papersReviewed }
        ];
        
        kpis.forEach(kpi => {
            const element = document.getElementById(kpi.id);
            if (element) {
                utils.animateCounter(element, 0, kpi.value);
            }
        });
    },
    
    initChart: () => {
        const chartElement = document.getElementById('cancer-types-chart');
        if (chartElement && typeof echarts !== 'undefined') {
            const chart = echarts.init(chartElement);
            
            const option = {
                backgroundColor: 'transparent',
                tooltip: {
                    trigger: 'axis',
                    backgroundColor: '#1e293b',
                    borderColor: '#334155',
                    borderWidth: 1,
                    textStyle: { color: '#e5e7eb', fontSize: 12 },
                    axisPointer: {
                        type: 'shadow',
                        shadowStyle: {
                            color: 'rgba(20, 184, 166, 0.1)'
                        }
                    },
                    formatter: function(params) {
                        const data = params[0];
                        const cancerType = OncoPurpose.analytics.topCancerTypes[data.dataIndex];
                        return `
                            <strong style="color: #10b981;">${data.name}</strong><br/>
                            Opportunities: <strong>${data.value}</strong><br/>
                            Avg. Confidence: <strong>${cancerType.confidence}%</strong>
                        `;
                    }
                },
                grid: {
                    left: '10%',
                    right: '5%',
                    bottom: '15%',
                    top: '5%'
                },
                xAxis: {
                    type: 'category',
                    data: OncoPurpose.analytics.topCancerTypes.map(item => item.name),
                    axisLabel: { color: '#94a3b8', fontSize: 11 },
                    axisLine: { lineStyle: { color: '#334155' } }
                },
                yAxis: {
                    type: 'value',
                    axisLabel: { color: '#94a3b8', fontSize: 11 },
                    splitLine: { lineStyle: { color: '#1e293b' } }
                },
                series: [{
                    data: OncoPurpose.analytics.topCancerTypes.map((item, index) => ({
                        value: item.opportunities,
                        itemStyle: {
                            color: ['#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#d1fae5'][index]
                        }
                    })),
                    type: 'bar',
                    barWidth: '40%',
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(16, 185, 129, 0.5)'
                        }
                    }
                }]
            };
            
            chart.setOption(option);
            
            // Responsive resize
            window.addEventListener('resize', () => {
                chart.resize();
            });
        }
    },
    
    initTable: () => {
        const tableBody = document.getElementById('drugs-table-body');
        if (tableBody) {
            // Load from localStorage (user-generated reports) + static demo data
            const savedReports = JSON.parse(localStorage.getItem('userAnalysisResults') || '[]');
            
            // Combine saved reports with demo data
            const allDrugs = [
                ...savedReports.map(report => ({
                    id: report.drug_name + '-' + report.cancer_type,
                    name: report.drug_name,
                    currentIndication: report.current_indication || 'Various',
                    newIndication: report.cancer_type,
                    confidence: (report.confidence_score > 1 ? report.confidence_score : report.confidence_score * 100),
                    marketSize: report.market_potential || '$1-3B',
                    phase: report.development_phase || 'Preclinical',
                    patentStatus: 'Active',
                    structure: 'resources/drug structure/metformin.png',
                    mechanism: report.mechanism || 'Under investigation',
                    evidence: report.evidence || 'Analysis in progress',
                    timeline: report.timeline || '2-4 years'
                })),
                ...OncoPurpose.drugs
            ];
            
            // Remove duplicates (user reports override demo data)
            const uniqueDrugs = [];
            const seen = new Set();
            
            allDrugs.forEach(drug => {
                const key = `${drug.name}-${drug.newIndication}`.toLowerCase();
                if (!seen.has(key)) {
                    seen.add(key);
                    uniqueDrugs.push(drug);
                }
            });
            
            tableBody.innerHTML = uniqueDrugs.map((drug, index) => `
                <tr class="table-row">
                    <td class="px-6 py-4">
                        <div class="flex items-center">
                            <img src="${drug.structure}" alt="${drug.name}" class="w-10 h-10 mr-3 rounded" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2240%22 height=%2240%22%3E%3Crect width=%2240%22 height=%2240%22 fill=%22%2314b8a6%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 font-size=%2220%22 fill=%22white%22%3E${drug.name.charAt(0)}%3C/text%3E%3C/svg%3E'">
                            <span class="font-medium" style="color: #f1f5f9;">${drug.name}</span>
                        </div>
                    </td>
                    <td class="px-6 py-4" style="color: #cbd5e1;">${drug.newIndication}</td>
                    <td class="px-6 py-4 text-right">
                        <div class="flex items-center justify-end space-x-3">
                            <div class="flex-1 max-w-[100px] bg-gray-700/30 rounded-full h-1.5">
                                <div class="confidence-bar h-1.5 rounded-full" style="width: ${drug.confidence}%; background: linear-gradient(90deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);"></div>
                            </div>
                            <span class="text-sm data-number" style="color: var(--accent-primary);">${drug.confidence}%</span>
                        </div>
                    </td>
                    <td class="px-6 py-4 text-right data-number" style="color: var(--accent-primary);">${drug.marketSize}</td>
                    <td class="px-6 py-4 text-center">
                        <div class="flex items-center justify-center space-x-2">
                            <button onclick="dashboard.viewDetails('${drug.name}', '${drug.newIndication}')" class="action-button-primary px-3 py-1.5 text-xs font-medium view-details-btn" style="color: white;" data-drug="${drug.name}" data-cancer="${drug.newIndication}">
                                <i data-lucide="arrow-right" style="width: 12px; height: 12px; display: inline; vertical-align: middle; margin-right: 4px;"></i>
                                View Details
                            </button>
                            <div class="relative">
                                <button class="action-button-secondary p-1.5 rounded" style="color: #94a3b8;">
                                    <i data-lucide="more-vertical" style="width: 16px; height: 16px;"></i>
                                </button>
                            </div>
                        </div>
                    </td>
                </tr>
            `).join('');
            
            // Re-initialize Lucide icons for dynamically added content
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        }
    },
    
    viewDetails: (drugName, cancerType) => {
        // Navigate to details page with drug and cancer parameters
        window.location.href = `details.html?drug=${encodeURIComponent(drugName)}&cancer=${encodeURIComponent(cancerType)}`;
    },
    
    saveOpportunity: (drugId) => {
        // Implement save functionality
        utils.showToast(`Drug ${drugId} saved to opportunities`);
    },
    
    exportData: (drugId) => {
        // Implement export functionality
        utils.showToast(`Data exported for drug ${drugId}`);
    }
};

// Discovery page functionality
const discovery = {
    init: () => {
        if (document.getElementById('discovery-search')) {
            discovery.initSearch();
            discovery.initFilters();
            discovery.initResults();
        }
    },
    
    initSearch: () => {
        const searchForm = document.getElementById('discovery-search');
        const analyzeBtn = document.getElementById('analyze-btn');
        
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                discovery.performAnalysis();
            });
        }
    },
    
    initFilters: () => {
        // Initialize filter toggles and interactions
        const filterToggle = document.getElementById('filter-toggle');
        const advancedFilters = document.getElementById('advanced-filters');
        
        if (filterToggle && advancedFilters) {
            filterToggle.addEventListener('click', () => {
                advancedFilters.classList.toggle('hidden');
            });
        }
    },
    
    initResults: () => {
        discovery.renderResults(OncoPurpose.drugs);
    },
    
    performAnalysis: () => {
        const analyzeBtn = document.getElementById('analyze-btn');
        const originalText = analyzeBtn.textContent;
        
        // Show loading state
        analyzeBtn.textContent = 'Analyzing...';
        analyzeBtn.disabled = true;
        analyzeBtn.classList.add('opacity-50');
        
        // Simulate analysis delay
        setTimeout(() => {
            analyzeBtn.textContent = originalText;
            analyzeBtn.disabled = false;
            analyzeBtn.classList.remove('opacity-50');
            
            // Update results
            discovery.renderResults(OncoPurpose.drugs);
            utils.showToast('Analysis complete! Results updated.');
        }, 2000);
    },
    
    renderResults: (drugs) => {
        const resultsGrid = document.getElementById('results-grid');
        if (resultsGrid) {
            // CHANGED: Use insertAdjacentHTML instead of innerHTML to NOT overwrite existing cards
            const cardsHTML = drugs.map((drug, index) => `
                <div class="bg-slate-800/80 backdrop-blur-sm rounded-xl p-6 border border-slate-700 hover:border-emerald-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-emerald-500/10">
                    <div class="flex items-start justify-between mb-4">
                        <div>
                            <h3 class="text-lg font-semibold text-white mb-1">${drug.name}</h3>
                            <p class="text-sm text-gray-400">${drug.currentIndication}</p>
                        </div>
                        <div class="w-12 h-12 rounded-lg" style="background: var(--bg-secondary); display: flex; align-items: center; justify-content: center;">
                            <span class="text-xl">💊</span>
                        </div>
                    </div>
                    
                    <div class="mb-4">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-sm text-gray-400">Confidence Score</span>
                            <span class="text-sm font-medium text-emerald-400">${drug.confidence}%</span>
                        </div>
                        <div class="w-full bg-gray-700 rounded-full h-2">
                            <div class="h-2 rounded" style="width: ${drug.confidence}%; background-color: #14b8a6;"></div>
                        </div>
                    </div>
                    
                    <div class="space-y-2 mb-4">
                        <div class="flex justify-between text-sm">
                            <span class="text-gray-400">Target Cancer:</span>
                            <span class="text-white">${drug.newIndication}</span>
                        </div>
                        <div class="flex justify-between text-sm">
                            <span class="text-gray-400">Market Size:</span>
                            <span class="text-green-400">${drug.marketSize}</span>
                        </div>
                        <div class="flex justify-between text-sm">
                            <span class="text-gray-400">Phase:</span>
                            <span class="text-yellow-400">${drug.phase}</span>
                        </div>
                    </div>
                    
                    <div class="flex space-x-2">
                        <button onclick="discovery.viewDetails(${drug.id})" class="flex-1 bg-teal-600 hover:bg-teal-700 text-white py-2 px-4 rounded text-sm transition-colors">
                            View Report
                        </button>
                        <button onclick="discovery.saveToProject(${drug.id})" class="bg-green-600 hover:bg-green-700 text-white py-2 px-3 rounded-lg text-sm transition-colors">
                            Save
                        </button>
                        <button onclick="deletePreloadedCard('${drug.name}', '${drug.newIndication}')" 
                                class="bg-red-600 hover:bg-red-700 text-white py-2 px-3 rounded-lg text-sm transition-colors"
                                title="Delete this analysis">
                            🗑️
                        </button>
                    </div>
                </div>
            `).join('');
            
            // CHANGED: Only set innerHTML if grid is empty, otherwise don't touch it
            if (resultsGrid.children.length === 0) {
                resultsGrid.innerHTML = cardsHTML;
            }
        }
    },
    
    viewDetails: (drugId) => {
        window.location.href = `details.html?id=${drugId}`;
    },
    
    saveToProject: (drugId) => {
        utils.showToast(`Drug saved to project portfolio`);
    }
};

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize navigation
    navigation.init();
    
    // Initialize page-specific functionality
    dashboard.init();
    discovery.init();
    
    // Initialize tooltips
    utils.initTooltips();
    
    // Initialize animations
    if (typeof anime !== 'undefined') {
        // Stagger animation for cards
        anime({
            targets: '.animate-card',
            translateY: [50, 0],
            opacity: [0, 1],
            delay: anime.stagger(100),
            duration: 800,
            easing: 'easeOutExpo'
        });
    }
    
    // Initialize typewriter effect for hero text
    if (document.getElementById('hero-typewriter') && typeof Typed !== 'undefined') {
        new Typed('#hero-typewriter', {
            strings: [
                'Accelerate Oncology Drug Repurposing with AI',
                'Reduce Time to Market by 70%',
                'AI-Powered Predictions for Cancer Treatment'
            ],
            typeSpeed: 50,
            backSpeed: 30,
            backDelay: 2000,
            loop: true
        });
    }

    // Ensure generic button handlers for buttons without explicit handlers
    const ensureButtonHandlers = () => {
        document.body.addEventListener('click', (e) => {
            const btn = e.target.closest('button');
            if (!btn) return;

            // Respect existing inline handlers and form submits
            if (btn.hasAttribute('onclick')) return;
            if (btn.type && btn.type.toLowerCase() === 'submit') return;
            if (btn.disabled) return;

            const text = (btn.textContent || '').trim();
            const action = (btn.dataset && btn.dataset.action) ? btn.dataset.action.toLowerCase() : text.toLowerCase();
            const btnId = btn.id || '';

            // Helper to safely attempt opening demo modal if present
            const tryOpenDemo = () => {
                if (typeof openDemoModal === 'function') {
                    openDemoModal();
                    return true;
                }
                if (document.getElementById('demo-modal')) {
                    document.getElementById('demo-modal').classList.remove('hidden');
                    return true;
                }
                return false;
            };

            // Handle specific button IDs
            if (btnId === 'request-demo-btn' || btnId === 'get-started-btn') {
                if (!tryOpenDemo()) utils.showToast('Demo request submitted');
                return;
            }
            if (btnId === 'watch-demo-btn') {
                utils.showToast('Opening demo video...');
                return;
            }
            if (btnId === 'analyze-btn') {
                utils.showToast('Analysis started — processing...');
                setTimeout(() => utils.showToast('Analysis complete!'), 2000);
                return;
            }
            if (btnId === 'filter-toggle') {
                const filters = document.getElementById('advanced-filters');
                if (filters) filters.classList.toggle('hidden');
                return;
            }

            // Map common button text to fallback behaviors
            if (/export|download|pdf/i.test(action)) {
                utils.showToast('Export started');
                return;
            }

            if (/save|add to project|save to/i.test(action)) {
                utils.showToast('Saved to your project');
                return;
            }

            if (/cite|citation|copy citation/i.test(action)) {
                utils.showToast('Citation copied to clipboard');
                return;
            }

            if (/share|share dashboard/i.test(action)) {
                utils.showToast('Share link copied to clipboard');
                return;
            }

            if (/load more/i.test(action)) {
                utils.showToast('Loading more items...');
                return;
            }

            if (/request demo|schedule demo|get started|start free trial/i.test(action)) {
                if (!tryOpenDemo()) utils.showToast('Demo request submitted');
                return;
            }

            if (/watch demo|watch video/i.test(action)) {
                utils.showToast('Opening demo video...');
                return;
            }

            if (/contact sales|contact us/i.test(action)) {
                utils.showToast('Contact request sent');
                return;
            }

            if (/clear filters|reset/i.test(action)) {
                utils.showToast('Filters cleared');
                return;
            }

            if (/view report|view details/i.test(action)) {
                utils.showToast('Opening detailed report...');
                return;
            }

            if (/run analysis|analyze/i.test(action)) {
                utils.showToast('Analysis started');
                setTimeout(() => utils.showToast('Analysis complete!'), 2000);
                return;
            }

            if (/generate report|generate/i.test(action)) {
                utils.showToast('Generating report...');
                setTimeout(() => utils.showToast('Report generated'), 1500);
                return;
            }

            if (/summarize/i.test(action)) {
                utils.showToast('AI summarization in progress...');
                setTimeout(() => utils.showToast('Summary ready'), 2000);
                return;
            }

            if (/copy|copy to clipboard/i.test(action)) {
                utils.showToast('Copied to clipboard');
                return;
            }

            if (/revoke|remove/i.test(action)) {
                utils.showToast('Action confirmed');
                return;
            }

            if (/invite|add member/i.test(action)) {
                utils.showToast('Invitation sent');
                return;
            }

            if (/reconnect/i.test(action)) {
                utils.showToast('Reconnecting...');
                return;
            }

            if (/change plan|upgrade/i.test(action)) {
                utils.showToast('Redirecting to plans...');
                return;
            }

            if (/update|change photo/i.test(action)) {
                utils.showToast('Update saved');
                return;
            }

            // Handle settings navigation buttons
            if (btn.classList.contains('settings-nav')) {
                const section = btn.dataset.section;
                if (section) {
                    document.querySelectorAll('.settings-nav').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    document.querySelectorAll('.settings-content').forEach(s => s.classList.add('hidden'));
                    const target = document.getElementById(`${section}-section`);
                    if (target) target.classList.remove('hidden');
                }
                return;
            }

            // Fallback: if button has a data-action attribute, show it
            if (btn.dataset && btn.dataset.action) {
                utils.showToast(`${btn.dataset.action}`);
                return;
            }

            // Generic fallback for unlabeled buttons
            if (text) {
                utils.showToast(`${text}`);
            }
        });
    };

    ensureButtonHandlers();
});

// Listen for localStorage changes (cross-page sync)
window.addEventListener('storage', (e) => {
    if (e.key === 'userAnalysisResults') {
        // Reload dashboard table when new reports are added
        if (typeof dashboard !== 'undefined' && dashboard.initTable) {
            dashboard.initTable();
        }
    }
});

// Also listen for same-page localStorage changes
const originalSetItem = localStorage.setItem;
localStorage.setItem = function(key, value) {
    const event = new Event('localStorageChange');
    event.key = key;
    event.newValue = value;
    window.dispatchEvent(event);
    originalSetItem.apply(this, arguments);
};

window.addEventListener('localStorageChange', (e) => {
    if (e.key === 'userAnalysisResults') {
        // Reload dashboard table when new reports are added
        if (typeof dashboard !== 'undefined' && dashboard.initTable) {
            dashboard.initTable();
        }
    }
});

// Export for global access
window.OncoPurpose = OncoPurpose;
window.utils = utils;
window.navigation = navigation;
window.dashboard = dashboard;
window.discovery = discovery;