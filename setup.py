#!/usr/bin/env python3
"""
Setup and Quick Start for Chat Converters
Run this first to make sure everything is ready!
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required packages are installed"""
    print("🔍 Checking dependencies...")
    
    required = ['pandas']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✅ {package} is installed")
        except ImportError:
            print(f"  ❌ {package} is missing")
            missing.append(package)
    
    if missing:
        print(f"\n📦 Installing missing packages: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print("  ✅ Installation complete!")
        except:
            print("  ⚠️ Could not auto-install. Please run:")
            print(f"     pip install {' '.join(missing)}")
    else:
        print("\n✅ All dependencies are installed!")

def show_quickstart():
    """Show quick start instructions"""
    
    print("\n" + "=" * 60)
    print("🚀 QUICK START GUIDE")
    print("=" * 60)
    
    print("""
📝 STEP 1: Upload Your Chat Export Files
   Place your conversation export files in the same directory:
   - conv_part_aa.txt
   - conv_part_ab.txt
   - Or your conversations.json file

📊 STEP 2: Choose Your Processing Method

   A) Quick Test (See how it works):
      python test_demonstration.py
   
   B) Single File Conversion:
      python quick_converter.py conv_part_aa.txt
   
   C) Batch Process Multiple Files:
      python batch_processor.py conv_part_*.txt
   
   D) Full Intelligent Processing:
      python intelligent_converter.py your_file.txt output_name

📤 STEP 3: Import to Gemini
   The converter creates CSV files ready for Gemini:
   - gemini_ready_chunk_001.csv
   - gemini_ready_chunk_002.csv
   - etc.
   
   Each file has <500 conversations to keep under 100KB.

🎯 KEY FEATURES:
   ✅ Extracts actual conversation content (not metadata!)
   ✅ Multi-category assignment (Project-GTR|AI Bot|Strategy)
   ✅ Specific tags (Valentina, Emma Brand, Framework, etc.)
   ✅ Relevance scoring (0-1 based on strategic value)
   ✅ Date extraction and formatting
   ✅ CSV format optimized for Gemini

📂 OUTPUT FILES:
   - *_chunk_XXX.csv : Your conversations in CSV format
   - *_report.json : Analysis of your archive
   - README.md : Full documentation

🆘 TROUBLESHOOTING:
   If you see "Description has metadata":
   → We extract from message content, not JSON structure
   
   If categories are generic:
   → We pattern-match against your actual projects
   
   If files are too large:
   → We auto-chunk into 500-record files

📈 WHAT YOU'LL SEE:
   After processing, you'll get a report showing:
   - Total conversations processed
   - Date range of your archive
   - Top categories (GTR, TNT Media, etc.)
   - Most used tags
   - Relevance distribution
""")
    
    print("=" * 60)
    print("Ready to start? Try: python test_demonstration.py")
    print("=" * 60)

def create_sample_file():
    """Create a sample file for testing if none exists"""
    
    sample_content = '''"title": "Test conversation about Valentina AI", 
"create_time": 1729958400.0,
"update_time": 1729958527.0,
"mapping": {
    "message-1": {
        "message": {
            "content": {
                "parts": ["I need help developing the Valentina AI personality for the GTR quiz funnel. She needs to be mysterious but approachable."]
            }
        }
    },
    "assistant-1": {
        "message": {
            "content": {
                "parts": ["Let's develop Valentina's character DNA. We'll focus on: voice tone (mysterious yet warm), personality traits (intuitive, wise, playful), and visual identity. For the quiz funnel, she should guide users through self-discovery."]
            }
        }
    }
}'''
    
    if not os.path.exists('sample_conversation.txt'):
        with open('sample_conversation.txt', 'w') as f:
            f.write(sample_content)
        print("\n📝 Created sample_conversation.txt for testing")
        return True
    return False

def main():
    print("=" * 60)
    print("💫 CHAT EXPORT TO CSV CONVERTER")
    print("   Intelligent Parsing for Gemini Import")
    print("=" * 60)
    
    # Check dependencies
    check_dependencies()
    
    # Create sample if needed
    if create_sample_file():
        print("   You can test with: python quick_converter.py sample_conversation.txt")
    
    # Show instructions
    show_quickstart()
    
    # Check for existing files
    print("\n🔍 Looking for conversation files...")
    
    found_files = []
    patterns = ['conv_part_*.txt', 'conversations.json', '*.json', '*.txt']
    
    for pattern in patterns:
        import glob
        files = glob.glob(pattern)
        found_files.extend(files)
    
    if found_files:
        print(f"\n📁 Found {len(found_files)} potential files:")
        for f in found_files[:10]:  # Show first 10
            print(f"   - {f}")
        
        if len(found_files) > 1 and any('conv_part' in f for f in found_files):
            print("\n💡 TIP: You have multiple conv_part files.")
            print("   Use: python batch_processor.py conv_part_*.txt")
    else:
        print("\n📂 No conversation files found in current directory.")
        print("   Upload your export files and run this script again.")

if __name__ == "__main__":
    main()
