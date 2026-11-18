from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import textwrap, os

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)

DARK    = RGBColor(0x26, 0x46, 0x53)   # brand teal-dark
TEAL    = RGBColor(0x2a, 0x9d, 0x8f)
ORANGE  = RGBColor(0xe9, 0xa2, 0x3b)
RED     = RGBColor(0xe6, 0x39, 0x46)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
LGRAY   = RGBColor(0xF4, 0xF6, 0xFA)
INK     = RGBColor(0x1d, 0x24, 0x33)
MUTED   = RGBColor(0x6b, 0x72, 0x80)
GOLD    = RGBColor(0xFF, 0xD7, 0x00)

BLANK = prs.slide_layouts[6]

def add_rect(slide, l,t,w,h, fill, opacity=None):
    shp = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    shp.line.fill.background()
    shp.fill.solid(); shp.fill.fore_color.rgb = fill
    return shp

def add_txt(slide, text, l,t,w,h, size=18, bold=False, color=WHITE,
            align=PP_ALIGN.LEFT, wrap=True):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = wrap
    p  = tf.paragraphs[0]; p.alignment = align
    run = p.add_run(); run.text = text
    run.font.size = Pt(size); run.font.bold = bold; run.font.color.rgb = color
    return tb

def header_bar(slide, title, subtitle=""):
    add_rect(slide, 0,0, 13.33,1.4, DARK)
    add_txt(slide, title, 0.35,0.08, 12,0.65, size=28, bold=True, color=WHITE)
    if subtitle:
        add_txt(slide, subtitle, 0.35,0.75, 12,0.55, size=14, bold=False, color=RGBColor(0xBD,0xD9,0xDF))

def accent_line(slide, y=1.4):
    add_rect(slide, 0, y, 13.33, 0.06, TEAL)

def bullet_box(slide, items, l,t,w,h, size=13, title=None, bg=LGRAY, tc=INK):
    add_rect(slide, l,t,w,h, bg)
    if title:
        add_txt(slide, title, l+0.15, t+0.08, w-0.3, 0.38, size=13, bold=True, color=DARK)
        t2 = t+0.45
    else:
        t2 = t+0.15
    for i,item in enumerate(items):
        add_txt(slide, f"▸  {item}", l+0.15, t2+i*0.35, w-0.3, 0.38, size=size, color=tc)

def code_box(slide, code_lines, l,t,w,h):
    add_rect(slide, l,t,w,h, RGBColor(0x1E,0x1E,0x2E))
    tb = slide.shapes.add_textbox(Inches(l+0.15), Inches(t+0.1), Inches(w-0.3), Inches(h-0.2))
    tf = tb.text_frame; tf.word_wrap = False
    for i,line in enumerate(code_lines):
        p = tf.add_paragraph() if i else tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run(); run.text = line
        run.font.size = Pt(10); run.font.color.rgb = RGBColor(0xCB,0xD5,0xE1)
        run.font.name = "Courier New"

def arrow(slide, x1,y1,x2,y2, color=TEAL, width_pt=2):
    from pptx.util import Pt as UPt
    import pptx.oxml.ns as ns
    from lxml import etree
    connector = slide.shapes.add_connector(1,
        Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    connector.line.color.rgb = color
    connector.line.width = UPt(width_pt)

# ── helper: rounded box label
def label_box(slide, text, l,t,w,h, bg=TEAL, fc=WHITE, size=12, bold=True):
    add_rect(slide, l,t,w,h, bg)
    add_txt(slide, text, l,t,w,h, size=size, bold=bold, color=fc, align=PP_ALIGN.CENTER)

# =============================================================================
# SLIDE 1 — TITLE
# =============================================================================
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0,0,13.33,7.5, DARK)
add_rect(sl, 0,0,13.33,0.12, GOLD)
add_rect(sl, 0,7.38,13.33,0.12, GOLD)
# decorative circles
for cx,cy,r,col in [(11.5,1.2,1.1,TEAL),(1.2,6.2,0.7,ORANGE),(12.5,6.5,0.5,RED)]:
    shp = sl.shapes.add_shape(9, Inches(cx-r),Inches(cy-r),Inches(r*2),Inches(r*2))
    shp.fill.solid(); shp.fill.fore_color.rgb = col
    shp.line.fill.background()
    shp.fill.fore_color.theme_color  # just access to avoid warnings

add_txt(sl,"Smart India Hackathon 2025",0.8,0.5,11.73,0.6,size=15,color=GOLD,bold=True,align=PP_ALIGN.CENTER)
add_txt(sl,"🛡️  PaySafe India",0.5,1.4,12.33,1.2,size=46,bold=True,color=WHITE,align=PP_ALIGN.CENTER)
add_txt(sl,"AI-Powered UPI Transaction Fraud Detection System",0.5,2.7,12.33,0.7,size=22,bold=False,color=RGBColor(0xBD,0xD9,0xDF),align=PP_ALIGN.CENTER)
add_rect(sl,4.5,3.55,4.33,0.06,TEAL)
add_txt(sl,"Real-time fraud scoring · 96.9% ROC-AUC · Flask Web App",0.5,3.75,12.33,0.55,size=14,color=MUTED,align=PP_ALIGN.CENTER)
add_txt(sl,"Team: PaySafe India  |  Domain: FinTech / Cybersecurity  |  Technology: Machine Learning + Flask",0.5,6.6,12.33,0.55,size=11,color=MUTED,align=PP_ALIGN.CENTER)

# =============================================================================
# SLIDE 2 — PROBLEM STATEMENT
# =============================================================================
sl = prs.slides.add_slide(BLANK)
add_rect(sl,0,0,13.33,7.5,LGRAY)
header_bar(sl,"Problem Statement","India's UPI ecosystem processes 13+ billion transactions/month — fraud is surging")
accent_line(sl)

stats = [("₹2,537 Cr","UPI Fraud Losses\n(FY 2023-24)"),("95,000+","Fraud Cases\nReported Annually"),("0.19–17%","Fraud Rate Varies\nAcross Datasets"),("< 2 sec","Window to Flag\nSuspicious Payment")]
for i,(val,lbl) in enumerate(stats):
    x = 0.4 + i*3.2
    add_rect(sl, x,1.6,2.9,1.6, DARK)
    add_txt(sl, val, x,1.7,2.9,0.8, size=26,bold=True,color=GOLD,align=PP_ALIGN.CENTER)
    add_txt(sl, lbl, x,2.45,2.9,0.7, size=11,color=RGBColor(0xBD,0xD9,0xDF),align=PP_ALIGN.CENTER)

add_txt(sl,"Core Challenges",0.4,3.45,12.5,0.4,size=15,bold=True,color=DARK)
challenges=[
    "Traditional rule-based systems miss novel, evolving fraud patterns",
    "Severe class imbalance — legitimate transactions outnumber fraud 5:1",
    "Real-time scoring required: decision must happen before payment clears",
    "No single feature flags fraud — requires holistic behavioural analysis",
    "Leaky synthetic datasets give false confidence — rigorous audit is essential",
]
for i,c in enumerate(challenges):
    add_rect(sl,0.4,3.9+i*0.56,12.5,0.5,WHITE)
    add_txt(sl,f"{'🔴' if i<2 else '🟠'}  {c}",0.55,3.92+i*0.56,12.2,0.44,size=12.5,color=INK)

# =============================================================================
# SLIDE 3 — PROJECT INTRODUCTION
# =============================================================================
sl = prs.slides.add_slide(BLANK)
add_rect(sl,0,0,13.33,7.5,LGRAY)
header_bar(sl,"Project Introduction — PaySafe India","End-to-end ML pipeline: data → model → live web application")
accent_line(sl)

add_rect(sl,0.4,1.6,8.2,5.6,WHITE)
add_txt(sl,"What is PaySafe India?",0.55,1.65,8,0.45,size=15,bold=True,color=DARK)
intro_pts=[
    "PaySafe India is a full-stack AI fraud detection system for UPI payments",
    "Trained on 26,393 real-pattern synthetic transactions (17.2% fraud)",
    "Implements 5 ML algorithms: K-Means, LR, Decision Tree, Random Forest, SVM",
    "Deployed as a Flask web app with real-time fraud probability scoring",
    "Features counterfactual driver explanations — tells WHY a payment is risky",
    "Covers complete ML workflow: EDA → Encoding → Preprocessing → Modelling",
    "REST API endpoint (/api/predict) for integration with banking systems",
    "Achieves 98.3% Precision and 96.9% ROC-AUC on held-out test set",
]
for i,pt in enumerate(intro_pts):
    add_txt(sl,f"✅  {pt}",0.55,2.2+i*0.52,7.9,0.48,size=12,color=INK)

add_rect(sl,8.85,1.6,4.1,1.2,DARK)
add_txt(sl,"Test Set Performance",8.95,1.65,3.9,0.4,size=12,bold=True,color=WHITE)
add_txt(sl,"Random Forest (Deployed)",8.95,2.05,3.9,0.35,size=11,color=TEAL)
add_txt(sl,"ROC-AUC",8.95,2.75,1.8,0.35,size=11,bold=True,color=WHITE)
add_txt(sl,"96.9%",10.75,2.75,2.1,0.35,size=16,bold=True,color=GOLD,align=PP_ALIGN.RIGHT)
add_txt(sl,"Precision",8.95,3.15,1.8,0.35,size=11,bold=True,color=WHITE)
add_txt(sl,"98.3%",10.75,3.15,2.1,0.35,size=16,bold=True,color=TEAL,align=PP_ALIGN.RIGHT)
add_txt(sl,"Recall",8.95,3.55,1.8,0.35,size=11,bold=True,color=WHITE)
add_txt(sl,"87.9%",10.75,3.55,2.1,0.35,size=16,bold=True,color=ORANGE,align=PP_ALIGN.RIGHT)
add_txt(sl,"F1-Score",8.95,3.95,1.8,0.35,size=11,bold=True,color=WHITE)
add_txt(sl,"92.8%",10.75,3.95,2.1,0.35,size=16,bold=True,color=RGBColor(0xA8,0xE6,0xCF),align=PP_ALIGN.RIGHT)

add_rect(sl,8.85,4.5,4.1,2.5,RGBColor(0x1E,0x2D,0x3A))
add_txt(sl,"Tech Stack",9.0,4.55,3.9,0.4,size=12,bold=True,color=TEAL)
for i,(lbl,val) in enumerate([("Language","Python 3.12"),("ML Lib","scikit-learn 1.8"),("Web","Flask 3.1"),("Data","Pandas 3.0 / NumPy"),("Deploy","joblib + Jinja2")]):
    add_txt(sl,f"{lbl}:",9.0,5.0+i*0.38,1.4,0.35,size=10.5,bold=True,color=MUTED)
    add_txt(sl,val,10.4,5.0+i*0.38,2.4,0.35,size=10.5,color=WHITE)

# =============================================================================
# SLIDE 4 — OBJECTIVES
# =============================================================================
sl = prs.slides.add_slide(BLANK)
add_rect(sl,0,0,13.33,7.5,LGRAY)
header_bar(sl,"Project Objectives","Six measurable goals driving every design decision")
accent_line(sl)

objs=[
    ("🎯","Detect UPI Fraud in Real Time","Score any transaction within milliseconds using a pre-trained pipeline served via Flask REST API"),
    ("📊","Rigorous Dataset Evaluation","Compare all 4 available UPI datasets using ROC-AUC baselines; select only those with genuine predictive signal"),
    ("🔍","Leakage-Free Feature Engineering","Audit every feature for data leakage; build a compact 14+2 behavioural feature set that generalises to unseen data"),
    ("🤖","Multi-Algorithm Benchmarking","Train and cross-validate 5 algorithms (K-Means, LR, DT, RF, SVM) and select the best by CV F1 — not test score"),
    ("📈","Fraud-Aware Evaluation Metrics","Report Precision, Recall, F1, ROC-AUC and PR-AUC; never quote accuracy alone on an imbalanced dataset"),
    ("🌐","Explainable & Deployable System","Provide counterfactual driver explanations per prediction; expose /api/predict and /health endpoints"),
]
for i,(icon,title,desc) in enumerate(objs):
    r,c = divmod(i,2)
    x = 0.4 + c*6.47
    y = 1.65 + r*1.8
    add_rect(sl,x,y,6.1,1.65,WHITE)
    add_rect(sl,x,y,0.55,1.65,DARK)
    add_txt(sl,icon,x,y+0.55,0.55,0.55,size=18,align=PP_ALIGN.CENTER)
    add_txt(sl,title,x+0.65,y+0.08,5.3,0.45,size=13,bold=True,color=DARK)
    add_txt(sl,desc,x+0.65,y+0.55,5.3,1.0,size=10.5,color=MUTED)

# =============================================================================
# SLIDE 5 — SCOPE & BENEFITS
# =============================================================================
sl = prs.slides.add_slide(BLANK)
add_rect(sl,0,0,13.33,7.5,LGRAY)
header_bar(sl,"Project Scope & Benefits","Where PaySafe India applies — and the value it delivers")
accent_line(sl)

add_rect(sl,0.4,1.6,5.9,5.6,WHITE)
add_txt(sl,"📌  Scope of Implementation",0.55,1.68,5.7,0.45,size=14,bold=True,color=DARK)
scope_items=[
    "UPI-based payment platforms (BHIM, PhonePe, GPay, Paytm)",
    "Banking fraud monitoring dashboards",
    "Real-time transaction gateway integration via REST API",
    "Regulatory reporting systems (RBI / NPCI)",
    "Synthetic fraud simulation and stress testing",
    "Academic and research use-cases in FinTech AI",
    "Any platform using behavioural transaction signals",
]
for i,s in enumerate(scope_items):
    add_txt(sl,f"→  {s}",0.55,2.22+i*0.56,5.7,0.5,size=11.5,color=INK)

add_rect(sl,6.55,1.6,6.4,5.6,WHITE)
add_txt(sl,"🏆  Key Benefits",6.7,1.68,6.2,0.45,size=14,bold=True,color=DARK)
benefits=[
    ("For Banks","Reduce fraud losses; automated first-pass screening before human review"),
    ("For Customers","Fewer false declines; only genuinely risky payments are blocked"),
    ("For Regulators","Audit-ready model card; explainable predictions with driver analysis"),
    ("For Developers","REST API; open pipeline; extend with new features without retraining"),
    ("For Society","Safer digital payments; builds trust in India's UPI infrastructure"),
]
for i,(who,what) in enumerate(benefits):
    add_rect(sl,6.6,2.22+i*0.94,6.2,0.85,LGRAY)
    add_txt(sl,who,6.75,2.27+i*0.94,2.0,0.38,size=12,bold=True,color=DARK)
    add_txt(sl,what,6.75,2.6+i*0.94,5.95,0.42,size=10.5,color=MUTED)

# =============================================================================
# SLIDE 6 — DATASETS
# =============================================================================
sl = prs.slides.add_slide(BLANK)
add_rect(sl,0,0,13.33,7.5,LGRAY)
header_bar(sl,"Datasets Used","Four UPI datasets evaluated — one selected for modelling via baseline AUC audit")
accent_line(sl)

hdrs=["Dataset","Rows","Fraud %","ROC-AUC","Role"]
widths=[3.5,1.4,1.2,1.5,5.33]
xs=[0.4,3.9,5.3,6.5,8.0]
for j,(h,w,x) in enumerate(zip(hdrs,widths,xs)):
    add_rect(sl,x,1.62,w-0.05,0.5,DARK)
    add_txt(sl,h,x,1.62,w-0.05,0.5,size=12,bold=True,color=WHITE,align=PP_ALIGN.CENTER)

rows=[
    ("fraud_dataset.csv","26,393","17.2%","0.969","✅ PRIMARY — K-Means, LR, DT, RF, SVM, Flask",TEAL),
    ("upi_transactions_2024.csv","250,000","0.19%","0.550","📊 EDA / Visualization / State merge only",ORANGE),
    ("upi_fraud_india_dataset.csv","1,000","100%","N/A","📖 Context only — all rows are fraud",MUTED),
    ("upi_data_new1.xlsx","500,000","15.9%","0.560","❌ REJECTED — anonymised codes, no signal",RED),
]
for i,(d,r,f,a,role,col) in enumerate(rows):
    bg = WHITE if i%2==0 else LGRAY
    vals=[d,r,f,a,role]
    for j,(v,w,x) in enumerate(zip(vals,widths,xs)):
        add_rect(sl,x,2.2+i*0.9,w-0.05,0.82,bg)
        sz=10.5 if j==0 else 11
        add_txt(sl,v,x+0.05,2.25+i*0.9,w-0.1,0.72,size=sz,color=INK if j!=4 else col)
    add_rect(sl,xs[0],2.2+i*0.9,0.06,0.82,col)

add_rect(sl,0.4,5.9,12.5,0.65,RGBColor(0xE8,0xF8,0xF5))
add_txt(sl,"💡  Key Insight: AUC=0.969 for fraud_dataset.csv vs AUC≈0.55 for others. Only features that carry genuine predictive signal were kept after leakage audit.",0.55,5.95,12.2,0.55,size=11.5,color=DARK)

# =============================================================================
# SLIDE 7 — SYSTEM ARCHITECTURE FLOW DIAGRAM
# =============================================================================
sl = prs.slides.add_slide(BLANK)
add_rect(sl,0,0,13.33,7.5,LGRAY)
header_bar(sl,"System Architecture","End-to-end flow from raw data to live fraud score")
accent_line(sl)

# Flow boxes
boxes=[
    (0.3, 2.1, 1.9, 1.1, "📂 Raw Data\nCSV / XLSX", DARK),
    (2.5, 2.1, 1.9, 1.1, "🔍 EDA &\nCleaning", DARK),
    (4.7, 2.1, 1.9, 1.1, "⚗️ Feature\nEngineering", DARK),
    (6.9, 2.1, 1.9, 1.1, "🤖 Model\nTraining", DARK),
    (9.1, 2.1, 1.9, 1.1, "💾 Save\nPipeline", DARK),
    (11.2,2.1, 1.9, 1.1, "🌐 Flask\nWeb App", TEAL),
]
for l,t,w,h,txt,col in boxes:
    add_rect(sl,l,t,w,h,col)
    add_txt(sl,txt,l,t,w,h,size=11,bold=True,color=WHITE,align=PP_ALIGN.CENTER)

# arrows between boxes
for i in range(len(boxes)-1):
    x1 = boxes[i][0]+boxes[i][2]
    x2 = boxes[i+1][0]
    y  = boxes[i][1]+boxes[i][3]/2
    add_rect(sl, x1, y-0.04, x2-x1, 0.08, TEAL)
    # arrowhead triangle
    arw = sl.shapes.add_shape(5, Inches(x2-0.18), Inches(y-0.14), Inches(0.22), Inches(0.28))
    arw.fill.solid(); arw.fill.fore_color.rgb = TEAL
    arw.line.fill.background()

# Sub-labels below
sub_labels=["Scripts 00-02","Scripts 02-04","Script 04","Scripts 05-06","Script 06","app/app.py"]
for i,(l,t,w,h,_,_) in enumerate(boxes):
    add_txt(sl,sub_labels[i],l,t+h+0.05,w,0.35,size=9,color=MUTED,align=PP_ALIGN.CENTER)

# Web App detail box
add_rect(sl,0.3,3.8,12.7,3.3,WHITE)
add_txt(sl,"🌐  Web Application Flow (PaySafe India — http://127.0.0.1:5000)",0.5,3.85,12.3,0.4,size=13,bold=True,color=DARK)

app_boxes=[
    (0.5,4.35,2.2,0.85,"User Opens\nBrowser","👤",DARK),
    (3.0,4.35,2.2,0.85,"Fills\nTransaction\nForm","📝",TEAL),
    (5.5,4.35,2.2,0.85,"POST /\nFlask Route","⚙️",DARK),
    (8.0,4.35,2.2,0.85,"Pipeline\nPredict\nProba","🤖",DARK),
    (10.5,4.35,2.2,0.85,"Result +\nDrivers\nDisplayed","📊",TEAL),
]
for l,t,w,h,txt,icon,col in app_boxes:
    add_rect(sl,l,t,w,h,col)
    add_txt(sl,f"{icon}\n{txt}",l,t,w,h,size=10,bold=True,color=WHITE,align=PP_ALIGN.CENTER)

for i in range(len(app_boxes)-1):
    x1=app_boxes[i][0]+app_boxes[i][2]
    x2=app_boxes[i+1][0]
    y =app_boxes[i][1]+app_boxes[i][3]/2
    add_rect(sl,x1,y-0.04,x2-x1,0.08,ORANGE)
    arw=sl.shapes.add_shape(5,Inches(x2-0.18),Inches(y-0.14),Inches(0.22),Inches(0.28))
    arw.fill.solid(); arw.fill.fore_color.rgb=ORANGE; arw.line.fill.background()

add_txt(sl,"API: POST /api/predict  →  JSON response  |  GET /health  →  model status & metrics",0.5,5.38,12.3,0.35,size=10,color=MUTED)
add_txt(sl,"Preprocess (impute+scale+OHE) → predict_proba → threshold=0.5 → counterfactual driver analysis",0.5,5.75,12.3,0.35,size=10,color=MUTED)
add_txt(sl,"Session fields: amount, time_of_day, auth_attempts, device_flag, IP_flag, pin_method, velocity…",0.5,6.1,12.3,0.35,size=10,color=MUTED)

# =============================================================================
# SLIDE 8 — ALGORITHM 1: K-MEANS
# =============================================================================
sl = prs.slides.add_slide(BLANK)
add_rect(sl,0,0,13.33,7.5,LGRAY)
header_bar(sl,"Algorithm 1 — K-Means Clustering (Unsupervised)","Detecting suspicious clusters WITHOUT using fraud labels during training")
accent_line(sl)

add_rect(sl,0.4,1.62,6.0,5.55,WHITE)
add_txt(sl,"Mathematical Foundation",0.55,1.68,5.8,0.42,size=14,bold=True,color=DARK)
math_lines=[
    "Objective: Minimise Within-Cluster Sum of Squares (WCSS)",
    "",
    "  J = Σ_k Σ_{x∈Cₖ} ‖x − μₖ‖²",
    "",
    "  where μₖ = (1/|Cₖ|) Σ_{x∈Cₖ} x  (centroid of cluster k)",
    "",
    "Algorithm (Lloyd's):",
    "  1. Initialise k centroids (k-means++)",
    "  2. Assign: cᵢ = argmin_k ‖xᵢ − μₖ‖²",
    "  3. Update: μₖ = mean of all points in cluster k",
    "  4. Repeat 2-3 until centroids stop moving",
    "",
    "Silhouette Score: s(i) = (b(i)−a(i)) / max(a(i),b(i))",
    "  a(i) = mean intra-cluster distance",
    "  b(i) = mean nearest-cluster distance",
    "  s ∈ [−1, 1]; higher = better separation",
    "",
    "Anomaly Score = min_k ‖x − μₖ‖  (distance to nearest centroid)",
]
for i,ln in enumerate(math_lines):
    add_txt(sl,ln,0.55,2.18+i*0.26,5.8,0.28,size=10,color=INK if not ln.startswith("  J") and not ln.startswith("  where") and not ln.startswith("  s(") else DARK,bold=ln.startswith("  J") or ln.startswith("  where"))

add_rect(sl,6.65,1.62,6.3,5.55,WHITE)
add_txt(sl,"Results & Insights",6.8,1.68,6.1,0.42,size=14,bold=True,color=DARK)
res_items=[
    "Dataset: 26,393 transactions, 14 scaled numeric features",
    "Optimal k=3 (highest silhouette score among k=2..8)",
    "Cluster with 100% fraud rate identified (733 transactions)",
    "Top 10% anomaly scores → 99% of those are fraud",
    "PCA (2 components) explains ~62% of variance",
    "",
    "Cluster Profiles:",
    "  Fraud cluster: high auth_attempts, fast PIN,",
    "  elevated failed_count, unusual device/IP",
    "",
    "Key Caveat:",
    "  K-Means isolated ONE tight fraud pattern.",
    "  ~40% of fraud looks 'normal' — still needs",
    "  supervised learning to catch it.",
    "",
    "Script: 05_KMeans_Unsupervised.py",
]
for i,r in enumerate(res_items):
    clr = TEAL if r.startswith("  Fraud") or r.startswith("  K-Means") or r.startswith("  ~40") or r.startswith("  supervised") else (DARK if r.endswith(":") else INK)
    add_txt(sl,r,6.8,2.18+i*0.31,6.1,0.3,size=10.5,color=clr,bold=r.endswith(":") and not r.startswith(" "))

# =============================================================================
# SLIDE 9 — ALGORITHM 2: LOGISTIC REGRESSION
# =============================================================================
sl = prs.slides.add_slide(BLANK)
add_rect(sl,0,0,13.33,7.5,LGRAY)
header_bar(sl,"Algorithm 2 — Logistic Regression","Probabilistic linear classifier with balanced class weights")
accent_line(sl)

add_rect(sl,0.4,1.62,6.0,5.55,WHITE)
add_txt(sl,"Mathematical Foundation",0.55,1.68,5.8,0.42,size=14,bold=True,color=DARK)
lr_math=[
    "Sigmoid function:",
    "  P(y=1|x) = σ(z) = 1 / (1 + e^(−z))",
    "  z = β₀ + β₁x₁ + β₂x₂ + … + βₙxₙ",
    "",
    "Log-Odds (Logit):",
    "  log[P/(1−P)] = β₀ + β₁x₁ + … + βₙxₙ",
    "",
    "Cost Function (Binary Cross-Entropy):",
    "  L = −(1/m) Σ [yᵢ log(ŷᵢ) + (1−yᵢ)log(1−ŷᵢ)]",
    "",
    "Optimisation: L-BFGS (quasi-Newton method)",
    "  Updates β to minimise L iteratively",
    "",
    "Class Imbalance: class_weight='balanced'",
    "  wᵢ = n / (2 × nᵢ)",
    "  Fraud class gets higher loss weight",
    "",
    "Odds Ratio: OR = e^βⱼ",
    "  OR > 1 → feature raises fraud probability",
    "  OR < 1 → feature lowers fraud probability",
]
for i,ln in enumerate(lr_math):
    add_txt(sl,ln,0.55,2.15+i*0.26,5.8,0.28,size=10,color=INK)

add_rect(sl,6.65,1.62,6.3,5.55,WHITE)
add_txt(sl,"Performance & Insights",6.8,1.68,6.1,0.42,size=14,bold=True,color=DARK)
lr_res=[
    ("Precision","96.2%",TEAL),
    ("Recall","88.4%",TEAL),
    ("F1-Score","92.1%",TEAL),
    ("ROC-AUC","96.5%",TEAL),
    ("Missed Fraud (FN)","105 txns",RED),
    ("False Alarms (FP)","32 txns",ORANGE),
    ("CV F1 (5-fold)","0.918 ± 0.005",DARK),
]
for i,(lbl,val,col) in enumerate(lr_res):
    add_rect(sl,6.8,2.2+i*0.52,6.0,0.46,LGRAY if i%2==0 else WHITE)
    add_txt(sl,lbl,6.95,2.24+i*0.52,3.5,0.38,size=12,color=INK)
    add_txt(sl,val,10.45,2.24+i*0.52,2.2,0.38,size=13,bold=True,color=col,align=PP_ALIGN.RIGHT)

add_txt(sl,"Top Fraud Drivers (Odds Ratios):",6.8,5.88,6.0,0.38,size=12,bold=True,color=DARK)
top_drivers=["auth_attempts (OR≈4.2)","failed_transaction_count (OR≈3.8)","unusual_device_flag (OR≈3.1)"]
for i,d in enumerate(top_drivers):
    add_txt(sl,f"  {i+1}. {d}",6.8,6.28+i*0.3,6.0,0.3,size=11,color=INK)

# =============================================================================
# SLIDE 10 — ALGORITHM 3: DECISION TREE
# =============================================================================
sl = prs.slides.add_slide(BLANK)
add_rect(sl,0,0,13.33,7.5,LGRAY)
header_bar(sl,"Algorithm 3 — Decision Tree Classifier","Interpretable if-else rules with Gini impurity splitting")
accent_line(sl)

add_rect(sl,0.4,1.62,6.0,5.55,WHITE)
add_txt(sl,"Mathematical Foundation",0.55,1.68,5.8,0.42,size=14,bold=True,color=DARK)
dt_math=[
    "Gini Impurity at node t:",
    "  Gini(t) = 1 − Σₖ p(k|t)²",
    "  p(k|t) = fraction of class k at node t",
    "  Pure node: Gini=0  |  Worst: Gini=0.5",
    "",
    "Information Gain:",
    "  IG = Gini(parent) − Σ (|Cⱼ|/|C|) × Gini(Cⱼ)",
    "  Split chosen to maximise IG",
    "",
    "Hyperparameters used:",
    "  max_depth = 6   (prevents overfitting)",
    "  min_samples_leaf = 20  (smooths boundaries)",
    "  class_weight = 'balanced'",
    "",
    "Prediction at leaf:",
    "  class = argmax_k count(k in leaf)",
    "",
    "Example top rule:",
    "  amount_zscore ≤ 1.2",
    "  └─ auth_attempts_zscore ≤ 0.8 → LEGIT",
    "  └─ auth_attempts_zscore > 0.8 → FRAUD",
]
for i,ln in enumerate(dt_math):
    add_txt(sl,ln,0.55,2.15+i*0.25,5.8,0.27,size=10,color=INK)

add_rect(sl,6.65,1.62,6.3,5.55,WHITE)
add_txt(sl,"Performance & Insights",6.8,1.68,6.1,0.42,size=14,bold=True,color=DARK)
dt_res=[
    ("Precision","92.6%",TEAL),
    ("Recall","89.1%",TEAL),
    ("F1-Score","90.8%",TEAL),
    ("ROC-AUC","96.2%",TEAL),
    ("Missed Fraud (FN)","99 txns",ORANGE),
    ("False Alarms (FP)","65 txns",RED),
    ("CV F1 (5-fold)","0.906 ± 0.006",DARK),
]
for i,(lbl,val,col) in enumerate(dt_res):
    add_rect(sl,6.8,2.2+i*0.52,6.0,0.46,LGRAY if i%2==0 else WHITE)
    add_txt(sl,lbl,6.95,2.24+i*0.52,3.5,0.38,size=12,color=INK)
    add_txt(sl,val,10.45,2.24+i*0.52,2.2,0.38,size=13,bold=True,color=col,align=PP_ALIGN.RIGHT)

add_txt(sl,"Advantages for Fraud Detection:",6.8,5.88,6.0,0.38,size=12,bold=True,color=DARK)
for i,adv in enumerate(["Human-readable if-else rules","No feature scaling required","Threshold behaviour transparent to regulators","Fastest inference time among all 4 classifiers"]):
    add_txt(sl,f"✓ {adv}",6.8,6.28+i*0.28,6.0,0.28,size=10.5,color=INK)

# =============================================================================
# SLIDE 11 — ALGORITHM 4: RANDOM FOREST (DEPLOYED)
# =============================================================================
sl = prs.slides.add_slide(BLANK)
add_rect(sl,0,0,13.33,7.5,LGRAY)
header_bar(sl,"Algorithm 4 — Random Forest  ★ DEPLOYED MODEL","Ensemble of 300 trees selected by highest 5-fold CV F1")
accent_line(sl)

add_rect(sl,0.4,1.62,6.0,5.55,WHITE)
add_txt(sl,"Mathematical Foundation",0.55,1.68,5.8,0.42,size=14,bold=True,color=DARK)
rf_math=[
    "Random Forest = Bagging + Feature Randomness",
    "",
    "For each tree t = 1…T (T=300):",
    "  1. Bootstrap sample Dₜ from training data",
    "     (sample n rows with replacement)",
    "  2. At each split: choose best feature from",
    "     random subset of m = √p features",
    "  3. Grow tree until min_samples_leaf=2",
    "",
    "Prediction (probability):",
    "  P(fraud|x) = (1/T) Σₜ pₜ(fraud|x)",
    "  Final: fraud if P(fraud|x) ≥ threshold",
    "",
    "Feature Importance (MDI):",
    "  Iⱼ = Σₜ Σ_nodes δ(feature=j) × ΔGini × nₙ/n",
    "  Higher = more splits use this feature",
    "",
    "Class Weight: balanced_subsample",
    "  Recomputed per bootstrap sample",
    "  Ensures minority fraud class is up-weighted",
]
for i,ln in enumerate(rf_math):
    add_txt(sl,ln,0.55,2.15+i*0.26,5.8,0.28,size=10,color=INK)

add_rect(sl,6.65,1.62,6.3,5.55,WHITE)
add_txt(sl,"Performance & Insights",6.8,1.68,6.1,0.42,size=14,bold=True,color=DARK)
rf_res=[
    ("Precision","98.3%",TEAL),
    ("Recall","87.9%",TEAL),
    ("F1-Score","92.8%",TEAL),
    ("ROC-AUC","96.9%",GOLD),
    ("Missed Fraud (FN)","110 txns",ORANGE),
    ("False Alarms (FP)","14 txns ⭐",TEAL),
    ("CV F1 (5-fold)","0.929 ± 0.004",DARK),
]
for i,(lbl,val,col) in enumerate(rf_res):
    add_rect(sl,6.8,2.2+i*0.52,6.0,0.46,RGBColor(0xE8,0xF8,0xF5) if i%2==0 else WHITE)
    add_txt(sl,lbl,6.95,2.24+i*0.52,3.5,0.38,size=12,color=INK)
    add_txt(sl,val,10.45,2.24+i*0.52,2.2,0.38,size=13,bold=True,color=col,align=PP_ALIGN.RIGHT)

add_txt(sl,"Why Random Forest was deployed:",6.8,5.88,6.0,0.38,size=12,bold=True,color=DARK)
for i,w in enumerate(["Highest CV F1 among probability-output models","Only 14 false alarms vs 32 (LR) and 65 (DT)","Supports predict_proba → threshold tuning","Robust to correlated features & outliers"]):
    add_txt(sl,f"⭐ {w}",6.8,6.26+i*0.28,6.0,0.28,size=10.5,color=INK)

# =============================================================================
# SLIDE 12 — ALGORITHM 5: SVM
# =============================================================================
sl = prs.slides.add_slide(BLANK)
add_rect(sl,0,0,13.33,7.5,LGRAY)
header_bar(sl,"Algorithm 5 — Support Vector Machine (RBF Kernel)","Maximum-margin classifier in high-dimensional feature space")
accent_line(sl)

add_rect(sl,0.4,1.62,6.0,5.55,WHITE)
add_txt(sl,"Mathematical Foundation",0.55,1.68,5.8,0.42,size=14,bold=True,color=DARK)
svm_math=[
    "Linear SVM — Find hyperplane w·x + b = 0 that",
    "maximises the margin 2/‖w‖:",
    "",
    "  min  ½‖w‖²",
    "  s.t. yᵢ(w·xᵢ + b) ≥ 1  ∀i",
    "",
    "Soft-Margin (C=1.0, allows misclassifications):",
    "  min ½‖w‖² + C Σᵢ ξᵢ",
    "  s.t. yᵢ(w·xᵢ+b) ≥ 1−ξᵢ,  ξᵢ ≥ 0",
    "",
    "RBF Kernel (handles non-linear boundaries):",
    "  K(xᵢ,xⱼ) = exp(−γ‖xᵢ−xⱼ‖²)",
    "  Maps data to infinite-dimensional space",
    "  γ controls how 'local' each support vector is",
    "",
    "Decision function:",
    "  f(x) = Σᵢ αᵢyᵢ K(xᵢ,x) + b",
    "  sign(f(x)) → class label",
    "",
    "Note: SVC without probability=True has no",
    "predict_proba → not selected for deployment",
]
for i,ln in enumerate(svm_math):
    add_txt(sl,ln,0.55,2.12+i*0.25,5.8,0.27,size=10,color=INK)

add_rect(sl,6.65,1.62,6.3,5.55,WHITE)
add_txt(sl,"Performance & Insights",6.8,1.68,6.1,0.42,size=14,bold=True,color=DARK)
svm_res=[
    ("Precision","99.6%",TEAL),
    ("Recall","86.6%",TEAL),
    ("F1-Score","92.6%",TEAL),
    ("ROC-AUC","96.6%",TEAL),
    ("Missed Fraud (FN)","122 txns",RED),
    ("False Alarms (FP)","3 txns ⭐",TEAL),
    ("CV F1 (5-fold)","0.923 ± 0.004",DARK),
]
for i,(lbl,val,col) in enumerate(svm_res):
    add_rect(sl,6.8,2.2+i*0.52,6.0,0.46,LGRAY if i%2==0 else WHITE)
    add_txt(sl,lbl,6.95,2.24+i*0.52,3.5,0.38,size=12,color=INK)
    add_txt(sl,val,10.45,2.24+i*0.52,2.2,0.38,size=13,bold=True,color=col,align=PP_ALIGN.RIGHT)

add_txt(sl,"Comparison Note:",6.8,5.88,6.0,0.38,size=12,bold=True,color=DARK)
for i,n in enumerate(["SVM has highest precision (99.6%) — fewest false alarms","But misses 122 fraud cases vs RF's 110","No predict_proba → cannot tune threshold easily","Still competitive; recommended if FP cost is very high"]):
    add_txt(sl,f"→ {n}",6.8,6.26+i*0.28,6.0,0.28,size=10.5,color=INK)

# =============================================================================
# SLIDE 13 — CODE SCREENSHOT: config.py + utils.py
# =============================================================================
sl = prs.slides.add_slide(BLANK)
add_rect(sl,0,0,13.33,7.5,LGRAY)
header_bar(sl,"Code — config.py & utils.py","Feature list, paths, preprocessing pipeline, data loaders")
accent_line(sl)

code_cfg=[
    "# config.py — single source of truth",
    "TARGET = 'is_fraud'",
    "RANDOM_STATE = 42",
    "TEST_SIZE = 0.20",
    "",
    "NUMERIC_FEATURES = [",
    "    'amount', 'transaction_amount_vs_sender_history',",
    "    'transaction_time_of_day', 'authentication_attempts',",
    "    'failed_transaction_count', 'transaction_velocity',",
    "    'session_duration', 'geographic_disparity',",
    "    'pin_entry_speed', 'otp_request_frequency',",
    "    'time_pressure_indicators','input_timing_consistency',",
    "    'unusual_device_flag', 'unusual_ip_flag',",
    "]",
    "CATEGORICAL_FEATURES = ['session_source','pin_entry_method']",
    "ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES",
]
code_box(sl, code_cfg, 0.3,1.62,6.5,3.3)

code_utils=[
    "# utils.py — shared preprocessing pipeline",
    "def build_preprocessor() -> ColumnTransformer:",
    "    numeric = Pipeline([",
    "        ('impute', SimpleImputer(strategy='median')),",
    "        ('scale',  StandardScaler())",
    "    ])",
    "    categorical = Pipeline([",
    "        ('impute', SimpleImputer(strategy='most_frequent')),",
    "        ('onehot', OneHotEncoder(handle_unknown='ignore',",
    "                                 sparse_output=False))",
    "    ])",
    "    return ColumnTransformer([",
    "        ('num', numeric, NUMERIC_FEATURES),",
    "        ('cat', categorical, CATEGORICAL_FEATURES),",
    "    ], sparse_threshold=0.0)",
    "",
    "def make_split(df):",
    "    X, y = df[ALL_FEATURES], df[TARGET]",
    "    return train_test_split(X, y, test_size=0.20,",
    "                            stratify=y, random_state=42)",
]
code_box(sl, code_utils, 6.98,1.62,6.0,3.3)

add_rect(sl,0.3,5.1,12.7,2.05,WHITE)
add_txt(sl,"Pipeline Design Rationale",0.5,5.15,12.3,0.4,size=13,bold=True,color=DARK)
for i,pt in enumerate([
    "Median imputation → robust to outliers in fraud data (amount, velocity are skewed)",
    "StandardScaler fitted on TRAIN only → prevents test-set information leaking into scaling parameters",
    "OneHotEncoder with handle_unknown='ignore' → safe for new categories seen at inference time",
    "ColumnTransformer applies different steps to numeric vs categorical columns in one atomic fit/transform",
]):
    add_txt(sl,f"{'→'} {pt}",0.5,5.6+i*0.36,12.3,0.33,size=11,color=INK)

# =============================================================================
# SLIDE 14 — CODE SCREENSHOT: 05_KMeans + 06_SupervisedModels
# =============================================================================
sl = prs.slides.add_slide(BLANK)
add_rect(sl,0,0,13.33,7.5,LGRAY)
header_bar(sl,"Code — K-Means & Supervised Model Training","Scripts 05 and 06: from raw data to trained pipeline")
accent_line(sl)

code_km=[
    "# 05_KMeans_Unsupervised.py",
    "X = StandardScaler().fit_transform(df[NUMERIC_FEATURES])",
    "y = df[TARGET].to_numpy()   # NOT given to K-Means",
    "",
    "# Elbow + Silhouette to find best k",
    "inertia = [KMeans(n_clusters=k, n_init=10,",
    "    random_state=42).fit(X).inertia_ for k in range(1,11)]",
    "sil = {k: silhouette_score(X, KMeans(n_clusters=k,",
    "    n_init=10,random_state=42).fit_predict(X),",
    "    sample_size=5000) for k in range(2,9)}",
    "best_k = max(sil, key=sil.get)",
    "",
    "km = KMeans(n_clusters=best_k,n_init=10,",
    "            random_state=42).fit(X)",
    "",
    "# Anomaly score = distance to nearest centroid",
    "dist = km.transform(X).min(axis=1)",
    "# top 10% flagged -> 99% fraud precision",
]
code_box(sl, code_km, 0.3,1.62,6.5,3.85)

code_sv=[
    "# 06_SupervisedModels.py",
    "models = {",
    "  'Logistic Regression': LogisticRegression(",
    "       max_iter=2000, class_weight='balanced'),",
    "  'Decision Tree': DecisionTreeClassifier(",
    "       max_depth=6, min_samples_leaf=20,",
    "       class_weight='balanced', random_state=42),",
    "  'Random Forest': RandomForestClassifier(",
    "       n_estimators=300, min_samples_leaf=2,",
    "       class_weight='balanced_subsample',",
    "       n_jobs=-1, random_state=42),",
    "  'SVM (RBF)': SVC(kernel='rbf', C=1.0,",
    "                   class_weight='balanced'),",
    "}",
    "pipes = {name: Pipeline([('prep',build_preprocessor()),",
    "                          ('model',m)])",
    "         for name,m in models.items()}",
    "cv = StratifiedKFold(n_splits=5,shuffle=True,",
    "                     random_state=42)",
]
code_box(sl, code_sv, 6.98,1.62,6.0,3.85)

add_rect(sl,0.3,5.65,12.7,1.5,WHITE)
add_txt(sl,"Model Selection Logic",0.5,5.7,12.3,0.38,size=13,bold=True,color=DARK)
add_txt(sl,"deployable = [n for n in models if hasattr(pipes[n],'predict_proba')]   # SVC excluded — no probabilities by default",0.5,6.1,12.3,0.32,size=10,color=RGBColor(0xCB,0xD5,0xE1))
add_txt(sl,"best = res.loc[deployable, 'cv_f1_mean'].idxmax()    # 'Random Forest' — selected by CROSS-VALIDATION, not test score",0.5,6.42,12.3,0.32,size=10,color=RGBColor(0xCB,0xD5,0xE1))
add_rect(sl,0.3,5.65,12.7,1.5,RGBColor(0x1E,0x1E,0x2E))
add_txt(sl,"deployable = [n for n in models if hasattr(pipes[n],'predict_proba')]",0.5,5.72,12.3,0.32,size=10.5,color=RGBColor(0xCB,0xD5,0xE1))
add_txt(sl,"best = res.loc[deployable, 'cv_f1_mean'].idxmax()   # → 'Random Forest'",0.5,6.04,12.3,0.32,size=10.5,color=TEAL)
add_txt(sl,"joblib.dump(final, MODELS / 'fraud_model.joblib')   # saves pipeline for Flask",0.5,6.36,12.3,0.32,size=10.5,color=RGBColor(0xCB,0xD5,0xE1))
add_txt(sl,"(MODELS/'model_meta.json').write_text(json.dumps(meta,indent=2))",0.5,6.68,12.3,0.32,size=10.5,color=RGBColor(0xCB,0xD5,0xE1))

# =============================================================================
# SLIDE 15 — CODE SCREENSHOT: Flask app.py
# =============================================================================
sl = prs.slides.add_slide(BLANK)
add_rect(sl,0,0,13.33,7.5,LGRAY)
header_bar(sl,"Code — Flask Web Application (app/app.py)","Live scoring endpoint, prediction logic, counterfactual drivers")
accent_line(sl)

code_app=[
    "# app/app.py — PaySafe India Flask server",
    "model = joblib.load(MODEL_PATH)   # pre-trained RF pipeline",
    "meta  = json.loads(META_PATH.read_text())",
    "NUMERIC, CATEGORICAL = meta['numeric_features'],",
    "                       meta['categorical_features']",
    "",
    "def score(values: dict) -> float:",
    "    row = pd.DataFrame([values])[NUMERIC+CATEGORICAL]",
    "    return float(model.predict_proba(row)[0, 1])",
    "",
    "def drivers(values, base_p, top=3):",
    "    out = []",
    "    for f in FIELDS:",
    "        alt = dict(values); alt[f['name']] = f['default']",
    "        drop = base_p - score(alt)",
    "        if drop >= 0.02:",
    "            out.append((f['label'], drop))",
    "    return sorted(out, key=lambda t: -t[1])[:top]",
    "",
    "@app.route('/', methods=['GET','POST'])",
    "def index():",
    "    if request.method == 'POST':",
    "        values = parse(request.form)",
    "        result = assess(values)   # {prob, band, drivers}",
    "    return render_template('index.html', result=result)",
    "",
    "@app.route('/api/predict', methods=['POST'])",
    "def api_predict():",
    "    return jsonify(assess(parse(request.get_json())))",
]
code_box(sl, code_app, 0.3,1.62,8.0,5.55)

add_rect(sl,8.6,1.62,4.4,5.55,WHITE)
add_txt(sl,"Web App Features",8.75,1.68,4.2,0.42,size=13,bold=True,color=DARK)
features=[
    "🌐 Real-time fraud scoring",
    "📊 Probability bar with threshold marker",
    "🔍 Counterfactual driver explanations",
    "⚡ Preset buttons (typical/suspicious)",
    "🔒 Input validation with friendly errors",
    "📡 REST API (/api/predict)",
    "💚 Health endpoint (/health)",
    "16 configurable transaction fields",
    "Main + Advanced field sections",
    "Fraud band: Low / Medium / High",
    "Model: Random Forest (300 trees)",
    "Threshold: 0.5 (configurable)",
    "Template: Jinja2 + Vanilla CSS",
    "Colour scheme matches brand palette",
]
for i,f in enumerate(features):
    add_txt(sl,f,8.75,2.18+i*0.36,4.1,0.33,size=11,color=INK if i>1 else DARK,bold=i<=1)

# =============================================================================
# SLIDE 16 — CODE: Leakage Audit + Preprocessing
# =============================================================================
sl = prs.slides.add_slide(BLANK)
add_rect(sl,0,0,13.33,7.5,LGRAY)
header_bar(sl,"Code — Leakage Audit & Feature Engineering (04_Encoding_Preprocessing.py)","Detecting and removing data leakage before model training")
accent_line(sl)

code_leak=[
    "# PART A — LEAKAGE AUDIT",
    "AUC_LIMIT = 0.94",
    "# Rule 1: single feature with AUC >= 0.94",
    "single_auc = {}",
    "for c in num_cols:",
    "    a = roc_auc_score(y, raw[c])",
    "    single_auc[c] = max(a, 1-a)",
    "rule1 = single_auc[single_auc>=0.94].index.tolist()",
    "",
    "# Rule 2: category that is 100% fraud",
    "#         AND covers >= 50% of all fraud rows",
    "for c in cat_cols:",
    "    g = raw.groupby(c)[TARGET].agg(n='size',fraud='sum')",
    "    g['share'] = g['fraud'] / total_fraud",
    "    for val,r in g.iterrows():",
    "        if r['fraud']==r['n'] and r['share']>=0.5:",
    "            rule2.append(c)",
    "",
    "# Rule 3: exact duplicate columns",
    "dup_mask = raw[num_cols].T.duplicated()",
    "rule3 = [c for c,d in zip(num_cols,dup_mask) if d]",
    "",
    "flagged = sorted(set(rule1)|set(rule2)|set(rule3))",
    "# Removed: receiver_account_age,",
    "# receiver_transaction_history,",
    "# merchant_category_code, handle_verification_status",
]
code_box(sl, code_leak, 0.3,1.62,6.5,5.55)

add_rect(sl,7.05,1.62,5.95,5.55,WHITE)
add_txt(sl,"Leakage Audit Results",7.2,1.68,5.75,0.42,size=13,bold=True,color=DARK)
add_txt(sl,"Accuracy Ladder (same RF, same split):",7.2,2.18,5.75,0.38,size=12,bold=True,color=DARK)

ladders=[
    ("L1: All columns (leaky)","AUC = 1.000",RED,"Memorises synthetic fraud recipe"),
    ("L2: Minus flagged cols","AUC = 1.000",ORANGE,"'Scenario markers' still present"),
    ("L3: Compact behavioural set","AUC = 0.965",TEAL,"Realistic & defensible — USED"),
]
for i,(lbl,auc,col,note) in enumerate(ladders):
    add_rect(sl,7.2,2.65+i*1.2,5.75,1.1,LGRAY)
    add_rect(sl,7.2,2.65+i*1.2,0.12,1.1,col)
    add_txt(sl,lbl,7.38,2.7+i*1.2,5.4,0.38,size=11.5,bold=True,color=INK)
    add_txt(sl,auc,7.38,3.05+i*1.2,2.5,0.35,size=14,bold=True,color=col)
    add_txt(sl,note,9.88,3.05+i*1.2,3.0,0.35,size=10,color=MUTED)

add_rect(sl,7.2,6.3,5.75,0.75,RGBColor(0xE8,0xF8,0xF5))
add_txt(sl,"💡 Columns removed: receiver_account_age, receiver_transaction_history, merchant_category_code, handle_verification_status, unusual_location_flag (duplicate)",7.3,6.35,5.6,0.65,size=9.5,color=DARK)

# =============================================================================
# SLIDE 17 — MODEL COMPARISON
# =============================================================================
sl = prs.slides.add_slide(BLANK)
add_rect(sl,0,0,13.33,7.5,LGRAY)
header_bar(sl,"Model Comparison — All Algorithms","Head-to-head results on 5,279 held-out test transactions")
accent_line(sl)

hdrs2=["Model","Precision","Recall","F1","ROC-AUC","CV F1","Missed Fraud","False Alarms","Status"]
ws=[2.2,1.2,1.1,1.0,1.2,1.15,1.5,1.5,1.43]
xs2=[0.3]
for w in ws[:-1]: xs2.append(xs2[-1]+w+0.0)

for j,(h,w,x) in enumerate(zip(hdrs2,ws,xs2)):
    add_rect(sl,x,1.62,w,0.5,DARK)
    add_txt(sl,h,x,1.62,w,0.5,size=10.5,bold=True,color=WHITE,align=PP_ALIGN.CENTER)

table=[
    ("Logistic Regression","96.2%","88.4%","92.1%","96.5%","0.918","105","32","Runner-up",TEAL),
    ("Decision Tree","92.6%","89.1%","90.8%","96.2%","0.906","99","65","Interpretable",ORANGE),
    ("Random Forest ⭐","98.3%","87.9%","92.8%","96.9%","0.929","110","14","DEPLOYED",TEAL),
    ("SVM (RBF)","99.6%","86.6%","92.6%","96.6%","0.923","122","3","High Prec.",MUTED),
]
for i,(model,prec,rec,f1,auc,cvf1,fn,fp,status,col) in enumerate(table):
    bg=RGBColor(0xE8,0xF8,0xF5) if i==2 else (WHITE if i%2==0 else LGRAY)
    vals=[model,prec,rec,f1,auc,cvf1,fn,fp,status]
    for j,(v,w,x) in enumerate(zip(vals,ws,xs2)):
        add_rect(sl,x,2.2+i*1.0,w,0.92,bg)
        bold=(i==2)
        fc=col if j==8 else (GOLD if i==2 and j in(1,2,3,4) else INK)
        add_txt(sl,v,x+0.04,2.24+i*1.0,w-0.08,0.84,size=11 if j!=0 else 10.5,bold=bold,color=fc,align=PP_ALIGN.CENTER if j!=0 else PP_ALIGN.LEFT)
    if i==2:
        add_rect(sl,xs2[0],2.2+i*1.0,0.08,0.92,GOLD)

add_rect(sl,0.3,6.28,12.7,0.85,RGBColor(0x1D,0x24,0x33))
add_txt(sl,"Key Takeaway: A dummy 'always-legitimate' baseline scores 82.8% accuracy with 0% recall (catches ZERO fraud). This is why accuracy is NEVER quoted alone for fraud detection. All four ML models dramatically outperform the baseline on recall and F1.",0.5,6.33,12.3,0.75,size=11,color=WHITE)

# =============================================================================
# SLIDE 18 — FUTURE SCOPE
# =============================================================================
sl = prs.slides.add_slide(BLANK)
add_rect(sl,0,0,13.33,7.5,LGRAY)
header_bar(sl,"Future Scope","Roadmap to transform PaySafe India into a production-grade system")
accent_line(sl)

future=[
    ("🧠","Deep Learning Models","Implement LSTM / Transformer-based models to capture sequential transaction patterns and temporal fraud behaviour across time windows"),
    ("📡","Real-Time Stream Processing","Integrate Apache Kafka + Spark Streaming for millisecond-level fraud scoring on live UPI transaction streams at scale"),
    ("🔐","Federated Learning","Train models across banks without sharing raw customer data — preserving privacy while improving detection accuracy collectively"),
    ("📊","Graph Neural Networks","Model account-to-account transaction networks; detect fraud rings and money-mule chains invisible to transaction-level models"),
    ("🤖","AutoML & Continuous Retraining","Automated pipeline to detect model drift, retrain on new fraud patterns, and deploy updated models with zero downtime"),
    ("📱","Mobile SDK Integration","Native Android/iOS SDK for banks to embed real-time PaySafe scoring directly into payment apps with <50ms latency"),
    ("🌐","Multilingual Explainability","Generate fraud explanations in Hindi, Tamil, Bengali — making the system accessible to fraud investigators across India"),
    ("🏛️","RBI Regulatory Compliance","Add model cards, bias audits, and explainability reports aligned with RBI's AI/ML guidelines for banking systems"),
]
for i,(icon,title,desc) in enumerate(future):
    r,c = divmod(i,2)
    x = 0.35 + c*6.52
    y = 1.65 + r*1.38
    add_rect(sl,x,y,6.15,1.28,WHITE)
    add_rect(sl,x,y,0.55,1.28,DARK if c==0 else TEAL)
    add_txt(sl,icon,x,y+0.3,0.55,0.55,size=18,align=PP_ALIGN.CENTER)
    add_txt(sl,title,x+0.62,y+0.08,5.35,0.42,size=12.5,bold=True,color=DARK)
    add_txt(sl,desc,x+0.62,y+0.5,5.35,0.72,size=10,color=MUTED)

# =============================================================================
# SLIDE 19 — THANK YOU
# =============================================================================
sl = prs.slides.add_slide(BLANK)
add_rect(sl,0,0,13.33,7.5,DARK)
add_rect(sl,0,0,13.33,0.12,GOLD)
add_rect(sl,0,7.38,13.33,0.12,GOLD)
for cx,cy,r,col in [(2.0,1.5,0.9,TEAL),(12.0,5.5,1.1,ORANGE),(1.5,6.0,0.5,RED),(11.5,1.5,0.6,RGBColor(0xFF,0xD7,0x00))]:
    shp=sl.shapes.add_shape(9,Inches(cx-r),Inches(cy-r),Inches(r*2),Inches(r*2))
    shp.fill.solid(); shp.fill.fore_color.rgb=col; shp.line.fill.background()

add_txt(sl,"🛡️",4.5,1.2,4.33,1.2,size=52,align=PP_ALIGN.CENTER)
add_txt(sl,"Thank You",0.5,2.35,12.33,1.0,size=48,bold=True,color=WHITE,align=PP_ALIGN.CENTER)
add_txt(sl,"PaySafe India — AI-Powered UPI Fraud Detection",0.5,3.4,12.33,0.65,size=20,color=RGBColor(0xBD,0xD9,0xDF),align=PP_ALIGN.CENTER)
add_rect(sl,4.5,4.15,4.33,0.06,TEAL)

metrics=[("96.9%","ROC-AUC"),("98.3%","Precision"),("92.8%","F1-Score"),("5 Algos","Benchmarked")]
for i,(val,lbl) in enumerate(metrics):
    x=1.2+i*2.8
    add_txt(sl,val,x,4.35,2.5,0.65,size=24,bold=True,color=GOLD,align=PP_ALIGN.CENTER)
    add_txt(sl,lbl,x,4.95,2.5,0.4,size=12,color=MUTED,align=PP_ALIGN.CENTER)

add_txt(sl,"Smart India Hackathon 2025  |  Domain: FinTech / Cybersecurity",0.5,5.6,12.33,0.45,size=13,color=MUTED,align=PP_ALIGN.CENTER)
add_txt(sl,"🌐 http://127.0.0.1:5000  |  📡 POST /api/predict  |  💚 GET /health",0.5,6.1,12.33,0.45,size=13,color=RGBColor(0xBD,0xD9,0xDF),align=PP_ALIGN.CENTER)

# =============================================================================
# SAVE
# =============================================================================
out = "/Users/avijitaditya/Desktop/PaySafe_India_SIH2025.pptx"
prs.save(out)
print(f"Saved: {out}")
print(f"Slides: {len(prs.slides)}")
