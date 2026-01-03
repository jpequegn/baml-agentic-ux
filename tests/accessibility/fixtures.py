"""Test fixtures for accessibility module tests.

This module provides sample schemas, responses, and configurations
for testing accessibility features at different compliance levels.

Issue #77 - Task 4.11: Testing & Documentation
"""

import pytest


# ============================================
# Sample Responses by Complexity
# ============================================


SIMPLE_RESPONSES = {
    "greeting": "Hello! How can I help you today?",
    "confirmation": "Done. Your task is saved.",
    "error": "Sorry, that did not work. Try again.",
    "list": "Here are your tasks:\n1. Buy milk\n2. Call mom\n3. Fix bike",
    "question": "What would you like to do next?",
}

MODERATE_RESPONSES = {
    "success": "Your task has been created successfully. You can find it in your task list on the home screen.",
    "error": "We encountered an error while processing your request. Please check your input and try again.",
    "help": "To create a new task, say 'add task' followed by the task name. You can also set a due date by saying 'by' and the date.",
    "status": "You have completed 5 tasks today. There are 3 remaining tasks in your list.",
}

COMPLEX_RESPONSES = {
    "technical": (
        "The authentication protocol necessitates the implementation of "
        "sophisticated verification methodologies that subsequently require "
        "comprehensive prerequisite configurations notwithstanding the "
        "aforementioned complexity of the authorization mechanisms."
    ),
    "jargon_heavy": (
        "To leverage our synergistic capabilities, we'll need to pivot our "
        "paradigm and align our vertical integration strategies while "
        "maintaining a holistic view of our scalable architecture."
    ),
    "long_sentences": (
        "The system will process your request through multiple stages of "
        "validation and verification to ensure compliance with security "
        "protocols and organizational policies before finally submitting "
        "the approved changes to the production environment where they "
        "will be reviewed by the operations team who will determine the "
        "appropriate deployment window based on system load and maintenance "
        "schedules that are defined in the operational guidelines document."
    ),
    "passive_voice": (
        "The document was created by the system. The settings were changed "
        "by the administrator. The file was uploaded by the user. The task "
        "was completed by the automated process."
    ),
}


# ============================================
# Sample Schemas by Compliance Level
# ============================================


LEVEL_A_SCHEMA = {
    "name": "Level A Task Manager",
    "description": "A task manager meeting Level A accessibility requirements",
    "version": "1.0.0",
    "accessibility": {
        "target_level": "A",
        "language": "en",
    },
    "components": [
        {
            "id": "greeting",
            "type": "message",
            "feedback": {
                "success_template": "Hello! I'm your task helper.",
            },
        },
        {
            "id": "create_task",
            "type": "action",
            "feedback": {
                "success_template": "Task added!",
                "error_template": "Could not add task.",
            },
        },
        {
            "id": "list_tasks",
            "type": "query",
            "feedback": {
                "success_template": "Here are your tasks.",
            },
        },
    ],
    "timing": {
        "response_timeout": 20000,
        "typing_indicator": True,
    },
}

LEVEL_AA_SCHEMA = {
    "name": "Level AA Accessible Assistant",
    "description": "An assistant meeting Level AA accessibility requirements",
    "version": "1.0.0",
    "accessibility": {
        "target_level": "AA",
        "language": "en",
        "plain_language": True,
        "reading_level_target": 8,
    },
    "components": [
        {
            "id": "welcome",
            "type": "message",
            "feedback": {
                "success_template": "Hi! I can help you with tasks.",
                "aria_label": "Welcome message",
            },
            "accessibility": {
                "screen_reader_text": "Welcome to the task manager",
            },
        },
        {
            "id": "create_task",
            "type": "action",
            "feedback": {
                "success_template": "Task created. It's in your list.",
                "error_template": "Task failed. Please try again.",
            },
            "accessibility": {
                "announce_on_complete": True,
            },
        },
        {
            "id": "search",
            "type": "query",
            "feedback": {
                "success_template": "Found {count} tasks.",
                "empty_template": "No tasks found.",
            },
        },
        {
            "id": "settings",
            "type": "navigation",
            "feedback": {
                "success_template": "Settings opened.",
            },
        },
    ],
    "timing": {
        "response_timeout": 30000,
        "typing_indicator": True,
        "allow_extension": True,
        "extension_multiplier": 2,
    },
}

LEVEL_AAA_SCHEMA = {
    "name": "Level AAA Maximum Accessibility",
    "description": "An interface meeting Level AAA accessibility requirements",
    "version": "1.0.0",
    "accessibility": {
        "target_level": "AAA",
        "language": "en",
        "plain_language": True,
        "reading_level_target": 6,
        "sign_language_support": True,
        "captions_enabled": True,
    },
    "components": [
        {
            "id": "greeting",
            "type": "message",
            "feedback": {
                "success_template": "Hi! I am here to help.",
                "aria_label": "Greeting",
            },
            "accessibility": {
                "screen_reader_text": "Greeting message",
                "focus_on_render": True,
            },
        },
        {
            "id": "help",
            "type": "message",
            "feedback": {
                "success_template": "Say 'add' to add a task.",
            },
        },
        {
            "id": "add_task",
            "type": "action",
            "feedback": {
                "success_template": "Task added!",
                "error_template": "Error. Try again.",
            },
            "accessibility": {
                "announce_on_complete": True,
                "confirmation_required": True,
            },
        },
    ],
    "timing": {
        "response_timeout": 60000,
        "typing_indicator": True,
        "allow_extension": True,
        "extension_multiplier": 3,
        "pause_on_focus_loss": True,
    },
    "input_methods": {
        "voice": True,
        "keyboard": True,
        "switch": True,
        "eye_tracking": True,
    },
}

NON_COMPLIANT_SCHEMA = {
    "name": "Non-Compliant Interface",
    "description": "An interface with multiple accessibility issues",
    "version": "1.0.0",
    "components": [
        {
            "id": "complex_welcome",
            "type": "message",
            "feedback": {
                "success_template": (
                    "The implementation of this sophisticated interface necessitates "
                    "the utilization of advanced methodologies for authorization and "
                    "authentication protocols that subsequently require prerequisite "
                    "configurations notwithstanding the aforementioned complexity."
                ),
            },
        },
        {
            "id": "jargon_action",
            "type": "action",
            "feedback": {
                "success_template": (
                    "Synergistic paradigm pivot achieved. Vertical integration "
                    "aligned with holistic scalable architecture metrics."
                ),
                "error_template": (
                    "Critical failure in asynchronous backend processing pipeline. "
                    "Authentication token invalidation triggered cascading errors."
                ),
            },
        },
    ],
    "timing": {
        "response_timeout": 5000,  # Too short
        "typing_indicator": False,
    },
}


# ============================================
# Test Data Sets
# ============================================


JARGON_SAMPLES = {
    "business": [
        "Let's leverage our core competencies to maximize stakeholder value.",
        "We need to pivot our strategy and align on deliverables.",
        "This synergistic approach will optimize our bandwidth.",
    ],
    "technical": [
        "The API endpoint requires authentication via OAuth2.",
        "The backend service handles async processing.",
        "Cache invalidation triggered the frontend reload.",
    ],
    "legal": [
        "The aforementioned party shall hereby indemnify.",
        "Notwithstanding the provisions herein contained.",
        "Subject to the terms and conditions therein specified.",
    ],
    "medical": [
        "The patient presents with acute symptoms.",
        "Administer the medication per the protocol.",
        "Monitor for adverse reactions.",
    ],
}

PLAIN_LANGUAGE_SAMPLES = [
    "Hello! How can I help you?",
    "Your task was saved.",
    "Here are your items.",
    "Sorry, that did not work.",
    "What do you want to do?",
]


# ============================================
# Pytest Fixtures
# ============================================


@pytest.fixture
def simple_schema():
    """Minimal schema for basic testing."""
    return {
        "name": "Simple Test",
        "components": [
            {
                "id": "test",
                "type": "message",
                "feedback": {"success_template": "Hello!"},
            }
        ],
    }


@pytest.fixture
def level_a_schema():
    """Schema meeting Level A requirements."""
    return LEVEL_A_SCHEMA.copy()


@pytest.fixture
def level_aa_schema():
    """Schema meeting Level AA requirements."""
    return LEVEL_AA_SCHEMA.copy()


@pytest.fixture
def level_aaa_schema():
    """Schema meeting Level AAA requirements."""
    return LEVEL_AAA_SCHEMA.copy()


@pytest.fixture
def non_compliant_schema():
    """Schema with accessibility violations."""
    return NON_COMPLIANT_SCHEMA.copy()


@pytest.fixture
def simple_responses():
    """Simple, accessible responses."""
    return SIMPLE_RESPONSES.copy()


@pytest.fixture
def complex_responses():
    """Complex responses with accessibility issues."""
    return COMPLEX_RESPONSES.copy()


@pytest.fixture
def jargon_samples():
    """Jargon samples by category."""
    return JARGON_SAMPLES.copy()
