"""
NetGuard-IDS: Safety, Ethics, and Governance Standards.
"""

import streamlit as st

st.set_page_config(page_title="About & Ethics | NetGuard-IDS", page_icon="⚖️", layout="wide")

st.title("⚖️ Safety, Ethics & Governance Policies")
st.markdown("NetGuard-IDS is engineered exclusively for defensive cybersecurity research, security posture audits, and authorized threat detection.")

st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🛡️ Ethical Mandate")
    st.markdown("""
    Port scanning, network reconnaissance, and traffic inspection against systems without prior explicit authorization
    can violate state, federal, and international computer misuse statutes, including:
    - **U.S. Computer Fraud and Abuse Act (CFAA, 18 U.S.C. § 1030)**
    - **UK Computer Misuse Act 1990**
    - **EU Cybercrime Convention (Budapest Convention)**
    - **Indian Information Technology Act, 2000 (Section 43 & 66)**

    NetGuard-IDS enforces programmatic guardrails to safeguard defensive compliance:
    1. **Pre-Scan User Authorization**: Mandatory verification of ownership or explicit written authorization.
    2. **Public IP Restriction in Cloud/Demo Environments**: Prohibits unconstrained scanning of unauthorized external public infrastructure.
    3. **Allowlisted Research Targets**: Specifically permits loopback (`127.0.0.1`), RFC1918 private subnets, and official testbeds like `scanme.nmap.org`.
    4. **Rate-Limiting & Thread Capping**: Minimizes network impact and prevents accidental denial of service during auditing.
    """)

with col2:
    st.subheader("⚙️ Technical Architecture Overview")
    st.markdown("""
    **Core Engine Capabilities:**
    - **Port Scanner:** Non-root Python socket TCP connect scanner with `concurrent.futures`, service detection, and application banner grabbing.
    - **Risk Engine:** Automated CVSS-style threat modeling that maps exposed daemons (e.g., Telnet, SMBv1, unauthenticated Redis/MongoDB) to actionable remediation playbooks.
    - **Machine Learning IDS:** Dual-model pipeline (Random Forest & XGBoost) trained on benchmark NSL-KDD network flows, classifying threats across **Normal, DoS, Probe, R2L, and U2R** categories.
    - **Persistence Layer:** Zero-dependency embedded SQLite database tracking historical scans and flow evaluations.
    """)

st.divider()

st.markdown("""
### 📜 Open Source License & Attribution
Distributed under the **MIT License**. Created for defensive engineering, cybersecurity education, and enterprise risk assessment.
""")
