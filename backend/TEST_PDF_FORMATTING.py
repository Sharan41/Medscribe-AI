#!/usr/bin/env python3
"""
Test script to verify PDF bullet point formatting
Run this to check if conversion is working correctly
"""
import sys
sys.path.insert(0, '.')

def test_conversion():
    """Test the bullet point conversion functions"""
    import re
    
    def _ensure_bullet_points(markdown: str) -> str:
        if not markdown:
            return ""
        
        lines = markdown.split("\n")
        result = []
        current_section_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith("##"):
                if current_section_lines:
                    result.extend(_process_section_lines(current_section_lines))
                    current_section_lines = []
                result.append(line)
                continue
            
            if not stripped:
                if current_section_lines:
                    result.extend(_process_section_lines(current_section_lines))
                    current_section_lines = []
                result.append("")
                continue
            
            current_section_lines.append(stripped)
        
        if current_section_lines:
            result.extend(_process_section_lines(current_section_lines))
        
        return "\n".join(result)
    
    def _process_section_lines(lines):
        result = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("- "):
                result.append(stripped)
            elif " - " in stripped:
                items = stripped.split(" - ")
                for item in items:
                    item = item.strip()
                    if item:
                        item = item.rstrip('.')
                        if item:
                            result.append(f"- {item}")
            else:
                result.append(f"- {stripped}")
        return result
    
    # Test with actual format from PDF
    test_cases = [
        """## Subjective
Abdominal pain - Sensation of a stomach ulcer

## Plan
Further investigation. - Prescribe antacids. - Follow up.""",
        
        """## Subjective
- Abdominal pain
- Sensation of a stomach ulcer

## Plan
- Further investigation
- Prescribe antacids
- Follow up"""
    ]
    
    print("="*70)
    print("PDF Bullet Point Conversion Test")
    print("="*70)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print("-"*70)
        print("INPUT:")
        print(test)
        print("\nOUTPUT:")
        result = _ensure_bullet_points(test)
        print(result)
        print("\n" + "="*70)
    
    print("\n✅ Conversion test complete!")
    print("   If output shows bullet points (- item), conversion works.")
    print("   Check server logs when generating PDF to see actual conversion.")

if __name__ == "__main__":
    test_conversion()

