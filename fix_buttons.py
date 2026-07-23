import re

files = [
    r'C:\Users\shash\PycharmProjects\PythonProject1\app.py',
    r'C:\Users\shash\PycharmProjects\PythonProject1\PythonProject1\app.py'
]

patterns = [
    (r'        if st\.button\(\"Calculate Property Valuation & Loan Terms\", key=\"btn_h_calc\"\):\n            with st\.spinner\(\"Analyzing property value and loan eligibility\.\.\.\"\):\n                from backend\.routers\.valuation import evaluate_loan_module, EvaluateLoanModuleInput\n                res = evaluate_loan_module\(EvaluateLoanModuleInput\((.*?)\)\)', 
     'h', "Calculate Property Valuation & Loan Terms", "Analyzing property value and loan eligibility..."),
    (r'        if st\.button\(\"Calculate Ag Valuation & Risk Score\", key=\"btn_a_calc\"\):\n            with st\.spinner\(\"Analyzing land value and agricultural risks\.\.\.\"\):\n                from backend\.routers\.valuation import evaluate_loan_module, EvaluateLoanModuleInput\n                res = evaluate_loan_module\(EvaluateLoanModuleInput\((.*?)\)\)', 
     'a', "Calculate Ag Valuation & Risk Score", "Analyzing land value and agricultural risks..."),
    (r'        if st\.button\(\"Calculate Commercial Valuation & EMI\", key=\"btn_c_calc\"\):\n            with st\.spinner\(\"Analyzing commercial property \+ cash flows\.\.\.\"\):\n                from backend\.routers\.valuation import evaluate_loan_module, EvaluateLoanModuleInput\n                res = evaluate_loan_module\(EvaluateLoanModuleInput\((.*?)\)\)', 
     'c', "Calculate Commercial Valuation & EMI", "Analyzing commercial property + cash flows..."),
    (r'        if st\.button\(\"Calculate Live Gold Valuation\", key=\"btn_g_calc\"\):\n            with st\.spinner\(\"Fetching live spot rates and evaluating purity\.\.\.\"\):\n                from backend\.routers\.valuation import evaluate_loan_module, EvaluateLoanModuleInput\n                res = evaluate_loan_module\(EvaluateLoanModuleInput\((.*?)\)\)', 
     'g', "Calculate Live Gold Valuation", "Fetching live spot rates and evaluating purity..."),
    (r'        if st\.button\(\"Calculate Farm Equipment Loan\", key=\"btn_f_calc\"\):\n            with st\.spinner\(\"Assessing equipment value \+ govt subsidies\.\.\.\"\):\n                from backend\.routers\.valuation import evaluate_loan_module, EvaluateLoanModuleInput\n                res = evaluate_loan_module\(EvaluateLoanModuleInput\((.*?)\)\)', 
     'f', "Calculate Farm Equipment Loan", "Assessing equipment value + govt subsidies..."),
    (r'        if st\.button\(\"Calculate Vehicle Loan Eligibility\", key=\"btn_v_calc\"\):\n            with st\.spinner\(\"Running vehicle depreciation and AI credit checks\.\.\.\"\):\n                from backend\.routers\.valuation import evaluate_loan_module, EvaluateLoanModuleInput\n                res = evaluate_loan_module\(EvaluateLoanModuleInput\((.*?)\)\)', 
     'v', "Calculate Vehicle Loan Eligibility", "Running vehicle depreciation and AI credit checks...")
]

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for regex_pattern, pfx, btn_text, spinner_text in patterns:
        def replacer(match):
            args = match.group(1)
            
            return f'''        btn_{pfx}_clicked = st.button("{btn_text}", key="btn_{pfx}_calc")
        if btn_{pfx}_clicked:
            st.session_state["{pfx}_calc_done"] = True
            st.session_state.pop("{pfx}_report_data", None)
            st.session_state.pop("{pfx}_res", None)
            
        if st.session_state.get("{pfx}_calc_done", False):
            if "{pfx}_res" not in st.session_state or btn_{pfx}_clicked:
                with st.spinner("{spinner_text}"):
                    from backend.routers.valuation import evaluate_loan_module, EvaluateLoanModuleInput
                    st.session_state["{pfx}_res"] = evaluate_loan_module(EvaluateLoanModuleInput({args}))
            res = st.session_state["{pfx}_res"]
            if True:'''
            
        content = re.sub(regex_pattern, replacer, content, flags=re.DOTALL)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
print('Done!')
