"""
Script to generate a comprehensive, realistic Acme Corp Employee Handbook PDF
with real headings, tables, policies, limits, numbers, and page numbers.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Don't draw header/footer on cover page
        if self._pageNumber > 1:
            # Header
            self.drawString(54, 750, "Acme Corporation — Employee Policy Handbook 2026")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.75)
            self.line(54, 742, 558, 742)
            
            # Footer
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 40, page_text)
            self.drawString(54, 40, "Confidential — Internal Company Policy Only")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.75)
            self.line(54, 52, 558, 52)
            
        self.restoreState()

def generate_handbook(output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=64,
        bottomMargin=64
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=colors.HexColor("#1e293b"),
        alignment=0,
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#475569"),
        spaceAfter=25
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1e40af"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1e293b")
    )
    
    table_hdr = ParagraphStyle(
        'TableHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    story = []

    # ================= COVER PAGE =================
    story.append(Spacer(1, 40))
    story.append(Paragraph("Acme Corporation", ParagraphStyle('CompanyBrand', fontName='Helvetica-Bold', fontSize=14, leading=16, textColor=colors.HexColor("#2563eb"), spaceAfter=15)))
    story.append(Paragraph("Employee Policy Handbook", title_style))
    story.append(Paragraph("Comprehensive Guidelines, Employee Benefits, Compensation, and Operational Standards", subtitle_style))
    story.append(Spacer(1, 20))
    
    meta_data = [
        [Paragraph("<b>Effective Date:</b>", body_style), Paragraph("January 1, 2026", body_style)],
        [Paragraph("<b>Version:</b>", body_style), Paragraph("4.2 (Annual Revision)", body_style)],
        [Paragraph("<b>HR Contact:</b>", body_style), Paragraph("hr@company.com | +1-800-555-0199", body_style)],
        [Paragraph("<b>Office Location:</b>", body_style), Paragraph("HQ - 4th Floor, 500 Enterprise Way, Tech Park", body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[120, 360])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(meta_table)
    
    story.append(Spacer(1, 30))
    story.append(Paragraph("<b>Notice:</b> This handbook summarizes company guidelines. While every effort is made to maintain complete accuracy, human resources reserves final authority on policy interpretation and implementation.", ParagraphStyle('Notice', fontName='Helvetica-Oblique', fontSize=9, leading=13, textColor=colors.HexColor("#64748b"))))
    
    story.append(PageBreak())

    # ================= SECTION 1: COMPENSATION & PAYROLL =================
    story.append(Paragraph("1. Compensation & Payroll Policy", h1_style))
    story.append(Paragraph("Acme Corporation is committed to delivering a transparent, merit-driven, and competitive compensation structure designed to attract, reward, and retain exceptional talent across all departments.", body_style))
    
    story.append(Paragraph("1.1 Salary Structure & Components", h2_style))
    story.append(Paragraph("Total compensation consists of the following components configured in the annual Cost to Company (CTC):", body_style))
    story.append(Paragraph("• <b>Base Salary:</b> Constitutes 50% of monthly CTC and forms the foundation for statutory deductions.", bullet_style))
    story.append(Paragraph("• <b>House Rent Allowance (HRA):</b> Constitutes 20% of CTC, subject to local tax exemption rules.", bullet_style))
    story.append(Paragraph("• <b>Special / Flexible Allowance:</b> Constitutes 20% of CTC, covering discretionary tax-efficient baskets.", bullet_style))
    story.append(Paragraph("• <b>Annual Performance Bonus:</b> Targeted at 10% to 25% of annual CTC depending on job band.", bullet_style))

    story.append(Paragraph("1.2 Pay Disbursal & Overtime", h2_style))
    story.append(Paragraph("All employee salaries are disbursed via electronic direct deposit on the <b>last business day of each calendar month</b>. When the last day coincides with a bank holiday or weekend, pay is released on the preceding working day.", body_style))
    story.append(Paragraph("Overtime policy applies exclusively to non-exempt staff (job bands L1 through L2). Overtime is compensated at <b>1.5x of the regular hourly rate</b> for all approved hours exceeding 40 hours in a given workweek. Prior written approval from the direct Line Manager is mandatory before logging overtime hours.", body_style))

    story.append(Paragraph("1.3 Performance Appraisal & Bonus Cycles", h2_style))
    story.append(Paragraph("The performance appraisal cycle runs annually from <b>April 1 to March 31</b> of each fiscal year:", body_style))
    
    comp_table_data = [
        [Paragraph("Milestone", table_hdr), Paragraph("Timeline", table_hdr), Paragraph("Eligibility / Action", table_hdr)],
        [Paragraph("Self & Peer Review", table_cell), Paragraph("March 1 - March 15", table_cell), Paragraph("All active employees completing >= 90 days tenure", table_cell)],
        [Paragraph("Manager Calibration", table_cell), Paragraph("March 16 - March 31", table_cell), Paragraph("Department heads review 1-5 rating distribution", table_cell)],
        [Paragraph("Bonus Payout", table_cell), Paragraph("April 30 payroll", table_cell), Paragraph("Requires minimum 6 months active service in FY", table_cell)],
        [Paragraph("Salary Revision Effective", table_cell), Paragraph("May 1", table_cell), Paragraph("Letters distributed via HR portal by April 25", table_cell)]
    ]
    t_comp = Table(comp_table_data, colWidths=[130, 120, 250])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")])
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 10))

    # ================= SECTION 2: ESOP & EQUITY =================
    story.append(Paragraph("2. Employee Stock Ownership Plan (ESOP)", h1_style))
    story.append(Paragraph("The Acme Employee Stock Ownership Plan (ESOP) provides full-time team members with an opportunity to participate in company growth, align long-term interests, and build meaningful wealth as equity shareholders.", body_style))

    story.append(Paragraph("2.1 Eligibility & Granting Guidelines", h2_style))
    story.append(Paragraph("Stock options are granted to full-time regular employees at Level 4 (L4 / Senior level) and above upon hiring, or during the annual compensation review based on exceptional performance ratings (ratings 4 and 5). Grant letters specifying option quantities and grant price are issued by the Compensation & Benefits Committee.", body_style))

    story.append(Paragraph("2.2 Vesting Schedule & The 1-Year Cliff", h2_style))
    story.append(Paragraph("All standard equity grants follow a <b>4-year vesting schedule</b> with a mandatory <b>1-year cliff</b>:", body_style))
    story.append(Paragraph("• <b>Year 1 (Cliff):</b> Exactly <b>25% of total options vest</b> on the completion of 12 full calendar months of continuous active employment from the Grant Vesting Commencement Date.", bullet_style))
    story.append(Paragraph("• <b>Years 2 through 4 (Monthly Vesting):</b> The remaining 75% vests in equal monthly increments of <b>2.083% per month</b> (1/48th of total grant per month) over the subsequent 36 months.", bullet_style))
    story.append(Paragraph("• <b>Unvested Options:</b> In the event of resignation or separation prior to the 12-month cliff, all options are completely forfeited without exception.", bullet_style))

    story.append(Paragraph("2.3 Exercise Windows & Separation Rules", h2_style))
    story.append(Paragraph("The exercise price is pegged to the Fair Market Value (FMV) established by the independent 409A valuation firm at the time of board approval. The post-termination exercise windows are strictly enforced:", body_style))
    story.append(Paragraph("• <b>Voluntary Resignation:</b> Employees have <b>90 calendar days</b> following their official last working day to exercise vested options. Any unexercised options expire immediately on day 91.", bullet_style))
    story.append(Paragraph("• <b>Retirement or Redundancy:</b> Employees are granted an extended <b>180 calendar days</b> to exercise vested equity.", bullet_style))
    story.append(Paragraph("• <b>Termination for Cause:</b> All options (both vested and unvested) are immediately cancelled and forfeited.", bullet_style))
    story.append(Paragraph("• <b>Taxation:</b> Exercise triggers perquisite tax calculated on the difference between FMV and strike price. Sale of shares triggers capital gains tax based on holding duration.", body_style))

    story.append(PageBreak())

    # ================= SECTION 3: CAFETERIA & DINING FACILITIES =================
    story.append(Paragraph("3. Cafeteria & Dining Facilities", h1_style))
    story.append(Paragraph("Acme provides state-of-the-art on-campus dining centers across all corporate facilities to promote health, team bonding, and comfortable workspaces.", body_style))

    story.append(Paragraph("3.1 Operating Hours & Service Timings", h2_style))
    story.append(Paragraph("The main cafeteria on Level 2 operates six days a week (Monday through Saturday) according to the following schedule:", body_style))

    cafe_table_data = [
        [Paragraph("Meal Service", table_hdr), Paragraph("Operating Hours", table_hdr), Paragraph("Coverage & Subsidies", table_hdr)],
        [Paragraph("Breakfast Service", table_cell), Paragraph("08:30 AM – 10:00 AM", table_cell), Paragraph("Subsidized breakfast buffet ($3.00 flat fee)", table_cell)],
        [Paragraph("Lunch Buffet", table_cell), Paragraph("12:30 PM – 02:30 PM", table_cell), Paragraph("100% Subsidized (Complimentary / Free for staff)", table_cell)],
        [Paragraph("Evening Snacks & High Tea", table_cell), Paragraph("04:30 PM – 06:00 PM", table_cell), Paragraph("100% Subsidized (Complimentary hot snacks, tea/coffee)", table_cell)],
        [Paragraph("Late Shift Dinner", table_cell), Paragraph("08:00 PM – 09:30 PM", table_cell), Paragraph("Free for employees logging approved shift past 8 PM", table_cell)]
    ]
    t_cafe = Table(cafe_table_data, colWidths=[120, 130, 250])
    t_cafe.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#065f46")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f0fdf4")])
    ]))
    story.append(t_cafe)
    story.append(Spacer(1, 10))

    story.append(Paragraph("3.2 Dietary Accommodations & Beverages", h2_style))
    story.append(Paragraph("Acme accommodates diverse dietary needs. Our vendors maintain clearly segregated and labeled counters for:", body_style))
    story.append(Paragraph("• <b>Vegetarian & Vegan:</b> Dedicated cookware and preparation lines certified daily.", bullet_style))
    story.append(Paragraph("• <b>Halal & Kosher:</b> Available upon request via the cafeteria pre-booking app.", bullet_style))
    story.append(Paragraph("• <b>Allergen & Gluten-Free:</b> Nut-free prep stations and daily gluten-free meal alternatives.", bullet_style))
    story.append(Paragraph("Barista-served espresso, artisan teas, sparkling water, and fresh fruit are available 24/7 across all pantry stations on floors 2, 3, and 4 at zero cost.", body_style))

    story.append(Paragraph("3.3 Guest Dining Policy", h2_style))
    story.append(Paragraph("Employees may invite external business partners, clients, or family members to join for lunch. Each employee is permitted up to <b>2 guest lunches per calendar month</b>. Employees must log the guest request via <i>facilities@company.com</i> at least 24 hours prior. A guest meal voucher fee of <b>$15.00 per guest</b> is deducted automatically via payroll.", body_style))

    story.append(Spacer(1, 10))

    # ================= SECTION 4: TRAVEL & EXPENSE REIMBURSEMENT =================
    story.append(Paragraph("4. Business Travel & Expense Reimbursement", h1_style))
    story.append(Paragraph("All business-related domestic and international travel must be booked through the corporate travel desk (travel@company.com) following prior budget approval from the Department Head.", body_style))

    story.append(Paragraph("4.1 Flight & Hotel Lodging Limits", h2_style))
    story.append(Paragraph("Travel accommodations are categorized based on destination tiers and flight duration:", body_style))
    story.append(Paragraph("• <b>Air Travel:</b> Economy Class is standard for all domestic travel and international flights under 6 hours duration. Business Class is authorized for international flights exceeding 6 hours with prior written sign-off from the Vice President (VP).", bullet_style))
    story.append(Paragraph("• <b>Tier 1 Metro Cities</b> (New York, San Francisco, London, Tokyo, Singapore): Hotel lodging up to <b>$250 per night</b> (excluding local taxes).", bullet_style))
    story.append(Paragraph("• <b>Tier 2 Cities</b> (Austin, Seattle, Berlin, Chicago, Toronto): Hotel lodging up to <b>$160 per night</b>.", bullet_style))
    story.append(Paragraph("• <b>Other Cities & Towns:</b> Hotel lodging up to <b>$120 per night</b>.", bullet_style))

    story.append(Paragraph("4.2 Daily Per Diem Rates & Vehicle Mileage", h2_style))
    story.append(Paragraph("Per diem allowances cover meals, tipping, and incidental personal expenses during travel where meals are not otherwise provided by an event or host:", body_style))
    story.append(Paragraph("• <b>Domestic Tier 1 Per Diem:</b> <b>$75.00 per day</b>.", bullet_style))
    story.append(Paragraph("• <b>Domestic Tier 2 Per Diem:</b> <b>$50.00 per day</b>.", bullet_style))
    story.append(Paragraph("• <b>International Travel Per Diem:</b> <b>$100.00 per day</b> flat allowance.", bullet_style))
    story.append(Paragraph("• <b>Personal Vehicle Mileage:</b> When an employee uses their personal vehicle for official company travel, mileage is reimbursed at <b>$0.67 per mile</b> (aligned with IRS standard mileage rates). Fuel receipts are not needed for mileage claims, but odometer logs are required.", bullet_style))

    story.append(Paragraph("4.3 Expense Filing Guidelines & Timelines", h2_style))
    story.append(Paragraph("All expense reports must be submitted via the Acme Finance Portal within <b>30 calendar days</b> of returning from the trip. Any expense claim submitted past 45 days is deemed void and non-reimbursable. Itemized receipts are mandatory for all single expenditures exceeding $25. Approved claims are processed and reimbursed within <b>10 business days</b>.", body_style))

    story.append(PageBreak())

    # ================= SECTION 5: LEAVE & TIME-OFF POLICIES =================
    story.append(Paragraph("5. Leave & Time-Off Policy", h1_style))
    story.append(Paragraph("Acme believes in supporting work-life harmony and personal rejuvenation through generous time-off entitlements. The annual leave cycle operates from January 1 through December 31.", body_style))

    story.append(Paragraph("5.1 Leave Entitlements Summary", h2_style))
    
    leave_table_data = [
        [Paragraph("Leave Category", table_hdr), Paragraph("Annual Quota", table_hdr), Paragraph("Accrual / Carryover Rules", table_hdr)],
        [Paragraph("Annual / Privilege Leave", table_cell), Paragraph("20 Days", table_cell), Paragraph("Accrues 1.67 days/month. Max 10 days carryover to next year.", table_cell)],
        [Paragraph("Casual / Personal Leave", table_cell), Paragraph("8 Days", table_cell), Paragraph("Credited on Jan 1. Cannot be carried forward (lapses Dec 31).", table_cell)],
        [Paragraph("Sick & Medical Leave", table_cell), Paragraph("10 Days", table_cell), Paragraph("Doctor's certificate mandatory for absences > 3 consecutive days.", table_cell)],
        [Paragraph("Maternity Leave", table_cell), Paragraph("26 Weeks", table_cell), Paragraph("100% paid for up to 2 surviving children. +4 weeks if medical need.", table_cell)],
        [Paragraph("Paternity Leave", table_cell), Paragraph("15 Working Days", table_cell), Paragraph("100% paid. Must be utilized within 6 months of childbirth/adoption.", table_cell)],
        [Paragraph("Bereavement Leave", table_cell), Paragraph("5 Days (Immediate)<br/>3 Days (Extended)", table_cell), Paragraph("Fully paid leave upon loss of immediate or extended family member.", table_cell)],
        [Paragraph("Compensatory Off (Comp-off)", table_cell), Paragraph("As Earned", table_cell), Paragraph("Earned for approved weekend/holiday work. Valid for 60 days.", table_cell)]
    ]
    t_leave = Table(leave_table_data, colWidths=[130, 90, 280])
    t_leave.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#7c2d12")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#fff7ed")])
    ]))
    story.append(t_leave)
    story.append(Spacer(1, 10))

    story.append(Paragraph("5.2 Application & Approval Protocols", h2_style))
    story.append(Paragraph("• <b>Planned Leaves (> 3 consecutive days):</b> Must be requested through the HR portal at least <b>14 calendar days in advance</b>.", bullet_style))
    story.append(Paragraph("• <b>Short Notice Leaves:</b> For casual or emergency sick leaves, notification must be submitted to the manager via Slack or email by 09:30 AM on the day of absence.", bullet_style))
    story.append(Paragraph("• <b>Encashment:</b> Unused Annual Leaves exceeding the 10-day carryover limit are not encashable during active employment, but are encashed upon separation based on basic pay.", bullet_style))

    story.append(Spacer(1, 10))

    # ================= SECTION 6: EMPLOYEE BENEFITS & WELLNESS =================
    story.append(Paragraph("6. Employee Health & Wellness Benefits", h1_style))
    story.append(Paragraph("We offer comprehensive healthcare, mental well-being, and family security benefits designed to protect employees and their dependents.", body_style))

    story.append(Paragraph("6.1 Group Medical & Dental Insurance", h2_style))
    story.append(Paragraph("• <b>Health Insurance (Mediclaim):</b> Acme provides group health coverage with a maximum sum insured of <b>$500,000 per family unit</b>. Coverage extends to employee, spouse/domestic partner, and up to 2 dependent children under age 26. Pre-existing medical conditions are covered from day 1 without waiting periods.", bullet_style))
    story.append(Paragraph("• <b>Parental Cover Add-on:</b> Employees may enroll dependent parents or parents-in-law under a subsidized group top-up policy with a 50% company contribution and 50% payroll co-pay.", bullet_style))
    story.append(Paragraph("• <b>Dental & Vision Allowance:</b> Employees receive up to <b>$1,500 annually per enrolled family member</b> for preventative dental exams, cleanings, corrective eye surgeries, glasses, or contact lenses.", bullet_style))

    story.append(Paragraph("6.2 Wellness Stipend & Mental Health", h2_style))
    story.append(Paragraph("• <b>Annual Wellness Reimbursement:</b> Acme reimburses up to <b>$600 per calendar year</b> for verified health expenses, including gym memberships, Pilates/yoga studios, fitness smartwatches, or ergonomics equipment.", bullet_style))
    story.append(Paragraph("• <b>Employee Assistance Program (EAP):</b> Free, 100% confidential mental wellness support providing up to <b>8 counseling sessions per year</b> for employees and immediate household members through our wellness partner, Spring Health.", bullet_style))

    story.append(Paragraph("6.3 Learning, Tuition & Development Stipend", h2_style))
    story.append(Paragraph("To foster continuous career growth, every full-time employee with at least 6 months of tenure is eligible for an <b>annual Learning Stipend of $1,200</b>. Eligible expenses include industry technical certifications, executive education modules, academic books, and recognized conference passes.", body_style))

    story.append(Spacer(1, 10))

    # ================= SECTION 7: GENERAL WORKPLACE POLICIES =================
    story.append(Paragraph("7. General Workplace Policies & Conduct", h1_style))
    story.append(Paragraph("7.1 Working Hours & Hybrid Work Model", h2_style))
    story.append(Paragraph("Acme observes a 40-hour standard workweek. Core collaboration hours are <b>10:00 AM to 4:00 PM local time</b>. Eligible engineering and product roles operate under a flexible hybrid policy permitting <b>up to 2 remote workdays per week</b> (typically Tuesdays and Thursdays or as agreed with team leadership).", body_style))

    story.append(Paragraph("7.2 Notice Period & Separation Guidelines", h2_style))
    story.append(Paragraph("• <b>Probationary Period:</b> New hires undergo a 90-day probationary period. During probation, either party may terminate employment with <b>30 calendar days notice</b>.", bullet_style))
    story.append(Paragraph("• <b>Confirmed Employees:</b> Following successful probation confirmation, the required notice period for voluntary resignation is <b>60 calendar days</b>. Buyout of notice period requires explicit approval from the Department VP and HR Director.", bullet_style))

    story.append(Paragraph("7.3 Contact Directory & Escalations", h2_style))
    story.append(Paragraph("For any questions, clarifications, or policy exceptions, reach out to the appropriate contact:", body_style))
    story.append(Paragraph("• <b>General HR Desk:</b> hr@company.com | Phone: +1-800-555-0199", bullet_style))
    story.append(Paragraph("• <b>Payroll & Tax Inquiries:</b> payroll@company.com", bullet_style))
    story.append(Paragraph("• <b>Travel Desk:</b> travel@company.com", bullet_style))
    story.append(Paragraph("• <b>Facilities & Dining:</b> facilities@company.com", bullet_style))
    story.append(Paragraph("• <b>Ethics & Whistleblower Hotline:</b> ethics@company.com (Confidential)", bullet_style))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Handbook PDF generated successfully at: {output_path}")

if __name__ == "__main__":
    generate_handbook("hr-policy-assistant/data/handbook.pdf")

