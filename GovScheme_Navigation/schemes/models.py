from django.db import models
import uuid

class CitizenProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_key = models.CharField(max_length=100, db_index=True, blank=True, null=True)
    full_name = models.CharField(max_length=150, blank=True, default="Citizen")
    age_group = models.CharField(max_length=50, help_text="e.g. 18-25, 26-40, 41-59, 60+")
    education_level = models.CharField(max_length=80, help_text="e.g. none, 10th_pass, 12th_pass, graduate, postgraduate")
    occupation = models.CharField(max_length=80, help_text="e.g. student, farmer, business_owner, salaried, unemployed, gig_worker")
    state = models.CharField(max_length=80, help_text="State or Union Territory")
    income_bracket = models.CharField(max_length=80, help_text="e.g. bpl, low_income, lower_middle, middle, higher")
    specific_category = models.CharField(max_length=80, help_text="e.g. general, obc, sc, st, pwd, woman_entrepreneur, minority")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile ({self.occupation}, {self.state}, {self.income_bracket})"


class Scheme(models.Model):
    LEVEL_CHOICES = [
        ('CENTRAL', 'Central Government (All-India)'),
        ('STATE', 'State Government Specific'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True, help_text="Short code e.g. PM-KISAN")
    name = models.CharField(max_length=255, help_text="Official Scheme Full Title")
    short_title = models.CharField(max_length=100, blank=True)
    ministry = models.CharField(max_length=255, help_text="Administering Ministry or Department")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='CENTRAL')
    state_scope = models.CharField(max_length=100, default='ALL', help_text="'ALL' or specific state name")
    sector_category = models.CharField(max_length=100, default='General', help_text="Agriculture, Education, Business, Health, Social Welfare, Housing")
    
    benefit_highlight = models.CharField(max_length=255, help_text="Key benefit e.g. ₹6,000 / year DBT or 35% Capital Subsidy")
    legal_description = models.TextField(help_text="Original gazette / statutory legal text")
    plain_language_summary = models.TextField(help_text="Simplified conversational summary for citizens")
    plain_language_eligibility = models.TextField(help_text="Simplified bullet points for citizen criteria")
    application_process = models.TextField(help_text="Markdown or JSON step-by-step application instructions")
    
    application_deadline = models.DateField(null=True, blank=True)
    deadline_text = models.CharField(max_length=100, default="Open Throughout Year")
    official_portal_name = models.CharField(max_length=150, default="National Portal of India")
    official_portal_url = models.URLField(max_length=500)
    helpline_number = models.CharField(max_length=50, blank=True, default="1800-115-555")
    
    tags = models.CharField(max_length=255, blank=True, help_text="Comma separated tags e.g. farmer, subsidy, direct_benefit")
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-featured', 'name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class EligibilityRule(models.Model):
    RULE_FIELD_CHOICES = [
        ('age_group', 'Age Group'),
        ('education_level', 'Education Level'),
        ('occupation', 'Occupation / Profession'),
        ('state', 'State / Region'),
        ('income_bracket', 'Income Bracket'),
        ('specific_category', 'Specific Category / Social Status'),
    ]

    OPERATOR_CHOICES = [
        ('in', 'Is in list'),
        ('not_in', 'Is not in list'),
        ('eq', 'Equals'),
        ('any', 'Applies to any / All eligible'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scheme = models.ForeignKey(Scheme, related_name='rules', on_delete=models.CASCADE)
    rule_field = models.CharField(max_length=50, choices=RULE_FIELD_CHOICES)
    operator = models.CharField(max_length=20, choices=OPERATOR_CHOICES, default='in')
    expected_values = models.TextField(help_text="JSON or comma-separated list of matching values")
    
    legal_clause_text = models.TextField(blank=True, help_text="Verbatim legal gazette clause")
    plain_language_rule = models.CharField(max_length=255, help_text="Plain conversational explanation for citizen")
    is_mandatory = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.scheme.code} Rule ({self.rule_field} {self.operator} {self.expected_values})"


class DocumentRequirement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scheme = models.ForeignKey(Scheme, related_name='documents', on_delete=models.CASCADE)
    document_name = models.CharField(max_length=150)
    why_required = models.CharField(max_length=255, help_text="Clear citizen-friendly reason why this is needed")
    issuing_authority = models.CharField(max_length=150, default="Competent State / Central Authority")
    is_mandatory = models.BooleanField(default=True)
    digilocker_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.scheme.code} Doc: {self.document_name}"


class ApplicationRecord(models.Model):
    STATUS_CHOICES = [
        ('SUBMITTED', 'Application Submitted'),
        ('DOCUMENT_VERIFICATION', 'Document Verification in Progress'),
        ('FIELD_INSPECTION', 'Field / Physical Inspection'),
        ('SANCTIONED', 'Sanction Order Generated'),
        ('DISBURSED', 'Benefit Disbursed / Disbursal Pending'),
        ('ACTION_REQUIRED', 'Citizen Action Required (Missing Document)'),
        ('REJECTED', 'Application Rejected / Non-Eligible'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_number = models.CharField(max_length=60, unique=True, db_index=True)
    scheme = models.ForeignKey(Scheme, related_name='applications', on_delete=models.CASCADE)
    applicant_name = models.CharField(max_length=150)
    applicant_phone = models.CharField(max_length=20)
    applicant_email = models.EmailField(blank=True)
    citizen_profile = models.ForeignKey(CitizenProfile, null=True, blank=True, on_delete=models.SET_NULL)
    
    current_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='SUBMITTED')
    status_summary = models.CharField(max_length=255, default="Application under primary scrutiny")
    official_portal_ref = models.CharField(max_length=100, blank=True, help_text="Government backend reference ID")
    benefit_amount = models.CharField(max_length=100, blank=True, default="Pending Sanction")
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.application_number} ({self.applicant_name} - {self.scheme.code})"


class StatusHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(ApplicationRecord, related_name='history', on_delete=models.CASCADE)
    stage = models.CharField(max_length=30, choices=ApplicationRecord.STATUS_CHOICES)
    title = models.CharField(max_length=150)
    officer_remarks = models.TextField(help_text="Official remarks or clear guidance for next step")
    action_required_note = models.TextField(blank=True, null=True, help_text="Action citizen must take if any")
    updated_by = models.CharField(max_length=120, default="District Nodal Verification Cell")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.application.application_number} -> {self.stage} @ {self.timestamp}"


class NotificationLog(models.Model):
    TYPE_CHOICES = [
        ('STATUS_UPDATE', 'Application Status Update'),
        ('DEADLINE_REMINDER', 'Scheme Deadline Reminder'),
        ('NEW_SCHEME', 'New Scheme Alert'),
        ('ACTION_REQUIRED', 'Action Required / Document Request'),
    ]

    CHANNEL_CHOICES = [
        ('IN_APP', 'In-App Notification'),
        ('SMS', 'SMS Alert'),
        ('WHATSAPP', 'WhatsApp Official Alert'),
        ('EMAIL', 'Email Notification'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    citizen_profile = models.ForeignKey(CitizenProfile, null=True, blank=True, on_delete=models.CASCADE)
    application = models.ForeignKey(ApplicationRecord, null=True, blank=True, on_delete=models.CASCADE)
    scheme = models.ForeignKey(Scheme, null=True, blank=True, on_delete=models.CASCADE)
    
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='STATUS_UPDATE')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='IN_APP')
    title = models.CharField(max_length=200)
    message = models.TextField()
    action_url = models.CharField(max_length=255, blank=True, default="#")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.channel}] {self.title}"
