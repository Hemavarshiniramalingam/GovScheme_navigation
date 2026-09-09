from django.test import TestCase, Client
from django.urls import reverse
from schemes.models import Scheme, EligibilityRule, DocumentRequirement, CitizenProfile, ApplicationRecord, StatusHistory, NotificationLog
from schemes.services.matcher import SchemeMatcher
from schemes.services.nlp_explainer import LegalToPlainLanguageTranslator
from schemes.services.notification_service import NotificationService
import json

class GovSchemeCoreTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create a test scheme
        self.scheme = Scheme.objects.create(
            code="TEST-SCHEME",
            name="National Youth Entrepreneurship Grant",
            short_title="Youth Grant",
            ministry="Ministry of Skill Development & Entrepreneurship",
            level="CENTRAL",
            state_scope="ALL",
            sector_category="Business",
            benefit_highlight="₹5,00,000 Zero-Interest Loan Grant",
            legal_description="The scheme provides margin money subsidy to prospective micro-entrepreneurs having attained majority.",
            plain_language_summary="Government grant giving ₹5 Lakh loan to help young entrepreneurs start a business.",
            plain_language_eligibility="• Age between 18 and 40 years.\n• Small business or self-employed.\n• Low to lower-middle income.",
            application_process="1. Apply online.\n2. Submit project proposal.\n3. Receive bank sanction.",
            official_portal_url="https://example.gov.in",
            is_active=True
        )

        # Create rules
        EligibilityRule.objects.create(
            scheme=self.scheme,
            rule_field='occupation',
            operator='in',
            expected_values='["business_owner", "unemployed"]',
            plain_language_rule="✓ Matched: Business Owner or Unemployed youth.",
            is_mandatory=True
        )
        EligibilityRule.objects.create(
            scheme=self.scheme,
            rule_field='age_group',
            operator='in',
            expected_values='["18-25", "26-40"]',
            plain_language_rule="✓ Matched: Age fits 18-40 bracket.",
            is_mandatory=True
        )

        # Create document requirement
        DocumentRequirement.objects.create(
            scheme=self.scheme,
            document_name="Aadhaar Card",
            why_required="Identity and age verification.",
            is_mandatory=True
        )

    def test_matching_engine_eligible(self):
        """Test matching engine returns eligible for matching citizen profile"""
        profile_data = {
            'age_group': '18-25',
            'education_level': 'graduate',
            'occupation': 'business_owner',
            'state': 'Maharashtra',
            'income_bracket': 'low_income',
            'specific_category': 'general',
        }
        res = SchemeMatcher.evaluate_scheme(profile_data, self.scheme)
        self.assertTrue(res['is_eligible'])
        self.assertEqual(res['match_score'], 100)
        self.assertIn('✓ Matched: Business Owner', res['matched_reasons'][0])

    def test_matching_engine_ineligible(self):
        """Test matching engine returns ineligible when mandatory criteria fail"""
        profile_data = {
            'age_group': '60+',  # Failed age
            'education_level': 'graduate',
            'occupation': 'farmer',  # Failed occupation
            'state': 'Maharashtra',
            'income_bracket': 'low_income',
            'specific_category': 'general',
        }
        res = SchemeMatcher.evaluate_scheme(profile_data, self.scheme)
        self.assertFalse(res['is_eligible'])
        self.assertTrue(len(res['unmet_reasons']) > 0)

    def test_nlp_translation_and_readability(self):
        """Test legal to plain language glossary and readability calculation"""
        legal_sample = "Beneficiary with operational landholding subject to direct benefit transfer via PFMS."
        translated = LegalToPlainLanguageTranslator.translate_legal_text(legal_sample)
        self.assertIn("farm land owned or cultivated", translated)
        self.assertIn("direct cash payment transferred to your bank account", translated)
        
        readability = LegalToPlainLanguageTranslator.calculate_readability("This is a simple plain language guide for all citizens.")
        self.assertGreater(readability, 60.0)

    def test_application_lifecycle_and_notifications(self):
        """Test application status change triggers multi-channel notification records"""
        app = ApplicationRecord.objects.create(
            application_number="APP-TEST-2026-1111",
            scheme=self.scheme,
            applicant_name="Test Citizen",
            applicant_phone="+91 99999 88888",
            current_status="SUBMITTED"
        )

        history = NotificationService.trigger_status_update(
            app, "SANCTIONED",
            remarks="Sanction order issued by District Collector.",
            officer_name="District Collector"
        )
        self.assertEqual(app.current_status, "SANCTIONED")
        self.assertEqual(StatusHistory.objects.filter(application=app).count(), 1)
        
        notifs = NotificationLog.objects.filter(application=app)
        self.assertTrue(notifs.exists())
        self.assertTrue(any(n.channel == 'IN_APP' for n in notifs))
        self.assertTrue(any(n.channel == 'SMS' for n in notifs))
        self.assertTrue(any(n.channel == 'WHATSAPP' for n in notifs))

    def test_web_routes_and_api(self):
        """Test home, results, tracking, and REST endpoints"""
        # Test Home
        r_home = self.client.get(reverse('schemes:home'))
        self.assertEqual(r_home.status_code, 200)

        # Test Results
        r_results = self.client.get(reverse('schemes:results'), {
            'age_group': '18-25',
            'occupation': 'business_owner'
        })
        self.assertEqual(r_results.status_code, 200)

        # Test Detail
        r_detail = self.client.get(reverse('schemes:scheme_detail', args=[self.scheme.code]))
        self.assertEqual(r_detail.status_code, 200)

        # Test Track Status
        r_track = self.client.get(reverse('schemes:track_status'))
        self.assertEqual(r_track.status_code, 200)

        # Test Notification API
        r_notif = self.client.get(reverse('schemes:api_notifications'))
        self.assertEqual(r_notif.status_code, 200)
        data = json.loads(r_notif.content)
        self.assertTrue(data['success'])
