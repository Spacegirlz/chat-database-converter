#!/usr/bin/env python3
"""
Test Demonstration: Proper Parsing vs Wrong Parsing
Shows exactly how we fix the description metadata issue
"""

import json
import re
from datetime import datetime

# Sample problematic data (like what GPT was mishandling)
SAMPLE_RAW_EXPORT = '''
"title": "Archive and asset management", 
"create_time": 1761376400.31522, 
"update_time": 1761376527.686519, 
"mapping": {
    "client-created-root": {
        "id": "client-created-root", 
        "message": null, 
        "parent": null, 
        "children": ["53f3d092-1697-4a8e-a4cf-24b928bd6643"]
    }, 
    "53f3d092-1697-4a8e-a4cf-24b928bd6643": {
        "id": "53f3d092-1697-4a8e-a4cf-24b928bd6643",
        "message": {
            "content": {
                "parts": ["I need help organizing my Google Drive archive and creating a searchable asset management system for all my copywriting work, templates, and client deliverables."]
            }
        }
    },
    "assistant-response-1": {
        "message": {
            "content": {
                "parts": ["I'll help you create a comprehensive asset management system. Let's start by understanding your current structure. We'll build a taxonomy that includes: 1) Client projects organized by brand, 2) Templates by copy type (email, landing, sales pages), 3) Research and strategy documents, 4) Frameworks and SOPs, 5) Performance data and case studies."]
            }
        }
    }
}
'''

def wrong_way_gpt_did_it():
    """This is what GPT was doing wrong"""
    print("❌ WRONG WAY (What GPT was doing):")
    print("-" * 50)
    
    # GPT was grabbing the raw metadata
    wrong_description = '"title": "Archive and asset management", "create_time": 1761376400.31522, "update_time": 1761376527.686519, "mapping": {"client-created-root": {"id": "client-created-root", "message": null, "parent": null, "children": ["53f3d092-1697-4a8e-a4cf-24b928bd6643"]}'
    
    print(f"Description: {wrong_description[:150]}...")
    print("\n⚠️ This is RAW METADATA, not actual content!")
    print("Categories: [Generic because can't understand metadata]")
    print("Tags: [Generic tags]")
    print()

def right_way_we_do_it():
    """This is how we properly extract content"""
    print("✅ RIGHT WAY (Our intelligent parsing):")
    print("-" * 50)
    
    # Extract the actual title
    title_match = re.search(r'"title":\s*"([^"]+)"', SAMPLE_RAW_EXPORT)
    title = title_match.group(1) if title_match else "Unknown"
    
    # Extract actual message content
    messages = []
    parts_matches = re.findall(r'"parts":\s*\["([^"]+)"', SAMPLE_RAW_EXPORT)
    for match in parts_matches:
        clean_msg = match.encode().decode('unicode_escape')
        messages.append(clean_msg)
    
    print(f"Title: {title}")
    print(f"\nExtracted Messages ({len(messages)} found):")
    for i, msg in enumerate(messages, 1):
        print(f"  Message {i}: {msg[:100]}...")
    
    # Create intelligent description from ACTUAL CONTENT
    description = create_intelligent_description(title, messages)
    print(f"\nIntelligent Description: {description}")
    
    # Smart categorization based on content
    categories = smart_categorize(title, messages)
    print(f"\nCategories: {categories}")
    
    # Specific tags from actual content
    tags = extract_specific_tags(title, messages)
    print(f"Tags: {tags}")
    
    # Extract proper date
    create_time_match = re.search(r'"create_time":\s*([\d.]+)', SAMPLE_RAW_EXPORT)
    if create_time_match:
        timestamp = float(create_time_match.group(1))
        date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        print(f"Date: {date} (exact)")

def create_intelligent_description(title, messages):
    """Create meaningful description from actual content"""
    
    # Analyze what the conversation is actually about
    all_text = f"{title} {' '.join(messages)}".lower()
    
    desc_parts = []
    
    # Identify main topic
    if 'archive' in all_text and 'asset' in all_text:
        desc_parts.append("Building searchable asset management system")
    
    # Identify specific deliverables/goals
    if 'google drive' in all_text:
        desc_parts.append("Google Drive organization")
    if 'copywriting' in all_text:
        desc_parts.append("copywriting portfolio structure")
    if 'template' in all_text:
        desc_parts.append("template taxonomy")
    
    # Add specific details from messages
    if messages:
        key_points = []
        if 'email' in messages[0]:
            key_points.append("email sequences")
        if 'landing' in messages[0]:
            key_points.append("landing pages")
        if 'client' in messages[0]:
            key_points.append("client deliverables")
        if key_points:
            desc_parts.append(f"Organizing: {', '.join(key_points)}")
    
    return ". ".join(desc_parts) if desc_parts else f"Discussion about {title}"

def smart_categorize(title, messages):
    """Categorize based on actual content"""
    
    categories = []
    all_text = f"{title} {' '.join(messages)}".lower()
    
    # Check for specific patterns
    if 'google drive' in all_text and 'asset' in all_text:
        categories.append("Google Drive")
    if 'archive' in all_text or 'management' in all_text:
        categories.append("Project Management")
    if 'copywriting' in all_text:
        categories.append("Copywriting Frameworks")
    if 'template' in all_text:
        categories.append("General Frameworks")
    if 'client' in all_text:
        categories.append("Client Management")
    
    return categories if categories else ["General Chat"]

def extract_specific_tags(title, messages):
    """Extract specific, useful tags"""
    
    tags = set()
    all_text = f"{title} {' '.join(messages)}".lower()
    
    # Tool/platform tags
    if 'google drive' in all_text:
        tags.add("Google Drive")
    
    # Work type tags
    if 'asset' in all_text:
        tags.add("Asset Management")
    if 'archive' in all_text:
        tags.add("Archive")
    if 'template' in all_text:
        tags.add("Templates")
    if 'framework' in all_text or 'system' in all_text:
        tags.add("Framework")
    if 'taxonomy' in all_text:
        tags.add("Taxonomy")
    
    # Deliverable tags
    if 'email' in all_text:
        tags.add("Email")
    if 'landing page' in all_text:
        tags.add("Landing Page")
    if 'sales page' in all_text:
        tags.add("Sales Page")
    
    return list(tags) if tags else ["General"]

def show_csv_output():
    """Show the final CSV-ready format"""
    print("\n📊 FINAL CSV OUTPUT:")
    print("-" * 50)
    
    # This is what goes to Gemini
    csv_row = {
        'name': 'Archive and asset management',
        'description': 'Building searchable asset management system. Google Drive organization. copywriting portfolio structure. template taxonomy. Organizing: client deliverables',
        'category': 'Google Drive|Project Management|Copywriting Frameworks',
        'tags': 'Google Drive,Asset Management,Templates,Framework,Email',
        'date': '2025-10-25',
        'date_source': 'exact',
        'relevance_score': 0.85,
        'message_volume': 2,
        'creator': 'Piet Weinman',
        'type': 'chatgpt',
        'url': 'https://chat.openai.com/c/abc123'
    }
    
    print("CSV Row (what Gemini sees):")
    for key, value in csv_row.items():
        print(f"  {key}: {value}")
    
    print("\n✅ This is clean, parseable, and meaningful!")

def main():
    print("=" * 60)
    print("DEMONSTRATION: Fixing the Description/Metadata Problem")
    print("=" * 60)
    print()
    
    # Show the wrong way
    wrong_way_gpt_did_it()
    
    print("\n" + "=" * 60 + "\n")
    
    # Show the right way
    right_way_we_do_it()
    
    print("\n" + "=" * 60 + "\n")
    
    # Show final output
    show_csv_output()
    
    print("\n" + "=" * 60)
    print("KEY DIFFERENCES:")
    print("-" * 60)
    print("❌ GPT's Way: Dumped raw JSON metadata into description field")
    print("✅ Our Way: Extracted actual conversation content from 'parts'")
    print()
    print("❌ GPT's Categories: Generic, couldn't understand metadata")  
    print("✅ Our Categories: Specific, based on actual conversation topics")
    print()
    print("❌ GPT's Tags: Generic placeholders")
    print("✅ Our Tags: Specific tools, deliverables, and concepts mentioned")
    print("=" * 60)

if __name__ == "__main__":
    main()
