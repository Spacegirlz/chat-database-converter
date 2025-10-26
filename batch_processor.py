#!/usr/bin/env python3
"""
Batch Processor for Multiple Conversation Export Files
Handles conv_part_aa.txt, conv_part_ab.txt, etc.
"""

import os
import glob
import json
import pandas as pd
from datetime import datetime
import sys

# Import from our main converter
sys.path.append(os.path.dirname(__file__))
from intelligent_converter import IntelligentConverter

def process_multiple_files(file_pattern="conv_part_*.txt"):
    """Process all matching conversation export files"""
    
    print("🔍 Batch Conversation Processor")
    print("=" * 60)
    
    # Find all matching files
    files = sorted(glob.glob(file_pattern))
    
    if not files:
        print(f"❌ No files found matching pattern: {file_pattern}")
        return
    
    print(f"📁 Found {len(files)} files to process:")
    for f in files:
        size_mb = os.path.getsize(f) / (1024 * 1024)
        print(f"  - {f} ({size_mb:.1f} MB)")
    
    # Initialize converter
    converter = IntelligentConverter()
    all_conversations = []
    
    # Process each file
    for i, file_path in enumerate(files, 1):
        print(f"\n📖 Processing file {i}/{len(files)}: {file_path}")
        print("-" * 40)
        
        try:
            # Parse conversations from this file
            conversations = converter.parse_chatgpt_export(file_path)
            print(f"  ✅ Extracted {len(conversations)} conversations")
            
            # Add file source info
            for conv in conversations:
                conv['source_file'] = os.path.basename(file_path)
            
            all_conversations.extend(conversations)
            
        except Exception as e:
            print(f"  ❌ Error processing {file_path}: {str(e)[:100]}")
            continue
    
    print(f"\n📊 Total conversations collected: {len(all_conversations)}")
    
    if not all_conversations:
        print("❌ No conversations extracted from any file")
        return
    
    # Remove duplicates based on title and date
    print("\n🔄 Removing duplicates...")
    seen = set()
    unique_conversations = []
    for conv in all_conversations:
        key = (conv['name'], conv.get('date', ''))
        if key not in seen:
            seen.add(key)
            unique_conversations.append(conv)
    
    print(f"  📝 Unique conversations: {len(unique_conversations)}")
    print(f"  🗑️ Duplicates removed: {len(all_conversations) - len(unique_conversations)}")
    
    # Sort by date
    print("\n📅 Sorting by date...")
    unique_conversations.sort(key=lambda x: x.get('date', '9999-99-99'))
    
    # Convert to CSV
    print("\n💾 Converting to CSV format...")
    output_files = converter.convert_to_csv(unique_conversations, "complete_archive")
    
    # Create comprehensive report
    print("\n📊 Creating comprehensive report...")
    create_batch_report(unique_conversations, files)
    
    print("\n✅ Batch processing complete!")
    print(f"📁 Created {len(output_files)} CSV files")
    print(f"📊 Report saved to complete_archive_report.json")
    
    return unique_conversations

def create_batch_report(conversations, source_files):
    """Create detailed report for batch processing"""
    
    report = {
        'processing_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'source_files': source_files,
        'total_conversations': len(conversations),
        'statistics': {
            'by_source_file': {},
            'by_date': {},
            'by_category': {},
            'by_relevance': {
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'top_tags': {},
            'top_projects': {}
        }
    }
    
    # Count by source file
    for conv in conversations:
        source = conv.get('source_file', 'unknown')
        report['statistics']['by_source_file'][source] = \
            report['statistics']['by_source_file'].get(source, 0) + 1
    
    # Count by month
    for conv in conversations:
        if conv.get('date'):
            month = conv['date'][:7]  # YYYY-MM
            report['statistics']['by_date'][month] = \
                report['statistics']['by_date'].get(month, 0) + 1
    
    # Category distribution
    for conv in conversations:
        for cat in conv.get('category', []):
            report['statistics']['by_category'][cat] = \
                report['statistics']['by_category'].get(cat, 0) + 1
    
    # Relevance distribution
    for conv in conversations:
        score = conv.get('relevance_score', 0.5)
        if score >= 0.8:
            report['statistics']['by_relevance']['high'] += 1
        elif score >= 0.5:
            report['statistics']['by_relevance']['medium'] += 1
        else:
            report['statistics']['by_relevance']['low'] += 1
    
    # Top tags
    all_tags = []
    for conv in conversations:
        all_tags.extend(conv.get('tags', []))
    from collections import Counter
    report['statistics']['top_tags'] = dict(Counter(all_tags).most_common(20))
    
    # Top projects
    project_cats = [cat for conv in conversations 
                   for cat in conv.get('category', []) 
                   if 'Project' in cat]
    report['statistics']['top_projects'] = dict(Counter(project_cats).most_common(10))
    
    # Save report
    with open('complete_archive_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n📈 Processing Summary:")
    print(f"  Total Files: {len(source_files)}")
    print(f"  Total Conversations: {len(conversations)}")
    
    if report['statistics']['by_date']:
        dates = sorted(report['statistics']['by_date'].keys())
        print(f"  Date Range: {dates[0]} to {dates[-1]}")
    
    print("\n  Top Projects:")
    for proj, count in list(report['statistics']['top_projects'].items())[:5]:
        print(f"    - {proj}: {count}")
    
    print("\n  Top Tags:")
    for tag, count in list(report['statistics']['top_tags'].items())[:5]:
        print(f"    - {tag}: {count}")

def merge_csv_files(pattern="complete_archive_chunk_*.csv", output="final_merged.csv"):
    """Merge all CSV chunks into one file (if needed for Gemini)"""
    
    print("\n🔀 Merging CSV files...")
    csv_files = sorted(glob.glob(pattern))
    
    if not csv_files:
        print("No CSV files to merge")
        return
    
    dfs = []
    for f in csv_files:
        df = pd.read_csv(f)
        dfs.append(df)
    
    merged = pd.concat(dfs, ignore_index=True)
    merged.to_csv(output, index=False)
    
    print(f"  ✅ Merged {len(csv_files)} files into {output}")
    print(f"  📊 Total records: {len(merged)}")
    
    return merged

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch process conversation exports')
    parser.add_argument('pattern', nargs='?', default='conv_part_*.txt',
                       help='File pattern to match (default: conv_part_*.txt)')
    parser.add_argument('--merge', action='store_true',
                       help='Merge all CSV outputs into one file')
    
    args = parser.parse_args()
    
    # Process all files
    conversations = process_multiple_files(args.pattern)
    
    # Optionally merge CSVs
    if args.merge and conversations:
        merge_csv_files()
