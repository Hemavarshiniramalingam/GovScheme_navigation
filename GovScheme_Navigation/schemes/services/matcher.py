import json
from django.db import models
from schemes.models import Scheme, EligibilityRule

class SchemeMatcher:
    """
    Evaluates citizen profile against all registered scheme eligibility rules
    using an AST-inspired deterministic matching engine with scoring and plain-language feedback.
    """

    @staticmethod
    def _parse_values(val_str):
        if not val_str:
            return []
        try:
            parsed = json.loads(val_str)
            if isinstance(parsed, list):
                return [str(x).strip().lower() for x in parsed]
            return [str(parsed).strip().lower()]
        except Exception:
            return [x.strip().lower() for x in val_str.split(',') if x.strip()]

    @classmethod
    def evaluate_scheme(cls, profile_data, scheme):
        """
        Evaluates a single scheme against citizen intake data.
        Returns a dict with match_score, is_eligible, matched_reasons, unmet_reasons.
        """
        rules = scheme.rules.all()
        if not rules.exists():
            return {
                'scheme': scheme,
                'match_score': 100,
                'is_eligible': True,
                'status_tag': 'Eligible',
                'matched_reasons': ['Universal scheme open to all citizens meeting general guidelines.'],
                'unmet_reasons': []
            }

        total_rules = rules.count()
        matched_count = 0
        mandatory_failed = False
        matched_reasons = []
        unmet_reasons = []

        # Extract normalized profile attributes
        user_age = str(profile_data.get('age_group', '')).strip().lower()
        user_edu = str(profile_data.get('education_level', '')).strip().lower()
        user_occ = str(profile_data.get('occupation', '')).strip().lower()
        user_state = str(profile_data.get('state', '')).strip().lower()
        user_income = str(profile_data.get('income_bracket', '')).strip().lower()
        user_cat = str(profile_data.get('specific_category', '')).strip().lower()

        profile_map = {
            'age_group': user_age,
            'education_level': user_edu,
            'occupation': user_occ,
            'state': user_state,
            'income_bracket': user_income,
            'specific_category': user_cat,
        }

        for rule in rules:
            field = rule.rule_field
            op = rule.operator
            expected = cls._parse_values(rule.expected_values)
            user_val = profile_map.get(field, '')

            passed = False

            if op == 'any' or 'all' in expected or '*' in expected or not expected:
                passed = True
            elif op == 'in':
                if user_val in expected:
                    passed = True
                # State scope fallback
                elif field == 'state' and ('all' in expected or scheme.state_scope.upper() == 'ALL'):
                    passed = True
                # Category universal fallback
                elif field == 'specific_category' and ('general' in expected or 'all' in expected or 'any' in expected):
                    passed = True
            elif op == 'not_in':
                if user_val not in expected:
                    passed = True
            elif op == 'eq':
                if expected and user_val == expected[0]:
                    passed = True

            if passed:
                matched_count += 1
                matched_reasons.append(rule.plain_language_rule or f"Matches {field.replace('_', ' ').title()} criteria.")
            else:
                if rule.is_mandatory:
                    mandatory_failed = True
                unmet_reasons.append(
                    f"Requires {field.replace('_', ' ').title()} in: {', '.join(expected).title()} (Your input: {user_val.replace('_', ' ').title() or 'Not specified'})"
                )

        score = int((matched_count / total_rules) * 100) if total_rules > 0 else 100
        is_eligible = (not mandatory_failed) and (score >= 70)

        status_tag = '100% Eligible' if score == 100 and not mandatory_failed else (
            'Highly Likely Eligible' if is_eligible and score >= 80 else (
                'Conditionally Eligible' if is_eligible else 'Not Eligible'
            )
        )

        return {
            'scheme': scheme,
            'match_score': score,
            'is_eligible': is_eligible,
            'status_tag': status_tag,
            'matched_reasons': matched_reasons,
            'unmet_reasons': unmet_reasons,
            'document_count': scheme.documents.count(),
        }

    @classmethod
    def match_all(cls, profile_data, sector_filter=None, level_filter=None, query=None):
        """
        Evaluates all active schemes and returns categorized, sorted results.
        """
        qs = Scheme.objects.filter(is_active=True).prefetch_related('rules', 'documents')

        if sector_filter and sector_filter != 'ALL':
            qs = qs.filter(sector_category__iexact=sector_filter)
        if level_filter and level_filter != 'ALL':
            qs = qs.filter(level__iexact=level_filter)
        if query:
            qs = qs.filter(
                models.Q(name__icontains=query) |
                models.Q(code__icontains=query) |
                models.Q(plain_language_summary__icontains=query) |
                models.Q(tags__icontains=query)
            )

        results = []
        for scheme in qs:
            eval_result = cls.evaluate_scheme(profile_data, scheme)
            results.append(eval_result)

        # Sort: Eligible first, then highest match score, then featured, then name
        results.sort(
            key=lambda x: (
                1 if x['is_eligible'] else 0,
                x['match_score'],
                1 if x['scheme'].featured else 0,
                x['scheme'].name
            ),
            reverse=True
        )

        eligible_schemes = [r for r in results if r['is_eligible']]
        other_schemes = [r for r in results if not r['is_eligible']]

        return {
            'total_evaluated': len(results),
            'eligible_count': len(eligible_schemes),
            'eligible_schemes': eligible_schemes,
            'other_schemes': other_schemes,
            'all_results': results
        }
