import ast
import re
import string

def make_key(text):
    text = text.lower()
    text = "".join(c if c.isalnum() else "_" for c in text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:40]

def extract_strings(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    translations = {}
    
    st_funcs = ["st.title", "st.header", "st.subheader", "st.markdown", "st.write", "st.button", "st.text_input", "st.number_input", "st.selectbox", "st.error", "st.success", "st.warning", "st.info", "st.sidebar.markdown", "st.sidebar.title", "st.sidebar.header", "st.sidebar.button", "st.sidebar.selectbox"]
    
    new_content = content
    for func in st_funcs:
        pattern = rf'({func}\s*\(\s*)(["\'])(.*?)\2'
        
        def replacer(match):
            prefix = match.group(1)
            quote = match.group(2)
            text = match.group(3)
            
            if not text.strip() or "{" in text:
                return match.group(0)
                
            key = make_key(text)
            if not key:
                return match.group(0)
                
            translations[key] = text
            return f'{prefix}t("{key}")'
            
        new_content = re.sub(pattern, replacer, new_content)

    return new_content, translations

if __name__ == "__main__":
    content, trans = extract_strings("app.py")
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)
        
    with open("PythonProject1/app.py", "w", encoding="utf-8") as f:
        f.write(content)
        
    with open("translations/en.py", "w", encoding="utf-8") as f:
        f.write("TRANSLATIONS = {\n")
        for k, v in trans.items():
            f.write(f'    "{k}": "{v}",\n')
        f.write("}\n")
    print(f"Extracted {len(trans)} translations.")
