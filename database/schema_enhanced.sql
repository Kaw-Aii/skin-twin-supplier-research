-- Enhanced Database Schema for SKIN-TWIN Supplier Research
-- Supabase PostgreSQL Database
-- Created: 2025-10-13
-- Purpose: Store and manage hypergraph data for South African skincare ingredient suppliers

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS research_log CASCADE;
DROP TABLE IF EXISTS hypergraph_edges CASCADE;
DROP TABLE IF EXISTS hypergraph_nodes CASCADE;

-- Hypergraph Nodes Table
-- Stores both suppliers and ingredients as nodes in the hypergraph
CREATE TABLE hypergraph_nodes (
    id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    timeset TEXT,
    modularity_class INTEGER,
    node_type TEXT CHECK (node_type IN ('supplier', 'ingredient')),
    
    -- Supplier-specific fields
    availability TEXT,
    pricing_estimate TEXT,
    supplier_url TEXT,
    notes TEXT,
    
    -- Ingredient-specific fields
    inci_name TEXT,
    cas_number TEXT,
    function TEXT,
    manufacturer TEXT,
    
    -- Metadata
    last_research_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Hypergraph Edges Table
-- Stores relationships between suppliers and ingredients
CREATE TABLE hypergraph_edges (
    id SERIAL PRIMARY KEY,
    source TEXT NOT NULL REFERENCES hypergraph_nodes(id) ON DELETE CASCADE,
    target TEXT NOT NULL REFERENCES hypergraph_nodes(id) ON DELETE CASCADE,
    edge_type TEXT DEFAULT 'supplies',
    weight REAL DEFAULT 1.0,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure unique edges
    UNIQUE(source, target, edge_type)
);

-- Research Log Table
-- Tracks research activities and findings
CREATE TABLE research_log (
    id SERIAL PRIMARY KEY,
    supplier_id TEXT REFERENCES hypergraph_nodes(id) ON DELETE CASCADE,
    research_date DATE NOT NULL,
    researcher TEXT,
    findings TEXT,
    sources TEXT[],
    confidence_level TEXT CHECK (confidence_level IN ('high', 'medium', 'low')),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_nodes_type ON hypergraph_nodes(node_type);
CREATE INDEX idx_nodes_modularity ON hypergraph_nodes(modularity_class);
CREATE INDEX idx_nodes_last_research ON hypergraph_nodes(last_research_date);
CREATE INDEX idx_edges_source ON hypergraph_edges(source);
CREATE INDEX idx_edges_target ON hypergraph_edges(target);
CREATE INDEX idx_research_supplier ON research_log(supplier_id);
CREATE INDEX idx_research_date ON research_log(research_date);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_nodes_updated_at
    BEFORE UPDATE ON hypergraph_nodes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_edges_updated_at
    BEFORE UPDATE ON hypergraph_edges
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Views for analysis
CREATE OR REPLACE VIEW supplier_summary AS
SELECT 
    n.id,
    n.label,
    n.availability,
    n.pricing_estimate,
    n.supplier_url,
    n.last_research_date,
    COUNT(e.target) AS ingredient_count
FROM hypergraph_nodes n
LEFT JOIN hypergraph_edges e ON n.id = e.source
WHERE n.node_type = 'supplier'
GROUP BY n.id, n.label, n.availability, n.pricing_estimate, n.supplier_url, n.last_research_date
ORDER BY ingredient_count DESC;

CREATE OR REPLACE VIEW ingredient_summary AS
SELECT 
    n.id,
    n.label,
    n.inci_name,
    n.function,
    n.manufacturer,
    COUNT(e.source) AS supplier_count
FROM hypergraph_nodes n
LEFT JOIN hypergraph_edges e ON n.id = e.target
WHERE n.node_type = 'ingredient'
GROUP BY n.id, n.label, n.inci_name, n.function, n.manufacturer
ORDER BY supplier_count DESC;

-- Comments for documentation
COMMENT ON TABLE hypergraph_nodes IS 'Stores both suppliers and ingredients as nodes in the hypergraph network';
COMMENT ON TABLE hypergraph_edges IS 'Stores supply relationships between suppliers and ingredients';
COMMENT ON TABLE research_log IS 'Tracks research activities and findings for each supplier';
COMMENT ON VIEW supplier_summary IS 'Summary view of suppliers with ingredient counts';
COMMENT ON VIEW ingredient_summary IS 'Summary view of ingredients with supplier counts';

