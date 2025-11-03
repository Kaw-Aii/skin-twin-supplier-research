import csv
import os
from datetime import datetime

# Research findings mapping
research_updates = {
    # Natchem/Greentech ingredients
    "NAT0001": {
        "availability": "Available - Greentech Distributor",
        "pricing": "Contact for quote",
        "website": "https://cpt.natchem.co.za/",
        "notes": "Exclusive distributor for Greentech in South Africa. Supplies top cosmetic manufacturers. Ecocert NaTrue ISO 22716 GMP certified. 16 ingredients (18% market share). Contact: 010 010 6174, WhatsApp: +27 82 331 4508"
    },
    
    # Meganede/Silab ingredients
    "MEG0001": {
        "availability": "Available - Silab Distributor",
        "pricing": "Contact for quote",
        "website": "https://www.meganede.com/",
        "notes": "Distributor of Silab (100+ natural active ingredients). Also represents Bioglitter, Gobiotics, Antaria. 15 ingredients (16% market share). EcoVadis Platinum status. Email: info@meganede.com"
    },
    
    # Croda ingredients
    "CRO0001": {
        "availability": "Available - Direct from Croda",
        "pricing": "Contact for quote",
        "website": "https://www.croda.com/en-gb/about-us/where-we-operate/emea/south-africa",
        "notes": "Established 1972. Centre of Excellence opened 2015 in Boksburg. 757 products globally, 200+ active ingredients. All 7 ingredients confirmed available. Phone: +27 11 397 2380. Premium biotech actives including Sederma portfolio."
    },
    
    # Botanichem
    "BOT0003": {
        "availability": "Online Shop Available",
        "pricing": "R352.35 - R10318.45 (online pricing)",
        "website": "https://botanichem.co.za/",
        "notes": "Full-service agency with transparent online pricing via The Personal Care Coach platform. Distributes BASF products. Offers stability testing, formulation, quality assurance. Only supplier with direct online pricing. Phone: 011 425 2206"
    },
    
    # AECI
    "AKU001": {
        "availability": "Personal Care Ingredients",
        "pricing": "Contact for quote",
        "website": "https://sc.aecichemicals.co.za/",
        "notes": "Diversified chemical company with personal care applications lab. Winner of 2022 Responsible Care Initiative. Focus on green chemistry and sustainability."
    },
    
    # A&E Connock
    "AEC001": {
        "availability": "Speciality Ingredients Supplier",
        "pricing": "Contact for quote",
        "website": "https://connock.co.uk/",
        "notes": "UK-based supplier of speciality ingredients to the personal care industry worldwide."
    },
    
    # o6 Agencies
    "06A0001": {
        "availability": "Fragrance and Flavour Supplier",
        "pricing": "Contact for quote",
        "website": "https://o6southafrica.com/",
        "notes": "Supplier of fragrances and flavors for the Southern and Eastern African markets."
    }
}

# Specific ingredient updates
ingredient_updates = {
    # Silab products via Meganede
    "R1905018": {"name": "Glyco Repair", "availability": "Available", "pricing": "Contact for quote", "notes": "GLYCO-REPAIR® from Silab. Regenerates natural skin repair processes. Dual action on epidermis and dermis."},
    "R1905027": {"name": "Deglysome", "availability": "Available", "pricing": "Contact for quote", "notes": "DEGLYSOME® from Silab. Protects against cellular and tissular glycation damage."},
    "R1905035": {"name": "Sebonormine OP", "availability": "Available", "pricing": "Contact for quote", "notes": "SEBONORMINE® from Silab. Triple action for oily skin, reduces sebum secretions."},
    "R1905041": {"name": "Unflamagyl", "availability": "Available", "pricing": "Contact for quote", "notes": "UNFLAMAGYL® from Silab. Anti-inflammaging ingredient, increases elasticity and tone."},
    "R1905046": {"name": "Dermapur HP OP", "availability": "Available", "pricing": "Contact for quote", "notes": "DERMAPUR® from Silab. Purifying and anti-acne action."},
    "R1905048": {"name": "Vitagenyl", "availability": "Available", "pricing": "Contact for quote", "notes": "VITAGENYL® from Silab. Adaptative anti-aging strategy, stimulates vitagene expression."},
    "R1905049": {"name": "Detoxyl OP", "availability": "Available", "pricing": "Contact for quote", "notes": "DETOXYL® from Silab. Powerful detoxifying agent, protects against urban pollutants."},
    "R1905050": {"name": "Celldetox", "availability": "Available", "pricing": "Contact for quote", "notes": "CELLDETOX® from Silab. Improves skin radiance, limits aging signs."},
    "R1905051": {"name": "Mitokinyl", "availability": "Available", "pricing": "Contact for quote", "notes": "MITOKINYL® from Silab. Mitochondrial energy booster."},
    "R1905052": {"name": "Fermiskin GR", "availability": "Available", "pricing": "Contact for quote", "notes": "FERMISKIN® from Silab. Firming action."},
    "R1905053": {"name": "Retilactyl D", "availability": "Available", "pricing": "Contact for quote", "notes": "RETILACTYL® from Silab. Retinol-like action."},
    "R1905054": {"name": "Raffermine 2", "availability": "Available", "pricing": "Contact for quote", "notes": "RAFFERMINE® from Silab. Firming and toning."},
    "R1905056": {"name": "Eternaline", "availability": "Available", "pricing": "Contact for quote", "notes": "ETERNALINE® from Silab. Longevity and anti-aging."},
    "R1905057": {"name": "Oxygeskin", "availability": "Available", "pricing": "Contact for quote", "notes": "OXYGESKIN® from Silab. Oxygenation and revitalization."},
    "R1905058": {"name": "Aquaphyline EL", "availability": "Available", "pricing": "Contact for quote", "notes": "AQUAPHYLINE® from Silab. Hydration and moisture retention."},
    
    # Croda products
    "R1901005": {"name": "Arlamol LST-LQ-(MH)", "availability": "Available", "pricing": "Contact for quote", "notes": "Arlamol™ LST from Croda. Light emollient with high skin spreading."},
    "R1905002": {"name": "Chronodyn", "availability": "Available", "pricing": "Contact for quote", "notes": "Chronodyn™ from Croda. Chronobiological cell energizer, tones and firms skin."},
    "R1905003": {"name": "Biopeptide CL", "availability": "Available", "pricing": "Contact for quote", "notes": "Biopeptide CL™ from Croda/Sederma. Messenger peptide for collagen renewal."},
    "R1905025": {"name": "Skin Tightener-ST(TM) PH", "availability": "Available", "pricing": "Contact for quote", "notes": "From Croda. Skin tightening and firming active."},
    "R1905026": {"name": "Beautifeye", "availability": "Available", "pricing": "Contact for quote", "notes": "From Croda. Eye contour care (may be Ameyezing 4.0™)."},
    "R1905033": {"name": "Evermat", "availability": "Available", "pricing": "Contact for quote", "notes": "Evermat™ from Croda. Mattifying and sebum control."},
    "R1905034": {"name": "Intenslim", "availability": "Available", "pricing": "Contact for quote", "notes": "Intenslim™ from Croda/Sederma. Natural fat burner, slimming active."},
    
    # Botanichem products
    "R1905039": {"name": "Epigenist LS10003", "availability": "Available", "pricing": "Contact for quote", "notes": "From Botanichem, likely via BASF or JAKA partners."},
    "R1905042": {"name": "Eperuline PW LS 9627", "availability": "Available", "pricing": "Contact for quote", "notes": "From Botanichem, likely via BASF or JAKA partners."},
}

def update_csv():
    input_file = '/home/ubuntu/skin-twin-supplier-research/data/RSNodes_updated.csv'
    output_file = '/home/ubuntu/skin-twin-supplier-research/data/RSNodes_updated_new.csv'
    
    updated_rows = []
    update_date = datetime.now().strftime("%Y-%m-%d")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        for row in reader:
            if len(row) < 9:
                updated_rows.append(row)
                continue
            
            node_id = row[0]
            
            # Update supplier information
            if node_id in research_updates:
                update = research_updates[node_id]
                row[4] = update.get("availability", row[4])
                row[5] = update.get("pricing", row[5])
                row[6] = update.get("website", row[6])
                row[7] = update.get("notes", row[7])
                row[8] = update_date
            
            # Update ingredient information
            if node_id in ingredient_updates:
                update = ingredient_updates[node_id]
                if update.get("name"):
                    row[1] = update["name"]
                row[4] = update.get("availability", row[4])
                row[5] = update.get("pricing", row[5])
                row[7] = update.get("notes", row[7])
                row[8] = update_date
            
            updated_rows.append(row)
    
    # Write updated data
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(updated_rows)
    
    print(f"Updated {len(updated_rows)} rows")
    print(f"Output written to: {output_file}")

if __name__ == "__main__":
    update_csv()
