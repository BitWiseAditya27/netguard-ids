import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
ax.set_xlim(0, 12)
ax.set_ylim(0, 7)
ax.axis('off')
fig.patch.set_facecolor('#0E1117')
ax.set_facecolor('#0E1117')

def box(x, y, w, h, title, sub, col='#1A1D24', border='#00D4B2'):
    r = patches.FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.15', facecolor=col, edgecolor=border, linewidth=2)
    ax.add_patch(r)
    ax.text(x + w/2, y + h*0.62, title, ha='center', va='center', color='white', weight='bold', fontsize=10)
    ax.text(x + w/2, y + h*0.28, sub, ha='center', va='center', color='#B0B8C4', fontsize=7.5)

# Workflow Stage 1: Ingestion & Input
box(0.5, 4.5, 2.4, 1.8, '1. User Input & Targets', '• Host/IP (127.0.0.1, RFC1918)\n• Scan Mode Selection\n• Flow CSV Upload\n• Mandatory Consent Check')

# Workflow Stage 2: Ethical Guard & Dispatcher
box(3.4, 4.5, 2.4, 1.8, '2. Ethical Validator', '• RFC 1918 Subnet Check\n• Public IP Blocking\n• scanme.nmap.org Whitelist\n• Rate & Thread Limit Caps')

# Workflow Stage 3A: Port Scanning
box(6.3, 4.5, 2.4, 1.8, '3A. Port Scanner Engine', '• Non-root Socket Connects\n• ThreadPoolExecutor\n• Banner Grabbing\n• Service Identification')

# Workflow Stage 3B: ML Traffic Classifier
box(6.3, 1.5, 2.4, 1.8, '3B. ML Classifier Engine', '• 41 NSL-KDD Features\n• Scaler & OneHot Pipeline\n• Random Forest & XGBoost\n• DoS / Probe / R2L / U2R')

# Workflow Stage 4A: CVSS Risk Engine
box(9.2, 4.5, 2.4, 1.8, '4A. CVSS Risk Engine', '• Port Threat Mapping\n• Banner Escalation (SMBv1)\n• Score Aggregator (0-100)\n• Risk Verdict (Low-Critical)')

# Workflow Stage 5: Output & Reporting
box(9.2, 1.5, 2.4, 1.8, '5. Reporting & UI Layer', '• Interactive Streamlit GUI\n• Plotly Gauges & Charts\n• SQLite Audit Logs\n• JSON / CSV / MD Export')

# Arrows
arr = dict(facecolor='#00D4B2', edgecolor='none', width=1.8, headwidth=7)
ax.annotate('', xy=(3.4, 5.4), xytext=(2.9, 5.4), arrowprops=arr)
ax.annotate('', xy=(6.3, 5.4), xytext=(5.8, 5.4), arrowprops=arr)
ax.annotate('', xy=(9.2, 5.4), xytext=(8.7, 5.4), arrowprops=arr)
ax.annotate('', xy=(6.3, 2.4), xytext=(4.6, 4.5), arrowprops=arr)
ax.annotate('', xy=(9.2, 2.4), xytext=(8.7, 2.4), arrowprops=arr)
ax.annotate('', xy=(10.4, 3.3), xytext=(10.4, 4.5), arrowprops=arr)

plt.title('NetGuard-IDS End-to-End Architectural Workflow', color='#00D4B2', fontsize=15, weight='bold', pad=12)
plt.savefig('C:/Users/py056/.gemini/antigravity/scratch/netguard-ids/docs/workflow_diagram.png', bbox_inches='tight', facecolor=fig.get_facecolor())
print('Generated workflow_diagram.png')
