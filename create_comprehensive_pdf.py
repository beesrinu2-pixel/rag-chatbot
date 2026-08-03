from fpdf import FPDF

class DetailedPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, "ApexTech Global - Internal Engineering & Operations Manual", border=0, new_x="LMARGIN", new_y="NEXT", align="R")
        self.line(10, 18, 200, 18)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()} | Confidential - Internal Use Only", align="C")

pdf = DetailedPDF()
pdf.set_auto_page_break(auto=True, margin=15)

# PAGE 1: AI Engineering Standards & Release Protocols
pdf.add_page()
pdf.set_font("Helvetica", "B", 16)
pdf.set_text_color(30, 41, 59)
pdf.cell(0, 10, "1. Software Architecture & CI/CD Release Protocols", new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)

pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(51, 65, 85)
pdf.multi_cell(0, 7,
"ApexTech follows a cloud-native microservices architecture communicating via gRPC for high-throughput internal RPCs and REST OpenAPI v3 for external integrations.\n\n"
"Code Review & Quality Thresholds:\n"
"- Every Pull Request requires a minimum of 2 peer approvals before merging into the main branch.\n"
"- Automated CI/CD pipelines require a minimum unit test coverage threshold of 85% and zero high-severity SAST vulnerabilities.\n\n"
"Release Windows:\n"
"- Production deployments occur exclusively during designated Release Windows: Tuesdays and Thursdays between 10:00 AM and 2:00 PM UTC.\n"
"- Emergency hotfixes require explicit sign-off from the VP of Engineering and the On-Call Incident Commander."
)

# PAGE 2: Cloud Infrastructure, Security & Data Privacy
pdf.add_page()
pdf.set_font("Helvetica", "B", 16)
pdf.set_text_color(30, 41, 59)
pdf.cell(0, 10, "2. Cloud Infrastructure, Security & Compliance", new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)

pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(51, 65, 85)
pdf.multi_cell(0, 7,
"Data Encryption Standards:\n"
"- All customer data at rest must be encrypted using AES-256 bit encryption key standards via Cloud KMS.\n"
"- Data in transit is strictly enforced with TLS 1.3 protocol encryption.\n\n"
"Key Rotation & Access Governance:\n"
"- Master encryption keys in Cloud KMS are automatically rotated every 90 days.\n"
"- Production environment access is granted strictly via Zero-Trust Just-In-Time (JIT) access approval lasting a maximum of 4 hours per session.\n\n"
"Data Retention & Compliance:\n"
"- ApexTech is certified SOC 2 Type II, ISO 27001, and GDPR compliant.\n"
"- Inactive user logs and telemetry data are automatically purged after 365 days of inactivity."
)

# PAGE 3: Machine Learning & RAG Vector System Specifications
pdf.add_page()
pdf.set_font("Helvetica", "B", 16)
pdf.set_text_color(30, 41, 59)
pdf.cell(0, 10, "3. Machine Learning & RAG Search Architecture", new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)

pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(51, 65, 85)
pdf.multi_cell(0, 7,
"Retrieval-Augmented Generation (RAG) Architecture:\n"
"- Text Chunking Strategy: Document parsing utilizes a recursive character splitter with a target chunk size of 500 tokens and a 100-token overlap.\n"
"- Embedding Model: Dense vector representations are computed using the SentenceTransformers 'all-MiniLM-L6-v2' model with a 384-dimensional vector space.\n"
"- Distance Metric: Vector similarity searches utilize Cosine Similarity distance metrics within ChromaDB vector stores.\n\n"
"LLM Fallback & Performance Targets:\n"
"- Primary LLM: Google Gemini 1.5 Flash (optimized for low-latency generation).\n"
"- Secondary Fallback: Google Gemini 1.5 Pro (triggered if context length exceeds 32k tokens).\n"
"- Latency Target: Vector retrieval must complete within < 120ms, and total end-to-end user query response time must remain under 1.8 seconds."
)

# PAGE 4: Benefits, Compensation & Sabbatical Policies
pdf.add_page()
pdf.set_font("Helvetica", "B", 16)
pdf.set_text_color(30, 41, 59)
pdf.cell(0, 10, "4. Employee Compensation, Wellness & Perks", new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)

pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(51, 65, 85)
pdf.multi_cell(0, 7,
"Health & Wellness Benefits:\n"
"- Health Insurance: 100% premium coverage for full-time employees and 80% coverage for eligible family dependents.\n"
"- Annual Wellness Stipend: Every employee receives a $1,500 annual flexible stipend usable for gym memberships, sports gear, or mental health applications.\n\n"
"Sabbatical & Long Service Rewards:\n"
"- Paid Sabbatical: Employees completing 4 consecutive years of full-time service are eligible for a 4-week fully paid sabbatical leave.\n"
"- Relocation Assistance: Up to $8,000 relocation reimbursement is offered for approved domestic or international office transfers."
)

# PAGE 5: Disaster Recovery, RTO/RPO & SLA Requirements
pdf.add_page()
pdf.set_font("Helvetica", "B", 16)
pdf.set_text_color(30, 41, 59)
pdf.cell(0, 10, "5. Disaster Recovery (DR) & Incident Response SLAs", new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)

pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(51, 65, 85)
pdf.multi_cell(0, 7,
"Disaster Recovery Metrics:\n"
"- Recovery Time Objective (RTO): Target RTO is 15 minutes for critical database clusters during regional failovers.\n"
"- Recovery Point Objective (RPO): Target RPO is 5 minutes maximum allowable data loss for transactional stores.\n\n"
"Incident Classification & Response SLAs:\n"
"- Severity 1 (Sev-1): Critical production outage affecting > 25% of active users. SLA Response: On-call engineer must acknowledge within 10 minutes and provide status updates every 30 minutes.\n"
"- Severity 2 (Sev-2): Non-critical feature degradation. SLA Response: Acknowledged within 30 minutes, update every 2 hours.\n"
"- Severity 3 (Sev-3): Minor bug with workaround. SLA Response: Addressed in regular sprint cycle within 5 business days."
)

pdf.output("comprehensive_tech_handbook.pdf")
print("Comprehensive 5-page PDF generated successfully!")
