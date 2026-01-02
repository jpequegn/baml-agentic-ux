"""Jargon detection and plain language simplification for LUI responses.

This module provides tools for detecting technical jargon and suggesting
plain language alternatives to improve accessibility.

Issue #71 - Task 4.5: Jargon Detection & Simplification
Part of #27 - Phase 4: LUI Accessibility Standards
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ============================================
# Enums
# ============================================


class JargonCategory(Enum):
    """Categories of jargon for filtering and reporting."""

    TECHNICAL = "technical"  # Software/IT terminology
    BUSINESS = "business"  # Corporate/business speak
    LEGAL = "legal"  # Legal terminology
    ACADEMIC = "academic"  # Academic/formal language
    MEDICAL = "medical"  # Medical terminology
    ABBREVIATION = "abbreviation"  # Acronyms and abbreviations
    GENERAL = "general"  # Overly complex general words


# ============================================
# Data Classes
# ============================================


@dataclass
class JargonTerm:
    """A detected jargon term with context and alternatives."""

    term: str  # The jargon term as found
    context: str  # Surrounding text providing context
    definition: Optional[str] = None  # Definition if available
    simple_alternative: Optional[str] = None  # Plain language replacement
    category: JargonCategory = JargonCategory.GENERAL
    position: int = 0  # Character position in original text

    def __hash__(self):
        return hash((self.term.lower(), self.position))

    def __eq__(self, other):
        if not isinstance(other, JargonTerm):
            return False
        return self.term.lower() == other.term.lower() and self.position == other.position


@dataclass
class SimplificationResult:
    """Result of simplifying text."""

    original_text: str
    simplified_text: str
    changes_made: list[str] = field(default_factory=list)
    terms_replaced: int = 0
    confidence: float = 1.0  # Confidence in replacements preserving meaning


# ============================================
# Jargon Database
# ============================================

# Technical jargon with plain alternatives
TECHNICAL_JARGON_DB: dict[str, dict] = {
    # Authentication & Security
    "authenticate": {
        "definition": "Verify identity through credentials",
        "simple": "verify your identity",
        "alternatives": ["log in", "sign in", "verify who you are"],
        "category": JargonCategory.TECHNICAL,
    },
    "authentication": {
        "definition": "The process of verifying identity",
        "simple": "identity check",
        "alternatives": ["login process", "sign-in", "verification"],
        "category": JargonCategory.TECHNICAL,
    },
    "authorization": {
        "definition": "Permission to access something",
        "simple": "permission",
        "alternatives": ["access rights", "approval"],
        "category": JargonCategory.TECHNICAL,
    },
    "credential": {
        "definition": "Login information like username/password",
        "simple": "login details",
        "alternatives": ["username and password", "login info"],
        "category": JargonCategory.TECHNICAL,
    },
    "credentials": {
        "definition": "Login information like username/password",
        "simple": "login details",
        "alternatives": ["username and password", "login info"],
        "category": JargonCategory.TECHNICAL,
    },
    # API & Development
    "endpoint": {
        "definition": "A URL where an API can be accessed",
        "simple": "connection point",
        "alternatives": ["address", "link", "URL"],
        "category": JargonCategory.TECHNICAL,
    },
    "parameter": {
        "definition": "A value passed to a function or API",
        "simple": "setting",
        "alternatives": ["option", "value", "input"],
        "category": JargonCategory.TECHNICAL,
    },
    "parameters": {
        "definition": "Values passed to a function or API",
        "simple": "settings",
        "alternatives": ["options", "values", "inputs"],
        "category": JargonCategory.TECHNICAL,
    },
    "instantiate": {
        "definition": "Create an instance of something",
        "simple": "create",
        "alternatives": ["make", "set up", "initialize"],
        "category": JargonCategory.TECHNICAL,
    },
    "initialize": {
        "definition": "Set up something for first use",
        "simple": "set up",
        "alternatives": ["start", "prepare", "configure"],
        "category": JargonCategory.TECHNICAL,
    },
    "configure": {
        "definition": "Set up settings and options",
        "simple": "set up",
        "alternatives": ["adjust settings", "customize"],
        "category": JargonCategory.TECHNICAL,
    },
    "configuration": {
        "definition": "Settings and options",
        "simple": "settings",
        "alternatives": ["setup", "options"],
        "category": JargonCategory.TECHNICAL,
    },
    "deprecated": {
        "definition": "No longer recommended for use",
        "simple": "outdated",
        "alternatives": ["old", "no longer supported", "being removed"],
        "category": JargonCategory.TECHNICAL,
    },
    "asynchronous": {
        "definition": "Not happening at the same time",
        "simple": "in the background",
        "alternatives": ["non-blocking", "separate"],
        "category": JargonCategory.TECHNICAL,
    },
    "synchronous": {
        "definition": "Happening at the same time",
        "simple": "immediate",
        "alternatives": ["in sequence", "one at a time"],
        "category": JargonCategory.TECHNICAL,
    },
    "callback": {
        "definition": "A function called when something completes",
        "simple": "response action",
        "alternatives": ["follow-up action", "next step"],
        "category": JargonCategory.TECHNICAL,
    },
    "token": {
        "definition": "A piece of data for authentication or identification",
        "simple": "access code",
        "alternatives": ["key", "code", "identifier"],
        "category": JargonCategory.TECHNICAL,
    },
    "cache": {
        "definition": "Stored data for faster access",
        "simple": "stored copy",
        "alternatives": ["saved data", "memory"],
        "category": JargonCategory.TECHNICAL,
    },
    "caching": {
        "definition": "Storing data for faster access",
        "simple": "saving for faster access",
        "alternatives": ["storing temporarily", "keeping a copy"],
        "category": JargonCategory.TECHNICAL,
    },
    # Business jargon
    "leverage": {
        "definition": "Use something to maximum advantage",
        "simple": "use",
        "alternatives": ["apply", "take advantage of"],
        "category": JargonCategory.BUSINESS,
    },
    "utilize": {
        "definition": "Make use of",
        "simple": "use",
        "alternatives": ["apply", "employ"],
        "category": JargonCategory.BUSINESS,
    },
    "utilization": {
        "definition": "The act of using something",
        "simple": "use",
        "alternatives": ["usage", "application"],
        "category": JargonCategory.BUSINESS,
    },
    "optimize": {
        "definition": "Make as effective as possible",
        "simple": "improve",
        "alternatives": ["make better", "enhance"],
        "category": JargonCategory.BUSINESS,
    },
    "optimization": {
        "definition": "The process of making something better",
        "simple": "improvement",
        "alternatives": ["enhancement", "fine-tuning"],
        "category": JargonCategory.BUSINESS,
    },
    "synergy": {
        "definition": "Combined effect greater than sum of parts",
        "simple": "combined effort",
        "alternatives": ["teamwork", "working together"],
        "category": JargonCategory.BUSINESS,
    },
    "paradigm": {
        "definition": "A typical example or pattern",
        "simple": "model",
        "alternatives": ["approach", "way of thinking"],
        "category": JargonCategory.BUSINESS,
    },
    "scalable": {
        "definition": "Can grow or shrink as needed",
        "simple": "flexible",
        "alternatives": ["adjustable", "expandable"],
        "category": JargonCategory.BUSINESS,
    },
    "proactive": {
        "definition": "Acting in advance",
        "simple": "ahead of time",
        "alternatives": ["prepared", "anticipating"],
        "category": JargonCategory.BUSINESS,
    },
    "stakeholder": {
        "definition": "Person with interest in something",
        "simple": "interested party",
        "alternatives": ["participant", "person involved"],
        "category": JargonCategory.BUSINESS,
    },
    "deliverable": {
        "definition": "Something that must be provided",
        "simple": "result",
        "alternatives": ["output", "product", "work product"],
        "category": JargonCategory.BUSINESS,
    },
    "bandwidth": {
        "definition": "Capacity to handle work",
        "simple": "time available",
        "alternatives": ["capacity", "availability"],
        "category": JargonCategory.BUSINESS,
    },
    # Academic/formal language
    "necessitate": {
        "definition": "Make necessary",
        "simple": "require",
        "alternatives": ["need", "call for"],
        "category": JargonCategory.ACADEMIC,
    },
    "necessitates": {
        "definition": "Makes necessary",
        "simple": "requires",
        "alternatives": ["needs", "calls for"],
        "category": JargonCategory.ACADEMIC,
    },
    "subsequently": {
        "definition": "After that",
        "simple": "then",
        "alternatives": ["after", "next", "later"],
        "category": JargonCategory.ACADEMIC,
    },
    "consequently": {
        "definition": "As a result",
        "simple": "so",
        "alternatives": ["therefore", "as a result"],
        "category": JargonCategory.ACADEMIC,
    },
    "furthermore": {
        "definition": "In addition",
        "simple": "also",
        "alternatives": ["and", "plus", "in addition"],
        "category": JargonCategory.ACADEMIC,
    },
    "moreover": {
        "definition": "In addition",
        "simple": "also",
        "alternatives": ["and", "plus", "besides"],
        "category": JargonCategory.ACADEMIC,
    },
    "notwithstanding": {
        "definition": "In spite of",
        "simple": "despite",
        "alternatives": ["even so", "regardless"],
        "category": JargonCategory.ACADEMIC,
    },
    "aforementioned": {
        "definition": "Mentioned earlier",
        "simple": "mentioned before",
        "alternatives": ["this", "the above", "previously stated"],
        "category": JargonCategory.ACADEMIC,
    },
    "heretofore": {
        "definition": "Before now",
        "simple": "until now",
        "alternatives": ["previously", "before this"],
        "category": JargonCategory.ACADEMIC,
    },
    "henceforth": {
        "definition": "From this time on",
        "simple": "from now on",
        "alternatives": ["going forward", "in the future"],
        "category": JargonCategory.ACADEMIC,
    },
    "whereby": {
        "definition": "By which",
        "simple": "by which",
        "alternatives": ["where", "through which"],
        "category": JargonCategory.ACADEMIC,
    },
    "methodology": {
        "definition": "A system of methods",
        "simple": "method",
        "alternatives": ["approach", "way", "process"],
        "category": JargonCategory.ACADEMIC,
    },
    "implementation": {
        "definition": "The act of putting something into effect",
        "simple": "setup",
        "alternatives": ["creating", "building", "making"],
        "category": JargonCategory.ACADEMIC,
    },
    "functionality": {
        "definition": "The features something has",
        "simple": "features",
        "alternatives": ["capabilities", "what it does"],
        "category": JargonCategory.ACADEMIC,
    },
    "prerequisite": {
        "definition": "Something required beforehand",
        "simple": "requirement",
        "alternatives": ["needed first", "must have"],
        "category": JargonCategory.ACADEMIC,
    },
    "facilitate": {
        "definition": "Make easier",
        "simple": "help",
        "alternatives": ["make easier", "enable"],
        "category": JargonCategory.ACADEMIC,
    },
    "ameliorate": {
        "definition": "Make better",
        "simple": "improve",
        "alternatives": ["fix", "make better"],
        "category": JargonCategory.ACADEMIC,
    },
    "cognizant": {
        "definition": "Aware of",
        "simple": "aware",
        "alternatives": ["knowing", "mindful"],
        "category": JargonCategory.ACADEMIC,
    },
    "elucidate": {
        "definition": "Make clear",
        "simple": "explain",
        "alternatives": ["clarify", "make clear"],
        "category": JargonCategory.ACADEMIC,
    },
    "expedite": {
        "definition": "Speed up",
        "simple": "speed up",
        "alternatives": ["hurry", "make faster"],
        "category": JargonCategory.ACADEMIC,
    },
    "enumerate": {
        "definition": "List one by one",
        "simple": "list",
        "alternatives": ["count", "go through"],
        "category": JargonCategory.ACADEMIC,
    },
    "validate": {
        "definition": "Check if something is correct",
        "simple": "check",
        "alternatives": ["verify", "confirm"],
        "category": JargonCategory.TECHNICAL,
    },
    "verification": {
        "definition": "The act of checking something",
        "simple": "check",
        "alternatives": ["confirmation", "proof"],
        "category": JargonCategory.TECHNICAL,
    },
}

# Common abbreviations
ABBREVIATION_DB: dict[str, dict] = {
    "API": {
        "definition": "Application Programming Interface",
        "simple": "software connection",
        "category": JargonCategory.ABBREVIATION,
    },
    "SDK": {
        "definition": "Software Development Kit",
        "simple": "development tools",
        "category": JargonCategory.ABBREVIATION,
    },
    "UI": {
        "definition": "User Interface",
        "simple": "screen design",
        "category": JargonCategory.ABBREVIATION,
    },
    "UX": {
        "definition": "User Experience",
        "simple": "how it feels to use",
        "category": JargonCategory.ABBREVIATION,
    },
    "URL": {
        "definition": "Uniform Resource Locator",
        "simple": "web address",
        "category": JargonCategory.ABBREVIATION,
    },
    "HTML": {
        "definition": "HyperText Markup Language",
        "simple": "web page code",
        "category": JargonCategory.ABBREVIATION,
    },
    "CSS": {
        "definition": "Cascading Style Sheets",
        "simple": "style code",
        "category": JargonCategory.ABBREVIATION,
    },
    "JSON": {
        "definition": "JavaScript Object Notation",
        "simple": "data format",
        "category": JargonCategory.ABBREVIATION,
    },
    "HTTPS": {
        "definition": "HyperText Transfer Protocol Secure",
        "simple": "secure web connection",
        "category": JargonCategory.ABBREVIATION,
    },
    "TLS": {
        "definition": "Transport Layer Security",
        "simple": "security protocol",
        "category": JargonCategory.ABBREVIATION,
    },
    "SSL": {
        "definition": "Secure Sockets Layer",
        "simple": "security protocol",
        "category": JargonCategory.ABBREVIATION,
    },
    "SQL": {
        "definition": "Structured Query Language",
        "simple": "database language",
        "category": JargonCategory.ABBREVIATION,
    },
    "PDF": {
        "definition": "Portable Document Format",
        "simple": "document file",
        "category": JargonCategory.ABBREVIATION,
    },
}


# ============================================
# Main Detector Class
# ============================================


class JargonDetector:
    """Detects technical jargon and suggests plain language alternatives.

    This detector scans text for technical, business, and academic jargon,
    providing definitions and plain language alternatives to improve
    accessibility.
    """

    def __init__(
        self,
        include_abbreviations: bool = True,
        categories: Optional[list[JargonCategory]] = None,
        custom_terms: Optional[dict[str, dict]] = None,
    ):
        """Initialize the detector.

        Args:
            include_abbreviations: Whether to detect abbreviations
            categories: Categories to detect (None = all)
            custom_terms: Additional custom terms to detect
        """
        self._include_abbreviations = include_abbreviations
        self._categories = categories
        self._custom_terms = custom_terms or {}

        # Build combined database
        self._database = self._build_database()

    def _build_database(self) -> dict[str, dict]:
        """Build the combined jargon database."""
        db = dict(TECHNICAL_JARGON_DB)

        if self._include_abbreviations:
            db.update(ABBREVIATION_DB)

        if self._custom_terms:
            db.update(self._custom_terms)

        # Filter by categories if specified
        if self._categories:
            db = {
                term: info
                for term, info in db.items()
                if info.get("category") in self._categories
            }

        return db

    def detect(self, text: str) -> list[JargonTerm]:
        """Detect jargon terms in text.

        Args:
            text: The text to scan for jargon

        Returns:
            List of detected JargonTerm objects
        """
        if not text or not text.strip():
            return []

        detected = []
        text_lower = text.lower()

        for term, info in self._database.items():
            # Build case-insensitive pattern
            pattern = r'\b' + re.escape(term) + r'\b'

            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Get surrounding context (up to 50 chars before/after)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]

                # Add ellipsis if truncated
                if start > 0:
                    context = "..." + context
                if end < len(text):
                    context = context + "..."

                jargon_term = JargonTerm(
                    term=match.group(),
                    context=context,
                    definition=info.get("definition"),
                    simple_alternative=info.get("simple"),
                    category=info.get("category", JargonCategory.GENERAL),
                    position=match.start(),
                )
                detected.append(jargon_term)

        # Sort by position for consistent ordering
        detected.sort(key=lambda t: t.position)

        # Remove duplicates (same term at same position)
        seen = set()
        unique = []
        for term in detected:
            key = (term.term.lower(), term.position)
            if key not in seen:
                seen.add(key)
                unique.append(term)

        return unique

    def suggest_replacements(self, text: str) -> str:
        """Replace jargon with plain language alternatives.

        Args:
            text: The text to simplify

        Returns:
            Text with jargon replaced by plain alternatives
        """
        if not text or not text.strip():
            return text

        result = text

        # Sort terms by length (longest first) to avoid partial replacements
        sorted_terms = sorted(
            self._database.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )

        for term, info in sorted_terms:
            if "simple" not in info:
                continue

            # Build case-preserving replacement
            pattern = r'\b' + re.escape(term) + r'\b'

            def replace_match(match):
                """Preserve original case style."""
                original = match.group()
                replacement = info["simple"]

                if original.isupper():
                    return replacement.upper()
                elif original[0].isupper():
                    return replacement.capitalize()
                else:
                    return replacement

            result = re.sub(pattern, replace_match, result, flags=re.IGNORECASE)

        return result

    def simplify(self, text: str) -> SimplificationResult:
        """Simplify text and return detailed result.

        Args:
            text: The text to simplify

        Returns:
            SimplificationResult with original, simplified, and changes
        """
        if not text or not text.strip():
            return SimplificationResult(
                original_text=text,
                simplified_text=text,
                changes_made=[],
                terms_replaced=0,
            )

        # Detect jargon first
        detected = self.detect(text)

        # Apply replacements
        simplified = self.suggest_replacements(text)

        # Build list of changes
        changes = []
        for term in detected:
            if term.simple_alternative:
                changes.append(f"'{term.term}' -> '{term.simple_alternative}'")

        return SimplificationResult(
            original_text=text,
            simplified_text=simplified,
            changes_made=changes,
            terms_replaced=len(detected),
            confidence=1.0 if len(detected) < 5 else 0.9,
        )

    def get_definition(self, term: str) -> Optional[str]:
        """Get the definition for a term.

        Args:
            term: The term to look up

        Returns:
            Definition string or None if not found
        """
        term_lower = term.lower()
        if term_lower in self._database:
            return self._database[term_lower].get("definition")
        return None

    def get_alternatives(self, term: str) -> list[str]:
        """Get all alternatives for a term.

        Args:
            term: The term to look up

        Returns:
            List of alternative phrases
        """
        term_lower = term.lower()
        if term_lower not in self._database:
            return []

        info = self._database[term_lower]
        alternatives = []

        if "simple" in info:
            alternatives.append(info["simple"])

        if "alternatives" in info:
            alternatives.extend(info["alternatives"])

        return list(dict.fromkeys(alternatives))  # Remove duplicates, preserve order

    def add_term(
        self,
        term: str,
        simple: str,
        definition: Optional[str] = None,
        category: JargonCategory = JargonCategory.GENERAL,
        alternatives: Optional[list[str]] = None,
    ) -> None:
        """Add a custom term to the detector.

        Args:
            term: The jargon term
            simple: Plain language replacement
            definition: Optional definition
            category: Category for the term
            alternatives: Additional alternatives
        """
        self._database[term.lower()] = {
            "definition": definition,
            "simple": simple,
            "category": category,
        }
        if alternatives:
            self._database[term.lower()]["alternatives"] = alternatives

    def remove_term(self, term: str) -> bool:
        """Remove a term from the detector.

        Args:
            term: The term to remove

        Returns:
            True if removed, False if not found
        """
        term_lower = term.lower()
        if term_lower in self._database:
            del self._database[term_lower]
            return True
        return False

    @property
    def term_count(self) -> int:
        """Get the number of terms in the database."""
        return len(self._database)

    def get_terms_by_category(self, category: JargonCategory) -> list[str]:
        """Get all terms in a category.

        Args:
            category: The category to filter by

        Returns:
            List of terms in that category
        """
        return [
            term
            for term, info in self._database.items()
            if info.get("category") == category
        ]
