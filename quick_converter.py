#!/usr/bin/env python3
"""
Quick Converter for Testing
Handles the specific parsing issues with conv_part_aa.txt
"""

import json
import csv
import re
from datetime import datetime
import pandas as pd

def quick_parse_conversations(file_path):
    """Quick parse for testing with your conv_part_aa.txt format"""
    
    print(f"📖 Reading {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    conversations = []
    
    # Split by "title": pattern
    parts = re.split(r'"title":\s*"', content)[1:]  # Skip first empty part
    
    print(f"🔍 Found {len(parts)} potential conversations")
    
    for i, part in enumerate(parts):
        try:
            # Extract title (everything up to next quote)
            title_end = part.find('"')
            if title_end == -1:
                continue
            title = part[:title_end]
            
            # Skip empty or default titles
            if not title or title == "New conversation":
                continue
            
            # Clean the title
            title = title.encode().decode('unicode_escape')
            title = title.replace('\\/', '/').replace('\\"', '"')
            
            # Extract create_time
            date_str = ""
            date_source = "missing"
            
            create_match = re.search(r'"create_time":\s*([\d.]+)', part)
            if create_match:
                timestamp = float(create_match.group(1))
                date_obj = datetime.fromtimestamp(timestamp)
                date_str = date_obj.strftime('%Y-%m-%d')
                date_source = "exact"
            
            # Extract actual conversation content (not metadata!)
            # Look for message content patterns
            messages = []
            
            # Pattern 1: "parts": ["content here"]
            parts_matches = re.findall(r'"parts":\s*\[\s*"([^"]+)"', part)
            for match in parts_matches:
                clean_msg = match.encode().decode('unicode_escape')
                if len(clean_msg) > 30 and not clean_msg.startswith('You are'):
                    messages.append(clean_msg[:200])  # Limit each message
            
            # Pattern 2: "content": "message here"
            if not messages:
                content_matches = re.findall(r'"content":\s*"([^"]+)"', part)
                for match in content_matches:
                    clean_msg = match.encode().decode('unicode_escape')
                    if len(clean_msg) > 30:
                        messages.append(clean_msg[:200])
            
            # Create description from ACTUAL CONTENT, not metadata
            description = create_smart_description(title, messages)
            
            # Determine category
            categories = determine_category(title, description)
            
            # Generate tags
            tags = generate_tags(title, description)
            
            # Calculate relevance
            relevance = calculate_relevance(title, categories, len(messages))
            
            conversations.append({
                'name': title[:100],  # Limit title length
                'description': description,
                'category': categories,
                'tags': tags,
                'date': date_str,
                'date_source': date_source,
                'relevance_score': relevance,
                'message_volume': len(messages),
                'creator': 'Piet Weinman',
                'type': 'chatgpt',
                'url': f"https://chat.openai.com/c/{i:06d}"
            })
            
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1} conversations...")
                
        except Exception as e:
            print(f"  ⚠️ Error processing conversation {i}: {str(e)[:50]}")
            continue
    
    print(f"✅ Successfully parsed {len(conversations)} conversations")
    return conversations

def create_smart_description(title, messages):
    """Create description from actual content, not metadata"""
    
    # Start with title context
    desc_parts = []
    title_lower = title.lower()
    
    # Check for specific project/topic indicators
    if 'valentina' in title_lower or 'sage' in title_lower:
        desc_parts.append("GTR AI persona development")
    elif 'emma' in title_lower or 'tnt' in title_lower:
        desc_parts.append("TNT Media brand strategy")
    elif 'resume' in title_lower or 'portfolio' in title_lower:
        desc_parts.append("Job application materials")
    elif 'email' in title_lower:
        desc_parts.append("Email copywriting")
    elif 'prompt' in title_lower:
        desc_parts.append("Prompt engineering")
    
    # Add content from actual messages if available
    if messages:
        # Use first meaningful message
        for msg in messages[:3]:
            if len(msg) > 50:
                # Extract key part of message
                clean_msg = msg.strip()
                if len(clean_msg) > 150:
                    clean_msg = clean_msg[:150] + "..."
                desc_parts.append(clean_msg)
                break
    
    # Combine parts
    if desc_parts:
        description = ". ".join(desc_parts)
    else:
        description = f"Discussion about {title}"
    
    # Ensure it's not metadata
    if '"mapping"' in description or '"create_time"' in description:
        description = f"Conversation about {title}"
    
    return description[:300]  # Limit to 300 chars

def determine_category(title, description):
    """Determine categories based on content"""
    
    categories = []
    content = f"{title} {description}".lower()
    
    # Category mapping
    if 'valentina' in content or 'sage' in content or 'gtr' in content:
        categories.append("Project – Get The Receipts (GTR)")
    if 'emma' in content or 'tnt' in content:
        categories.append("Project – TNT Media")
    if 'prompt' in content:
        categories.append("Prompt Engineering")
    if 'email' in content and ('sequence' in content or 'campaign' in content):
        categories.append("Copywriting - Emails")
    if 'job' in content or 'resume' in content or 'portfolio' in content:
        categories.append("Job - Copywriting")
    if 'ai' in content and ('bot' in content or 'assistant' in content):
        categories.append("AI Bot Configurations")
    if 'strategy' in content or 'framework' in content:
        categories.append("Business Strategy")
    if 'research' in content:
        categories.append("Customer Research")
    
    if not categories:
        categories.append("General Chat")
    
    return categories[:3]  # Max 3 categories

def generate_tags(title, description):
    """Generate specific tags"""
    
    tags = set()
    content = f"{title} {description}".lower()
    
    # Project tags
    if 'valentina' in content:
        tags.add("Valentina")
    if 'sage' in content:
        tags.add("Sage")
    if 'emma' in content:
        tags.add("Emma Brand")
    if 'tnt' in content:
        tags.add("TNT")
    
    # Tool tags
    if 'claude' in content:
        tags.add("Claude")
    if 'gpt' in content or 'chatgpt' in content:
        tags.add("ChatGPT")
    if 'n8n' in content:
        tags.add("n8n")
    
    # Work type tags
    if 'prompt' in content:
        tags.add("Prompt")
    if 'email' in content:
        tags.add("Email")
    if 'strategy' in content:
        tags.add("Strategy")
    if 'research' in content:
        tags.add("Research")
    if 'framework' in content:
        tags.add("Framework")
    if 'automation' in content:
        tags.add("Automation")
    
    if not tags:
        tags.add("General")
    
    return list(tags)[:5]  # Max 5 tags

def calculate_relevance(title, categories, message_count):
    """Calculate relevance score"""
    
    score = 0.5  # Base score
    
    # Boost for project work
    if any('Project' in cat for cat in categories):
        score += 0.2
    
    # Boost for specific work types
    if any(cat in categories for cat in ["Prompt Engineering", "Business Strategy", 
                                          "Copywriting - Emails", "AI Bot Configurations"]):
        score += 0.15
    
    # Boost for longer conversations
    if message_count > 10:
        score += 0.1
    elif message_count > 5:
        score += 0.05
    
    # Penalty for general chat
    if categories == ["General Chat"]:
        score -= 0.2
    
    return round(min(max(score, 0.1), 1.0), 2)

def save_to_csv(conversations, output_prefix="gemini_ready"):
    """Save to CSV files optimized for Gemini"""
    
    # Convert to CSV format
    csv_data = []
    for conv in conversations:
        csv_data.append({
            'name': conv['name'],
            'description': conv['description'],
            'category': '|'.join(conv['category']),  # Pipe separator for multiple
            'tags': ','.join(conv['tags']),  # Comma separator for tags
            'date': conv['date'],
            'date_source': conv['date_source'],
            'relevance_score': conv['relevance_score'],
            'message_volume': conv['message_volume'],
            'creator': conv['creator'],
            'type': conv['type'],
            'url': conv['url']
        })
    
    # Create DataFrame
    df = pd.DataFrame(csv_data)
    
    # Split into chunks of 500
    chunk_size = 500
    num_chunks = (len(df) + chunk_size - 1) // chunk_size
    
    output_files = []
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, len(df))
        chunk_df = df.iloc[start_idx:end_idx]
        
        filename = f"{output_prefix}_chunk_{i+1:03d}.csv"
        chunk_df.to_csv(filename, index=False, quoting=csv.QUOTE_MINIMAL)
        output_files.append(filename)
        
        file_size = len(chunk_df)
        print(f"  💾 Saved {filename}: {file_size} records")
    
    return output_files

def create_quick_report(conversations):
    """Create a quick summary report"""
    
    print("\n📊 Quick Analysis Report:")
    print(f"  Total Conversations: {len(conversations)}")
    
    # Date range
    dates = [c['date'] for c in conversations if c['date']]
    if dates:
        print(f"  Date Range: {min(dates)} to {max(dates)}")
    
    # Category distribution
    cat_counts = {}
    for conv in conversations:
        for cat in conv['category']:
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
    
    print("\n  Top Categories:")
    for cat, count in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"    - {cat}: {count}")
    
    # Tag distribution
    tag_counts = {}
    for conv in conversations:
        for tag in conv['tags']:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    print("\n  Top Tags:")
    for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"    - {tag}: {count}")
    
    # Relevance distribution
    high_rel = sum(1 for c in conversations if c['relevance_score'] >= 0.8)
    med_rel = sum(1 for c in conversations if 0.5 <= c['relevance_score'] < 0.8)
    low_rel = sum(1 for c in conversations if c['relevance_score'] < 0.5)
    
    print(f"\n  Relevance Distribution:")
    print(f"    - High (0.8+): {high_rel}")
    print(f"    - Medium (0.5-0.7): {med_rel}")
    print(f"    - Low (<0.5): {low_rel}")

# Main execution
if __name__ == "__main__":
    import sys
    
    print("🚀 Quick Conversation Converter")
    print("=" * 50)
    
    # Get input file
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "conv_part_aa.txt"
        print(f"No input file specified, looking for {input_file}")
    
    # Parse conversations
    conversations = quick_parse_conversations(input_file)
    
    if not conversations:
        print("❌ No conversations found. Check the file format.")
        sys.exit(1)
    
    # Save to CSV
    print(f"\n💾 Saving to CSV files...")
    output_files = save_to_csv(conversations)
    
    # Create report
    create_quick_report(conversations)
    
    print(f"\n✅ Complete! Created {len(output_files)} CSV files")
    print("📤 Ready to import into Gemini!")
    
    # Show first few entries as preview
    print("\n📋 Preview of first 3 entries:")
    for i, conv in enumerate(conversations[:3]):
        print(f"\n  Entry {i+1}:")
        print(f"    Name: {conv['name'][:50]}...")
        print(f"    Description: {conv['description'][:100]}...")
        print(f"    Categories: {', '.join(conv['category'])}")
        print(f"    Tags: {', '.join(conv['tags'])}")
        print(f"    Relevance: {conv['relevance_score']}")
