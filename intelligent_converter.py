#!/usr/bin/env python3
"""
Intelligent Conversation Export Converter
Handles ChatGPT and Claude exports -> Clean CSV for Gemini
"""

import json
import csv
import pandas as pd
import re
from datetime import datetime
import os
from typing import Dict, List, Optional, Any
import hashlib

class IntelligentConverter:
    def __init__(self):
        # Your actual category taxonomy
        self.categories = [
            "AI Bot Configurations",
            "Ad Copy Frameworks", 
            "Business Strategy",
            "Client Management",
            "Company Culture",
            "Content Strategy",
            "Copywriting Frameworks",
            "Copywriting - Emails",
            "Copywriting - Landing Page",
            "Copywriting - Sales Page",
            "Copywriting - Website",
            "Copywriting - Ads",
            "Copywriting - Funnels",
            "Copywriting Prompts",
            "Customer Research",
            "Email & Newsletters",
            "Finance",
            "GEO SEO Frameworks",
            "General Chat",
            "General Frameworks",
            "Generated Data",
            "Google Drive",
            "HR",
            "Health - Therapy",
            "Health - [Focus]",
            "Idea Research & New Projects",
            "Job - AI Consultant",
            "Job - Copywriting", 
            "Job - Strategy",
            "Job - UX Writing",
            "Landing Pages",
            "Legal",
            "Market Research",
            "Marketing",
            "Miscellaneous AI Research",
            "Newsletters",
            "Project Management",
            "Project – AI Valentina",
            "Project – Copy Accelerator (CA)",
            "Project – Emma Brand",
            "Project – GEO SEO AI",
            "Project – Get The Receipts (GTR)",
            "Project – PaleoHacks / David Sinick",
            "Project – Pauline Longdon",
            "Project – TNT Media",
            "Prompt Engineering",
            "Sales Page Systems",
            "Training & Resources",
            "VSL Frameworks",
            "Voice & Tone Systems"
        ]
        
        # Category detection patterns
        self.category_patterns = {
            "Project – Get The Receipts (GTR)": [
                "valentina", "sage", "receipts", "gtr", "ofm", 
                "quiz funnel", "personality test", "archetype"
            ],
            "Project – TNT Media": [
                "emma", "tnt", "tom clayson", "media buying",
                "acquisition", "creative strategy"
            ],
            "Project – PaleoHacks / David Sinick": [
                "paleohacks", "david sinick", "health funnel", "vsl",
                "keto", "paleo", "supplement"
            ],
            "AI Bot Configurations": [
                "system prompt", "personality", "voice", "tone",
                "character", "persona", "chatbot", "assistant config"
            ],
            "Job - Copywriting": [
                "portfolio", "writing sample", "application", "cover letter",
                "resume", "job posting", "interview prep"
            ],
            "Job - AI Consultant": [
                "ai consulting", "ai strategy", "implementation", "ai advisor"
            ],
            "Health - Therapy": [
                "trauma", "healing", "therapy", "emotional", "anxiety",
                "depression", "coping", "mental health", "processing"
            ],
            "Prompt Engineering": [
                "prompt", "few-shot", "zero-shot", "chain of thought",
                "system message", "instruction", "template"
            ],
            "Copywriting - Emails": [
                "email sequence", "subject line", "email campaign",
                "newsletter", "broadcast", "autoresponder"
            ],
            "Copywriting - Sales Page": [
                "sales page", "long form", "sales letter", "checkout",
                "order form", "guarantee", "testimonial"
            ],
            "Business Strategy": [
                "strategy", "planning", "roadmap", "framework",
                "analysis", "competitive", "positioning"
            ],
            "Customer Research": [
                "customer research", "avatar", "persona", "survey",
                "interview", "voice of customer", "market research"
            ]
        }
        
        # Smart tagging patterns
        self.tag_patterns = {
            # Tools & Platforms
            "tools": ["claude", "gpt", "chatgpt", "n8n", "cursor", "zapier", 
                     "make", "airtable", "notion", "figma", "canva"],
            
            # Techniques & Frameworks
            "techniques": ["aida", "pas", "fab", "storytelling", "urgency",
                          "scarcity", "social proof", "authority", "reciprocity"],
            
            # Deliverables
            "deliverables": ["email sequence", "landing page", "sales page",
                           "vsl script", "ad copy", "headline", "hook",
                           "lead magnet", "webinar", "funnel"],
            
            # Client/Project specific
            "clients": ["valentina", "sage", "emma", "tom", "david sinick",
                       "pauline", "stefan georgi", "luka mills"],
            
            # Work types
            "work_types": ["research", "strategy", "copywriting", "automation",
                         "analysis", "optimization", "testing", "implementation"]
        }

    def parse_chatgpt_export(self, file_path: str) -> List[Dict]:
        """Parse ChatGPT conversation export properly"""
        conversations = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Handle different export formats
        if content.startswith('['):  # JSON array
            data = json.loads(content)
        elif content.startswith('{'):  # Single JSON object
            data = [json.loads(content)]
        else:  # Raw text export (your conv_part_aa.txt format)
            data = self.parse_raw_text_export(content)
        
        for conv_data in data:
            parsed = self.extract_conversation_details(conv_data)
            if parsed:
                conversations.append(parsed)
        
        return conversations
    
    def parse_raw_text_export(self, content: str) -> List[Dict]:
        """Parse the raw text export format like conv_part_aa.txt"""
        conversations = []
        
        # Split by conversation boundaries
        conv_splits = re.split(r'"title":\s*"', content)
        
        for i, conv_text in enumerate(conv_splits[1:], 1):  # Skip first empty split
            try:
                # Extract title
                title_match = re.match(r'([^"]+)"', conv_text)
                if not title_match:
                    continue
                
                title = title_match.group(1)
                
                # Extract timestamps
                create_time = None
                update_time = None
                
                create_match = re.search(r'"create_time":\s*([\d.]+)', conv_text)
                if create_match:
                    create_time = float(create_match.group(1))
                
                update_match = re.search(r'"update_time":\s*([\d.]+)', conv_text)
                if update_match:
                    update_time = float(update_match.group(1))
                
                # Extract actual message content (not metadata)
                messages = self.extract_messages_from_raw(conv_text)
                
                conversations.append({
                    'title': title,
                    'create_time': create_time,
                    'update_time': update_time,
                    'messages': messages,
                    'raw_text': conv_text[:5000]  # Keep some raw for fallback
                })
            except Exception as e:
                print(f"Error parsing conversation {i}: {e}")
                continue
        
        return conversations
    
    def extract_messages_from_raw(self, conv_text: str) -> List[str]:
        """Extract actual message content from the conversation"""
        messages = []
        
        # Look for actual message content patterns
        # Pattern 1: "content": {"parts": ["actual message here"]}
        content_matches = re.findall(r'"parts":\s*\["([^"]+)"', conv_text)
        messages.extend(content_matches)
        
        # Pattern 2: "text": {"value": "message content"}
        text_matches = re.findall(r'"value":\s*"([^"]+)"', conv_text)
        messages.extend(text_matches)
        
        # Pattern 3: "message": {"content": "..."}
        msg_matches = re.findall(r'"content":\s*"([^"]+)"', conv_text)
        messages.extend(msg_matches)
        
        # Clean and filter messages
        cleaned_messages = []
        for msg in messages:
            # Unescape unicode
            msg = msg.encode().decode('unicode_escape')
            # Remove system messages and empty content
            if len(msg) > 20 and not msg.startswith('You are'):
                cleaned_messages.append(msg)
        
        return cleaned_messages
    
    def extract_conversation_details(self, conv_data: Dict) -> Optional[Dict]:
        """Extract meaningful details from conversation data"""
        
        # Get basic info
        title = conv_data.get('title', '')
        if not title or title == 'New conversation':
            return None
        
        # Get timestamps
        create_time = conv_data.get('create_time')
        update_time = conv_data.get('update_time', create_time)
        
        # Convert timestamp to date
        date_str = None
        date_source = 'missing'
        if create_time:
            try:
                if isinstance(create_time, (int, float)):
                    date_obj = datetime.fromtimestamp(create_time)
                    date_str = date_obj.strftime('%Y-%m-%d')
                    date_source = 'exact'
            except:
                pass
        
        # Extract messages for content analysis
        messages = conv_data.get('messages', [])
        if not messages and 'raw_text' in conv_data:
            messages = self.extract_messages_from_raw(conv_data['raw_text'])
        
        # Create intelligent description
        description = self.create_intelligent_description(title, messages)
        
        # Determine categories
        categories = self.determine_categories(title, description, messages)
        
        # Generate specific tags
        tags = self.generate_specific_tags(title, description, messages)
        
        # Calculate relevance score
        relevance_score = self.calculate_relevance_score(
            title, description, categories, tags, messages
        )
        
        # Count message volume
        message_volume = len(messages)
        
        return {
            'name': self.clean_title(title),
            'description': description,
            'category': categories,
            'tags': tags,
            'date': date_str or '',
            'date_source': date_source,
            'relevance_score': relevance_score,
            'message_volume': message_volume,
            'creator': 'Piet Weinman',
            'type': 'chatgpt',
            'url': f"https://chat.openai.com/c/{self.generate_id(title)}"
        }
    
    def create_intelligent_description(self, title: str, messages: List[str]) -> str:
        """Create a meaningful description from conversation content"""
        
        # Combine title and message snippets
        content = title.lower()
        if messages:
            # Take first and last substantial messages
            content += ' ' + ' '.join(messages[:2] + messages[-2:])
        
        description_parts = []
        
        # Identify the main topic
        if 'valentina' in content or 'sage' in content:
            description_parts.append("AI persona development for GTR quiz funnel")
        elif 'emma' in content or 'tnt' in content:
            description_parts.append("TNT Media brand and acquisition strategy")
        elif 'resume' in content or 'portfolio' in content:
            description_parts.append("Job application materials and portfolio development")
        elif 'prompt' in content:
            description_parts.append("Prompt engineering and template development")
        elif 'email' in content and 'sequence' in content:
            description_parts.append("Email sequence copywriting and optimization")
        elif 'landing' in content or 'sales page' in content:
            description_parts.append("Landing/sales page copy and conversion optimization")
        elif 'research' in content:
            description_parts.append("Market and customer research analysis")
        elif 'strategy' in content:
            description_parts.append("Strategic planning and framework development")
        else:
            # Extract key phrases from messages
            key_phrases = self.extract_key_phrases(messages)
            if key_phrases:
                description_parts.append(f"Discussion of {', '.join(key_phrases[:3])}")
        
        # Add specific deliverables if found
        deliverables = self.extract_deliverables(content)
        if deliverables:
            description_parts.append(f"Created: {', '.join(deliverables)}")
        
        # Add tools/techniques if found
        tools = self.extract_tools(content)
        if tools:
            description_parts.append(f"Using: {', '.join(tools)}")
        
        # Combine and limit length
        description = '. '.join(description_parts)
        
        # If still too generic, use intelligent summary of messages
        if len(description) < 50 and messages:
            # Take meaningful snippet from messages
            for msg in messages:
                if len(msg) > 100:
                    description = msg[:200] + "..."
                    break
        
        return description[:300]  # Limit to 300 chars
    
    def determine_categories(self, title: str, description: str, 
                            messages: List[str]) -> List[str]:
        """Intelligently determine categories"""
        
        categories = []
        content = f"{title} {description} {' '.join(messages[:5])}".lower()
        
        # Score each category
        category_scores = {}
        
        for category, patterns in self.category_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in content:
                    score += 1
            if score > 0:
                category_scores[category] = score
        
        # Get top categories (multi-category assignment)
        if category_scores:
            sorted_categories = sorted(category_scores.items(), 
                                     key=lambda x: x[1], reverse=True)
            categories = [cat[0] for cat in sorted_categories[:3]]
        
        # Fallback to general category detection
        if not categories:
            if any(word in content for word in ['prompt', 'template', 'system']):
                categories.append("Prompt Engineering")
            elif any(word in content for word in ['email', 'sequence', 'newsletter']):
                categories.append("Copywriting - Emails")
            elif any(word in content for word in ['strategy', 'planning', 'framework']):
                categories.append("Business Strategy")
            elif any(word in content for word in ['research', 'customer', 'avatar']):
                categories.append("Customer Research")
            else:
                categories.append("General Chat")
        
        return categories
    
    def generate_specific_tags(self, title: str, description: str, 
                              messages: List[str]) -> List[str]:
        """Generate specific, useful tags"""
        
        tags = set()
        content = f"{title} {description} {' '.join(messages[:3])}".lower()
        
        # Check each tag category
        for category, patterns in self.tag_patterns.items():
            for pattern in patterns:
                if pattern in content:
                    # Add the actual term found, not the category
                    tags.add(pattern.title())
        
        # Add specific project indicators
        if 'gtr' in content or 'receipts' in content:
            tags.add("GTR")
        if 'tnt' in content:
            tags.add("TNT")
        if 'paleohacks' in content:
            tags.add("PaleoHacks")
        
        # Add work type indicators
        if 'framework' in content:
            tags.add("Framework")
        if 'template' in content:
            tags.add("Template")
        if 'automation' in content or 'n8n' in content:
            tags.add("Automation")
        if 'analysis' in content or 'audit' in content:
            tags.add("Analysis")
        
        # Add deliverable types
        if 'email sequence' in content:
            tags.add("Email Sequence")
        if 'landing page' in content:
            tags.add("Landing Page")
        if 'sales page' in content:
            tags.add("Sales Page")
        if 'vsl' in content:
            tags.add("VSL")
        
        # Limit to 5 most relevant tags
        return list(tags)[:5] if tags else ["General"]
    
    def calculate_relevance_score(self, title: str, description: str, 
                                 categories: List[str], tags: List[str], 
                                 messages: List[str]) -> float:
        """Calculate relevance score based on content value"""
        
        score = 0.5  # Base score
        
        # Boost for project work
        if any('Project' in cat for cat in categories):
            score += 0.2
        
        # Boost for frameworks/templates
        if any(tag in tags for tag in ['Framework', 'Template', 'System']):
            score += 0.15
        
        # Boost for specific deliverables
        if any(tag in tags for tag in ['Email Sequence', 'Landing Page', 'Sales Page']):
            score += 0.15
        
        # Boost for substantial conversations
        if len(messages) > 10:
            score += 0.1
        
        # Boost for strategy/analysis
        if 'Business Strategy' in categories or 'Analysis' in tags:
            score += 0.1
        
        # Penalty for general chat
        if categories == ['General Chat']:
            score -= 0.2
        
        # Penalty for very short conversations
        if len(messages) < 3:
            score -= 0.1
        
        return min(max(score, 0.1), 1.0)  # Keep between 0.1 and 1.0
    
    def extract_deliverables(self, text: str) -> List[str]:
        """Extract specific deliverables mentioned"""
        deliverables = []
        patterns = {
            'email sequence': r'email\s+sequence',
            'landing page': r'landing\s+page',
            'sales page': r'sales\s+page',
            'VSL script': r'vsl\s+script',
            'ad copy': r'ad\s+copy',
            'headline': r'headline',
            'hook': r'hook',
            'framework': r'framework',
            'template': r'template'
        }
        
        for name, pattern in patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                deliverables.append(name)
        
        return deliverables[:3]  # Max 3 deliverables
    
    def extract_tools(self, text: str) -> List[str]:
        """Extract tools and platforms mentioned"""
        tools = []
        tool_patterns = {
            'Claude': r'claude',
            'ChatGPT': r'chatgpt|gpt',
            'n8n': r'n8n',
            'Cursor': r'cursor',
            'Zapier': r'zapier',
            'Airtable': r'airtable'
        }
        
        for name, pattern in tool_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                tools.append(name)
        
        return tools[:3]  # Max 3 tools
    
    def extract_key_phrases(self, messages: List[str]) -> List[str]:
        """Extract key phrases from messages"""
        key_phrases = []
        
        # Simple key phrase extraction
        for msg in messages[:3]:  # Check first 3 messages
            # Look for phrases that indicate main topics
            if 'how to' in msg.lower():
                match = re.search(r'how to ([^.!?]+)', msg, re.IGNORECASE)
                if match:
                    key_phrases.append(match.group(1)[:30])
            
            if 'create' in msg.lower() or 'build' in msg.lower():
                match = re.search(r'(?:create|build)\s+(?:a\s+)?([^.!?]+)', msg, re.IGNORECASE)
                if match:
                    key_phrases.append(match.group(1)[:30])
        
        return key_phrases
    
    def clean_title(self, title: str) -> str:
        """Clean and format title"""
        # Unescape unicode characters
        title = title.encode().decode('unicode_escape')
        # Remove special characters but keep important ones
        title = re.sub(r'[^\w\s\-–—:,.\(\)]', '', title)
        # Truncate if too long
        return title[:100]
    
    def generate_id(self, title: str) -> str:
        """Generate a consistent ID from title"""
        return hashlib.md5(title.encode()).hexdigest()[:12]
    
    def convert_to_csv(self, conversations: List[Dict], output_path: str, 
                      chunk_size: int = 500) -> List[str]:
        """Convert to CSV format optimized for Gemini"""
        
        output_files = []
        
        for i in range(0, len(conversations), chunk_size):
            chunk = conversations[i:i+chunk_size]
            
            # Prepare for CSV
            csv_data = []
            for conv in chunk:
                csv_data.append({
                    'name': conv['name'],
                    'description': conv['description'],
                    'category': '|'.join(conv['category']) if isinstance(conv['category'], list) else conv['category'],
                    'tags': ','.join(conv['tags']) if isinstance(conv['tags'], list) else conv['tags'],
                    'date': conv['date'],
                    'date_source': conv['date_source'],
                    'relevance_score': round(conv['relevance_score'], 2),
                    'message_volume': conv['message_volume'],
                    'creator': conv['creator'],
                    'type': conv['type'],
                    'url': conv['url']
                })
            
            # Create DataFrame and save
            df = pd.DataFrame(csv_data)
            
            # Generate filename
            chunk_num = (i // chunk_size) + 1
            filename = f"{output_path}_chunk_{chunk_num:03d}.csv"
            
            # Save with proper quoting
            df.to_csv(filename, index=False, quoting=csv.QUOTE_MINIMAL)
            output_files.append(filename)
            
            print(f"✅ Created {filename}: {len(chunk)} records, {os.path.getsize(filename)/1024:.1f}KB")
        
        return output_files
    
    def create_summary_report(self, conversations: List[Dict], output_path: str):
        """Create a summary report of the conversion"""
        
        report = {
            'total_conversations': len(conversations),
            'date_range': {
                'earliest': min([c['date'] for c in conversations if c['date']]),
                'latest': max([c['date'] for c in conversations if c['date']])
            },
            'categories_distribution': {},
            'top_tags': {},
            'relevance_distribution': {
                'high (0.8-1.0)': 0,
                'medium (0.5-0.7)': 0,
                'low (0.0-0.4)': 0
            },
            'missing_dates': 0
        }
        
        # Analyze categories
        for conv in conversations:
            for cat in conv['category']:
                report['categories_distribution'][cat] = report['categories_distribution'].get(cat, 0) + 1
        
        # Analyze tags
        all_tags = []
        for conv in conversations:
            all_tags.extend(conv['tags'])
        from collections import Counter
        report['top_tags'] = dict(Counter(all_tags).most_common(20))
        
        # Analyze relevance
        for conv in conversations:
            score = conv['relevance_score']
            if score >= 0.8:
                report['relevance_distribution']['high (0.8-1.0)'] += 1
            elif score >= 0.5:
                report['relevance_distribution']['medium (0.5-0.7)'] += 1
            else:
                report['relevance_distribution']['low (0.0-0.4)'] += 1
        
        # Count missing dates
        report['missing_dates'] = sum(1 for c in conversations if not c['date'])
        
        # Save report
        with open(f"{output_path}_report.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n📊 Conversion Report:")
        print(f"Total Conversations: {report['total_conversations']}")
        print(f"Date Range: {report['date_range']['earliest']} to {report['date_range']['latest']}")
        print(f"Missing Dates: {report['missing_dates']}")
        print(f"\nTop Categories:")
        for cat, count in sorted(report['categories_distribution'].items(), 
                                key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {cat}: {count}")
        print(f"\nTop Tags:")
        for tag, count in list(report['top_tags'].items())[:5]:
            print(f"  - {tag}: {count}")

def main():
    """Main conversion function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python intelligent_converter.py <input_file> [output_prefix]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_prefix = sys.argv[2] if len(sys.argv) > 2 else "gemini_ready"
    
    print(f"🚀 Starting intelligent conversion of {input_file}")
    print(f"📝 Output prefix: {output_prefix}")
    
    converter = IntelligentConverter()
    
    # Parse the input file
    if 'gpt' in input_file.lower() or 'chatgpt' in input_file.lower():
        conversations = converter.parse_chatgpt_export(input_file)
    else:
        print("Note: Assuming ChatGPT format. For Claude exports, add 'claude' to filename.")
        conversations = converter.parse_chatgpt_export(input_file)
    
    print(f"📚 Parsed {len(conversations)} conversations")
    
    # Convert to CSV
    csv_files = converter.convert_to_csv(conversations, output_prefix)
    
    # Create summary report
    converter.create_summary_report(conversations, output_prefix)
    
    print(f"\n✨ Conversion complete!")
    print(f"📁 Created {len(csv_files)} CSV files")
    print(f"📊 Report saved to {output_prefix}_report.json")

if __name__ == "__main__":
    main()
