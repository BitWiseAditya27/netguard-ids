# 🎓 NetGuard-IDS: Viva & Teacher Presentation Guide
**Author / Presenter:** Aditya Yadav (`BitWiseAditya27`)  
**Project:** NetGuard-IDS (Network Intrusion Detection & Port Risk Analyzer)

This document contains everything you need to **ace your project evaluation, teacher viva, and live demonstration**.

---

## ⏱️ 1. 2-Minute Elevator Pitch (How to Introduce Your Project)
> *"Respected teachers and evaluators, today I present **NetGuard-IDS** — an enterprise-grade defensive cybersecurity suite that unifies two essential pillars of security: **Active Perimeter Port Risk Auditing** and **AI-Driven Network Intrusion Detection**.*
>
> *Traditional tools like Nmap require raw administrative root privileges and lack threat-risk scoring, while classic intrusion detection systems like Snort rely on static signatures that struggle with subtle attack variations. NetGuard-IDS solves this by providing: (1) an unprivileged multithreaded socket scanner with automated CVSS-style risk scoring, (2) an ML flow classifier trained on the NSL-KDD benchmark that detects DoS, Probes, R2L, and U2R attacks with 98.3% accuracy, and (3) an interactive executive dashboard with SQLite audit persistence and one-click report exports."*

---

## 🖥️ 2. Live Demo Script (Step-by-Step for the Teacher)

Follow this sequence when showing the project on your laptop or hosted cloud:

### Step 1: Open the SOC Dashboard (`app.py`)
- Show the **Security Operations Center (SOC) Feed**.
- Point out the real-time metric cards: *Total Hosts Audited*, *ML Traffic Files Analyzed*, *Malicious Flows Intercepted*, and *Latest Security Verdict*.
- Explain: *"This provides the security officer with a birds-eye view of all internal host health and telemetry."*

### Step 2: Demonstrate the Port Scanner (`pages/1_🔍_Port_Scanner.py`)
1. Show the **Safety & Authorization Policy**:
   - Point out the mandatory checkbox: *"I confirm that I own this target system or have explicit written authorization to scan it."* (Explain that clicking without authorization will block execution).
2. Type in `127.0.0.1` (or click **Hosted Demo Mode**).
3. Click **"Launch Port Audit"**:
   - Show the real-time progress bar.
   - Point to the **Plotly Cyber Risk Index Gauge (0–100)** and the **Vulnerability Severity Donut Chart**.
   - Show the detected open ports table with grabbed service banners and **Actionable Remediation Guidance** (e.g. why SMB 445 should be firewalled against WannaCry/EternalBlue, why Telnet should be migrated to SSH).
4. **Teacher Test Case (Policy Enforcement):**
   - Type in an arbitrary public IP like `8.8.8.8` and try to scan with Demo Mode OFF.
   - Show that the system immediately blocks it with a policy violation warning to protect external networks.

### Step 3: Demonstrate the ML Traffic Classifier (`pages/2_🧠_Traffic_Analysis.py`)
1. Click **"Load Bundled Benchmark CSV (50 Flows)"** (or upload your own flow CSV).
2. Watch the Random Forest & XGBoost model execute in sub-100ms.
3. Show:
   - Total Analyzed Flows vs Malicious Intrusions.
   - **Attack Taxonomy Distribution Chart** (`Normal`, `DoS`, `Probe`, `R2L`, `U2R`).
   - Per-row flow prediction table showing the exact model **Confidence %**.
   - Click **"Download Annotated Predictions CSV"** to demonstrate SIEM export capabilities.

### Step 4: Show the Audit History & Export (`pages/3_📋_Risk_Report.py`)
- Show that every scan is automatically persisted in an embedded SQLite database.
- Demonstrate one-click report downloads in **JSON**, **CSV**, and **Markdown Executive Summary**.

---

## 🎯 3. Top 10 Viva Questions Teachers Ask (With Model Answers)

#### Q1: Why did you choose Random Forest over Deep Learning (like CNN/RNN) for this project?
> **Answer:** *"Network intrusion flows in datasets like NSL-KDD are tabular data with discrete numerical and categorical features (bytes, duration, flags). Research and empirical benchmarks consistently show that tree-based ensembles (Random Forest and XGBoost) outperform Deep Learning on tabular data in terms of both accuracy (98.3% vs ~95%), inference latency (<10ms per batch), and explainability, without requiring dedicated GPU infrastructure."*

#### Q2: How is your Port Scanner different from Nmap?
> **Answer:** *"Nmap uses raw socket packet crafting (such as TCP SYN half-open scans) which requires root/administrator privileges and external C libraries. NetGuard-IDS uses Python's standard `socket` with non-blocking TCP connects inside `concurrent.futures.ThreadPoolExecutor`. This allows it to run in user space without root, across Windows, Linux, and cloud containers, while adding automated CVSS-style risk scoring which Nmap doesn't provide natively."*

#### Q3: What attack categories does your ML model detect?
> **Answer:** *"It maps threats into 5 core classes:
> 1. **Normal**: Standard benign traffic.
> 2. **DoS (Denial of Service)**: e.g. Neptune, Smurf, Teardrop (resource exhaustion).
> 3. **Probe**: e.g. Nmap, Portsweep, Satan (reconnaissance).
> 4. **R2L (Remote to Local)**: e.g. Guess Password, FTP Write, Warez (unauthorized remote access).
> 5. **U2R (User to Root)**: e.g. Buffer Overflow, Rootkit (local privilege escalation)."*

#### Q4: What is the NSL-KDD dataset and why did you use it?
> **Answer:** *"NSL-KDD is a refined and widely accepted benchmark dataset based on KDD Cup 99. It resolves critical issues found in the original KDD dataset, such as redundant duplicate records that artificially skewed classifier accuracy, making it the academic benchmark standard for evaluating network intrusion detection systems."*

#### Q5: How do you compute the 0–100 Risk Score?
> **Answer:** *"We use a weighted hybrid algorithm. Each open service is assigned a CVSS v3.1 base score and a severity tier (Critical: 30, High: 18, Medium: 8, Low: 3). We combine the cumulative exposure score with the maximum detected CVSS score: `Score = min(100, (raw_score * 0.8) + (max_cvss * 3.5))`. If dangerous services like SMBv1, Telnet, or unauthenticated Redis are present, the score escalates to CRITICAL."*

#### Q6: How do you prevent attackers from using your tool maliciously?
> **Answer:** *"We have enforced programmatic ethical guardrails:
> 1. A mandatory pre-scan ownership consent checkbox.
> 2. Hardcoded target allowlisting restricting audits strictly to `localhost`, private RFC1918 subnets (`10.x`, `172.16-31.x`, `192.168.x`), and authorized research targets like `scanme.nmap.org`.
> 3. Arbitrary external public IPs are blocked at the validator level.
> 4. Rate-limiting and thread caps prevent denial-of-service on scanned networks."*

#### Q7: Why use Streamlit instead of React/Django or Flask?
> **Answer:** *"Streamlit enables reactive, stateful Python applications without the overhead of maintaining decoupled REST APIs and frontend JavaScript builds. For a cybersecurity data-intensive tool with dynamic Plotly charts, Streamlit allows instant data re-rendering and lower maintenance complexity."*

#### Q8: How is scan data stored?
> **Answer:** *"We use SQLite with thread-safe connections. It requires zero external database installation, supports instant persistence of scan metrics and ML predictions, and can be queried or backed up as a single portable file."*

#### Q9: What happens if outbound scanning is blocked on cloud hosting like Streamlit Cloud?
> **Answer:** *"Cloud hosting providers frequently block outbound raw sockets to prevent abuse. We engineered a seamless 'Hosted Demo Mode' toggle that provides authentic simulated telemetry based on real-world enterprise compromise scenarios, ensuring the evaluator can test all dashboard features anywhere."*

#### Q10: What are the future enhancements for this project?
> **Answer:** *"1. Real-time live packet capture via Scapy or eBPF hardware taps. 2. Unsupervised LSTM Autoencoders for zero-day anomaly detection. 3. Automated alerting webhooks directly into enterprise SIEMs like Splunk or Elastic."*

---

## 📁 4. Summary of Files Ready to Present to Your Teacher

| File | Type | Description |
| :--- | :--- | :--- |
| **`docs/Presentation.pptx`** | PowerPoint | 10 high-impact dark-themed slides with architecture, tables & metrics |
| **`docs/Synopsis.docx`** | Word Doc | Formal project synopsis with literature review, IEEE references & diagram |
| **`docs/SRS.docx`** | Word Doc | IEEE 830-1998 compliant requirements specification with RTM matrix |
| **`docs/Tech_Stack.docx`** | Word Doc | Exhaustive technology justification & architectural workflows |
| **`docs/architecture_diagram.png`** | Image | High-resolution multi-tier architecture block diagram |
| **`docs/VIVA_AND_PRESENTATION_GUIDE.md`** | Markdown | This complete speech script, demo steps, and Q&A cheat sheet |
