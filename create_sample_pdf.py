from fpdf import FPDF

pdf = FPDF()

# Page 1: Working Hours & Remote Policy
pdf.add_page()
pdf.set_font("Helvetica", "B", 16)
pdf.cell(0, 10, "Acme Corp - Employee Handbook (Page 1)", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.ln(5)

pdf.set_font("Helvetica", "B", 13)
pdf.cell(0, 10, "1. Working Hours & Remote Work Policy", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 11)
pdf.multi_cell(0, 7, 
"Standard office hours are from 9:00 AM to 6:00 PM, Monday through Friday.\n"
"All full-time employees must be available during Core Hours between 11:00 AM and 4:00 PM EST.\n"
"Employees are eligible to work remotely up to 2 days per week (Tuesdays and Thursdays) with prior approval from their team lead."
)

# Page 2: Leave Entitlements
pdf.add_page()
pdf.set_font("Helvetica", "B", 16)
pdf.cell(0, 10, "Acme Corp - Employee Handbook (Page 2)", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.ln(5)

pdf.set_font("Helvetica", "B", 13)
pdf.cell(0, 10, "2. Leave & Vacation Policy", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 11)
pdf.multi_cell(0, 7,
"Annual Paid Time Off (PTO): All full-time staff receive 20 days of paid vacation per calendar year.\n"
"Sick Leave: Employees are entitled to 10 days of fully paid sick leave annually.\n"
"Parental Leave: Primary caregivers receive 16 weeks of fully paid parental leave, while secondary caregivers receive 6 weeks."
)

# Page 3: Stipends & Allowances
pdf.add_page()
pdf.set_font("Helvetica", "B", 16)
pdf.cell(0, 10, "Acme Corp - Employee Handbook (Page 3)", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.ln(5)

pdf.set_font("Helvetica", "B", 13)
pdf.cell(0, 10, "3. Equipment & Learning Stipends", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 11)
pdf.multi_cell(0, 7,
"Home Office Setup Allowance: A one-time $500 stipend is provided upon joining for home workstation setup.\n"
"Professional Development: Every employee is allocated $1,200 annually for books, certification courses, and industry conferences.\n"
"Hardware Replacement: Laptops and primary workstations are eligible for standard hardware upgrade every 3 years."
)

pdf.output("sample_company_policy.pdf")
print("PDF created successfully!")
