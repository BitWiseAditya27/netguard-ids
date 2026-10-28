"""
Build College_Presentation.pptx in the exact EduSense presentation format and layout:
- Slide 1: Left-aligned presentation by Aditya Yadav, Ashutosh Mehta, Atishay Jain, Right-aligned Project Title.
- Slide 2 to 12: Content slides with exact title header and slide number at the bottom right.
- Slide 13: Thank You!
Clean, professional white background with deep navy/royal blue accents.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

DOCS_DIR = r"C:\Users\py056\.gemini\antigravity\scratch\netguard-ids\docs"
OUTPUT_PPTX = os.path.join(DOCS_DIR, "EduSense_Format_Presentation.pptx")
WF_IMG = os.path.join(DOCS_DIR, "workflow_diagram.png")

# Classic Academic Format Colors
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_TEXT_MAIN = RGBColor(30, 41, 59)      # Deep slate #1E293B
COLOR_TITLE = RGBColor(15, 23, 42)          # Almost black #0F172A
COLOR_ACCENT = RGBColor(30, 58, 138)        # Classic academic navy #1E3A8A
COLOR_MUTED = RGBColor(100, 116, 139)       # Slate muted #64748B

def set_slide_background_white(slide):
    bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(7.5))
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = COLOR_WHITE
    bg_shape.line.fill.background()
    return bg_shape

def add_standard_slide(prs, title_text, slide_number, bullet_points):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background_white(slide)

    # Title Box
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(8.4), Inches(0.9))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(26)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_ACCENT

    # Thin decorative line under title
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.65), Inches(8.4), Inches(0.04))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_ACCENT
    line.line.fill.background()

    # Content Box
    content_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.9), Inches(8.4), Inches(4.8))
    tf_c = content_box.text_frame
    tf_c.word_wrap = True

    for i, pt in enumerate(bullet_points):
        p = tf_c.paragraphs[0] if i == 0 else tf_c.add_paragraph()
        p.text = pt
        p.font.size = Pt(15)
        p.font.color.rgb = COLOR_TEXT_MAIN
        p.space_after = Pt(14)
        p.level = 0

    # Slide Number at bottom right (EduSense layout)
    num_box = slide.shapes.add_textbox(Inches(8.5), Inches(6.8), Inches(0.8), Inches(0.4))
    p_n = num_box.text_frame.paragraphs[0]
    p_n.text = str(slide_number)
    p_n.font.size = Pt(12)
    p_n.font.color.rgb = COLOR_MUTED
    p_n.alignment = PP_ALIGN.RIGHT

    return slide

def generate_edusense_style_main_deck():
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    # ==================== SLIDE 1: EXACT EDUSENSE FORMAT ====================
    # "Presentation by- Aditya Yadav Ashutosh Mehta Atishay Jain       [Title]"
    s1 = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background_white(s1)

    # Left: Presentation by
    by_box = s1.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(4.2), Inches(3.5))
    tf_by = by_box.text_frame
    tf_by.word_wrap = True
    
    p_by = tf_by.paragraphs[0]
    p_by.text = "Presentation by-"
    p_by.font.size = Pt(18)
    p_by.font.bold = True
    p_by.font.color.rgb = COLOR_ACCENT
    p_by.space_after = Pt(10)

    for name in ["Aditya Yadav", "Ashutosh Mehta", "Atishay Jain"]:
        pn = tf_by.add_paragraph()
        pn.text = name
        pn.font.size = Pt(16)
        pn.font.color.rgb = COLOR_TEXT_MAIN
        pn.space_after = Pt(6)

    # Right: Project Title (NetGuard-IDS - Network Intrusion Detection & Port Risk Analyzer)
    title_box = s1.shapes.add_textbox(Inches(5.0), Inches(2.0), Inches(4.3), Inches(3.5))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True

    pt1 = tf_title.paragraphs[0]
    pt1.text = "NetGuard-IDS"
    pt1.font.size = Pt(32)
    pt1.font.bold = True
    pt1.font.color.rgb = COLOR_ACCENT
    pt1.space_after = Pt(8)

    pt2 = tf_title.add_paragraph()
    pt2.text = "Network Intrusion Detection & Port Risk Analyzer"
    pt2.font.size = Pt(18)
    pt2.font.bold = True
    pt2.font.color.rgb = COLOR_TITLE
    pt2.space_after = Pt(12)

    pt3 = tf_title.add_paragraph()
    pt3.text = "A Dual-Engine Defensive Cybersecurity & Machine Learning Platform"
    pt3.font.size = Pt(13)
    pt3.font.color.rgb = COLOR_MUTED

    # ==================== SLIDE 2: INTRODUCTION ====================
    add_standard_slide(
        prs,
        title_text="INTRODUCTION",
        slide_number=2,
        bullet_points=[
            "Rapid expansion of enterprise networks and remote endpoints has created severe perimeter visibility gaps.",
            "Manual tracking of open host ports, unauthorized services, and malicious flow anomalies is impractical at scale.",
            "Need for an automated, unified defensive system to support network administrators, auditors, and SOC analysts.",
            "Proposed Solution: A Machine Learning & socket-based platform to identify at-risk open ports, calculate automated CVSS risk scores, and detect live network intrusions in real time."
        ]
    )

    # ==================== SLIDE 3: PROBLEM STATEMENT ====================
    add_standard_slide(
        prs,
        title_text="Problem Statement",
        slide_number=3,
        bullet_points=[
            "Enterprise institutions and infrastructure handle millions of network packets daily.",
            "Traditional port scanners (e.g., Nmap) require root privileges, manual CLI flags, and fail to predict cyber risk scores.",
            "Classic signature-based NIDS (e.g., Snort) struggle to detect novel attack variations before damage escalates.",
            "Difficult to coordinate between port vulnerability discovery and real-time flow intrusion detection for timely containment.",
            "Results in missed opportunities to neutralize dangerous entry vectors (SMB 445, RDP 3389, Telnet 23) before ransomware compromise."
        ]
    )

    # ==================== SLIDE 4: OBJECTIVES ====================
    add_standard_slide(
        prs,
        title_text="Objectives",
        slide_number=4,
        bullet_points=[
            "Develop an automated predictive identification system for high-risk open ports and unauthorized daemons.",
            "Preprocess network flow telemetry using standardization and one-hot encoding feature pipelines.",
            "Train ML classification models (Random Forest & XGBoost) on NSL-KDD benchmark data to predict intrusions.",
            "Detect 5 threat classes: Normal, DoS, Probe, R2L (Remote-to-Local), and U2R (User-to-Root).",
            "Provide real-time dashboarding through an interactive web interface with Plotly telemetry.",
            "Improve threat mitigation speed and reduce system administrator intervention time."
        ]
    )

    # ==================== SLIDE 5: SYSTEM METHODOLOGY (OVERVIEW) ====================
    add_standard_slide(
        prs,
        title_text="System Methodology (Overview)",
        slide_number=5,
        bullet_points=[
            "Target Ingestion: Gathering host IP targets and uploaded network flow CSV captures.",
            "Data Preprocessing: Standardizing flow metrics and validating RFC1918 safety policies.",
            "Feature Extraction: Extracting key risk indicators (duration, protocol_type, src_bytes, serror_rate).",
            "Model Training: Training Random Forest & XGBoost classifiers for multi-class threat prediction.",
            "Model Evaluation: Testing accuracy (98.30%), F1-scores (0.9826), and confusion matrices.",
            "Web Interface Development: Building the NetGuard-IDS multi-page dashboard.",
            "Deployment: Hosting on Streamlit Community Cloud."
        ]
    )

    # ==================== SLIDE 6: OPERATING ENVIRONMENT ====================
    add_standard_slide(
        prs,
        title_text="Operating Environment",
        slide_number=6,
        bullet_points=[
            "Software: Python 3.10+, Pandas, NumPy, Scikit-learn, XGBoost, Streamlit, SQLite 3, Plotly.",
            "Architecture: Dual Defensive Engine (Multithreaded Socket Scanner + ML Flow Classifier), SQLite Database, Web Interface.",
            "Execution Privilege: User-space unprivileged socket connects (Zero root/sudo dependency).",
            "Cloud Platform: Streamlit Community Cloud persistent environment with Hosted Demo Mode fallback.",
            "Browser Support: Chrome, Edge, Firefox, Safari."
        ]
    )

    # ==================== SLIDE 7: NON-FUNCTIONAL REQUIREMENTS ====================
    add_standard_slide(
        prs,
        title_text="Non-Functional Requirements",
        slide_number=7,
        bullet_points=[
            "Fast response time for real-time risk alerts (sub-second port scanning, sub-100ms ML batch inference).",
            "Ethical and safety protection restricting public IP scanning via programmatic RFC1918 target whitelisting.",
            "Secure handling of network flow records without executing unverified system commands (Zero shell=True).",
            "High reliability and fault tolerance with graceful TCP connect timeout recovery.",
            "Scalability for enterprise and institution-wide network adoption."
        ]
    )

    # ==================== SLIDE 8: USER CLASSES ====================
    add_standard_slide(
        prs,
        title_text="User Classes",
        slide_number=8,
        bullet_points=[
            "Security Engineers & SOC Analysts: Track perimeter health, evaluate intrusion distributions, and export tagged predictions.",
            "System & Network Administrators: Identify exposed services, review CVSS risk verdicts, and apply concrete hardening playbooks.",
            "Penetration Testers & Compliance Auditors: Conduct authorized audits with exportable JSON/CSV/Markdown compliance reports.",
            "Academic Evaluators & Researchers: Evaluate dual-engine defensive network architectures and ML classification benchmarks."
        ]
    )

    # ==================== SLIDE 9: ADVANTAGES ====================
    add_standard_slide(
        prs,
        title_text="Advantages",
        slide_number=9,
        bullet_points=[
            "Automated identification of network vulnerabilities and malicious traffic in a single pane of glass.",
            "Reduces manual administrative effort through automated CVSS rule-based risk scoring (0–100).",
            "Tailored support through actionable remediation guidance mapped to real-world exploit vectors.",
            "High predictive accuracy (98.30% Random Forest, 98.25% XGBoost) on NSL-KDD benchmark flows.",
            "Scalable solution for various educational tiers, enterprise intranets, and lab environments."
        ]
    )

    # ==================== SLIDE 10: LIMITATIONS ====================
    add_standard_slide(
        prs,
        title_text="Limitations",
        slide_number=10,
        bullet_points=[
            "Predictive accuracy depends heavily on network flow dataset quality and consistent attribute formatting.",
            "May struggle with zero-day external evasion techniques not captured in training data.",
            "Serverless cloud hosting environments restrict raw outbound TCP sockets (mitigated by Hosted Demo Mode).",
            "Requires consistent telemetry input or flow captures from network taps and monitoring points."
        ]
    )

    # ==================== SLIDE 11: FUTURE SCOPE ====================
    add_standard_slide(
        prs,
        title_text="Future Scope",
        slide_number=11,
        bullet_points=[
            "Live packet sniffing integration using eBPF or Scapy promiscuous hardware captures.",
            "Integration with existing Enterprise SIEM platforms (Splunk, Elastic SIEM, Syslog).",
            "Deep learning models (e.g., Unsupervised LSTM Autoencoders) for more nuanced behavioral and zero-day anomaly analysis.",
            "Automated firewall rule injection (active IPS) for immediate mitigation of detected attacking IPs."
        ]
    )

    # ==================== SLIDE 12: CONCLUSION ====================
    add_standard_slide(
        prs,
        title_text="Conclusion",
        slide_number=12,
        bullet_points=[
            "Proactive network perimeter defense and traffic monitoring are essential for modern digital infrastructure.",
            "NetGuard-IDS provides an automated, AI-driven environment for risk detection and intrusion prevention.",
            "Combines unprivileged socket auditing with 98.30% accurate ML classification and actionable CVSS hardening playbooks.",
            "Helps create a more supportive, resilient, and secure institutional network ecosystem."
        ]
    )

    # ==================== SLIDE 13: THANK YOU ====================
    s13 = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background_white(s13)

    t_box13 = s13.shapes.add_textbox(Inches(1.0), Inches(2.6), Inches(8.0), Inches(2.5))
    tf13 = t_box13.text_frame
    
    p_ty = tf13.paragraphs[0]
    p_ty.text = "Thank You!"
    p_ty.font.size = Pt(44)
    p_ty.font.bold = True
    p_ty.font.color.rgb = COLOR_ACCENT
    p_ty.alignment = PP_ALIGN.CENTER

    p_qa = tf13.add_paragraph()
    p_qa.text = "\nQuestions & Discussions are Welcome"
    p_qa.font.size = Pt(18)
    p_qa.font.color.rgb = COLOR_TITLE
    p_qa.alignment = PP_ALIGN.CENTER

    prs.save(OUTPUT_PPTX)
    print(f"Generated EduSense-format college presentation at: {OUTPUT_PPTX}")

if __name__ == "__main__":
    generate_edusense_style_main_deck()
