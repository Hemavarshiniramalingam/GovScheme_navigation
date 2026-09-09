import re

class LegalToPlainLanguageTranslator:
    """
    NLP & Rule-based translation pipeline that converts legalistic statutory provisions,
    gazette notifications, and complex eligibility criteria into citizen-friendly conversational English.
    """

    # Comprehensive legal terminology mapping dictionary
    GLOSSARY = {
        r'\boperational landholding\b': 'farm land owned or cultivated',
        r'\bgross parental income\b': 'total family yearly earnings',
        r'\bannual family income from all sources\b': 'total combined earnings of your household per year',
        r'\bdirect benefit transfer\b': 'direct cash payment transferred to your bank account',
        r'\bpfms\b': 'Public Financial Management System (direct govt bank transfer)',
        r'\binterest subvention\b': 'government discount on loan interest rate',
        r'\bmargin money subsidy\b': 'free government cash grant that you do not have to repay',
        r'\bbelow poverty line\b': 'BPL ration card holder or low income household',
        r'\bdomicile of the state\b': 'permanent resident of this state',
        r'\bundergoing regular full-time course\b': 'enrolled in regular college or school classes',
        r'\bcadre / gazetted officer\b': 'senior authorized government official',
        r'\bnon-creamy layer\b': 'OBC category family earning below the annual income ceiling',
        r'\bstatutory declaration\b': 'official signed self-attestation or affidavit',
        r'\bante-natal care\b': 'pregnancy check-ups and maternal healthcare',
        r'\bempaneled healthcare provider\b': 'registered hospital offering free cash-less treatments',
        r'\bdisbursal in tranches\b': 'money paid in planned installment stages',
        r'\bcredit linked subsidy\b': 'interest discount applied directly to your home or business loan'
    }

    @classmethod
    def translate_legal_text(cls, legal_text):
        """
        Replaces dense bureaucratic jargon with citizen-friendly equivalents.
        """
        if not legal_text:
            return ""
        
        simplified = legal_text
        for pattern, replacement in cls.GLOSSARY.items():
            simplified = re.sub(pattern, replacement, simplified, flags=re.IGNORECASE)
        
        # Clean double spaces and normalize punctuation
        simplified = re.sub(r'\s+', ' ', simplified).strip()
        return simplified

    @classmethod
    def calculate_readability(cls, text):
        """
        Computes an approximate Flesch Reading Ease score to ensure citizen accessibility (Goal: > 60).
        """
        if not text:
            return 70.0
        
        words = re.findall(r'\b\w+\b', text)
        sentences = re.split(r'[\.\?!]+', text)
        sentences = [s for s in sentences if s.strip()]
        
        if not words or not sentences:
            return 75.0
        
        total_words = len(words)
        total_sentences = max(len(sentences), 1)
        
        # Simple syllable estimation
        syllables = 0
        for word in words:
            w = word.lower()
            count = len(re.findall(r'[aeiouy]+', w))
            syllables += max(count, 1)
            
        asl = total_words / total_sentences
        asw = syllables / total_words
        
        score = 206.835 - (1.015 * asl) - (84.6 * asw)
        return round(max(0, min(100, score)), 1)

    @classmethod
    def generate_citizen_summary(cls, scheme):
        """
        Synthesizes a 3-point plain language card for any scheme.
        """
        benefit = scheme.benefit_highlight or "Financial & Social Assistance"
        plain_summary = cls.translate_legal_text(scheme.plain_language_summary or scheme.legal_description)
        readability = cls.calculate_readability(plain_summary)

        return {
            'plain_benefit': benefit,
            'plain_summary': plain_summary,
            'readability_score': readability,
            'readability_level': 'Easy to Understand (Citizen Grade)' if readability >= 60 else 'Intermediate',
            'official_authority': scheme.ministry
        }
