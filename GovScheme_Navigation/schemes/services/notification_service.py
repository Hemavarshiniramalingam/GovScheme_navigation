from schemes.models import NotificationLog, ApplicationRecord, StatusHistory

class NotificationService:
    """
    Multi-channel notification dispatcher and event bus.
    Triggers citizen alerts via SMS, WhatsApp, Email, and In-App drawers.
    """

    TEMPLATES = {
        'SUBMITTED': {
            'title': 'Application Submitted: {scheme_name}',
            'sms': 'GovScheme Alert: Your application {app_num} for {scheme_name} has been received and forwarded for scrutiny. Track at: {track_url}',
            'whatsapp': '🏛️ *GovScheme Official Update*\n\nHello {name},\nYour application *{app_num}* for *{scheme_name}* has been successfully submitted.\n\n📅 *Date:* {date}\n🔗 *Track Status:* {track_url}',
            'email': 'Your application {app_num} for {scheme_name} is under initial departmental review.'
        },
        'DOCUMENT_VERIFICATION': {
            'title': 'Documents Under Verification: {scheme_name}',
            'sms': 'GovScheme Alert: Your documents for {app_num} are currently being scrutinized by the verification officer.',
            'whatsapp': '📄 *Document Verification In Progress*\n\nApplication: *{app_num}*\nScheme: *{scheme_name}*\nRemarks: {remarks}',
            'email': 'Verification officers are reviewing your submitted documents for {app_num}.'
        },
        'ACTION_REQUIRED': {
            'title': '⚠️ Action Required: Additional Document Needed',
            'sms': 'GovScheme URGENT: Additional document required for application {app_num}. Please upload before deadline: {track_url}',
            'whatsapp': '⚠️ *Action Required for Application {app_num}*\n\nReason: {remarks}\n👉 Please submit the missing document immediately at {track_url}',
            'email': 'Action required on your government application {app_num}. Please review officer remarks.'
        },
        'FIELD_INSPECTION': {
            'title': 'Field Verification Scheduled: {scheme_name}',
            'sms': 'GovScheme Update: Field inspection officer assigned for {app_num}. Please keep original documents ready.',
            'whatsapp': '🔍 *Field Inspection Notice*\n\nApplication: *{app_num}*\nOfficer has been assigned for field validation. Please keep your physical IDs and land/business records handy.',
            'email': 'Field verification stage initiated for {app_num}.'
        },
        'SANCTIONED': {
            'title': '🎉 Sanction Order Issued: {scheme_name}',
            'sms': 'GovScheme CONGRATULATIONS! Sanction Order approved for application {app_num}. Benefit: {benefit}.',
            'whatsapp': '🎉 *Congratulations! Scheme Sanctioned*\n\nApplication: *{app_num}*\nScheme: *{scheme_name}*\nBenefit: *{benefit}*\nYour sanction letter is ready to download!',
            'email': 'Sanction order approved for {app_num}. Benefit processing has been initiated.'
        },
        'DISBURSED': {
            'title': '✅ Funds Disbursed / DBT Credited: {scheme_name}',
            'sms': 'GovScheme SUCCESS: Benefit amount for {app_num} has been disbursed via DBT/PFMS to your linked bank account.',
            'whatsapp': '✅ *Benefit Disbursal Successful*\n\nApplication: *{app_num}*\nScheme: *{scheme_name}*\nStatus: Transferred via Direct Benefit Transfer (Aadhaar / PFMS).',
            'email': 'Your government benefit for {app_num} has been successfully credited.'
        },
        'DEADLINE_REMINDER': {
            'title': '⏳ Deadline Approaching: {scheme_name}',
            'sms': 'GovScheme Reminder: Application deadline for {scheme_name} is approaching ({deadline}). Apply now: {apply_url}',
            'whatsapp': '⏳ *Upcoming Scheme Deadline*\n\nScheme: *{scheme_name}*\nDeadline: *{deadline}*\nDon\'t miss out on benefits up to {benefit}!\nApply here: {apply_url}',
            'email': 'Scheme application deadline reminder for {scheme_name}.'
        }
    }

    @classmethod
    def trigger_status_update(cls, application, new_status, remarks="", officer_name="District Nodal Officer", action_note=""):
        """
        Updates application status, logs history, and dispatches multi-channel notifications.
        """
        application.current_status = new_status
        application.status_summary = remarks or f"Status changed to {new_status}"
        application.save()

        # Add history log
        history = StatusHistory.objects.create(
            application=application,
            stage=new_status,
            title=new_status.replace('_', ' ').title(),
            officer_remarks=remarks or f"Application reached {new_status.replace('_', ' ').title()} stage.",
            action_required_note=action_note,
            updated_by=officer_name
        )

        template = cls.TEMPLATES.get(new_status, cls.TEMPLATES['SUBMITTED'])
        scheme_name = application.scheme.short_title or application.scheme.name
        
        ctx = {
            'name': application.applicant_name,
            'app_num': application.application_number,
            'scheme_name': scheme_name,
            'track_url': f"/track/?app_num={application.application_number}",
            'remarks': remarks or 'Application is progressing smoothly.',
            'date': application.last_updated.strftime('%d %b %Y'),
            'benefit': application.benefit_amount or application.scheme.benefit_highlight,
        }

        # Create In-App Notification
        title = template['title'].format(**ctx)
        msg = template['whatsapp'].format(**ctx)
        
        NotificationLog.objects.create(
            citizen_profile=application.citizen_profile,
            application=application,
            scheme=application.scheme,
            notification_type='ACTION_REQUIRED' if new_status == 'ACTION_REQUIRED' else 'STATUS_UPDATE',
            channel='IN_APP',
            title=title,
            message=msg,
            action_url=f"/track/?app_num={application.application_number}"
        )

        # Create simulated SMS Log
        NotificationLog.objects.create(
            citizen_profile=application.citizen_profile,
            application=application,
            scheme=application.scheme,
            notification_type='STATUS_UPDATE',
            channel='SMS',
            title=f"SMS: {title}",
            message=template['sms'].format(**ctx),
            action_url=f"/track/?app_num={application.application_number}"
        )

        # Create simulated WhatsApp Log
        NotificationLog.objects.create(
            citizen_profile=application.citizen_profile,
            application=application,
            scheme=application.scheme,
            notification_type='STATUS_UPDATE',
            channel='WHATSAPP',
            title=f"WhatsApp: {title}",
            message=msg,
            action_url=f"/track/?app_num={application.application_number}"
        )

        return history
