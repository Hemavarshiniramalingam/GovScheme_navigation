import json
import uuid
import random
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Count, Q
from schemes.models import Scheme, EligibilityRule, DocumentRequirement, CitizenProfile, ApplicationRecord, StatusHistory, NotificationLog
from schemes.services.matcher import SchemeMatcher
from schemes.services.nlp_explainer import LegalToPlainLanguageTranslator
from schemes.services.notification_service import NotificationService

def get_or_create_profile(request):
    """Helper to maintain citizen profile across session"""
    profile_id = request.session.get('citizen_profile_id')
    profile = None
    if profile_id:
        try:
            profile = CitizenProfile.objects.get(id=profile_id)
        except CitizenProfile.DoesNotExist:
            profile = None
    return profile

def home_view(request):
    """Portal Home Page with Hero, Quick Stats, Categories, and 6-Step Intake Wizard"""
    profile = get_or_create_profile(request)
    
    total_schemes = Scheme.objects.filter(is_active=True).count()
    featured_schemes = Scheme.objects.filter(is_active=True, featured=True)[:4]
    sectors = Scheme.objects.values_list('sector_category', flat=True).distinct()
    
    # Quick sample tracking applications
    sample_apps = ApplicationRecord.objects.all().select_related('scheme')[:4]

    context = {
        'total_schemes': total_schemes,
        'featured_schemes': featured_schemes,
        'sectors': sorted(list(set(sectors))),
        'profile': profile,
        'sample_apps': sample_apps,
    }
    return render(request, 'home.html', context)

def results_view(request):
    """Personalized Scheme Matches Dashboard with Plain-Language Reasoning"""
    # Extract intake parameters from GET or session
    age_group = request.GET.get('age_group', '26-40')
    education_level = request.GET.get('education_level', '12th_pass')
    occupation = request.GET.get('occupation', 'farmer')
    state = request.GET.get('state', 'Uttar Pradesh')
    income_bracket = request.GET.get('income_bracket', 'low_income')
    specific_category = request.GET.get('specific_category', 'general')

    sector_filter = request.GET.get('sector', 'ALL')
    level_filter = request.GET.get('level', 'ALL')
    query = request.GET.get('q', '').strip()

    profile_data = {
        'age_group': age_group,
        'education_level': education_level,
        'occupation': occupation,
        'state': state,
        'income_bracket': income_bracket,
        'specific_category': specific_category,
    }

    # Save to session profile
    profile = get_or_create_profile(request)
    if not profile:
        profile = CitizenProfile.objects.create(
            age_group=age_group,
            education_level=education_level,
            occupation=occupation,
            state=state,
            income_bracket=income_bracket,
            specific_category=specific_category,
        )
        request.session['citizen_profile_id'] = str(profile.id)
    else:
        profile.age_group = age_group
        profile.education_level = education_level
        profile.occupation = occupation
        profile.state = state
        profile.income_bracket = income_bracket
        profile.specific_category = specific_category
        profile.save()

    # Evaluate matching
    matching_result = SchemeMatcher.match_all(
        profile_data,
        sector_filter=sector_filter,
        level_filter=level_filter,
        query=query
    )

    sectors = Scheme.objects.values_list('sector_category', flat=True).distinct()

    context = {
        'profile_data': profile_data,
        'profile': profile,
        'matching_result': matching_result,
        'eligible_schemes': matching_result['eligible_schemes'],
        'other_schemes': matching_result['other_schemes'],
        'total_evaluated': matching_result['total_evaluated'],
        'eligible_count': matching_result['eligible_count'],
        'sector_filter': sector_filter,
        'level_filter': level_filter,
        'query': query,
        'sectors': sorted(list(set(sectors))),
    }
    return render(request, 'results.html', context)

def scheme_detail_view(request, scheme_code):
    """Deep-dive Scheme View with Side-by-Side Legal vs Plain Language Explainer"""
    scheme = get_or_create_profile(request)
    scheme_obj = get_object_or_404(Scheme, code=scheme_code)
    
    # Process with NLP synthesizer
    nlp_summary = LegalToPlainLanguageTranslator.generate_citizen_summary(scheme_obj)
    
    # Process application steps
    steps = [s.strip() for s in scheme_obj.application_process.split('\n') if s.strip()]
    
    # Process eligibility bullet points
    eligibility_bullets = [e.strip() for e in scheme_obj.plain_language_eligibility.split('\n') if e.strip()]

    context = {
        'scheme': scheme_obj,
        'nlp_summary': nlp_summary,
        'steps': steps,
        'eligibility_bullets': eligibility_bullets,
        'documents': scheme_obj.documents.all(),
        'rules': scheme_obj.rules.all(),
    }
    return render(request, 'scheme_detail.html', context)

def track_status_view(request):
    """Application Status Tracking Center with 5-Stage Stepper & Action Prompts"""
    app_num = request.GET.get('app_num', '').strip()
    application = None
    stage_index = 1
    history_logs = []
    error_message = None

    if app_num:
        try:
            application = ApplicationRecord.objects.select_related('scheme', 'citizen_profile').prefetch_related('history').get(
                Q(application_number__iexact=app_num) | Q(official_portal_ref__iexact=app_num)
            )
            history_logs = application.history.all()
            
            # Map status to stage index (1 to 5)
            stage_map = {
                'SUBMITTED': 1,
                'DOCUMENT_VERIFICATION': 2,
                'FIELD_INSPECTION': 3,
                'SANCTIONED': 4,
                'DISBURSED': 5,
                'ACTION_REQUIRED': 2,
                'REJECTED': 0
            }
            stage_index = stage_map.get(application.current_status, 1)

        except ApplicationRecord.DoesNotExist:
            error_message = f"No application record found for reference '{app_num}'. Please check your application ID or try one of the sample tracking IDs."

    # Sample applications for quick one-click testing
    all_sample_apps = ApplicationRecord.objects.all().select_related('scheme')[:6]

    context = {
        'app_num': app_num,
        'application': application,
        'stage_index': stage_index,
        'history_logs': history_logs,
        'error_message': error_message,
        'sample_apps': all_sample_apps,
    }
    return render(request, 'track_status.html', context)

def blueprint_view(request):
    """In-app Technical Architecture Blueprint & System Specifications Viewer"""
    return render(request, 'blueprint.html')

# -------------------------------------------------------------
# REST & AJAX API Endpoints
# -------------------------------------------------------------

@require_GET
def api_track_status(request):
    """API endpoint for fetching status history asynchronously"""
    app_num = request.GET.get('app_num', '').strip()
    if not app_num:
        return JsonResponse({'success': False, 'error': 'Application number is required'}, status=400)

    try:
        app = ApplicationRecord.objects.select_related('scheme').prefetch_related('history').get(
            Q(application_number__iexact=app_num) | Q(official_portal_ref__iexact=app_num)
        )
        
        stage_map = {
            'SUBMITTED': 1,
            'DOCUMENT_VERIFICATION': 2,
            'FIELD_INSPECTION': 3,
            'SANCTIONED': 4,
            'DISBURSED': 5,
            'ACTION_REQUIRED': 2,
            'REJECTED': 0
        }

        history_data = [
            {
                'stage': h.stage,
                'title': h.title,
                'remarks': h.officer_remarks,
                'action_note': h.action_required_note,
                'officer': h.updated_by,
                'date': h.timestamp.strftime('%d %b %Y, %I:%M %p')
            }
            for h in app.history.all()
        ]

        return JsonResponse({
            'success': True,
            'application_number': app.application_number,
            'scheme_name': app.scheme.name,
            'scheme_code': app.scheme.code,
            'applicant_name': app.applicant_name,
            'current_status': app.current_status,
            'status_label': app.get_current_status_display(),
            'status_summary': app.status_summary,
            'stage_index': stage_map.get(app.current_status, 1),
            'benefit_amount': app.benefit_amount,
            'portal_ref': app.official_portal_ref,
            'history': history_data
        })
    except ApplicationRecord.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Application not found'}, status=404)

@csrf_exempt
@require_POST
def api_simulate_transition(request):
    """
    Simulation API: Allows reviewers/citizens to step forward application stages
    and watch real-time notification alerts trigger!
    """
    try:
        data = json.loads(request.body)
        app_num = data.get('app_num')
        target_status = data.get('target_status')
        remarks = data.get('remarks', '')
        officer = data.get('officer', 'State Verification Officer')
        action_note = data.get('action_note', '')

        app = ApplicationRecord.objects.get(application_number=app_num)
        NotificationService.trigger_status_update(
            app,
            new_status=target_status,
            remarks=remarks or f"Status transitioned to {target_status.replace('_', ' ').title()} during system verification.",
            officer_name=officer,
            action_note=action_note
        )

        return JsonResponse({
            'success': True,
            'message': f"Application {app_num} updated to {target_status}",
            'new_status': target_status,
            'status_label': app.get_current_status_display()
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@require_POST
def api_quick_apply(request):
    """
    Simulates a citizen 1-Click Guided Application creation
    Generates a unique Application Tracking ID and dispatches submission notifications!
    """
    try:
        data = json.loads(request.body)
        scheme_code = data.get('scheme_code')
        applicant_name = data.get('applicant_name', 'Citizen Applicant')
        applicant_phone = data.get('applicant_phone', '+91 98765 00000')
        applicant_email = data.get('applicant_email', 'applicant@example.gov.in')

        scheme = Scheme.objects.get(code=scheme_code)
        profile = get_or_create_profile(request)

        # Generate unique Gov-format application number
        random_digits = random.randint(1000, 9999)
        prefix = scheme_code.replace('-', '')[:6].upper()
        app_number = f"APP-{prefix}-2026-{random_digits}"

        app_record = ApplicationRecord.objects.create(
            application_number=app_number,
            scheme=scheme,
            applicant_name=applicant_name,
            applicant_phone=applicant_phone,
            applicant_email=applicant_email,
            citizen_profile=profile,
            current_status='SUBMITTED',
            status_summary="Application successfully registered on GovScheme portal. Under primary scrutiny.",
            official_portal_ref=f"GOV-{prefix}-{random_digits}",
            benefit_amount=scheme.benefit_highlight
        )

        # Trigger submission notification
        NotificationService.trigger_status_update(
            app_record,
            new_status='SUBMITTED',
            remarks=f"Application registered with {scheme.official_portal_name}. Verification queue assigned.",
            officer_name="GovScheme Central Gateway"
        )

        return JsonResponse({
            'success': True,
            'application_number': app_number,
            'scheme_name': scheme.name,
            'redirect_url': f"/track/?app_num={app_number}"
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@require_GET
def api_get_notifications(request):
    """Returns recent notification alerts for the top-bar notification drawer"""
    notifs = NotificationLog.objects.all().select_related('scheme')[:12]
    
    data = [
        {
            'id': str(n.id),
            'title': n.title,
            'message': n.message,
            'type': n.notification_type,
            'channel': n.channel,
            'is_read': n.is_read,
            'action_url': n.action_url,
            'time_ago': n.created_at.strftime('%d %b %H:%M')
        }
        for n in notifs
    ]
    return JsonResponse({
        'success': True,
        'count': len(data),
        'unread_count': len([x for x in data if not x['is_read']]),
        'notifications': data
    })

@csrf_exempt
@require_POST
def api_mark_notification_read(request, notif_id):
    """Marks a notification as read"""
    try:
        notif = NotificationLog.objects.get(id=notif_id)
        notif.is_read = True
        notif.save()
        return JsonResponse({'success': True})
    except NotificationLog.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'}, status=404)
