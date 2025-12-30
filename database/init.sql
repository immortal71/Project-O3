-- OncoPurpose Database Schema
-- MySQL 8.0

-- Drugs table (stores all drug data from Broad Hub and other sources)
CREATE TABLE IF NOT EXISTS drugs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    drug_name VARCHAR(255) NOT NULL,
    clinical_phase VARCHAR(50),
    mechanism_of_action TEXT,
    target VARCHAR(500),
    disease_area VARCHAR(255),
    indication TEXT,
    source VARCHAR(50) DEFAULT 'broad_hub',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_drug_name (drug_name),
    INDEX idx_clinical_phase (clinical_phase),
    INDEX idx_source (source)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Hero cases table (gold standard repurposing examples)
CREATE TABLE IF NOT EXISTS hero_cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    drug_name VARCHAR(255) NOT NULL,
    original_indication VARCHAR(255),
    repurposed_cancer VARCHAR(255) NOT NULL,
    confidence_score DECIMAL(3,2),
    trial_count INT DEFAULT 0,
    citations INT DEFAULT 0,
    mechanism TEXT,
    pathways TEXT,
    evidence_level VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_drug_name (drug_name),
    INDEX idx_confidence (confidence_score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Generated outputs table (stores all generated predictions/analyses)
CREATE TABLE IF NOT EXISTS generated_outputs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    output_type VARCHAR(50) NOT NULL,  -- 'prediction', 'analysis', 'image', etc.
    drug_name VARCHAR(255),
    cancer_type VARCHAR(255),
    input_parameters JSON,
    output_data JSON,
    file_path VARCHAR(500),  -- for images/PDFs
    confidence_score DECIMAL(3,2),
    status VARCHAR(50) DEFAULT 'completed',  -- 'pending', 'completed', 'failed'
    user_id VARCHAR(100),
    session_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_output_type (output_type),
    INDEX idx_drug_name (drug_name),
    INDEX idx_session (session_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Mechanisms of action table (indexed for fast lookup)
CREATE TABLE IF NOT EXISTS mechanisms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mechanism_name VARCHAR(255) NOT NULL UNIQUE,
    drug_count INT DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_mechanism (mechanism_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Targets table (indexed for fast lookup)
CREATE TABLE IF NOT EXISTS targets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    target_name VARCHAR(255) NOT NULL UNIQUE,
    drug_count INT DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_target (target_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Drug-Mechanism relationship table (many-to-many)
CREATE TABLE IF NOT EXISTS drug_mechanisms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    drug_id INT NOT NULL,
    mechanism_id INT NOT NULL,
    FOREIGN KEY (drug_id) REFERENCES drugs(id) ON DELETE CASCADE,
    FOREIGN KEY (mechanism_id) REFERENCES mechanisms(id) ON DELETE CASCADE,
    UNIQUE KEY unique_drug_mechanism (drug_id, mechanism_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Drug-Target relationship table (many-to-many)
CREATE TABLE IF NOT EXISTS drug_targets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    drug_id INT NOT NULL,
    target_id INT NOT NULL,
    FOREIGN KEY (drug_id) REFERENCES drugs(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES targets(id) ON DELETE CASCADE,
    UNIQUE KEY unique_drug_target (drug_id, target_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Analytics/Stats cache table
CREATE TABLE IF NOT EXISTS analytics_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cache_key VARCHAR(255) NOT NULL UNIQUE,
    cache_value JSON,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_cache_key (cache_key),
    INDEX idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User activity log (optional for analytics)
CREATE TABLE IF NOT EXISTS activity_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100),
    action VARCHAR(100),
    endpoint VARCHAR(255),
    parameters JSON,
    response_time_ms INT,
    status_code INT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_action (action),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
