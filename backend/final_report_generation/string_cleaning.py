import re
import json

def extract_and_save_json(text, output_file='output.json'):
    """
    Extract JSON from LLM output and save to file.
    Returns the parsed JSON object.
    """
    try:
        # Find JSON in code blocks or standalone
        code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if code_block_match:
            json_str = code_block_match.group(1)
        else:
            # Try to find the largest JSON object
            json_match = re.search(r'\{(?:[^{}]|\{[^{}]*\})*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                print("No JSON structure found in text")
                return None
        
        # Clean common LLM JSON issues
        json_str = clean_llm_json(json_str)
        
        # Parse JSON
        json_obj = json.loads(json_str)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_obj, f, indent=2, ensure_ascii=False)
        
        print(f"✓ JSON successfully extracted and saved to {output_file}")
        
        # Return the parsed object
        return json_obj
        
    except json.JSONDecodeError as e:
        print(f"✗ JSON parsing error: {e}")
        print(f"Attempted to parse around: ...{json_str[max(0, e.pos-100):e.pos+100]}...")
        
        # Try aggressive cleaning
        try:
            json_str = aggressive_clean_json(json_str)
            json_obj = json.loads(json_str)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_obj, f, indent=2, ensure_ascii=False)
            
            print(f"✓ JSON extracted with aggressive cleaning and saved to {output_file}")
            return json_obj
        except Exception as e2:
            print(f"✗ Could not parse JSON even with aggressive cleaning: {e2}")
            # Save the problematic JSON for debugging
            with open(f"failed_{output_file}", 'w', encoding='utf-8') as f:
                f.write(json_str)
            print(f"Saved failed JSON to failed_{output_file} for debugging")
            return None
    
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return None


def clean_llm_json(json_str):
    """Clean common LLM JSON formatting issues"""
    # Remove comments (// style)
    json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)
    
    # Remove trailing commas before closing braces/brackets
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    # Fix common key inconsistencies
    json_str = re.sub(r'"Ts_end"', '"ts_end"', json_str)
    json_str = re.sub(r'"Ts_start"', '"ts_start"', json_str)
    
    # Fix unescaped quotes within string values
    # This regex finds strings and escapes internal quotes
    def escape_quotes_in_string(match):
        full_match = match.group(0)
        # Don't touch the outer quotes
        inner = full_match[1:-1]
        # Escape any unescaped quotes inside
        inner = inner.replace('\\"', '___ESCAPED_QUOTE___')  # Temporarily mark already escaped
        inner = inner.replace('"', '\\"')  # Escape unescaped quotes
        inner = inner.replace('___ESCAPED_QUOTE___', '\\"')  # Restore
        return f'"{inner}"'
    
    # Apply to all string values (between quotes)
    # This is tricky - we need to be careful not to break the JSON structure
    # Better approach: use a more targeted fix
    
    return json_str


def aggressive_clean_json(json_str):
    """More aggressive cleaning for severely malformed JSON"""
    
    # Strategy: Find problematic quote fields and fix them
    def fix_quote_field(match):
        key = match.group(1)
        value = match.group(2)
        
        # Escape all internal quotes in the value
        # First, preserve already escaped quotes
        value = value.replace('\\"', '___TEMP_ESCAPE___')
        # Escape unescaped quotes
        value = value.replace('"', '\\"')
        # Restore the temp escapes
        value = value.replace('___TEMP_ESCAPE___', '\\"')
        
        return f'"{key}": "{value}"'
    
    # Fix "quote" fields specifically (the problematic ones in your data)
    json_str = re.sub(
        r'"(quote|description|suggestion|summary|context)":\s*"((?:[^"\\]|\\.)*?)"',
        fix_quote_field,
        json_str
    )
    
    # Remove trailing commas more aggressively
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    
    # Fix any remaining newlines within strings
    json_str = re.sub(r'\\n', ' ', json_str)
    
    return json_str