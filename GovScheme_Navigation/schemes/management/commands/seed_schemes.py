from django.core.management.base import BaseCommand
from schemes.models import Scheme, EligibilityRule, DocumentRequirement, CitizenProfile, ApplicationRecord, StatusHistory, NotificationLog
from schemes.services.notification_service import NotificationService
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Seeds realistic Central and State Government schemes, eligibility rules, document lists, and mock applications.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Flushing old test data and seeding fresh government schemes..."))

        # Clear existing
        NotificationLog.objects.all().delete()
        StatusHistory.objects.all().delete()
        ApplicationRecord.objects.all().delete()
        DocumentRequirement.objects.all().delete()
        EligibilityRule.objects.all().delete()
        Scheme.objects.all().delete()
        CitizenProfile.objects.all().delete()

        # -------------------------------------------------------------
        # 1. PM-KISAN (Agriculture)
        # -------------------------------------------------------------
        pm_kisan = Scheme.objects.create(
            code="PM-KISAN",
            name="Pradhan Mantri Kisan Samman Nidhi",
            short_title="PM-Kisan Income Support",
            ministry="Ministry of Agriculture & Farmers Welfare",
            level="CENTRAL",
            state_scope="ALL",
            sector_category="Agriculture",
            benefit_highlight="₹6,000 / year direct cash support (₹2,000 in 3 installments)",
            legal_description="The Scheme provides income support to all landholding farmer families across the country to enable them to take care of expenses related to agriculture and allied activities as well as domestic needs. Operational landholding records verified by state revenue departments shall be prerequisites under Section 4(1). Exclusions include institutional landholders and constitutional post holders.",
            plain_language_summary="A central government financial assistance scheme providing ₹6,000 every year in three equal installments of ₹2,000 directly transferred into the farmer's bank account to support agricultural inputs, seeds, fertilizers, and household farming expenses.",
            plain_language_eligibility="• You are a small, marginal, or medium farmer with cultivable land registered in your name.\n• You or your spouse are not income-tax payers or constitutional post holders.\n• Valid Aadhaar linked with your bank account is mandatory.",
            application_process="1. Visit the official PM-KISAN portal or your local CSC / Panchayat Centre.\n2. Click on 'New Farmer Registration' and enter your Aadhaar and mobile number.\n3. Enter state, district, sub-district, village, and upload land Khasra/Khatauni documents.\n4. Complete e-KYC via OTP or biometric scan.\n5. Track approval status online via your Aadhaar or Application Reference ID.",
            deadline_text="Open Throughout the Year (Ongoing DBT)",
            official_portal_name="PM-KISAN Official Portal",
            official_portal_url="https://pmkisan.gov.in",
            helpline_number="155261 / 011-24300606",
            tags="farmer, agriculture, dbt, direct cash, fertilizer support",
            is_active=True,
            featured=True
        )

        EligibilityRule.objects.create(
            scheme=pm_kisan, rule_field='occupation', operator='in', expected_values='["farmer", "agri_worker"]',
            legal_clause_text="Beneficiary family comprising husband, wife and minor children owning cultivable land as per land records.",
            plain_language_rule="✓ Matched: You are engaged in Farming or Agricultural Work.",
            is_mandatory=True
        )
        EligibilityRule.objects.create(
            scheme=pm_kisan, rule_field='income_bracket', operator='in', expected_values='["bpl", "low_income", "lower_middle"]',
            legal_clause_text="Families not falling under exclusion criteria including income-tax payers.",
            plain_language_rule="✓ Matched: Household income meets the small/marginal farmer limits.",
            is_mandatory=True
        )
        EligibilityRule.objects.create(
            scheme=pm_kisan, rule_field='state', operator='in', expected_values='["all"]',
            legal_clause_text="Nationwide applicability across all States and Union Territories.",
            plain_language_rule="✓ Open to all States and Union Territories in India.",
            is_mandatory=False
        )

        DocumentRequirement.objects.create(
            scheme=pm_kisan, document_name="Aadhaar Card",
            why_required="Required for biometric e-KYC and Direct Benefit Transfer (DBT) verification.",
            issuing_authority="UIDAI", is_mandatory=True, digilocker_available=True
        )
        DocumentRequirement.objects.create(
            scheme=pm_kisan, document_name="Land Ownership Record (Khatauni / RoR)",
            why_required="Proves you own cultivable agricultural land in your name.",
            issuing_authority="State Revenue / Tehsil Department", is_mandatory=True, digilocker_available=True
        )
        DocumentRequirement.objects.create(
            scheme=pm_kisan, document_name="Bank Account Passbook / Cancelled Cheque",
            why_required="Bank account must be Aadhaar-seeded for direct payment credit.",
            issuing_authority="Any Scheduled Bank or Post Office", is_mandatory=True, digilocker_available=False
        )

        # -------------------------------------------------------------
        # 2. PMEGP (Business & Entrepreneurship)
        # -------------------------------------------------------------
        pmegp = Scheme.objects.create(
            code="PMEGP",
            name="Prime Minister's Employment Generation Programme",
            short_title="PMEGP Business Setup Subsidy",
            ministry="Ministry of Micro, Small and Medium Enterprises (MSME)",
            level="CENTRAL",
            state_scope="ALL",
            sector_category="Business",
            benefit_highlight="Up to 35% Govt Subsidy on Loans up to ₹50 Lakh (Manufacturing) & ₹20 Lakh (Services)",
            legal_description="A credit-linked subsidy programme administered through KVIC as the nodal agency at the national level. Margin money subsidy of 15% to 35% is disbursed by government through designated nodal banks based on location (rural/urban) and social category. Minimum qualifying educational standard of 8th standard pass applies for projects exceeding statutory threshold limits.",
            plain_language_summary="A major government funding initiative that helps you start a new business, shop, or manufacturing unit by providing bank loans with up to 35% government subsidy (free money grant you don't repay).",
            plain_language_eligibility="• Any individual above 18 years of age wishing to set up a new enterprise.\n• Minimum 8th class pass for projects costing above ₹10 Lakh in manufacturing or ₹5 Lakh in services.\n• Subsidy: 25% in urban areas and 35% in rural areas for special categories (women, SC/ST, OBC, minorities, PwD).",
            application_process="1. Prepare your project report (Detailed Project Report - DPR) highlighting costs and equipment.\n2. Fill online application on KVIC PMEGP e-Portal (www.kviconline.gov.in).\n3. Upload photograph, project report, Aadhaar, caste/special category certificate, and educational certificate.\n4. District Level Task Force Committee (DLTFC) reviews the application and forwards it to your chosen bank.\n5. Bank inspects premises, sanctions loan, and claims margin money subsidy from Govt.",
            deadline_text="Open Throughout the Year",
            official_portal_name="KVIC PMEGP Portal",
            official_portal_url="https://www.kviconline.gov.in/pmegpeportal/",
            helpline_number="1800-180-6763",
            tags="business, startup, msme, subsidy, loan, self employment",
            is_active=True,
            featured=True
        )

        EligibilityRule.objects.create(
            scheme=pmegp, rule_field='occupation', operator='in', expected_values='["business_owner", "unemployed", "student", "gig_worker"]',
            legal_clause_text="Any individual entrepreneur intending to establish a new micro enterprise.",
            plain_language_rule="✓ Matched: You are planning to start or expand a micro business / self-employment.",
            is_mandatory=True
        )
        EligibilityRule.objects.create(
            scheme=pmegp, rule_field='age_group', operator='in', expected_values='["18-25", "26-40", "41-59"]',
            legal_clause_text="Applicant must be at least 18 years of age at time of submission.",
            plain_language_rule="✓ Matched: Age is 18 years or above.",
            is_mandatory=True
        )
        EligibilityRule.objects.create(
            scheme=pmegp, rule_field='education_level', operator='in', expected_values='["10th_pass", "12th_pass", "graduate", "postgraduate", "diploma_iti"]',
            legal_clause_text="Educational criteria for projects above benchmark thresholds.",
            plain_language_rule="✓ Matched: Education level qualifies for loan projects.",
            is_mandatory=False
        )

        DocumentRequirement.objects.create(
            scheme=pmegp, document_name="Detailed Project Report (DPR)",
            why_required="Outlines what business you will start, machinery needed, expected income, and total costs.",
            issuing_authority="Prepared by Applicant / CA / MSME Helpdesk", is_mandatory=True, digilocker_available=False
        )
        DocumentRequirement.objects.create(
            scheme=pmegp, document_name="Aadhaar & PAN Card",
            why_required="Identity and tax verification for business registration and bank sanction.",
            issuing_authority="UIDAI & Income Tax Department", is_mandatory=True, digilocker_available=True
        )
        DocumentRequirement.objects.create(
            scheme=pmegp, document_name="Highest Education Marksheet",
            why_required="Confirms educational qualification criteria for project sanction.",
            issuing_authority="Recognized Education Board / University", is_mandatory=True, digilocker_available=True
        )

        # -------------------------------------------------------------
        # 3. Post-Matric Scholarship (Education)
        # -------------------------------------------------------------
        scholarship = Scheme.objects.create(
            code="PMS-SCHOLAR",
            name="Centrally Sponsored Post-Matric Scholarship Scheme",
            short_title="Post-Matric Higher Education Scholarship",
            ministry="Ministry of Social Justice & Empowerment",
            level="CENTRAL",
            state_scope="ALL",
            sector_category="Education",
            benefit_highlight="100% Course Fee Waiver + Up to ₹13,500/year Living Maintenance Allowance",
            legal_description="The objective of the scheme is to provide financial assistance to students belonging to disadvantaged categories studying at post-matriculation or post-secondary stage. Employed parents' gross aggregate income ceiling is fixed at ₹2,50,000 per annum under Gazette notifications. Scholarships are paid through DBT on the National Scholarship Portal (NSP).",
            plain_language_summary="A government scholarship that pays for your full college tuition fees, exam fees, plus gives you a monthly cash allowance to cover hostel, books, and living expenses for 11th, 12th, ITI, Diploma, Undergraduate, and Postgraduate degrees.",
            plain_language_eligibility="• You are currently enrolled in a recognized college, university, or polytechnic.\n• Total family annual income from all sources is ₹2.50 Lakh or less.\n• Applicable for SC, ST, OBC, EWS, and minority students.",
            application_process="1. Register on National Scholarship Portal (scholarships.gov.in) with your Aadhaar.\n2. Select Post-Matric Scholarship scheme for your state and category.\n3. Upload your college bonafide certificate, previous mark sheet, and income certificate.\n4. Institute verification officer verifies your admission record online.\n5. Scholarship funds are credited directly to your bank account via PFMS.",
            application_deadline=date.today() + timedelta(days=45),
            deadline_text="31st October (Annual Academic Cycle)",
            official_portal_name="National Scholarship Portal (NSP)",
            official_portal_url="https://scholarships.gov.in",
            helpline_number="0120-6619540",
            tags="scholarship, student, education, college, fee waiver, post matric",
            is_active=True,
            featured=True
        )

        EligibilityRule.objects.create(
            scheme=scholarship, rule_field='occupation', operator='in', expected_values='["student"]',
            legal_clause_text="Beneficiary must be pursuing recognized regular post-secondary education.",
            plain_language_rule="✓ Matched: You are a Student enrolled in post-school education.",
            is_mandatory=True
        )
        EligibilityRule.objects.create(
            scheme=scholarship, rule_field='income_bracket', operator='in', expected_values='["bpl", "low_income"]',
            legal_clause_text="Total family income from all sources does not exceed INR 2,50,000 p.a.",
            plain_language_rule="✓ Matched: Family yearly earnings are ₹2.50 Lakh or lower.",
            is_mandatory=True
        )
        EligibilityRule.objects.create(
            scheme=scholarship, rule_field='specific_category', operator='in', expected_values='["sc", "st", "obc", "pwd", "minority", "general"]',
            legal_clause_text="Eligible categories as designated under affirmative action provisions.",
            plain_language_rule="✓ Matched: Social category qualifies for scholarship benefits.",
            is_mandatory=True
        )

        DocumentRequirement.objects.create(
            scheme=scholarship, document_name="Income Certificate (Tahsildar / SDO)",
            why_required="Verifies your family income is within the ₹2.5 Lakh annual ceiling.",
            issuing_authority="Revenue Department / Tehsildar", is_mandatory=True, digilocker_available=True
        )
        DocumentRequirement.objects.create(
            scheme=scholarship, document_name="College Bonafide & Fee Receipt",
            why_required="Confirms active admission in current academic semester/year.",
            issuing_authority="College / University Registrar", is_mandatory=True, digilocker_available=False
        )
        DocumentRequirement.objects.create(
            scheme=scholarship, document_name="Previous Year Marksheet",
            why_required="Validates passing marks in previous qualification.",
            issuing_authority="State Board / University", is_mandatory=True, digilocker_available=True
        )

        # -------------------------------------------------------------
        # 4. Ayushman Bharat (Health)
        # -------------------------------------------------------------
        ayushman = Scheme.objects.create(
            code="AB-PMJAY",
            name="Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana",
            short_title="Ayushman Bharat Free Health Cover",
            ministry="Ministry of Health and Family Welfare (NHA)",
            level="CENTRAL",
            state_scope="ALL",
            sector_category="Healthcare",
            benefit_highlight="₹5,00,000 / year Cashless Hospitalization per family across 27,000+ hospitals",
            legal_description="PM-JAY provides secondary and tertiary care hospitalization through a network of Empaneled Health Care Providers (EHCP). Entitlement is based on deprivation and occupational criteria defined under SECC 2011 database. There is no restriction on family size, age or gender.",
            plain_language_summary="The world's largest government-funded healthcare scheme providing completely free, cashless medical treatment and surgery up to ₹5,00,000 every year for your entire family across both private and government hospitals.",
            plain_language_eligibility="• Low income, BPL, daily wage workers, rural households, and vulnerable urban workers.\n• Covers all family members with zero cap on family size or age.\n• Covers surgery, ICU, medicines, diagnostics, and pre/post-hospitalization.",
            application_process="1. Check your name on the Ayushman Bharat portal (beneficiary.nha.gov.in) or call 14555.\n2. Visit any government hospital, empaneled private hospital, or nearest CSC Centre.\n3. Show your Aadhaar card or Ration card to the 'Ayushman Mitra' desk.\n4. Complete quick biometric e-KYC on the spot.\n5. Download and print your instant Golden Ayushman PVC Card.",
            deadline_text="Open Throughout the Year (Lifelong Benefit)",
            official_portal_name="National Health Authority (NHA)",
            official_portal_url="https://beneficiary.nha.gov.in",
            helpline_number="14555 / 1800-111-565",
            tags="health, hospital, insurance, free treatment, surgery, medicine",
            is_active=True,
            featured=True
        )

        EligibilityRule.objects.create(
            scheme=ayushman, rule_field='income_bracket', operator='in', expected_values='["bpl", "low_income", "lower_middle"]',
            legal_clause_text="Deprivation category households as indexed under SECC criteria.",
            plain_language_rule="✓ Matched: Family falls within the healthcare assistance income brackets.",
            is_mandatory=True
        )
        EligibilityRule.objects.create(
            scheme=ayushman, rule_field='state', operator='in', expected_values='["all"]',
            legal_clause_text="Nationwide portability across all participating states and hospital chains.",
            plain_language_rule="✓ Free treatment valid across any empaneled hospital anywhere in India.",
            is_mandatory=False
        )

        DocumentRequirement.objects.create(
            scheme=ayushman, document_name="Ration Card / NFSA Card",
            why_required="Identifies all family members eligible under the household card.",
            issuing_authority="Food & Civil Supplies Department", is_mandatory=True, digilocker_available=True
        )
        DocumentRequirement.objects.create(
            scheme=ayushman, document_name="Aadhaar Card of Family Members",
            why_required="Used for real-time biometric e-KYC at hospital reception desk.",
            issuing_authority="UIDAI", is_mandatory=True, digilocker_available=True
        )

        # -------------------------------------------------------------
        # 5. PM Awas Yojana Gramin (Housing)
        # -------------------------------------------------------------
        pm_awas = Scheme.objects.create(
            code="PMAY-G",
            name="Pradhan Mantri Awaas Yojana - Gramin",
            short_title="PM Awas Pucca House Grant",
            ministry="Ministry of Rural Development",
            level="CENTRAL",
            state_scope="ALL",
            sector_category="Housing",
            benefit_highlight="₹1,20,000 Cash Grant + ₹12,000 Toilet Incentive + 90 Days MGNREGA Wages",
            legal_description="Under PMAY-G, financial assistance is provided for construction of a minimum 25 sq.m pucca house including a dedicated hygienic cooking space. Funds are released in 3 tranches directly into beneficiary accounts upon geo-tagged photographic verification of foundation, lintel, and roof stages.",
            plain_language_summary="Government grant of ₹1,20,000 (₹1.30 Lakh in hilly states) paid directly to your bank account in 3 stages to build a solid brick/concrete home, plus an additional ₹12,000 for toilet construction.",
            plain_language_eligibility="• Houseless families or those living in kutcha / temporary dilapidated houses.\n• Low-income or BPL households verified through Gram Sabha priority lists.\n• Land ownership or allotted homestead land.",
            application_process="1. Apply through your Gram Panchayat or Block Development Officer (BDO).\n2. Field team visits and captures geo-tagged photos of existing kutcha structure.\n3. Gram Sabha reviews and adds name to Awaas+ priority list.\n4. Sanction order released and 1st installment (₹40,000) credited to start foundation.\n5. Subsequent installments released as each building stage is photographed.",
            deadline_text="Ongoing Annual Allocation",
            official_portal_name="AwaasSoft Portal",
            official_portal_url="https://pmayg.nic.in",
            helpline_number="1800-11-6446",
            tags="housing, home grant, rural, pucca house, bpl, construction",
            is_active=True,
            featured=False
        )

        EligibilityRule.objects.create(
            scheme=pm_awas, rule_field='income_bracket', operator='in', expected_values='["bpl", "low_income"]',
            legal_clause_text="Households classified under housing deprivation criteria.",
            plain_language_rule="✓ Matched: Family qualifies under housing assistance income limits.",
            is_mandatory=True
        )
        EligibilityRule.objects.create(
            scheme=pm_awas, rule_field='occupation', operator='in', expected_values='["farmer", "gig_worker", "unemployed", "homemaker", "agri_worker"]',
            legal_clause_text="Vulnerable rural households lacking durable residential assets.",
            plain_language_rule="✓ Matched: Eligible occupational profile for rural housing grants.",
            is_mandatory=False
        )

        DocumentRequirement.objects.create(
            scheme=pm_awas, document_name="BPL / Ration Card",
            why_required="Confirms socio-economic status and household member count.",
            issuing_authority="Department of Food and Civil Supplies", is_mandatory=True, digilocker_available=True
        )
        DocumentRequirement.objects.create(
            scheme=pm_awas, document_name="Land Title / Patta / Possession Certificate",
            why_required="Proves you own or have government authorization for the house plot.",
            issuing_authority="Panchayat / Circle Officer", is_mandatory=True, digilocker_available=False
        )

        # -------------------------------------------------------------
        # 6. Digital India Tech Internship Scheme (Tech / Youth)
        # -------------------------------------------------------------
        tech_intern = Scheme.objects.create(
            code="DIIS-2026",
            name="Digital India Tech & AI Internship Scheme",
            short_title="Digital India Govt AI Internship",
            ministry="Ministry of Electronics and Information Technology (MeitY)",
            level="CENTRAL",
            state_scope="ALL",
            sector_category="Technology",
            benefit_highlight="₹20,000 / month Stipend + Official MeitY Experience Certificate & AI GovTech Exposure",
            legal_description="MeitY invites applications for 3 to 6 months technical internships from Indian students pursuing undergraduate or postgraduate technical curricula. Interns are placed with National Informatics Centre (NIC), Digital India Corporation, or AI Task Forces.",
            plain_language_summary="A prestigious paid internship with the Ministry of IT where college students and fresh graduates work on national digital projects (AI, cloud, cyber security, DigiLocker) while receiving ₹20,000 monthly stipend.",
            plain_language_eligibility="• Students in B.Tech, MCA, M.Sc (CS/IT), MBA or Diploma in engineering with min 60% marks.\n• Age between 18 and 28 years.\n• Open to students across all Indian states and institutions.",
            application_process="1. Create profile on MeitY Internship Portal.\n2. Submit online application with resume, statement of purpose, and college NOC.\n3. Shortlisted candidates attend virtual technical interview with project mentors.\n4. Selected interns receive offer letter with assigned mentor and domain.\n5. Complete internship and receive monthly ₹20,000 stipend directly in bank account.",
            application_deadline=date.today() + timedelta(days=28),
            deadline_text="Last Date: 30th November (Winter Cohort)",
            official_portal_name="MeitY Internship Portal",
            official_portal_url="https://www.meity.gov.in/internship-scheme",
            helpline_number="011-24364756",
            tags="internship, student, technology, ai, stipend, coding, graduate",
            is_active=True,
            featured=False
        )

        EligibilityRule.objects.create(
            scheme=tech_intern, rule_field='occupation', operator='in', expected_values='["student", "unemployed"]',
            legal_clause_text="Candidate must be enrolled student or recent graduate in STEM streams.",
            plain_language_rule="✓ Matched: You are a Student or recent graduate.",
            is_mandatory=True
        )
        EligibilityRule.objects.create(
            scheme=tech_intern, rule_field='education_level', operator='in', expected_values='["graduate", "postgraduate", "diploma_iti"]',
            legal_clause_text="Minimum enrollment in recognized tertiary technical qualifications.",
            plain_language_rule="✓ Matched: Education level is College Graduate / Diploma / Tech student.",
            is_mandatory=True
        )
        EligibilityRule.objects.create(
            scheme=tech_intern, rule_field='age_group', operator='in', expected_values='["18-25", "26-40"]',
            legal_clause_text="Age bracket between 18 to 28 years as of application closing date.",
            plain_language_rule="✓ Matched: Age fits the youth internship guidelines.",
            is_mandatory=True
        )

        DocumentRequirement.objects.create(
            scheme=tech_intern, document_name="College NOC / Recommendation Letter",
            why_required="Confirms college authorization to undertake 3-6 months internship.",
            issuing_authority="Head of Department / Dean", is_mandatory=True, digilocker_available=False
        )
        DocumentRequirement.objects.create(
            scheme=tech_intern, document_name="Technical Resume & Portfolio",
            why_required="Evaluates programming, technical, or analytical skills for project placement.",
            issuing_authority="Applicant", is_mandatory=True, digilocker_available=False
        )

        # -------------------------------------------------------------
        # 7. PM Surya Ghar (Renewable Energy)
        # -------------------------------------------------------------
        solar = Scheme.objects.create(
            code="SURYA-GHAR",
            name="PM Surya Ghar: Muft Bijli Yojana",
            short_title="PM Rooftop Solar Subsidy",
            ministry="Ministry of New and Renewable Energy (MNRE)",
            level="CENTRAL",
            state_scope="ALL",
            sector_category="Green Energy",
            benefit_highlight="Direct Cash Subsidy up to ₹78,000 for 3kW Solar + Up to 300 Units Free Power / Month",
            legal_description="The scheme provides capital subsidy for residential rooftop solar plant installations: ₹30,000 for 1kW, ₹60,000 for 2kW, and ₹78,000 for 3kW or higher systems. Grid-tied net metering is facilitated through local distribution companies (DISCOMs).",
            plain_language_summary="Government pays up to ₹78,000 directly into your bank account when you install rooftop solar panels on your house, bringing your electricity bill down to ₹0 while earning money by feeding surplus solar power into the grid.",
            plain_language_eligibility="• You own a residential house with suitable unshaded roof space.\n• You have an active domestic electricity connection in your or family member's name.\n• No previous government solar subsidy claimed for the same electricity meter.",
            application_process="1. Register on National Rooftop Solar Portal (pmsuryaghar.gov.in) with electricity consumer number.\n2. Apply online for technical feasibility approval from your local DISCOM.\n3. Choose any registered solar vendor and get rooftop installation completed.\n4. DISCOM inspects installation and installs bi-directional net meter.\n5. Central subsidy (₹78,000) is credited to your bank account within 30 days.",
            deadline_text="Open Throughout Year",
            official_portal_name="PM Surya Ghar National Portal",
            official_portal_url="https://pmsuryaghar.gov.in",
            helpline_number="15555",
            tags="solar, electricity, green energy, subsidy, rooftop, power",
            is_active=True,
            featured=False
        )

        EligibilityRule.objects.create(
            scheme=solar, rule_field='age_group', operator='in', expected_values='["18-25", "26-40", "41-59", "60+"]',
            legal_clause_text="Applicant must be an adult Indian citizen with residential power meter.",
            plain_language_rule="✓ Matched: Adult homeowner with electricity meter.",
            is_mandatory=False
        )

        DocumentRequirement.objects.create(
            scheme=solar, document_name="Latest Electricity Bill (Last 3 Months)",
            why_required="Verifies active domestic electricity connection number and sanctioned load.",
            issuing_authority="State Electricity DISCOM", is_mandatory=True, digilocker_available=True
        )
        DocumentRequirement.objects.create(
            scheme=solar, document_name="Roof Ownership / House Tax Receipt",
            why_required="Confirms legal right to install solar panels on the roof.",
            issuing_authority="Municipal Corporation / Panchayat", is_mandatory=True, digilocker_available=True
        )

        # -------------------------------------------------------------
        # 8. Mukhyamantri Mahila Udyami Yojana (State: Women Entrepreneurship)
        # -------------------------------------------------------------
        mahila_biz = Scheme.objects.create(
            code="MMUY-STATE",
            name="Mukhyamantri Mahila Udyami Yojana",
            short_title="Women Entrepreneur Startup Grant",
            ministry="Department of Industries & State MSME Mission",
            level="STATE",
            state_scope="Uttar Pradesh, Bihar, Madhya Pradesh, Rajasthan, Maharashtra",
            sector_category="Women Empowerment",
            benefit_highlight="₹10,00,000 Total Assistance (₹5,00,000 100% Free Grant + ₹5 Lakh Interest-Free Loan)",
            legal_description="State flagship scheme to stimulate industrial enterprise among women. Total project outlay of INR 10 Lakhs is financed through 50% non-repayable capital grant (INR 5 Lakh) and 50% interest-free term loan repayable in 84 monthly installments after a one-year moratorium period.",
            plain_language_summary="A dedicated women's enterprise initiative where the state government gives ₹10 Lakh to help women start a manufacturing or service enterprise — where ₹5 Lakh is a completely free grant and ₹5 Lakh is a 0% interest loan with 7 years to repay.",
            plain_language_eligibility="• Woman citizen aged 18 to 50 years.\n• Resident of participating state (UP, Bihar, MP, Rajasthan, Maharashtra).\n• Educational qualification: 12th pass, ITI, Polytechnic, or Graduate degree.\n• Individual enterprise or 100% women-owned partnership.",
            application_process="1. Register on the State Udyami Portal with Aadhaar and educational certificates.\n2. Select your desired manufacturing/service industry trade from the approved 102 trades list.\n3. Shortlisted applicants attend 2-week free state entrepreneurship training.\n4. Grant amount (₹5 Lakh) + Interest-free loan sanctioned in phased tranches.\n5. Government field mentors assist in factory setup, machinery procurement, and GST registration.",
            deadline_text="Quarterly Selection Cycles",
            official_portal_name="State Industries & MSME Portal",
            official_portal_url="https://udyami.bihar.gov.in",
            helpline_number="1800-345-6214",
            tags="women, entrepreneur, loan, grant, zero interest, factory, startup",
            is_active=True,
            featured=True
        )

        EligibilityRule.objects.create(
            scheme=mahila_biz, rule_field='specific_category', operator='in', expected_values='["woman_entrepreneur", "sc", "st", "obc", "pwd", "general"]',
            legal_clause_text="Scheme specifically tailored for women citizens residing in the state.",
            plain_language_rule="✓ Matched: Targeted for Women Entrepreneurs and enterprise founders.",
            is_mandatory=True
        )
        EligibilityRule.objects.create(
            scheme=mahila_biz, rule_field='education_level', operator='in', expected_values='["12th_pass", "graduate", "postgraduate", "diploma_iti"]',
            legal_clause_text="Minimum intermediate (10+2) or equivalent technical diploma.",
            plain_language_rule="✓ Matched: 12th Pass or higher technical qualification.",
            is_mandatory=True
        )

        DocumentRequirement.objects.create(
            scheme=mahila_biz, document_name="State Domicile Certificate (Niwas Praman Patra)",
            why_required="Proves permanent residency in the state.",
            issuing_authority="Sub-Divisional Magistrate (SDM) / Revenue Officer", is_mandatory=True, digilocker_available=True
        )
        DocumentRequirement.objects.create(
            scheme=mahila_biz, document_name="12th / Diploma / Degree Certificate",
            why_required="Validates educational eligibility for industrial entrepreneurship scheme.",
            issuing_authority="State Board / University", is_mandatory=True, digilocker_available=True
        )
        DocumentRequirement.objects.create(
            scheme=mahila_biz, document_name="Current Bank Account / Cancelled Cheque",
            why_required="Business bank account for disbursing loan-cum-subsidy funds.",
            issuing_authority="Bank Branch", is_mandatory=True, digilocker_available=False
        )

        # -------------------------------------------------------------
        # Seed Mock Citizen Profiles & Applications for Live Status Tracking
        # -------------------------------------------------------------
        prof_ramesh = CitizenProfile.objects.create(
            full_name="Ramesh Kumar",
            age_group="41-59",
            education_level="10th_pass",
            occupation="farmer",
            state="Uttar Pradesh",
            income_bracket="low_income",
            specific_category="obc"
        )

        app_kisan = ApplicationRecord.objects.create(
            application_number="APP-KISAN-2026-8942",
            scheme=pm_kisan,
            applicant_name="Ramesh Kumar",
            applicant_phone="+91 98765 43210",
            applicant_email="ramesh.k@example.gov.in",
            citizen_profile=prof_ramesh,
            current_status="SANCTIONED",
            status_summary="Sanction order issued by District Agriculture Officer. DBT payment queue active.",
            official_portal_ref="PMK-UP-VARANASI-2026-8942",
            benefit_amount="₹6,000 / year (First tranche ₹2,000 ready for credit)"
        )
        NotificationService.trigger_status_update(
            app_kisan, "SUBMITTED",
            remarks="Application successfully received at Tehsil verification portal.",
            officer_name="Tehsil Revenue Clerk"
        )
        NotificationService.trigger_status_update(
            app_kisan, "DOCUMENT_VERIFICATION",
            remarks="Land records (Khatauni) cross-verified with UP Bhulekh database. All verified.",
            officer_name="Lekhpal / Revenue Officer"
        )
        NotificationService.trigger_status_update(
            app_kisan, "SANCTIONED",
            remarks="District Level Sanction Order #DAO/2026/8942 approved. DBT payment instruction forwarded to PFMS.",
            officer_name="District Agriculture Officer, Varanasi"
        )

        # Application 2: Scholarship (Document Verification)
        prof_amit = CitizenProfile.objects.create(
            full_name="Amit Kumar Das",
            age_group="18-25",
            education_level="graduate",
            occupation="student",
            state="Maharashtra",
            income_bracket="low_income",
            specific_category="sc"
        )
        app_scholar = ApplicationRecord.objects.create(
            application_number="APP-SCHOLAR-2026-1049",
            scheme=scholarship,
            applicant_name="Amit Kumar Das",
            applicant_phone="+91 98112 34567",
            applicant_email="amit.das@example.edu.in",
            citizen_profile=prof_amit,
            current_status="DOCUMENT_VERIFICATION",
            status_summary="College nodal verification completed. State scholarship cell reviewing income certificate.",
            official_portal_ref="NSP-MH-2026-104988",
            benefit_amount="₹48,000 Tuition Waiver + ₹1,200/mo Maintenance Allowance"
        )
        NotificationService.trigger_status_update(
            app_scholar, "SUBMITTED",
            remarks="Online NSP registration completed. College verification pending.",
            officer_name="NSP Automated Bridge"
        )
        NotificationService.trigger_status_update(
            app_scholar, "DOCUMENT_VERIFICATION",
            remarks="College Dean validated enrollment record. State social welfare cell reviewing income certificate authenticity.",
            officer_name="College Nodal Officer & State Desk"
        )

        # Application 3: PMEGP Business (Field Inspection)
        prof_sunita = CitizenProfile.objects.create(
            full_name="Sunita Verma",
            age_group="26-40",
            education_level="graduate",
            occupation="business_owner",
            state="Madhya Pradesh",
            income_bracket="lower_middle",
            specific_category="woman_entrepreneur"
        )
        app_pmegp = ApplicationRecord.objects.create(
            application_number="APP-PMEGP-2026-5521",
            scheme=pmegp,
            applicant_name="Sunita Verma",
            applicant_phone="+91 97554 11223",
            applicant_email="sunita.verma@ecobiz.in",
            citizen_profile=prof_sunita,
            current_status="FIELD_INSPECTION",
            status_summary="District Level Task Force Committee (DLTFC) scheduled site inspection for Food Processing Unit.",
            official_portal_ref="KVIC-MP-BHOPAL-5521",
            benefit_amount="35% Rural Subsidy on ₹18,50,000 Loan (Govt Grant: ₹6,47,500)"
        )
        NotificationService.trigger_status_update(
            app_pmegp, "SUBMITTED",
            remarks="PMEGP e-Portal application submitted with DPR for Agro-Processing unit.",
            officer_name="KVIC Portal Gateway"
        )
        NotificationService.trigger_status_update(
            app_pmegp, "DOCUMENT_VERIFICATION",
            remarks="Project financial viability and PAN/Caste certificates verified by DIC Officer.",
            officer_name="General Manager, District Industries Centre"
        )
        NotificationService.trigger_status_update(
            app_pmegp, "FIELD_INSPECTION",
            remarks="Physical inspection of proposed manufacturing shed scheduled for 12th of this month. Keep building ownership documents ready.",
            officer_name="Lead District Bank Officer & DIC Inspector"
        )

        # Application 4: Action Required on Mahila Udyami
        prof_anjali = CitizenProfile.objects.create(
            full_name="Anjali Kumari",
            age_group="26-40",
            education_level="12th_pass",
            occupation="business_owner",
            state="Bihar",
            income_bracket="low_income",
            specific_category="woman_entrepreneur"
        )
        app_mahila = ApplicationRecord.objects.create(
            application_number="APP-MAHILA-2026-9012",
            scheme=mahila_biz,
            applicant_name="Anjali Kumari",
            applicant_phone="+91 94310 88990",
            applicant_email="anjali.udyami@example.com",
            citizen_profile=prof_anjali,
            current_status="ACTION_REQUIRED",
            status_summary="⚠️ Upload required: Clear digital copy of Domicile Certificate (Niwas Praman Patra).",
            official_portal_ref="BIH-UDYAMI-2026-9012",
            benefit_amount="₹5,00,000 Grant + ₹5,00,000 Interest-Free Loan"
        )
        NotificationService.trigger_status_update(
            app_mahila, "SUBMITTED",
            remarks="Online registration for Garment Manufacturing unit submitted.",
            officer_name="State Udyami Portal"
        )
        NotificationService.trigger_status_update(
            app_mahila, "ACTION_REQUIRED",
            remarks="Uploaded Domicile Certificate is blurred/unreadable. Please re-upload a clear copy issued by SDM or Circle Officer.",
            officer_name="State Scrutiny Desk, Patna",
            action_note="Upload clear PDF of Domicile Certificate within 7 days to avoid application cancellation."
        )

        # Application 5: PM Awas Yojana (Disbursed)
        prof_meena = CitizenProfile.objects.create(
            full_name="Meena Devi",
            age_group="41-59",
            education_level="none",
            occupation="gig_worker",
            state="Rajasthan",
            income_bracket="bpl",
            specific_category="woman_entrepreneur"
        )
        app_awas = ApplicationRecord.objects.create(
            application_number="APP-AWAS-2026-7734",
            scheme=pm_awas,
            applicant_name="Meena Devi",
            applicant_phone="+91 96101 22334",
            applicant_email="",
            citizen_profile=prof_meena,
            current_status="DISBURSED",
            status_summary="All 3 tranches (₹1,20,000) + Swachh Bharat toilet grant (₹12,000) credited via PFMS DBT.",
            official_portal_ref="PMAYG-RJ-JAIPUR-7734",
            benefit_amount="₹1,32,000 (Full Construction Grant Credited)"
        )
        NotificationService.trigger_status_update(
            app_awas, "SUBMITTED",
            remarks="PMAY-G registration registered under Gram Sabha priority list.",
            officer_name="Gram Rozgar Sevak"
        )
        NotificationService.trigger_status_update(
            app_awas, "FIELD_INSPECTION",
            remarks="Geo-tagged photos of foundation and lintel level uploaded and approved on AwaasSoft.",
            officer_name="Block Development Officer"
        )
        NotificationService.trigger_status_update(
            app_awas, "SANCTIONED",
            remarks="Final completion certificate signed by Block Engineer.",
            officer_name="District Rural Development Agency (DRDA)"
        )
        NotificationService.trigger_status_update(
            app_awas, "DISBURSED",
            remarks="Final installment of ₹40,000 credited to Bank of Baroda A/c ending 8812. Total ₹1.32 Lakh released.",
            officer_name="Public Financial Management System (PFMS)"
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded 8 real-world government schemes, rules, and 5 live test application tracking records!"))
