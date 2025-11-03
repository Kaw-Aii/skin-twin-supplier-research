import csv
import json
import subprocess
from datetime import datetime

# Project ID for Neon
PROJECT_ID = "damp-brook-31747632"

def run_neon_sql(sql_statement):
    """Execute SQL statement via Neon MCP CLI"""
    cmd = [
        "manus-mcp-cli", "tool", "call", "run_sql",
        "--server", "neon",
        "--input", json.dumps({
            "params": {
                "projectId": PROJECT_ID,
                "sql": sql_statement
            }
        })
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def load_nodes_from_csv():
    """Load nodes from RSNodes_updated_new.csv"""
    csv_file = '/home/ubuntu/skin-twin-supplier-research/data/RSNodes_updated_new.csv'
    
    nodes_data = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        
        for row in reader:
            if len(row) < 9:
                continue
            
            node_id = row[0]
            name = row[1]
            label = row[2]
            modularity = row[3]
            availability = row[4]
            pricing = row[5]
            website = row[6]
            notes = row[7]
            last_updated = row[8]
            
            # Determine node type
            if modularity and modularity.strip():
                node_type = "ingredient"
                supplier_id = modularity
            else:
                node_type = "supplier"
                supplier_id = None
            
            # Build metadata
            metadata = {
                "label": label,
                "availability": availability,
                "pricing": pricing,
                "website": website,
                "notes": notes,
                "last_updated": last_updated
            }
            
            if supplier_id:
                metadata["supplier_id"] = supplier_id
            
            nodes_data.append((node_id, node_type, name, metadata))
    
    return nodes_data

def load_edges_from_csv():
    """Load edges from RSEdges.csv"""
    csv_file = '/home/ubuntu/skin-twin-supplier-research/data/RSEdges.csv'
    
    edges_data = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        
        for row in reader:
            if len(row) < 4:
                continue
            
            source = row[0]
            target = row[1]
            edge_type = row[2]
            weight = row[3] if len(row) > 3 else "1"
            
            metadata = {
                "type": edge_type,
                "weight": weight
            }
            
            edges_data.append((source, target, metadata))
    
    return edges_data

def main():
    print("=" * 80)
    print("LOADING DATA TO NEON DATABASE")
    print("=" * 80)
    print()
    
    # Clear existing data
    print("Clearing existing data...")
    success, stdout, stderr = run_neon_sql("DELETE FROM edges;")
    if success:
        print("✅ Edges cleared")
    else:
        print(f"❌ Error clearing edges: {stderr}")
    
    success, stdout, stderr = run_neon_sql("DELETE FROM nodes;")
    if success:
        print("✅ Nodes cleared")
    else:
        print(f"❌ Error clearing nodes: {stderr}")
    
    print()
    
    # Load nodes
    print("Loading nodes from CSV...")
    nodes_data = load_nodes_from_csv()
    print(f"Found {len(nodes_data)} nodes to load")
    
    # Insert nodes in batches
    batch_size = 10
    for i in range(0, len(nodes_data), batch_size):
        batch = nodes_data[i:i+batch_size]
        
        values = []
        for node_id, node_type, name, metadata in batch:
            # Escape single quotes in strings
            name_escaped = name.replace("'", "''")
            metadata_json = json.dumps(metadata).replace("'", "''")
            
            values.append(f"('{node_id}', '{node_type}', '{name_escaped}', '{metadata_json}'::jsonb)")
        
        sql = f"""
        INSERT INTO nodes (id, type, name, metadata)
        VALUES {', '.join(values)}
        ON CONFLICT (id) DO UPDATE SET
            type = EXCLUDED.type,
            name = EXCLUDED.name,
            metadata = EXCLUDED.metadata,
            updated_at = NOW();
        """
        
        success, stdout, stderr = run_neon_sql(sql)
        if success:
            print(f"✅ Loaded batch {i//batch_size + 1} ({len(batch)} nodes)")
        else:
            print(f"❌ Error loading batch {i//batch_size + 1}: {stderr[:200]}")
    
    print()
    
    # Load edges
    print("Loading edges from CSV...")
    edges_data = load_edges_from_csv()
    print(f"Found {len(edges_data)} edges to load")
    
    # Insert edges in batches
    for i in range(0, len(edges_data), batch_size):
        batch = edges_data[i:i+batch_size]
        
        values = []
        for source, target, metadata in batch:
            metadata_json = json.dumps(metadata).replace("'", "''")
            values.append(f"('{source}', '{target}', '{metadata_json}'::jsonb)")
        
        sql = f"""
        INSERT INTO edges (source_id, target_id, metadata)
        VALUES {', '.join(values)};
        """
        
        success, stdout, stderr = run_neon_sql(sql)
        if success:
            print(f"✅ Loaded batch {i//batch_size + 1} ({len(batch)} edges)")
        else:
            print(f"❌ Error loading batch {i//batch_size + 1}: {stderr[:200]}")
    
    print()
    print("=" * 80)
    print("DATA LOADING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
