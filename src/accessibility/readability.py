"""Readability analysis engine for LUI responses.

This module implements Flesch-Kincaid, Flesch Reading Ease, and SMOG
readability analysis following established formulas and best practices.

Formulas:
- Flesch Reading Ease: 206.835 - 1.015(ASL) - 84.6(ASW)
- Flesch-Kincaid Grade: 0.39(ASL) + 11.8(ASW) - 15.59
- SMOG: 1.0430 * sqrt(polysyllables * 30/sentences) + 3.1291

Where:
- ASL = Average Sentence Length (words per sentence)
- ASW = Average Syllables per Word
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Optional


# ============================================
# Constants
# ============================================

# Common abbreviations that shouldn't be treated as sentence endings
ABBREVIATIONS = frozenset([
    "mr", "mrs", "ms", "dr", "prof", "sr", "jr", "vs", "etc", "inc", "ltd",
    "co", "corp", "st", "ave", "blvd", "rd", "ft", "mt", "gen", "col", "lt",
    "sgt", "capt", "rev", "hon", "gov", "pres", "dept", "est", "approx",
    "no", "nos", "vol", "vols", "pg", "pp", "fig", "figs", "ch", "sec",
    "ed", "eds", "trans", "repr", "e.g", "i.e", "cf", "al", "et",
])

# UK Government recommendation for maximum words per sentence
MAX_RECOMMENDED_SENTENCE_LENGTH = 25

# Minimum sentences required for SMOG grade calculation
MIN_SENTENCES_FOR_SMOG = 30

# Common vowel patterns for syllable counting
VOWELS = "aeiouy"

# Silent 'e' suffixes that don't add a syllable
SILENT_E_SUFFIXES = ["le", "ble", "ple", "tle", "dle", "fle", "gle", "kle", "zle"]

# Word endings that typically add a syllable
SYLLABLE_ADDING_ENDINGS = ["ia", "io", "iu", "ea", "eo", "ua", "uo", "ii", "ious"]


# ============================================
# Data Classes
# ============================================


@dataclass
class ReadabilityMetrics:
    """Complete readability metrics for a text."""

    word_count: int
    sentence_count: int
    syllable_count: int
    average_sentence_length: float
    average_syllables_per_word: float
    flesch_reading_ease: float  # 0-100 scale (higher = easier)
    flesch_kincaid_grade: float  # US grade level
    smog_grade: Optional[float] = None  # Requires 30+ sentences
    polysyllable_count: int = 0  # Words with 3+ syllables
    complex_word_percentage: float = 0.0

    def __post_init__(self):
        """Validate and clamp values to reasonable ranges."""
        # Flesch Reading Ease can theoretically go negative for very complex text
        # but we clamp to 0-100 for practical use
        self.flesch_reading_ease = max(0.0, min(100.0, self.flesch_reading_ease))

        # Grade level should not be negative
        self.flesch_kincaid_grade = max(0.0, self.flesch_kincaid_grade)

        if self.smog_grade is not None:
            self.smog_grade = max(0.0, self.smog_grade)

    @property
    def reading_level_description(self) -> str:
        """Get human-readable description of the reading level."""
        fre = self.flesch_reading_ease

        if fre >= 90:
            return "Very Easy (5th grade)"
        elif fre >= 80:
            return "Easy (6th grade)"
        elif fre >= 70:
            return "Fairly Easy (7th grade)"
        elif fre >= 60:
            return "Standard (8th-9th grade)"
        elif fre >= 50:
            return "Fairly Difficult (10th-12th grade)"
        elif fre >= 30:
            return "Difficult (College)"
        else:
            return "Very Difficult (College Graduate)"

    @property
    def meets_plain_language(self) -> bool:
        """Check if text meets plain language standards (8th grade or below)."""
        return self.flesch_kincaid_grade <= 8.0


@dataclass
class SentenceAnalysis:
    """Analysis results for a single sentence."""

    text: str
    word_count: int
    syllable_count: int
    average_syllables_per_word: float
    is_long: bool  # >25 words per UK Government guidelines
    polysyllable_words: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def complexity_score(self) -> float:
        """Calculate complexity score (0-1, higher = more complex)."""
        # Combine length and syllable complexity
        length_score = min(1.0, self.word_count / 50)  # Normalize to ~50 words max
        syllable_score = min(1.0, (self.average_syllables_per_word - 1.0) / 2.0)
        return (length_score * 0.6) + (syllable_score * 0.4)


# ============================================
# Syllable Counter
# ============================================


class SyllableCounter:
    """Counts syllables in English words using pattern matching.

    Algorithm:
    1. Count vowel groups (consecutive vowels count as one)
    2. Adjust for silent 'e' at end of words
    3. Handle special patterns (prefixes, suffixes, exceptions)
    4. Minimum of 1 syllable per word
    """

    # Exceptions dictionary for common words with irregular syllable counts
    EXCEPTIONS: dict[str, int] = {
        # 1-syllable words often miscounted
        "the": 1, "to": 1, "you": 1, "are": 1, "were": 1,
        "been": 1, "have": 1, "does": 1, "they": 1, "their": 1,
        "there": 1, "where": 1, "which": 1, "while": 1, "through": 1,
        "though": 1, "those": 1, "these": 1, "some": 1, "come": 1,
        "done": 1, "gone": 1, "one": 1, "once": 1, "give": 1,
        "live": 1, "love": 1, "move": 1, "prove": 1, "whose": 1,
        "else": 1, "since": 1, "hence": 1, "once": 1, "please": 1,
        "piece": 1, "peace": 1, "scene": 1, "scheme": 1, "guide": 1,
        # 2-syllable words
        "area": 3, "idea": 3, "being": 2, "seeing": 2, "doing": 2,
        "going": 2, "create": 2, "created": 3, "creates": 2,
        "people": 2, "little": 2, "every": 3, "really": 3,
        "being": 2, "having": 2, "using": 2, "making": 2,
        "orange": 2, "different": 3, "interested": 4, "interesting": 4,
        "business": 3, "family": 3, "usually": 4, "actually": 4,
        "especially": 5, "experience": 4, "education": 4,
        "beautiful": 3, "chocolate": 3, "comfortable": 4,
        "general": 3, "natural": 3, "several": 3,
        # Technical/common words
        "queue": 1, "quite": 1, "quote": 1, "unique": 2,
        "league": 1, "vague": 1, "rogue": 1, "dialogue": 3,
        "catalogue": 3, "technique": 2, "antique": 2,
    }

    @classmethod
    def count(cls, word: str) -> int:
        """Count syllables in a word.

        Args:
            word: The word to count syllables in

        Returns:
            Number of syllables (minimum 1)
        """
        if not word:
            return 0

        # Normalize word
        word = word.lower().strip()
        word = re.sub(r"[^a-z]", "", word)

        if not word:
            return 0

        # Check exceptions first
        if word in cls.EXCEPTIONS:
            return cls.EXCEPTIONS[word]

        # Basic syllable count from vowel groups
        syllables = cls._count_vowel_groups(word)

        # Adjust for patterns
        syllables = cls._adjust_for_patterns(word, syllables)

        # Minimum 1 syllable
        return max(1, syllables)

    @classmethod
    def _count_vowel_groups(cls, word: str) -> int:
        """Count groups of consecutive vowels."""
        count = 0
        prev_is_vowel = False

        for char in word:
            is_vowel = char in VOWELS
            if is_vowel and not prev_is_vowel:
                count += 1
            prev_is_vowel = is_vowel

        return count

    @classmethod
    def _adjust_for_patterns(cls, word: str, count: int) -> int:
        """Adjust syllable count based on common patterns."""
        # Silent 'e' at end (but not 'le' endings which are syllabic)
        if word.endswith("e") and len(word) > 2:
            if not any(word.endswith(suffix) for suffix in SILENT_E_SUFFIXES):
                # Check if it's not a two-letter vowel ending
                if len(word) > 1 and word[-2] not in VOWELS:
                    count -= 1

        # Syllable-adding endings
        for ending in SYLLABLE_ADDING_ENDINGS:
            if word.endswith(ending):
                count += 1
                break

        # -ed ending: usually silent unless preceded by 't' or 'd'
        if word.endswith("ed") and len(word) > 2:
            if word[-3] not in "td":
                count -= 1

        # -es ending: adds syllable only after 's', 'x', 'z', 'ch', 'sh'
        if word.endswith("es") and len(word) > 2:
            if word[-3] not in "sxz" and not word.endswith("ches") and not word.endswith("shes"):
                count -= 1

        # Common prefixes that add syllables
        prefixes = [("re", 1), ("pre", 1), ("un", 1), ("dis", 1), ("mis", 1)]
        for prefix, adj in prefixes:
            if word.startswith(prefix) and len(word) > len(prefix) + 2:
                # Only if the rest starts with a consonant
                rest = word[len(prefix):]
                if rest and rest[0] not in VOWELS:
                    # Already counted, no adjustment needed
                    pass

        # -tion, -sion endings are 1 syllable
        if word.endswith("tion") or word.endswith("sion"):
            # These are typically counted correctly but let's ensure
            pass

        return count

    @classmethod
    def count_in_text(cls, text: str) -> tuple[int, int, list[str]]:
        """Count total syllables in text, also returning polysyllable words.

        Args:
            text: The text to analyze

        Returns:
            Tuple of (total_syllables, polysyllable_count, polysyllable_words)
        """
        words = cls._tokenize_words(text)
        total = 0
        polysyllable_count = 0
        polysyllable_words = []

        for word in words:
            syllables = cls.count(word)
            total += syllables
            if syllables >= 3:
                polysyllable_count += 1
                polysyllable_words.append(word)

        return total, polysyllable_count, polysyllable_words

    @staticmethod
    def _tokenize_words(text: str) -> list[str]:
        """Extract words from text."""
        # Remove punctuation but keep apostrophes in contractions
        text = re.sub(r"[^\w\s'-]", " ", text)
        # Split on whitespace
        words = text.split()
        # Filter out empty strings and pure punctuation
        return [w.strip("'-") for w in words if w.strip("'-")]


# ============================================
# Sentence Detector
# ============================================


class SentenceDetector:
    """Detects sentence boundaries handling abbreviations and edge cases."""

    # Pattern to match sentence endings
    # Handles: period, question mark, exclamation mark
    # But not: abbreviations, decimal numbers, ellipsis
    SENTENCE_END_PATTERN = re.compile(
        r"""
        (?<![A-Z])          # Not preceded by a single capital (e.g., "Mr.")
        (?<!\b[Dd]r)        # Not after "Dr" or "dr"
        (?<!\b[Mm]r)        # Not after "Mr" or "mr"
        (?<!\b[Mm]rs)       # Not after "Mrs" or "mrs"
        (?<!\b[Mm]s)        # Not after "Ms" or "ms"
        (?<!\b[Pp]rof)      # Not after "Prof"
        (?<!\b[Ss]t)        # Not after "St"
        (?<!\b[Jj]r)        # Not after "Jr"
        (?<!\b[Ss]r)        # Not after "Sr"
        (?<!\b[Vv]s)        # Not after "vs"
        (?<!\b[Ee]tc)       # Not after "etc"
        (?<!\b[Ii]nc)       # Not after "Inc"
        (?<!\b[Ll]td)       # Not after "Ltd"
        (?<!\be\.g)         # Not after "e.g"
        (?<!\bi\.e)         # Not after "i.e"
        (?<!\d)             # Not after a digit (decimal numbers)
        [.!?]               # Sentence-ending punctuation
        (?=\s+[A-Z]|\s*$)   # Followed by space+capital or end of string
        """,
        re.VERBOSE
    )

    @classmethod
    def split(cls, text: str) -> list[str]:
        """Split text into sentences.

        Args:
            text: The text to split

        Returns:
            List of sentences
        """
        if not text or not text.strip():
            return []

        # Normalize whitespace
        text = " ".join(text.split())

        # Simple approach: split on sentence-ending punctuation followed by space+capital
        # This handles most cases while avoiding abbreviation pitfalls
        sentences = []

        # Use a simpler, more robust splitting approach
        # Split on .!? followed by one or more spaces and a capital letter
        parts = re.split(r'([.!?]+)\s+(?=[A-Z])', text)

        current = ""
        for i, part in enumerate(parts):
            if re.match(r'^[.!?]+$', part):
                # This is punctuation, append to current
                current += part
            else:
                if current:
                    sentences.append(current.strip())
                current = part

        if current.strip():
            sentences.append(current.strip())

        # Handle case where there's no sentence-ending punctuation
        if not sentences:
            return [text.strip()]

        return [s for s in sentences if s.strip()]

    @classmethod
    def count(cls, text: str) -> int:
        """Count sentences in text.

        Args:
            text: The text to count sentences in

        Returns:
            Number of sentences (minimum 1 for non-empty text)
        """
        sentences = cls.split(text)
        return len(sentences) if sentences else (1 if text.strip() else 0)


# ============================================
# Readability Analyzer
# ============================================


class ReadabilityAnalyzer:
    """Analyzes text readability using standard formulas.

    Provides Flesch-Kincaid Grade Level, Flesch Reading Ease,
    and SMOG Grade metrics for text assessment.
    """

    def __init__(self):
        """Initialize the analyzer."""
        self._syllable_counter = SyllableCounter
        self._sentence_detector = SentenceDetector

    def analyze(self, text: str) -> ReadabilityMetrics:
        """Analyze text and return readability metrics.

        Args:
            text: The text to analyze

        Returns:
            ReadabilityMetrics with all calculated values

        Note:
            SMOG grade is only calculated for texts with 30+ sentences.
            For shorter texts, smog_grade will be None.
        """
        if not text or not text.strip():
            return ReadabilityMetrics(
                word_count=0,
                sentence_count=0,
                syllable_count=0,
                average_sentence_length=0.0,
                average_syllables_per_word=0.0,
                flesch_reading_ease=100.0,  # Empty text is "easy"
                flesch_kincaid_grade=0.0,
                smog_grade=None,
                polysyllable_count=0,
                complex_word_percentage=0.0,
            )

        # Count basic metrics
        sentences = self._sentence_detector.split(text)
        sentence_count = len(sentences) if sentences else 1

        # Tokenize words
        words = SyllableCounter._tokenize_words(text)
        word_count = len(words)

        if word_count == 0:
            return ReadabilityMetrics(
                word_count=0,
                sentence_count=sentence_count,
                syllable_count=0,
                average_sentence_length=0.0,
                average_syllables_per_word=0.0,
                flesch_reading_ease=100.0,
                flesch_kincaid_grade=0.0,
                smog_grade=None,
                polysyllable_count=0,
                complex_word_percentage=0.0,
            )

        # Count syllables and polysyllables
        syllable_count, polysyllable_count, _ = self._syllable_counter.count_in_text(text)

        # Calculate averages
        asl = word_count / sentence_count  # Average Sentence Length
        asw = syllable_count / word_count if word_count > 0 else 0  # Average Syllables per Word

        # Calculate Flesch Reading Ease
        # Formula: 206.835 - 1.015(ASL) - 84.6(ASW)
        fre = 206.835 - (1.015 * asl) - (84.6 * asw)

        # Calculate Flesch-Kincaid Grade Level
        # Formula: 0.39(ASL) + 11.8(ASW) - 15.59
        fk_grade = (0.39 * asl) + (11.8 * asw) - 15.59

        # Calculate SMOG Grade (only if 30+ sentences)
        smog = None
        if sentence_count >= MIN_SENTENCES_FOR_SMOG:
            # Formula: 1.0430 * sqrt(polysyllables * 30/sentences) + 3.1291
            smog = 1.0430 * math.sqrt(polysyllable_count * (30 / sentence_count)) + 3.1291

        # Calculate complex word percentage
        complex_pct = (polysyllable_count / word_count * 100) if word_count > 0 else 0

        return ReadabilityMetrics(
            word_count=word_count,
            sentence_count=sentence_count,
            syllable_count=syllable_count,
            average_sentence_length=round(asl, 2),
            average_syllables_per_word=round(asw, 2),
            flesch_reading_ease=round(fre, 2),
            flesch_kincaid_grade=round(fk_grade, 2),
            smog_grade=round(smog, 2) if smog is not None else None,
            polysyllable_count=polysyllable_count,
            complex_word_percentage=round(complex_pct, 2),
        )

    def analyze_for_grade_level(self, text: str, target_grade: float) -> dict:
        """Analyze text and provide recommendations for target grade level.

        Args:
            text: The text to analyze
            target_grade: Target grade level (e.g., 8.0 for 8th grade)

        Returns:
            Dictionary with analysis and recommendations
        """
        metrics = self.analyze(text)

        recommendations = []

        if metrics.flesch_kincaid_grade > target_grade:
            grade_diff = metrics.flesch_kincaid_grade - target_grade

            if metrics.average_sentence_length > 20:
                recommendations.append(
                    f"Shorten sentences (current avg: {metrics.average_sentence_length:.1f} words, "
                    f"target: <20 words)"
                )

            if metrics.average_syllables_per_word > 1.5:
                recommendations.append(
                    f"Use simpler words (current avg: {metrics.average_syllables_per_word:.2f} syllables, "
                    f"target: <1.5 syllables)"
                )

            if metrics.complex_word_percentage > 10:
                recommendations.append(
                    f"Reduce complex words (current: {metrics.complex_word_percentage:.1f}%, "
                    f"target: <10%)"
                )

        return {
            "metrics": metrics,
            "target_grade": target_grade,
            "current_grade": metrics.flesch_kincaid_grade,
            "meets_target": metrics.flesch_kincaid_grade <= target_grade,
            "grade_difference": round(metrics.flesch_kincaid_grade - target_grade, 2),
            "recommendations": recommendations,
        }


# ============================================
# Sentence Analyzer
# ============================================


class SentenceAnalyzer:
    """Analyzes individual sentences for readability and provides recommendations."""

    def __init__(self):
        """Initialize the sentence analyzer."""
        self._syllable_counter = SyllableCounter
        self._sentence_detector = SentenceDetector

    def analyze_sentences(self, text: str) -> list[SentenceAnalysis]:
        """Analyze each sentence in the text.

        Args:
            text: The text to analyze

        Returns:
            List of SentenceAnalysis objects, one per sentence
        """
        sentences = self._sentence_detector.split(text)
        results = []

        for sentence in sentences:
            analysis = self._analyze_single_sentence(sentence)
            results.append(analysis)

        return results

    def _analyze_single_sentence(self, sentence: str) -> SentenceAnalysis:
        """Analyze a single sentence.

        Args:
            sentence: The sentence to analyze

        Returns:
            SentenceAnalysis with metrics and recommendations
        """
        words = SyllableCounter._tokenize_words(sentence)
        word_count = len(words)

        if word_count == 0:
            return SentenceAnalysis(
                text=sentence,
                word_count=0,
                syllable_count=0,
                average_syllables_per_word=0.0,
                is_long=False,
                polysyllable_words=[],
                recommendations=[],
            )

        # Count syllables
        syllable_count, _, polysyllable_words = self._syllable_counter.count_in_text(sentence)
        asw = syllable_count / word_count

        # Check if sentence is too long (>25 words per UK Government)
        is_long = word_count > MAX_RECOMMENDED_SENTENCE_LENGTH

        # Generate recommendations
        recommendations = self._generate_recommendations(
            word_count, asw, is_long, polysyllable_words
        )

        return SentenceAnalysis(
            text=sentence,
            word_count=word_count,
            syllable_count=syllable_count,
            average_syllables_per_word=round(asw, 2),
            is_long=is_long,
            polysyllable_words=polysyllable_words,
            recommendations=recommendations,
        )

    def _generate_recommendations(
        self,
        word_count: int,
        asw: float,
        is_long: bool,
        polysyllable_words: list[str],
    ) -> list[str]:
        """Generate recommendations for improving sentence readability.

        Args:
            word_count: Number of words in sentence
            asw: Average syllables per word
            is_long: Whether sentence exceeds length recommendation
            polysyllable_words: List of complex words

        Returns:
            List of recommendation strings
        """
        recommendations = []

        if is_long:
            recommendations.append(
                f"Consider splitting this sentence ({word_count} words). "
                f"UK Government recommends ≤{MAX_RECOMMENDED_SENTENCE_LENGTH} words."
            )

        if asw > 2.0:
            recommendations.append(
                f"High syllable density ({asw:.1f} per word). Consider simpler vocabulary."
            )

        if len(polysyllable_words) > 3:
            # Limit to first 5 complex words
            examples = polysyllable_words[:5]
            recommendations.append(
                f"Contains {len(polysyllable_words)} complex words. "
                f"Consider simplifying: {', '.join(examples)}"
            )
        elif len(polysyllable_words) > 0 and word_count < 10:
            # Short sentence with complex words
            recommendations.append(
                f"Short sentence with complex words: {', '.join(polysyllable_words)}. "
                f"Consider simpler alternatives."
            )

        return recommendations

    def get_summary(self, analyses: list[SentenceAnalysis]) -> dict:
        """Get summary statistics for sentence analyses.

        Args:
            analyses: List of SentenceAnalysis objects

        Returns:
            Dictionary with summary statistics
        """
        if not analyses:
            return {
                "sentence_count": 0,
                "long_sentence_count": 0,
                "long_sentence_percentage": 0.0,
                "average_words_per_sentence": 0.0,
                "average_syllables_per_word": 0.0,
                "total_polysyllable_words": 0,
                "sentences_needing_attention": 0,
            }

        total_words = sum(a.word_count for a in analyses)
        total_syllables = sum(a.syllable_count for a in analyses)
        long_count = sum(1 for a in analyses if a.is_long)
        attention_count = sum(1 for a in analyses if a.recommendations)
        total_polysyllables = sum(len(a.polysyllable_words) for a in analyses)

        return {
            "sentence_count": len(analyses),
            "long_sentence_count": long_count,
            "long_sentence_percentage": round(long_count / len(analyses) * 100, 1),
            "average_words_per_sentence": round(total_words / len(analyses), 1),
            "average_syllables_per_word": round(
                total_syllables / total_words if total_words > 0 else 0, 2
            ),
            "total_polysyllable_words": total_polysyllables,
            "sentences_needing_attention": attention_count,
        }
