import requests
import json
import sys
import random

def test_flow_api(task, domain, problem_context, input_context, output_context, 
                  process_areas, constraints, debug=False):
    """Test the flow API endpoint."""
    base_url = "http://localhost:8000"
    
    # Prepare request data
    data = {
        "task": task,
        "domain": domain,
        "problem_context": problem_context,
        "input_context": input_context,
        "output_context": output_context,
        "process_areas": process_areas,
        "constraints": constraints,
        "model_name": "gpt-4o",
        "temperature": 0.7
    }
    
    if debug:
        endpoint = f"{base_url}/flow/debug"
    else:
        endpoint = f"{base_url}/flow/create"
    
    response = requests.post(endpoint, json=data)
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        print("Success!")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    else:
        print("Error:")
        print(response.text)
        return None

# Define problem scenarios for retail catalog
catalog_item_setup_scenarios = [
    {
        "task": "Build an automated workflow for new product onboarding in retail catalog",
        "problem_context": "Retailer struggles with lengthy manual processes to set up new products in system, causing delays in time-to-market and inconsistent product information across channels",
        "input_context": "Raw supplier product information including images, specifications, pricing, and inventory details in various formats (Excel, CSV, PDF)",
        "output_context": "Standardized product records ready for multi-channel distribution with complete attributes, categorization, and quality-checked media assets",
        "constraints": ["Must handle 500+ new SKUs daily", "Must preserve supplier relationship to product", "Must flag incomplete product information for review"]
    },
    {
        "task": "Create a seasonal merchandise planning system for retail catalog management",
        "problem_context": "Retail merchandising team needs to efficiently plan, schedule, and coordinate seasonal product introductions across multiple departments and sales channels",
        "input_context": "Seasonal calendars, historical performance data, vendor lead times, and departmental capacity constraints",
        "output_context": "Optimized seasonal merchandise plan with introduction timelines, promotional schedules, and resource allocation recommendations",
        "constraints": ["Must account for 30+ merchandise departments", "Must integrate with existing inventory systems", "Should provide at least 6-month planning horizon"]
    },
    {
        "task": "Design a product attribute standardization system for catalog management",
        "problem_context": "Inconsistent product attributes across categories making search and comparison difficult for customers and creating challenges for cross-selling and inventory management",
        "input_context": "Existing product database with varying attribute schemas across categories, industry standard attribute templates, and competitor attribute analysis",
        "output_context": "Standardized attribute schema by product category with data migration plan, governance rules, and validation protocols",
        "constraints": ["Must support 50+ product categories", "Must maintain backward compatibility", "Should recommend attribute importance weighting for search relevance"]
    },
    {
        "task": "Create a workflow for product bundle and kit assembly in retail catalog",
        "problem_context": "Retail marketing team needs to efficiently create and manage product bundles and kits consisting of multiple individual SKUs for promotions and special offerings",
        "input_context": "Individual product data, pricing rules, inventory availability, promotional calendar, and historical bundle performance metrics",
        "output_context": "Complete bundle/kit product records with appropriate pricing, images, descriptions, component relationships, and inventory logic",
        "constraints": ["Must maintain inventory relationships", "Must support dynamic pricing rules", "Should generate appropriate bundle images"]
    },
    {
        "task": "Develop a product variant management system for retail catalog",
        "problem_context": "Retailer struggles with managing product variants (size, color, style) efficiently, leading to customer confusion and inventory management issues",
        "input_context": "Base product information, variant specifications, inventory levels by variant, and variant-specific assets (images, measurements)",
        "output_context": "Structured variant catalog with proper parent-child relationships, variant-specific attributes, and consistent presentation across channels",
        "constraints": ["Must support up to 200 variants per product", "Must preserve SEO value across variants", "Should optimize variant selection UI based on availability"]
    },
    {
        "task": "Create an automated product categorization system for retail catalog",
        "problem_context": "Manual product categorization causing inconsistencies, misplaced products, and poor customer navigation experience in online and physical catalog",
        "input_context": "Product descriptions, attributes, images, existing category hierarchy, and vendor-supplied categorization",
        "output_context": "Accurately categorized products with primary and secondary category assignments, navigation path recommendations, and category-specific attribute completion",
        "constraints": ["Must work with 100,000+ existing products", "Must handle multiple category assignments", "Should recommend category refinements based on product clusters"]
    }
]

catalog_compliance_scenarios = [
    {
        "task": "Build a regulatory compliance verification system for retail product listings",
        "problem_context": "Retailer must ensure all product listings comply with various regulations including CPSC standards, California Prop 65, textile labeling requirements, and country-specific regulations",
        "input_context": "Product specifications, materials listing, country of origin, certifications, target markets, and applicable regulatory requirements database",
        "output_context": "Compliance verification report with pass/fail status, required warning labels, certification verification, and recommended corrective actions",
        "constraints": ["Must verify against latest regulations", "Must provide clear compliance explanations", "Should generate compliant warning label text when required"]
    },
    {
        "task": "Create a sustainable product certification validation workflow",
        "problem_context": "Retailer needs to verify and monitor sustainability claims and certifications (organic, fair trade, recycled content) to prevent greenwashing and ensure marketing claims are substantiated",
        "input_context": "Supplier-provided certification documents, sustainability claims, certification authority databases, and product material composition data",
        "output_context": "Validated sustainability credentials with certification expiration monitoring, appropriate marketing claim language, and required documentation for audit purposes",
        "constraints": ["Must verify certificate authenticity", "Must track certification renewal dates", "Should flag inconsistencies between claims and documentation"]
    },
    {
        "task": "Develop a product safety compliance monitoring system for children's products",
        "problem_context": "Retailer must ensure all children's products meet strict safety standards, have appropriate age recommendations, and include required safety warnings to avoid recalls and liability",
        "input_context": "Product specifications, test reports, age grading documentation, component materials, and current safety standards by product category and region",
        "output_context": "Safety compliance assessment with age-grading validation, required testing verification, warning label requirements, and potential safety concerns flagging",
        "constraints": ["Must apply CPSC, EN71, and ISO standards", "Must validate all safety test reports", "Should identify products requiring third-party testing"]
    },
    {
        "task": "Create a pricing and promotion compliance verification system",
        "problem_context": "Retailer needs to ensure pricing, discounts, and promotional claims comply with consumer protection regulations and company policies to avoid deceptive pricing allegations",
        "input_context": "Current and historical pricing data, promotional calendars, competitor pricing, minimum advertised price agreements, and applicable pricing regulations",
        "output_context": "Pricing compliance report with verification of reference price claims, promotion duration compliance, and recommended compliant promotional language",
        "constraints": ["Must track pricing history for reference price validation", "Must enforce vendor MAP policies", "Should identify non-compliant pricing patterns"]
    },
    {
        "task": "Develop an accessibility compliance verification system for product catalog",
        "problem_context": "Retailer must ensure product catalog content meets accessibility standards for visually impaired and other disabled customers to avoid ADA compliance issues",
        "input_context": "Product images, descriptions, specification tables, navigation structure, and current accessibility standards/guidelines",
        "output_context": "Accessibility audit report with compliance status, recommended alt-text improvements, content structure issues, and prioritized remediation steps",
        "constraints": ["Must verify WCAG 2.1 compliance", "Must prioritize high-traffic product pages", "Should generate recommended alt-text for non-compliant images"]
    },
    {
        "task": "Create an international trade compliance verification system for retail catalog",
        "problem_context": "Retailer selling internationally needs to ensure products comply with import/export regulations, duties, restricted substance rules, and country-specific requirements",
        "input_context": "Product specifications, materials, country of origin, harmonized tariff codes, destination markets, and international trade restriction database",
        "output_context": "International compliance assessment with market-specific restrictions, documentation requirements, tariff code verification, and shipping restriction alerts",
        "constraints": ["Must cover regulations for 30+ countries", "Must update with regulatory changes", "Should calculate landed cost estimates by market"]
    }
]

if __name__ == "__main__":
    # Choose catalog domain and process area
    domain = "Retail Catalog"
    
    if len(sys.argv) > 1:
        process_area = sys.argv[1].lower()
    else:
        process_area = random.choice(["item-setup", "compliance"])
    
    # Select scenario based on process area
    if process_area == "item-setup":
        scenarios = catalog_item_setup_scenarios
        process_areas = ["Item-Setup"]
    else:
        scenarios = catalog_compliance_scenarios
        process_areas = ["Compliance"]
    
    # Use scenario index if provided, otherwise random
    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        scenario_index = int(sys.argv[2]) % len(scenarios)
    else:
        scenario_index = random.randint(0, len(scenarios) - 1)
    
    scenario = scenarios[scenario_index]
    
    # Check if debug mode is enabled
    debug_mode = False
    if len(sys.argv) > 3 and sys.argv[3].lower() == "debug":
        debug_mode = True
    
    print(f"Testing API with scenario #{scenario_index + 1} from {process_area}:")
    print(f"Task: {scenario['task']}")
    print(f"Process Areas: {process_areas}")
    print(f"Debug mode: {debug_mode}")
    
    # Call the API test function
    test_flow_api(
        task=scenario['task'],
        domain=domain,
        problem_context=scenario['problem_context'],
        input_context=scenario['input_context'],
        output_context=scenario['output_context'],
        process_areas=process_areas,
        constraints=scenario['constraints'],
        debug=debug_mode
    )