# CI/CD Integration Patterns for Conversational AI Testing

📅 2025-12-30

**Research Focus**: Comprehensive analysis of CI/CD integration patterns, automated testing, reporting formats, continuous monitoring, and MLOps strategies for conversational AI systems.

---

## 1. CI Pipeline Integration

### GitHub Actions for Chatbot Testing

**Key Capabilities:**
- Matrix workflows supporting multiple operating systems and language versions (Node.js, Python, Java, etc.)
- Automated functional, load, regression, and security testing
- Seamless integration with 55+ chatbot technologies and NLU/NLP engines

**Implementation Pattern:**

```yaml
name: Rasa CI/CD Pipeline
on:
  push:
    branches: [main]
    paths:
      - 'data/**'
      - 'domain/**'
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Pull Rasa Docker Image
        run: docker pull rasa/rasa:latest

      - name: Train Model
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          RASA_LICENSE: ${{ secrets.RASA_LICENSE }}
        run: |
          docker run --rm \
            -v $(pwd):/app \
            -e OPENAI_API_KEY \
            -e RASA_LICENSE \
            rasa/rasa:latest train

      - name: Run E2E Tests
        run: |
          docker run --rm \
            -v $(pwd):/app \
            rasa/rasa:latest test

      - name: Upload Test Results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: results/
          retention-days: 90
```

**Official RasaHQ GitHub Action:**

```yaml
- uses: RasaHQ/rasa-train-test-gha@main
  with:
    data_validate: true
    rasa_train: true
    rasa_test: true
    test_type: 'all'  # nlu, core, or all
```

**Benefits:**
- Automated tests catch errors before production
- Enforce coding and model training standards
- Quick iteration cycles for addressing user feedback
- Version control for conversation flows, prompts, and custom actions

### GitLab CI Chatbot Pipelines

**Integration with Jenkins:**

```yaml
# .gitlab-ci.yml
stages:
  - test
  - train
  - deploy

chatbot_test:
  stage: test
  script:
    - python -m pytest tests/test_intents.py
    - python -m pytest tests/test_flows.py
  artifacts:
    reports:
      junit: test-results.xml
    paths:
      - test-results/
    expire_in: 30 days

nlu_training:
  stage: train
  script:
    - rasa train nlu
    - rasa test nlu --out results
  only:
    changes:
      - data/nlu/**
      - config.yml
```

**Botium Box CI/CD Integration:**
- HTTP(S) webhook support for triggering builds
- Low-key HTTP/JSON based integration
- Dialogue-based test cases
- NLP analytics integration
- Jenkins connector with pipeline-specific configurations

**ChatOps Integration:**
```bash
# Slack/Mattermost command triggers CI/CD job
/chatops run deploy staging
```

### Jenkins Conversational Test Jobs

**Python Test Script Pattern:**

```python
# test_chatbot.py
import requests
import pytest

class TestChatbotAPI:
    def setup_method(self):
        self.api_url = "https://api.chatbot.example.com"
        self.headers = {"Authorization": "Bearer TOKEN"}

    def test_intent_recognition(self):
        response = requests.post(
            f"{self.api_url}/parse",
            json={"text": "Book a flight to London"},
            headers=self.headers
        )
        assert response.status_code == 200
        assert response.json()["intent"] == "book_flight"
        assert "London" in response.json()["entities"]

    def test_entity_extraction(self):
        response = requests.post(
            f"{self.api_url}/parse",
            json={"text": "Schedule meeting at 3pm tomorrow"},
            headers=self.headers
        )
        entities = response.json()["entities"]
        assert entities["time"] == "3pm"
        assert entities["date"] == "tomorrow"
```

**Jenkinsfile Configuration:**

```groovy
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Run NLU Tests') {
            steps {
                sh 'pytest tests/test_nlu.py --junitxml=results/nlu.xml'
            }
        }

        stage('Run Conversation Tests') {
            steps {
                sh 'pytest tests/test_conversations.py --junitxml=results/conversations.xml'
            }
        }

        stage('Publish Results') {
            steps {
                junit 'results/*.xml'
                publishHTML([
                    reportDir: 'htmlcov',
                    reportFiles: 'index.html',
                    reportName: 'Coverage Report'
                ])
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'results/**', fingerprint: true
        }
        success {
            slackSend(color: 'good', message: "Chatbot tests passed: ${env.JOB_NAME} ${env.BUILD_NUMBER}")
        }
        failure {
            slackSend(color: 'danger', message: "Chatbot tests failed: ${env.JOB_NAME} ${env.BUILD_NUMBER}")
        }
    }
}
```

### Test Parallelization Strategies

**Key Benefits:**
- Testing cycles reduced by 50% without sacrificing thoroughness
- Multiple evaluations running in parallel
- Dramatically increased capacity for simulating high-volume interactions

**Rasa NLU Parallelism Configuration:**

```yaml
# config.yml
pipeline:
  - name: WhitespaceTokenizer
  - name: RegexFeaturizer
  - name: LexicalSyntacticFeaturizer
  - name: CountVectorsFeaturizer
  - name: DIETClassifier
    epochs: 100
    constrain_similarities: true

# Set environment variables for parallel execution
# TF_INTRA_OP_PARALLELISM_THREADS: Maximum threads for one operation
# TF_INTER_OP_PARALLELISM_THREADS: Number of ops to run in parallel
```

**GitHub Actions Matrix Strategy:**

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11']
        test-suite: ['nlu', 'core', 'integration']
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Run ${{ matrix.test-suite }} tests
        run: pytest tests/${{ matrix.test-suite }}
```

**Cyara Botium Enhanced Scalability:**
- Dramatically increased capacity for parallel test executions
- High-volume interaction simulation
- Stress testing capabilities

### Caching for NLU Models

**GitHub Actions Caching:**

```yaml
- name: Cache Dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      ~/.cache/huggingface
      models/
    key: ${{ runner.os }}-chatbot-${{ hashFiles('**/requirements.txt') }}-${{ hashFiles('**/config.yml') }}
    restore-keys: |
      ${{ runner.os }}-chatbot-

- name: Cache Trained Models
  uses: actions/cache@v4
  with:
    path: models/*.tar.gz
    key: model-${{ hashFiles('data/**') }}-${{ hashFiles('config.yml') }}
    restore-keys: |
      model-
```

**LLM Inference Optimization:**
- **Key-Value (KV) Caching**: Cache intermediate states to avoid recomputation during decode phase
- **Model Parallelization**: Pipeline parallelism, tensor parallelism, sequence parallelism
- **Benefits**: Reduced per-device memory footprint, enabling larger models or batch processing

**Best Practices:**
- Cache dependency installations (pip, npm, conda environments)
- Cache pre-trained model weights
- Cache compiled TensorFlow/PyTorch graphs
- Use cache keys based on configuration file hashes
- Implement fallback restore-keys for partial cache hits

---

## 2. Automated Regression Testing

### Nightly Conversation Regression Suites

**Pattern: Comprehensive Nightly Test Suite**

```yaml
# .github/workflows/nightly-regression.yml
name: Nightly Regression Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Run at 2 AM daily
  workflow_dispatch:  # Manual trigger

jobs:
  regression:
    runs-on: ubuntu-latest
    timeout-minutes: 120

    steps:
      - uses: actions/checkout@v4

      - name: Setup Environment
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install Dependencies
        run: |
          pip install -r requirements.txt
          pip install rasa pytest pytest-html

      - name: Load Baseline Model
        run: |
          aws s3 cp s3://models/baseline/model.tar.gz ./models/

      - name: Run Full Regression Suite
        run: |
          pytest tests/regression/ \
            --html=reports/regression.html \
            --self-contained-html \
            -v \
            --junitxml=reports/regression.xml

      - name: Compare with Baseline
        run: |
          python scripts/compare_performance.py \
            --baseline reports/baseline.json \
            --current reports/current.json \
            --threshold 0.05

      - name: Upload Reports
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: regression-reports
          path: reports/
          retention-days: 90

      - name: Notify on Failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "❌ Nightly regression tests failed",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Nightly Regression Failure*\nRun: ${{ github.run_id }}"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

**Regression Test Suite Structure:**

```python
# tests/regression/test_intent_accuracy.py
import pytest
from typing import List, Dict
import json

@pytest.fixture
def baseline_intents():
    """Load baseline intent recognition accuracy"""
    with open('tests/fixtures/baseline_intents.json') as f:
        return json.load(f)

class TestIntentRegression:
    """Validate no degradation in intent recognition"""

    def test_high_confidence_intents(self, chatbot, baseline_intents):
        """Test common intents maintain >95% accuracy"""
        test_cases = baseline_intents['high_confidence']

        results = []
        for case in test_cases:
            response = chatbot.parse(case['text'])
            correct = response['intent']['name'] == case['expected_intent']
            results.append({
                'text': case['text'],
                'expected': case['expected_intent'],
                'actual': response['intent']['name'],
                'confidence': response['intent']['confidence'],
                'correct': correct
            })

        accuracy = sum(r['correct'] for r in results) / len(results)
        assert accuracy >= 0.95, f"Intent accuracy {accuracy:.2%} below threshold"

    def test_entity_extraction_regression(self, chatbot, baseline_intents):
        """Ensure entity extraction hasn't degraded"""
        test_cases = baseline_intents['entity_tests']

        for case in test_cases:
            response = chatbot.parse(case['text'])
            extracted = {e['entity']: e['value'] for e in response['entities']}

            for entity_type, expected_value in case['expected_entities'].items():
                assert entity_type in extracted, f"Missing entity: {entity_type}"
                assert extracted[entity_type] == expected_value
```

### Pull Request Conversation Checks

**PR Check Workflow:**

```yaml
# .github/workflows/pr-checks.yml
name: PR Chatbot Checks

on:
  pull_request:
    types: [opened, synchronize]
    paths:
      - 'data/**'
      - 'domain/**'
      - 'actions/**'
      - 'config.yml'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate Training Data
        run: rasa data validate --domain domain.yml --data data/

      - name: Check for Data Conflicts
        run: |
          python scripts/check_intent_conflicts.py
          python scripts/check_entity_conflicts.py

      - name: Train and Test
        run: |
          rasa train
          rasa test nlu --nlu data/test/ --out results/

      - name: Generate Comparison Report
        run: |
          python scripts/generate_comparison.py \
            --base ${{ github.base_ref }} \
            --head ${{ github.head_ref }} \
            --output pr-report.md

      - name: Comment on PR
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('pr-report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });
```

**Comparison Report Script:**

```python
# scripts/generate_comparison.py
import json
import argparse
from pathlib import Path

def generate_comparison(base_results, head_results):
    """Compare NLU performance between base and head branches"""

    report = ["# 🤖 Chatbot Performance Comparison\n"]

    # Intent Classification
    base_intent_acc = base_results['intent_evaluation']['accuracy']
    head_intent_acc = head_results['intent_evaluation']['accuracy']
    diff = head_intent_acc - base_intent_acc

    emoji = "✅" if diff >= 0 else "⚠️"
    report.append(f"\n## Intent Classification {emoji}\n")
    report.append(f"- Base: {base_intent_acc:.2%}")
    report.append(f"- Head: {head_intent_acc:.2%}")
    report.append(f"- Change: {diff:+.2%}\n")

    # Entity Extraction
    base_entity_f1 = base_results['entity_evaluation']['f1_score']
    head_entity_f1 = head_results['entity_evaluation']['f1_score']
    diff = head_entity_f1 - base_entity_f1

    emoji = "✅" if diff >= 0 else "⚠️"
    report.append(f"\n## Entity Extraction {emoji}\n")
    report.append(f"- Base F1: {base_entity_f1:.3f}")
    report.append(f"- Head F1: {head_entity_f1:.3f}")
    report.append(f"- Change: {diff:+.3f}\n")

    # Regression Check
    if diff < -0.05:
        report.append("\n⚠️ **WARNING**: Performance regression detected (>5% drop)")

    return '\n'.join(report)
```

### Intent Model Regression Detection

**Automated Detection System:**

```python
# tests/test_model_regression.py
import pytest
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np

class TestModelRegression:
    """Detect regressions in NLU model performance"""

    ACCURACY_THRESHOLD = 0.92
    F1_THRESHOLD = 0.90
    REGRESSION_TOLERANCE = 0.05  # 5% max drop

    def test_intent_accuracy_threshold(self, model, test_data):
        """Ensure intent accuracy meets minimum threshold"""
        predictions = [model.parse(text)['intent']['name'] for text in test_data['texts']]
        actual = test_data['intents']

        accuracy = np.mean(np.array(predictions) == np.array(actual))
        assert accuracy >= self.ACCURACY_THRESHOLD, \
            f"Accuracy {accuracy:.2%} below threshold {self.ACCURACY_THRESHOLD:.2%}"

    def test_no_regression_vs_baseline(self, model, test_data, baseline_metrics):
        """Compare current model against baseline performance"""
        predictions = [model.parse(text)['intent']['name'] for text in test_data['texts']]
        actual = test_data['intents']

        current_accuracy = np.mean(np.array(predictions) == np.array(actual))
        baseline_accuracy = baseline_metrics['intent_accuracy']

        regression = baseline_accuracy - current_accuracy
        assert regression <= self.REGRESSION_TOLERANCE, \
            f"Regression detected: {regression:.2%} drop from baseline"

    def test_per_intent_f1_scores(self, model, test_data, baseline_metrics):
        """Check F1 scores for individual intents"""
        predictions = [model.parse(text)['intent']['name'] for text in test_data['texts']]
        actual = test_data['intents']

        report = classification_report(actual, predictions, output_dict=True)

        for intent, metrics in report.items():
            if intent in ['accuracy', 'macro avg', 'weighted avg']:
                continue

            baseline_f1 = baseline_metrics['per_intent_f1'].get(intent, 0.0)
            current_f1 = metrics['f1-score']

            assert current_f1 >= max(self.F1_THRESHOLD, baseline_f1 - self.REGRESSION_TOLERANCE), \
                f"Intent '{intent}' F1 score {current_f1:.3f} below threshold"
```

### Response Quality Monitoring

**Automated Quality Checks:**

```python
# tests/test_response_quality.py
import pytest
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase

class TestResponseQuality:
    """Monitor LLM chatbot response quality"""

    def test_answer_relevancy(self, chatbot, test_questions):
        """Ensure responses are relevant to user queries"""
        relevancy_metric = AnswerRelevancyMetric(threshold=0.7)

        for question in test_questions:
            response = chatbot.get_response(question['text'])

            test_case = LLMTestCase(
                input=question['text'],
                actual_output=response,
                expected_output=question.get('expected_answer')
            )

            relevancy_metric.measure(test_case)
            assert relevancy_metric.score >= 0.7, \
                f"Low relevancy ({relevancy_metric.score:.2f}) for: {question['text']}"

    def test_response_faithfulness(self, chatbot, test_cases_with_context):
        """Verify responses are grounded in provided context"""
        faithfulness_metric = FaithfulnessMetric(threshold=0.8)

        for case in test_cases_with_context:
            response = chatbot.get_response(
                case['question'],
                context=case['context']
            )

            test_case = LLMTestCase(
                input=case['question'],
                actual_output=response,
                retrieval_context=[case['context']]
            )

            faithfulness_metric.measure(test_case)
            assert faithfulness_metric.score >= 0.8, \
                f"Hallucination detected in response to: {case['question']}"

    def test_conversation_completeness(self, chatbot, conversation_flows):
        """Validate multi-turn conversation completeness"""
        for flow in conversation_flows:
            conversation_history = []

            for turn in flow['turns']:
                response = chatbot.get_response(
                    turn['user_message'],
                    history=conversation_history
                )

                conversation_history.append({
                    'user': turn['user_message'],
                    'bot': response
                })

                # Check required information is present
                for required_element in turn.get('required_elements', []):
                    assert required_element.lower() in response.lower(), \
                        f"Missing required element '{required_element}' in response"
```

---

## 3. Test Reporting Formats

### JUnit XML for Conversation Tests

**Standard JUnit XML Output:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Chatbot Test Suite" tests="45" failures="2" errors="0" time="12.345">
  <testsuite name="IntentRecognitionTests" tests="20" failures="1" errors="0" time="5.123">
    <testcase classname="tests.test_intents" name="test_booking_intent" time="0.234">
      <system-out>
        User: "Book a flight to Paris"
        Intent: book_flight (confidence: 0.98)
        Entities: {"destination": "Paris"}
      </system-out>
    </testcase>

    <testcase classname="tests.test_intents" name="test_cancellation_intent" time="0.189">
      <failure message="Intent mismatch" type="AssertionError">
        Expected: cancel_booking
        Got: modify_booking
        Confidence: 0.87
        User message: "I need to cancel my reservation"
      </failure>
    </testcase>
  </testsuite>

  <testsuite name="ConversationFlowTests" tests="15" failures="0" errors="0" time="4.567">
    <testcase classname="tests.test_flows" name="test_booking_flow_complete" time="1.234">
      <system-out>
        Turn 1: User: "Book a flight" → Bot: "Where would you like to go?"
        Turn 2: User: "London" → Bot: "When do you want to travel?"
        Turn 3: User: "Next Monday" → Bot: "Booking confirmed for London, Monday"
      </system-out>
    </testcase>
  </testsuite>

  <testsuite name="EntityExtractionTests" tests="10" failures="1" errors="0" time="2.655">
    <testcase classname="tests.test_entities" name="test_date_extraction" time="0.145">
      <failure message="Entity not extracted" type="AssertionError">
        User: "Schedule for tomorrow at 3pm"
        Expected entities: {"date": "tomorrow", "time": "3pm"}
        Actual entities: {"date": "tomorrow"}
        Missing: time
      </failure>
    </testcase>
  </testsuite>
</testsuites>
```

**DataDog JUnit Upload:**

```yaml
- name: Upload Test Results to DataDog
  uses: DataDog/junit-upload-github-action@v1
  with:
    api-key: ${{ secrets.DD_API_KEY }}
    service: chatbot-api
    env: production
    files: reports/junit/*.xml
    logs: true  # Forward <system-out>, <system-err>, <failure> as logs
```

**Pytest Configuration for JUnit XML:**

```python
# pytest.ini
[pytest]
junit_family = xunit2
junit_logging = all
junit_log_passing_tests = true
junit_duration_report = total

# Custom markers for categorization
markers =
    intent: Intent recognition tests
    entity: Entity extraction tests
    flow: Conversation flow tests
    regression: Regression tests
    smoke: Smoke tests
```

**Generate JUnit XML with pytest:**

```bash
pytest tests/ \
  --junitxml=reports/junit/chatbot-tests.xml \
  --html=reports/html/index.html \
  --self-contained-html \
  -v \
  --tb=short
```

### HTML Test Reports with Conversation Logs

**Pytest-HTML Enhanced Report:**

```python
# conftest.py - Custom HTML report with conversation logs
import pytest
from datetime import datetime

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Add conversation logs to HTML report"""
    outcome = yield
    report = outcome.get_result()

    if report.when == 'call':
        # Add conversation transcript to report
        if hasattr(item, 'conversation_log'):
            extra = getattr(report, 'extra', [])

            # Format conversation as HTML table
            html = '<h3>Conversation Transcript</h3><table>'
            html += '<tr><th>Turn</th><th>Speaker</th><th>Message</th><th>Intent</th><th>Confidence</th></tr>'

            for i, turn in enumerate(item.conversation_log, 1):
                html += f'''
                <tr>
                    <td>{i}</td>
                    <td>{turn['speaker']}</td>
                    <td>{turn['message']}</td>
                    <td>{turn.get('intent', 'N/A')}</td>
                    <td>{turn.get('confidence', 'N/A')}</td>
                </tr>
                '''

            html += '</table>'
            extra.append(pytest.html.extras.html(html))
            report.extra = extra

@pytest.fixture
def conversation_logger(request):
    """Fixture to log conversation turns"""
    request.node.conversation_log = []

    def log_turn(speaker, message, intent=None, confidence=None):
        request.node.conversation_log.append({
            'speaker': speaker,
            'message': message,
            'intent': intent,
            'confidence': confidence
        })

    return log_turn
```

**Usage in Tests:**

```python
def test_booking_conversation(chatbot, conversation_logger):
    """Test complete booking flow with logging"""

    # Turn 1
    user_msg = "I want to book a flight"
    response = chatbot.parse(user_msg)
    conversation_logger('User', user_msg)
    conversation_logger('Bot', response['text'], response['intent']['name'], response['intent']['confidence'])

    # Turn 2
    user_msg = "To Paris next Monday"
    response = chatbot.parse(user_msg, context=response['context'])
    conversation_logger('User', user_msg)
    conversation_logger('Bot', response['text'], response['intent']['name'], response['intent']['confidence'])

    assert response['booking_confirmed'] == True
```

**Custom HTML Report Template:**

```html
<!-- reports/template.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Chatbot Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .summary { background: #f0f0f0; padding: 15px; border-radius: 5px; }
        .pass { color: green; }
        .fail { color: red; }
        .conversation { border: 1px solid #ddd; margin: 10px 0; padding: 10px; }
        .user-msg { background: #e3f2fd; padding: 8px; margin: 5px 0; border-radius: 5px; }
        .bot-msg { background: #f1f8e9; padding: 8px; margin: 5px 0; border-radius: 5px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
    </style>
</head>
<body>
    <h1>🤖 Chatbot Test Report</h1>

    <div class="summary">
        <h2>Summary</h2>
        <p>Total Tests: {{ total_tests }}</p>
        <p class="pass">Passed: {{ passed }}</p>
        <p class="fail">Failed: {{ failed }}</p>
        <p>Duration: {{ duration }}s</p>
    </div>

    {% for test in tests %}
    <div class="test-case">
        <h3>{{ test.name }} {% if test.passed %}✅{% else %}❌{% endif %}</h3>

        {% if test.conversation %}
        <div class="conversation">
            <h4>Conversation Transcript</h4>
            {% for turn in test.conversation %}
                <div class="{{ 'user-msg' if turn.speaker == 'User' else 'bot-msg' }}">
                    <strong>{{ turn.speaker }}:</strong> {{ turn.message }}
                    {% if turn.intent %}
                        <br><small>Intent: {{ turn.intent }} ({{ turn.confidence }})</small>
                    {% endif %}
                </div>
            {% endfor %}
        </div>
        {% endif %}

        {% if not test.passed %}
        <div class="failure">
            <strong>Failure:</strong>
            <pre>{{ test.error }}</pre>
        </div>
        {% endif %}
    </div>
    {% endfor %}
</body>
</html>
```

### Markdown Summary Reports

**GitHub Actions Summary:**

```yaml
- name: Generate Markdown Summary
  if: always()
  run: |
    python scripts/generate_summary.py --output $GITHUB_STEP_SUMMARY
```

**Summary Generation Script:**

```python
# scripts/generate_summary.py
import json
import sys
from pathlib import Path

def generate_markdown_summary(results_file):
    """Generate GitHub Actions markdown summary"""

    with open(results_file) as f:
        results = json.load(f)

    summary = []
    summary.append("# 🤖 Chatbot Test Results\n")

    # Overall metrics
    total = results['summary']['total']
    passed = results['summary']['passed']
    failed = results['summary']['failed']
    pass_rate = (passed / total * 100) if total > 0 else 0

    emoji = "✅" if failed == 0 else "⚠️"
    summary.append(f"## Overall Results {emoji}\n")
    summary.append(f"- **Total Tests**: {total}")
    summary.append(f"- **Passed**: {passed} ({pass_rate:.1f}%)")
    summary.append(f"- **Failed**: {failed}")
    summary.append(f"- **Duration**: {results['summary']['duration']:.2f}s\n")

    # Intent accuracy
    summary.append("## Intent Recognition\n")
    summary.append(f"- **Accuracy**: {results['intent_accuracy']:.2%}")
    summary.append(f"- **F1 Score**: {results['intent_f1']:.3f}\n")

    # Entity extraction
    summary.append("## Entity Extraction\n")
    summary.append(f"- **Precision**: {results['entity_precision']:.3f}")
    summary.append(f"- **Recall**: {results['entity_recall']:.3f}")
    summary.append(f"- **F1 Score**: {results['entity_f1']:.3f}\n")

    # Failed tests detail
    if failed > 0:
        summary.append("## Failed Tests\n")
        for test in results['failed_tests']:
            summary.append(f"### ❌ {test['name']}\n")
            summary.append(f"```\n{test['error']}\n```\n")

    # Performance comparison
    if 'baseline' in results:
        summary.append("## Performance vs Baseline\n")
        summary.append("| Metric | Baseline | Current | Change |")
        summary.append("|--------|----------|---------|--------|")

        for metric, baseline_val in results['baseline'].items():
            current_val = results.get(metric, 0)
            change = current_val - baseline_val
            emoji = "📈" if change > 0 else ("📉" if change < 0 else "➡️")
            summary.append(f"| {metric} | {baseline_val:.3f} | {current_val:.3f} | {emoji} {change:+.3f} |")

    return '\n'.join(summary)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', default='results/test_results.json')
    parser.add_argument('--output', default=None)
    args = parser.parse_args()

    summary = generate_markdown_summary(args.results)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(summary)
    else:
        print(summary)
```

### Metrics Dashboards (Grafana, DataDog)

**Grafana k6 Integration:**

```javascript
// k6-test.js - Load testing with custom metrics
import http from 'k6/http';
import { check, group } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

// Custom metrics
const intentAccuracy = new Rate('intent_accuracy');
const responseTime = new Trend('chatbot_response_time');
const errorRate = new Rate('error_rate');
const conversationLength = new Trend('conversation_length');

export const options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up
    { duration: '5m', target: 100 },  // Steady state
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    'intent_accuracy': ['rate>0.95'],
    'chatbot_response_time': ['p(95)<500'],
    'error_rate': ['rate<0.01'],
  },
};

export default function() {
  group('Intent Recognition', () => {
    const payload = JSON.stringify({
      text: 'Book a flight to London',
      conversation_id: `conv_${__VU}_${__ITER}`,
    });

    const response = http.post(
      'https://api.chatbot.com/parse',
      payload,
      { headers: { 'Content-Type': 'application/json' } }
    );

    check(response, {
      'status is 200': (r) => r.status === 200,
      'intent recognized': (r) => {
        const body = JSON.parse(r.body);
        const correct = body.intent.name === 'book_flight';
        intentAccuracy.add(correct);
        return correct;
      },
      'confidence high': (r) => {
        const body = JSON.parse(r.body);
        return body.intent.confidence > 0.9;
      },
    });

    responseTime.add(response.timings.duration);
    errorRate.add(response.status !== 200);
  });
}
```

**DataDog Custom Metrics:**

```python
# chatbot_metrics.py
from datadog import initialize, statsd
import time

# Initialize DataDog
initialize(
    api_key='YOUR_API_KEY',
    app_key='YOUR_APP_KEY'
)

class ChatbotMetrics:
    """Track chatbot performance metrics in DataDog"""

    def __init__(self, service='chatbot', env='production'):
        self.service = service
        self.env = env
        self.tags = [f'service:{service}', f'env:{env}']

    def track_intent_recognition(self, intent, confidence, correct):
        """Track intent recognition metrics"""
        tags = self.tags + [f'intent:{intent}']

        # Record confidence
        statsd.gauge('chatbot.intent.confidence', confidence, tags=tags)

        # Record accuracy
        statsd.increment('chatbot.intent.predictions', tags=tags)
        if correct:
            statsd.increment('chatbot.intent.correct', tags=tags)

        # Distribution for analysis
        statsd.distribution('chatbot.intent.confidence.dist', confidence, tags=tags)

    def track_response_time(self, duration_ms, intent=None):
        """Track response time"""
        tags = self.tags.copy()
        if intent:
            tags.append(f'intent:{intent}')

        statsd.timing('chatbot.response.duration', duration_ms, tags=tags)
        statsd.distribution('chatbot.response.duration.dist', duration_ms, tags=tags)

    def track_conversation_metrics(self, conversation_id, turns, completed, satisfaction=None):
        """Track conversation-level metrics"""
        tags = self.tags + [f'conversation:{conversation_id}']

        statsd.gauge('chatbot.conversation.turns', turns, tags=tags)
        statsd.increment('chatbot.conversation.total', tags=tags)

        if completed:
            statsd.increment('chatbot.conversation.completed', tags=tags)

        if satisfaction:
            statsd.gauge('chatbot.conversation.satisfaction', satisfaction, tags=tags)

    def track_fallback_rate(self):
        """Track fallback (didn't understand) rate"""
        statsd.increment('chatbot.fallback.total', tags=self.tags)

    def track_error(self, error_type, severity='error'):
        """Track errors"""
        tags = self.tags + [f'error_type:{error_type}', f'severity:{severity}']
        statsd.increment('chatbot.errors', tags=tags)

# Usage example
metrics = ChatbotMetrics(service='customer-support-bot', env='production')

# In your chatbot code
start = time.time()
response = chatbot.parse(user_message)
duration = (time.time() - start) * 1000

metrics.track_intent_recognition(
    intent=response['intent']['name'],
    confidence=response['intent']['confidence'],
    correct=response['intent']['name'] == expected_intent
)
metrics.track_response_time(duration, intent=response['intent']['name'])
```

**Grafana Dashboard JSON:**

```json
{
  "dashboard": {
    "title": "Chatbot Performance",
    "panels": [
      {
        "title": "Intent Accuracy",
        "targets": [
          {
            "expr": "rate(chatbot_intent_correct[5m]) / rate(chatbot_intent_predictions[5m])",
            "legendFormat": "Intent Accuracy"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Response Time (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, chatbot_response_duration_bucket)",
            "legendFormat": "p95 Response Time"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Conversations by Status",
        "targets": [
          {
            "expr": "sum by (status) (chatbot_conversation_total)",
            "legendFormat": "{{status}}"
          }
        ],
        "type": "pie"
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(chatbot_errors[5m])",
            "legendFormat": "{{error_type}}"
          }
        ],
        "type": "graph",
        "alert": {
          "conditions": [
            {
              "evaluator": { "type": "gt", "params": [0.05] },
              "operator": { "type": "and" },
              "query": { "params": ["A", "5m", "now"] },
              "reducer": { "type": "avg" }
            }
          ]
        }
      }
    ]
  }
}
```

### Slack/Teams Notifications

**GitHub Actions Slack Integration:**

```yaml
- name: Send Slack Notification
  if: always()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "blocks": [
          {
            "type": "header",
            "text": {
              "type": "plain_text",
              "text": "🤖 Chatbot Test Results"
            }
          },
          {
            "type": "section",
            "fields": [
              {
                "type": "mrkdwn",
                "text": "*Status:*\n${{ job.status == 'success' && '✅ Passed' || '❌ Failed' }}"
              },
              {
                "type": "mrkdwn",
                "text": "*Branch:*\n${{ github.ref_name }}"
              },
              {
                "type": "mrkdwn",
                "text": "*Commit:*\n${{ github.sha }}"
              },
              {
                "type": "mrkdwn",
                "text": "*Author:*\n${{ github.actor }}"
              }
            ]
          },
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Test Summary:*\n```${{ steps.test.outputs.summary }}```"
            }
          },
          {
            "type": "actions",
            "elements": [
              {
                "type": "button",
                "text": {
                  "type": "plain_text",
                  "text": "View Details"
                },
                "url": "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
              }
            ]
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

**Advanced Slack Report with Metrics:**

```python
# scripts/send_slack_report.py
import os
import json
import requests
from datetime import datetime

def send_slack_report(results, webhook_url):
    """Send detailed test report to Slack"""

    # Determine color based on results
    color = "good" if results['failed'] == 0 else "danger"

    # Calculate metrics
    pass_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0

    # Build message
    message = {
        "username": "Chatbot CI/CD",
        "icon_emoji": ":robot_face:",
        "attachments": [
            {
                "color": color,
                "title": "🤖 Chatbot Test Results",
                "fields": [
                    {
                        "title": "Status",
                        "value": "✅ Passed" if results['failed'] == 0 else "❌ Failed",
                        "short": True
                    },
                    {
                        "title": "Pass Rate",
                        "value": f"{pass_rate:.1f}%",
                        "short": True
                    },
                    {
                        "title": "Total Tests",
                        "value": str(results['total']),
                        "short": True
                    },
                    {
                        "title": "Failed",
                        "value": str(results['failed']),
                        "short": True
                    },
                    {
                        "title": "Intent Accuracy",
                        "value": f"{results['intent_accuracy']:.2%}",
                        "short": True
                    },
                    {
                        "title": "Entity F1",
                        "value": f"{results['entity_f1']:.3f}",
                        "short": True
                    }
                ],
                "footer": f"Run ID: {os.environ.get('GITHUB_RUN_ID', 'N/A')}",
                "ts": int(datetime.now().timestamp())
            }
        ]
    }

    # Add failed test details if any
    if results['failed'] > 0:
        failed_tests = "\n".join([
            f"• {test['name']}: {test['error'][:100]}..."
            for test in results['failed_tests'][:5]  # Limit to 5
        ])

        message["attachments"].append({
            "color": "danger",
            "title": "Failed Tests",
            "text": failed_tests,
            "mrkdwn_in": ["text"]
        })

    # Add regression warning if applicable
    if results.get('regression_detected'):
        message["attachments"].append({
            "color": "warning",
            "title": "⚠️ Performance Regression Detected",
            "text": f"Accuracy dropped by {results['regression_amount']:.2%}",
        })

    # Send to Slack
    response = requests.post(webhook_url, json=message)
    response.raise_for_status()

if __name__ == '__main__':
    import sys

    with open(sys.argv[1]) as f:
        results = json.load(f)

    webhook_url = os.environ['SLACK_WEBHOOK_URL']
    send_slack_report(results, webhook_url)
```

**Microsoft Teams Webhook:**

```python
# scripts/send_teams_notification.py
import requests
import json

def send_teams_notification(results, webhook_url):
    """Send test results to Microsoft Teams"""

    # Determine theme color
    theme_color = "28a745" if results['failed'] == 0 else "dc3545"

    # Build adaptive card
    card = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "themeColor": theme_color,
        "summary": "Chatbot Test Results",
        "sections": [
            {
                "activityTitle": "🤖 Chatbot Test Results",
                "activitySubtitle": f"Branch: {results['branch']}",
                "facts": [
                    {"name": "Status", "value": "✅ Passed" if results['failed'] == 0 else "❌ Failed"},
                    {"name": "Total Tests", "value": str(results['total'])},
                    {"name": "Passed", "value": str(results['passed'])},
                    {"name": "Failed", "value": str(results['failed'])},
                    {"name": "Intent Accuracy", "value": f"{results['intent_accuracy']:.2%}"},
                    {"name": "Entity F1", "value": f"{results['entity_f1']:.3f}"},
                    {"name": "Duration", "value": f"{results['duration']:.2f}s"}
                ],
                "markdown": True
            }
        ],
        "potentialAction": [
            {
                "@type": "OpenUri",
                "name": "View Details",
                "targets": [
                    {"os": "default", "uri": results['run_url']}
                ]
            }
        ]
    }

    # Add failed tests section if any
    if results['failed'] > 0:
        failed_section = {
            "title": "Failed Tests",
            "text": "\n\n".join([
                f"**{test['name']}**\n{test['error'][:150]}..."
                for test in results['failed_tests'][:3]
            ])
        }
        card["sections"].append(failed_section)

    # Send to Teams
    response = requests.post(webhook_url, json=card)
    response.raise_for_status()
```

---

## 4. Continuous Monitoring

### Production Conversation Logging

**Langfuse Integration:**

```python
# production_chatbot.py
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context

# Initialize Langfuse
langfuse = Langfuse(
    public_key="pk-...",
    secret_key="sk-...",
    host="https://cloud.langfuse.com"
)

class ProductionChatbot:
    """Production chatbot with observability"""

    @observe()
    def handle_message(self, user_id: str, message: str, conversation_id: str = None):
        """Process user message with full observability"""

        # Create or update conversation trace
        if not conversation_id:
            conversation_id = f"conv_{user_id}_{int(time.time())}"

        langfuse_context.update_current_trace(
            user_id=user_id,
            session_id=conversation_id,
            metadata={
                "channel": "web",
                "user_tier": self.get_user_tier(user_id)
            }
        )

        # Parse intent
        intent_result = self.parse_intent(message)

        # Generate response
        response = self.generate_response(intent_result, message)

        # Log metrics
        langfuse_context.update_current_observation(
            metadata={
                "intent": intent_result['intent'],
                "confidence": intent_result['confidence'],
                "entities": intent_result['entities']
            }
        )

        return response

    @observe(as_type="generation")
    def generate_response(self, intent_result, user_message):
        """Generate response with LLM tracking"""

        prompt = self.build_prompt(intent_result, user_message)

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        # Langfuse automatically captures:
        # - Model name, parameters
        # - Input/output tokens
        # - Latency
        # - Cost

        return response.choices[0].message.content

    @observe()
    def parse_intent(self, message):
        """Parse user intent with tracking"""

        result = self.nlu_model.parse(message)

        # Log to Langfuse
        langfuse_context.update_current_observation(
            name="intent_recognition",
            metadata={
                "model": "rasa_nlu_v3.2",
                "intent": result['intent']['name'],
                "confidence": result['intent']['confidence']
            }
        )

        return result
```

**Structured Logging:**

```python
# logging_config.py
import logging
import json
from datetime import datetime

class ConversationLogger:
    """Structured logging for conversations"""

    def __init__(self, service_name='chatbot'):
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.INFO)

        # JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(self.JSONFormatter())
        self.logger.addHandler(handler)

    class JSONFormatter(logging.Formatter):
        """Format logs as JSON for easy parsing"""

        def format(self, record):
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'service': 'chatbot',
                'message': record.getMessage(),
            }

            # Add extra fields if present
            if hasattr(record, 'conversation_id'):
                log_data['conversation_id'] = record.conversation_id
            if hasattr(record, 'user_id'):
                log_data['user_id'] = record.user_id
            if hasattr(record, 'intent'):
                log_data['intent'] = record.intent
            if hasattr(record, 'confidence'):
                log_data['confidence'] = record.confidence
            if hasattr(record, 'duration_ms'):
                log_data['duration_ms'] = record.duration_ms

            return json.dumps(log_data)

    def log_conversation_turn(self, conversation_id, user_id, user_message, bot_response, metadata):
        """Log a conversation turn"""
        self.logger.info(
            'conversation_turn',
            extra={
                'conversation_id': conversation_id,
                'user_id': user_id,
                'user_message': user_message,
                'bot_response': bot_response,
                'intent': metadata.get('intent'),
                'confidence': metadata.get('confidence'),
                'entities': metadata.get('entities'),
                'duration_ms': metadata.get('duration_ms')
            }
        )

    def log_error(self, conversation_id, user_id, error_type, error_message):
        """Log conversation error"""
        self.logger.error(
            'conversation_error',
            extra={
                'conversation_id': conversation_id,
                'user_id': user_id,
                'error_type': error_type,
                'error_message': error_message
            }
        )

# Usage
logger = ConversationLogger()
logger.log_conversation_turn(
    conversation_id='conv_12345',
    user_id='user_789',
    user_message='Book a flight',
    bot_response='Where would you like to go?',
    metadata={
        'intent': 'book_flight',
        'confidence': 0.95,
        'entities': {},
        'duration_ms': 234
    }
)
```

### Real-time Quality Scoring

**LLM-as-a-Judge for Real-time Scoring:**

```python
# quality_scoring.py
from openai import OpenAI
import json

class RealTimeQualityScorer:
    """Score chatbot responses in real-time"""

    def __init__(self, openai_api_key):
        self.client = OpenAI(api_key=openai_api_key)
        self.metrics = ['relevancy', 'coherence', 'helpfulness', 'safety']

    def score_response(self, user_message, bot_response, context=None):
        """Score a chatbot response across multiple dimensions"""

        prompt = self._build_scoring_prompt(user_message, bot_response, context)

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert evaluator of chatbot responses."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )

        scores = json.loads(response.choices[0].message.content)

        # Calculate overall score
        scores['overall'] = sum(scores[m] for m in self.metrics) / len(self.metrics)

        return scores

    def _build_scoring_prompt(self, user_message, bot_response, context):
        """Build prompt for LLM-as-a-judge"""

        prompt = f"""Evaluate the following chatbot response:

User Message: {user_message}
Bot Response: {bot_response}
"""

        if context:
            prompt += f"\nContext: {context}\n"

        prompt += """
Rate the response on a scale of 0-10 for each dimension:

1. Relevancy: How relevant is the response to the user's message?
2. Coherence: How coherent and well-structured is the response?
3. Helpfulness: How helpful is the response in addressing the user's need?
4. Safety: Is the response safe, appropriate, and free from harmful content?

Return your evaluation as JSON:
{
  "relevancy": <score>,
  "coherence": <score>,
  "helpfulness": <score>,
  "safety": <score>,
  "reasoning": "<brief explanation>"
}
"""

        return prompt

    def detect_quality_issues(self, scores, thresholds=None):
        """Detect if response has quality issues"""

        if thresholds is None:
            thresholds = {
                'relevancy': 7.0,
                'coherence': 7.0,
                'helpfulness': 6.0,
                'safety': 9.0,
                'overall': 7.0
            }

        issues = []
        for metric, threshold in thresholds.items():
            if scores.get(metric, 10) < threshold:
                issues.append({
                    'metric': metric,
                    'score': scores[metric],
                    'threshold': threshold,
                    'severity': 'high' if scores[metric] < threshold - 2 else 'medium'
                })

        return issues

# Usage in production
scorer = RealTimeQualityScorer(openai_api_key=os.environ['OPENAI_API_KEY'])

user_msg = "How do I reset my password?"
bot_response = chatbot.get_response(user_msg)

# Score in background (async)
scores = scorer.score_response(user_msg, bot_response)

# Alert on quality issues
issues = scorer.detect_quality_issues(scores)
if issues:
    alert_monitoring_system(issues)
```

**DeepEval Integration:**

```python
# deepeval_monitoring.py
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, HallucinationMetric
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset
import asyncio

class ProductionEvaluator:
    """Continuous evaluation in production"""

    def __init__(self):
        self.relevancy_metric = AnswerRelevancyMetric(threshold=0.7)
        self.faithfulness_metric = FaithfulnessMetric(threshold=0.8)
        self.hallucination_metric = HallucinationMetric(threshold=0.3)

    async def evaluate_response(self, user_input, response, context=None):
        """Evaluate a single response asynchronously"""

        test_case = LLMTestCase(
            input=user_input,
            actual_output=response,
            retrieval_context=[context] if context else None
        )

        # Run metrics in parallel
        tasks = [
            self.relevancy_metric.a_measure(test_case),
            self.faithfulness_metric.a_measure(test_case) if context else None,
            self.hallucination_metric.a_measure(test_case) if context else None
        ]

        await asyncio.gather(*[t for t in tasks if t is not None])

        results = {
            'relevancy_score': self.relevancy_metric.score,
            'relevancy_passed': self.relevancy_metric.score >= 0.7
        }

        if context:
            results.update({
                'faithfulness_score': self.faithfulness_metric.score,
                'faithfulness_passed': self.faithfulness_metric.score >= 0.8,
                'hallucination_score': self.hallucination_metric.score,
                'hallucination_passed': self.hallucination_metric.score <= 0.3
            })

        return results

    def batch_evaluate(self, conversations):
        """Batch evaluate multiple conversations"""

        test_cases = [
            LLMTestCase(
                input=conv['user_message'],
                actual_output=conv['bot_response'],
                retrieval_context=conv.get('context')
            )
            for conv in conversations
        ]

        dataset = EvaluationDataset(test_cases=test_cases)

        # Evaluate dataset
        results = dataset.evaluate([
            self.relevancy_metric,
            self.faithfulness_metric,
            self.hallucination_metric
        ])

        return results

# Usage in production monitoring
evaluator = ProductionEvaluator()

# Evaluate sample of production traffic (e.g., 1% of conversations)
async def monitor_conversation(user_msg, bot_response, context=None):
    if random.random() < 0.01:  # Sample 1%
        results = await evaluator.evaluate_response(user_msg, bot_response, context)

        # Log to monitoring system
        metrics_client.gauge('chatbot.quality.relevancy', results['relevancy_score'])

        # Alert on failures
        if not results['relevancy_passed']:
            alert_system.send_alert('Low relevancy score detected')
```

### Anomaly Detection

**Drift Detection:**

```python
# drift_detection.py
import numpy as np
from scipy.stats import ks_2samp
from sklearn.metrics.pairwise import cosine_similarity

class DriftDetector:
    """Detect data and concept drift in production"""

    def __init__(self, baseline_embeddings, baseline_intents):
        self.baseline_embeddings = np.array(baseline_embeddings)
        self.baseline_intents = baseline_intents
        self.baseline_intent_dist = self._calculate_intent_distribution(baseline_intents)

    def detect_embedding_drift(self, current_embeddings, threshold=0.05):
        """Detect drift in input embeddings using KS test"""

        current_embeddings = np.array(current_embeddings)

        # KS test for each dimension
        p_values = []
        for dim in range(self.baseline_embeddings.shape[1]):
            statistic, p_value = ks_2samp(
                self.baseline_embeddings[:, dim],
                current_embeddings[:, dim]
            )
            p_values.append(p_value)

        # Drift detected if significant number of dimensions show drift
        drift_ratio = np.mean(np.array(p_values) < threshold)

        return {
            'drift_detected': drift_ratio > 0.2,  # >20% of dimensions
            'drift_ratio': drift_ratio,
            'p_values': p_values
        }

    def detect_intent_drift(self, current_intents, threshold=0.1):
        """Detect drift in intent distribution"""

        current_dist = self._calculate_intent_distribution(current_intents)

        # Calculate distribution shift
        drift_scores = {}
        for intent in set(list(self.baseline_intent_dist.keys()) + list(current_dist.keys())):
            baseline_freq = self.baseline_intent_dist.get(intent, 0)
            current_freq = current_dist.get(intent, 0)
            drift_scores[intent] = abs(current_freq - baseline_freq)

        max_drift = max(drift_scores.values()) if drift_scores else 0

        return {
            'drift_detected': max_drift > threshold,
            'max_drift': max_drift,
            'drift_scores': drift_scores
        }

    def detect_semantic_drift(self, current_embeddings):
        """Detect semantic drift using cosine similarity"""

        # Calculate centroid of baseline and current embeddings
        baseline_centroid = np.mean(self.baseline_embeddings, axis=0).reshape(1, -1)
        current_centroid = np.mean(current_embeddings, axis=0).reshape(1, -1)

        # Cosine similarity between centroids
        similarity = cosine_similarity(baseline_centroid, current_centroid)[0][0]

        return {
            'drift_detected': similarity < 0.9,  # <90% similarity
            'similarity': similarity,
            'drift_magnitude': 1 - similarity
        }

    def _calculate_intent_distribution(self, intents):
        """Calculate intent frequency distribution"""
        total = len(intents)
        dist = {}
        for intent in set(intents):
            dist[intent] = intents.count(intent) / total
        return dist

# Usage in production monitoring
detector = DriftDetector(
    baseline_embeddings=load_baseline_embeddings(),
    baseline_intents=load_baseline_intents()
)

# Periodic drift check (e.g., every hour)
def check_for_drift():
    # Get last hour's production data
    recent_data = fetch_recent_conversations(hours=1)

    embeddings = [msg['embedding'] for msg in recent_data]
    intents = [msg['predicted_intent'] for msg in recent_data]

    # Check for drift
    embedding_drift = detector.detect_embedding_drift(embeddings)
    intent_drift = detector.detect_intent_drift(intents)
    semantic_drift = detector.detect_semantic_drift(embeddings)

    if any([embedding_drift['drift_detected'],
            intent_drift['drift_detected'],
            semantic_drift['drift_detected']]):

        alert_system.send_alert({
            'type': 'drift_detected',
            'embedding_drift': embedding_drift,
            'intent_drift': intent_drift,
            'semantic_drift': semantic_drift,
            'timestamp': datetime.now().isoformat()
        })
```

**Anomaly Detection with Statistical Methods:**

```python
# anomaly_detection.py
from sklearn.ensemble import IsolationForest
import pandas as pd

class ConversationAnomalyDetector:
    """Detect anomalous conversations"""

    def __init__(self, contamination=0.05):
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.fitted = False

    def fit(self, historical_conversations):
        """Train on historical conversation metrics"""

        features = self._extract_features(historical_conversations)
        self.model.fit(features)
        self.fitted = True

    def detect_anomalies(self, conversations):
        """Detect anomalous conversations"""

        if not self.fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        features = self._extract_features(conversations)
        predictions = self.model.predict(features)
        scores = self.model.score_samples(features)

        # -1 = anomaly, 1 = normal
        anomalies = []
        for i, (conv, pred, score) in enumerate(zip(conversations, predictions, scores)):
            if pred == -1:
                anomalies.append({
                    'conversation_id': conv['id'],
                    'anomaly_score': -score,  # Higher = more anomalous
                    'features': features.iloc[i].to_dict(),
                    'conversation': conv
                })

        return anomalies

    def _extract_features(self, conversations):
        """Extract numerical features from conversations"""

        features = []
        for conv in conversations:
            features.append({
                'num_turns': len(conv['turns']),
                'avg_confidence': np.mean([t['confidence'] for t in conv['turns']]),
                'min_confidence': min([t['confidence'] for t in conv['turns']]),
                'num_fallbacks': sum(1 for t in conv['turns'] if t['intent'] == 'fallback'),
                'avg_response_time': np.mean([t['response_time_ms'] for t in conv['turns']]),
                'max_response_time': max([t['response_time_ms'] for t in conv['turns']]),
                'unique_intents': len(set(t['intent'] for t in conv['turns'])),
                'intent_switches': sum(1 for i in range(1, len(conv['turns']))
                                     if conv['turns'][i]['intent'] != conv['turns'][i-1]['intent']),
                'conversation_duration': conv['turns'][-1]['timestamp'] - conv['turns'][0]['timestamp']
            })

        return pd.DataFrame(features)

# Usage
detector = ConversationAnomalyDetector(contamination=0.05)

# Train on historical data
historical_convs = load_historical_conversations(days=30)
detector.fit(historical_convs)

# Detect anomalies in recent conversations
recent_convs = fetch_recent_conversations(hours=1)
anomalies = detector.detect_anomalies(recent_convs)

for anomaly in anomalies:
    print(f"Anomalous conversation detected: {anomaly['conversation_id']}")
    print(f"Anomaly score: {anomaly['anomaly_score']:.3f}")

    # Send to manual review queue
    review_queue.add(anomaly)
```

### A/B Testing Infrastructure

**Feature Flag System:**

```python
# ab_testing.py
import hashlib
import random

class ABTestingFramework:
    """A/B testing for chatbot models and prompts"""

    def __init__(self):
        self.experiments = {}

    def create_experiment(self, experiment_id, variants, traffic_split=None):
        """
        Create a new A/B test

        Args:
            experiment_id: Unique identifier
            variants: Dict of variant_name -> config
            traffic_split: Dict of variant_name -> percentage (defaults to equal split)
        """

        if traffic_split is None:
            n_variants = len(variants)
            traffic_split = {name: 1.0/n_variants for name in variants.keys()}

        # Validate traffic split sums to 1.0
        assert abs(sum(traffic_split.values()) - 1.0) < 0.01, "Traffic split must sum to 1.0"

        self.experiments[experiment_id] = {
            'variants': variants,
            'traffic_split': traffic_split,
            'cumulative_split': self._calculate_cumulative_split(traffic_split)
        }

    def get_variant(self, experiment_id, user_id):
        """Get variant assignment for a user"""

        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Deterministic assignment based on user_id
        hash_value = int(hashlib.md5(f"{experiment_id}:{user_id}".encode()).hexdigest(), 16)
        percentage = (hash_value % 10000) / 10000.0  # 0.0 to 1.0

        # Find variant based on cumulative split
        cumulative = self.experiments[experiment_id]['cumulative_split']
        for variant_name, threshold in cumulative.items():
            if percentage < threshold:
                return variant_name, self.experiments[experiment_id]['variants'][variant_name]

        # Fallback (shouldn't happen)
        return list(self.experiments[experiment_id]['variants'].keys())[0], \
               list(self.experiments[experiment_id]['variants'].values())[0]

    def _calculate_cumulative_split(self, traffic_split):
        """Calculate cumulative traffic split for assignment"""
        cumulative = {}
        total = 0
        for variant_name in sorted(traffic_split.keys()):
            total += traffic_split[variant_name]
            cumulative[variant_name] = total
        return cumulative

# Example usage
ab_testing = ABTestingFramework()

# Create experiment: Test GPT-4 vs GPT-3.5
ab_testing.create_experiment(
    experiment_id='model_comparison_v1',
    variants={
        'gpt4': {'model': 'gpt-4', 'temperature': 0.7},
        'gpt35': {'model': 'gpt-3.5-turbo', 'temperature': 0.7}
    },
    traffic_split={'gpt4': 0.2, 'gpt35': 0.8}  # 20% GPT-4, 80% GPT-3.5
)

# Get variant for user
def get_chatbot_response(user_id, message):
    variant_name, config = ab_testing.get_variant('model_comparison_v1', user_id)

    # Use assigned model
    response = openai.ChatCompletion.create(
        model=config['model'],
        messages=[{"role": "user", "content": message}],
        temperature=config['temperature']
    )

    # Log experiment data
    log_experiment_result(
        experiment_id='model_comparison_v1',
        user_id=user_id,
        variant=variant_name,
        response=response.choices[0].message.content
    )

    return response.choices[0].message.content
```

**Statistical Analysis:**

```python
# ab_analysis.py
from scipy import stats
import pandas as pd

class ABTestAnalyzer:
    """Analyze A/B test results"""

    def __init__(self, significance_level=0.05):
        self.significance_level = significance_level

    def analyze_binary_metric(self, variant_a_data, variant_b_data):
        """
        Analyze binary metrics (e.g., user satisfaction, task completion)

        Returns: {
            'variant_a_rate': float,
            'variant_b_rate': float,
            'difference': float,
            'p_value': float,
            'significant': bool,
            'winner': str or None
        }
        """

        # Calculate conversion rates
        a_successes = sum(variant_a_data)
        a_total = len(variant_a_data)
        a_rate = a_successes / a_total if a_total > 0 else 0

        b_successes = sum(variant_b_data)
        b_total = len(variant_b_data)
        b_rate = b_successes / b_total if b_total > 0 else 0

        # Chi-square test
        contingency_table = [
            [a_successes, a_total - a_successes],
            [b_successes, b_total - b_successes]
        ]
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

        significant = p_value < self.significance_level
        difference = b_rate - a_rate

        winner = None
        if significant:
            winner = 'B' if difference > 0 else 'A'

        return {
            'variant_a_rate': a_rate,
            'variant_b_rate': b_rate,
            'difference': difference,
            'relative_improvement': (difference / a_rate * 100) if a_rate > 0 else 0,
            'p_value': p_value,
            'significant': significant,
            'winner': winner
        }

    def analyze_continuous_metric(self, variant_a_data, variant_b_data):
        """
        Analyze continuous metrics (e.g., response time, satisfaction score)

        Returns similar dict as binary metric
        """

        # Calculate means
        a_mean = np.mean(variant_a_data)
        b_mean = np.mean(variant_b_data)

        # T-test
        t_stat, p_value = stats.ttest_ind(variant_a_data, variant_b_data)

        significant = p_value < self.significance_level
        difference = b_mean - a_mean

        winner = None
        if significant:
            winner = 'B' if difference > 0 else 'A'

        return {
            'variant_a_mean': a_mean,
            'variant_b_mean': b_mean,
            'difference': difference,
            'relative_improvement': (difference / a_mean * 100) if a_mean != 0 else 0,
            'p_value': p_value,
            'significant': significant,
            'winner': winner
        }

    def calculate_sample_size(self, baseline_rate, mde, power=0.8):
        """
        Calculate required sample size per variant

        Args:
            baseline_rate: Current conversion rate (e.g., 0.5 for 50%)
            mde: Minimum detectable effect (e.g., 0.05 for 5% improvement)
            power: Statistical power (default 0.8)
        """

        # Using simplified formula
        z_alpha = stats.norm.ppf(1 - self.significance_level/2)
        z_beta = stats.norm.ppf(power)

        p1 = baseline_rate
        p2 = baseline_rate + mde
        p_avg = (p1 + p2) / 2

        n = ((z_alpha + z_beta)**2 * 2 * p_avg * (1 - p_avg)) / (p2 - p1)**2

        return int(np.ceil(n))

# Usage
analyzer = ABTestAnalyzer(significance_level=0.05)

# Fetch results from experiment
results = fetch_experiment_results('model_comparison_v1')

# Analyze user satisfaction (binary metric)
satisfaction_analysis = analyzer.analyze_binary_metric(
    variant_a_data=results['gpt35']['satisfied'],
    variant_b_data=results['gpt4']['satisfied']
)

print(f"GPT-3.5 satisfaction: {satisfaction_analysis['variant_a_rate']:.2%}")
print(f"GPT-4 satisfaction: {satisfaction_analysis['variant_b_rate']:.2%}")
print(f"Improvement: {satisfaction_analysis['relative_improvement']:.1f}%")
print(f"Statistically significant: {satisfaction_analysis['significant']}")
if satisfaction_analysis['winner']:
    print(f"Winner: Variant {satisfaction_analysis['winner']}")

# Analyze response time (continuous metric)
response_time_analysis = analyzer.analyze_continuous_metric(
    variant_a_data=results['gpt35']['response_times'],
    variant_b_data=results['gpt4']['response_times']
)

# Calculate required sample size for future tests
required_sample = analyzer.calculate_sample_size(
    baseline_rate=0.75,  # 75% current satisfaction
    mde=0.05,  # Detect 5% improvement
    power=0.8
)
print(f"Required sample size per variant: {required_sample}")
```

### Canary Deployments for Bots

**Kubernetes Canary Deployment:**

```yaml
# canary-deployment.yaml
apiVersion: v1
kind: Service
metadata:
  name: chatbot-service
spec:
  selector:
    app: chatbot
  ports:
    - port: 8080
      targetPort: 8080
---
# Stable deployment (90% traffic)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chatbot-stable
spec:
  replicas: 9
  selector:
    matchLabels:
      app: chatbot
      version: stable
  template:
    metadata:
      labels:
        app: chatbot
        version: stable
    spec:
      containers:
      - name: chatbot
        image: chatbot:v1.2.0
        ports:
        - containerPort: 8080
        env:
        - name: MODEL_VERSION
          value: "v1.2.0"
        - name: DEPLOYMENT_TYPE
          value: "stable"
---
# Canary deployment (10% traffic)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chatbot-canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: chatbot
      version: canary
  template:
    metadata:
      labels:
        app: chatbot
        version: canary
    spec:
      containers:
      - name: chatbot
        image: chatbot:v1.3.0-rc1
        ports:
        - containerPort: 8080
        env:
        - name: MODEL_VERSION
          value: "v1.3.0-rc1"
        - name: DEPLOYMENT_TYPE
          value: "canary"
```

**Argo Rollouts Progressive Delivery:**

```yaml
# argo-rollout.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: chatbot-rollout
spec:
  replicas: 10
  strategy:
    canary:
      steps:
      - setWeight: 10   # 10% canary traffic
      - pause: {duration: 10m}  # Observe for 10 minutes
      - analysis:
          templates:
          - templateName: chatbot-success-rate
          - templateName: chatbot-latency
      - setWeight: 20
      - pause: {duration: 10m}
      - analysis:
          templates:
          - templateName: chatbot-success-rate
      - setWeight: 50
      - pause: {duration: 10m}
      - setWeight: 80
      - pause: {duration: 5m}

  revisionHistoryLimit: 3
  selector:
    matchLabels:
      app: chatbot

  template:
    metadata:
      labels:
        app: chatbot
    spec:
      containers:
      - name: chatbot
        image: chatbot:v1.3.0
        ports:
        - containerPort: 8080
---
# Analysis template for success rate
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: chatbot-success-rate
spec:
  metrics:
  - name: success-rate
    interval: 60s
    failureLimit: 3
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          sum(rate(chatbot_requests_total{status="success"}[5m])) /
          sum(rate(chatbot_requests_total[5m]))
    successCondition: result >= 0.95  # 95% success rate required
---
# Analysis template for latency
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: chatbot-latency
spec:
  metrics:
  - name: p95-latency
    interval: 60s
    failureLimit: 3
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          histogram_quantile(0.95,
            sum(rate(chatbot_response_duration_bucket[5m])) by (le)
          )
    successCondition: result <= 500  # p95 < 500ms
```

**Automated Rollback Logic:**

```python
# canary_monitor.py
import requests
import time
from datetime import datetime, timedelta

class CanaryMonitor:
    """Monitor canary deployment and trigger rollback if needed"""

    def __init__(self, prometheus_url, thresholds):
        self.prometheus_url = prometheus_url
        self.thresholds = thresholds

    def query_prometheus(self, query):
        """Query Prometheus for metrics"""
        response = requests.get(
            f"{self.prometheus_url}/api/v1/query",
            params={'query': query}
        )
        return response.json()['data']['result']

    def check_canary_health(self, deployment_name):
        """Check if canary deployment is healthy"""

        issues = []

        # Check error rate
        error_rate_query = f'''
        sum(rate(chatbot_requests_total{{deployment="{deployment_name}-canary",status="error"}}[5m])) /
        sum(rate(chatbot_requests_total{{deployment="{deployment_name}-canary"}}[5m]))
        '''

        error_rate_result = self.query_prometheus(error_rate_query)
        if error_rate_result:
            error_rate = float(error_rate_result[0]['value'][1])
            if error_rate > self.thresholds['max_error_rate']:
                issues.append(f"Error rate {error_rate:.2%} exceeds threshold {self.thresholds['max_error_rate']:.2%}")

        # Check latency
        latency_query = f'''
        histogram_quantile(0.95,
          sum(rate(chatbot_response_duration_bucket{{deployment="{deployment_name}-canary"}}[5m])) by (le)
        )
        '''

        latency_result = self.query_prometheus(latency_query)
        if latency_result:
            p95_latency = float(latency_result[0]['value'][1])
            if p95_latency > self.thresholds['max_p95_latency_ms']:
                issues.append(f"P95 latency {p95_latency:.0f}ms exceeds threshold {self.thresholds['max_p95_latency_ms']}ms")

        # Check intent accuracy (custom metric)
        accuracy_query = f'''
        sum(rate(chatbot_intent_correct{{deployment="{deployment_name}-canary"}}[5m])) /
        sum(rate(chatbot_intent_predictions{{deployment="{deployment_name}-canary"}}[5m]))
        '''

        accuracy_result = self.query_prometheus(accuracy_query)
        if accuracy_result:
            accuracy = float(accuracy_result[0]['value'][1])
            if accuracy < self.thresholds['min_intent_accuracy']:
                issues.append(f"Intent accuracy {accuracy:.2%} below threshold {self.thresholds['min_intent_accuracy']:.2%}")

        return {
            'healthy': len(issues) == 0,
            'issues': issues,
            'timestamp': datetime.now().isoformat()
        }

    def trigger_rollback(self, deployment_name, reason):
        """Trigger rollback of canary deployment"""

        print(f"🚨 TRIGGERING ROLLBACK: {reason}")

        # Scale down canary to 0
        os.system(f"kubectl scale deployment/{deployment_name}-canary --replicas=0")

        # Send alert
        requests.post(
            os.environ['SLACK_WEBHOOK_URL'],
            json={
                'text': f'🚨 Canary Rollback Triggered',
                'blocks': [
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': f'*Deployment:* {deployment_name}\n*Reason:* {reason}'
                        }
                    }
                ]
            }
        )

    def monitor_canary(self, deployment_name, duration_minutes=30, check_interval_seconds=60):
        """Monitor canary for specified duration"""

        print(f"Starting canary monitoring for {deployment_name}")
        print(f"Duration: {duration_minutes} minutes")

        end_time = datetime.now() + timedelta(minutes=duration_minutes)

        while datetime.now() < end_time:
            health_check = self.check_canary_health(deployment_name)

            if not health_check['healthy']:
                self.trigger_rollback(deployment_name, "; ".join(health_check['issues']))
                return False

            print(f"✅ Canary healthy at {health_check['timestamp']}")
            time.sleep(check_interval_seconds)

        print(f"✅ Canary monitoring complete. Deployment healthy.")
        return True

# Usage
monitor = CanaryMonitor(
    prometheus_url='http://prometheus:9090',
    thresholds={
        'max_error_rate': 0.05,  # 5%
        'max_p95_latency_ms': 500,
        'min_intent_accuracy': 0.92
    }
)

# Monitor canary deployment
success = monitor.monitor_canary(
    deployment_name='chatbot',
    duration_minutes=30,
    check_interval_seconds=60
)

if success:
    # Promote canary to stable
    os.system("kubectl set image deployment/chatbot-stable chatbot=chatbot:v1.3.0")
```

---

## 5. MLOps for Conversational AI

### Model Versioning for NLU

**DVC (Data Version Control):**

```bash
# Initialize DVC
dvc init

# Track model artifacts
dvc add models/nlu_model.tar.gz
dvc add models/intent_classifier.pkl
dvc add models/entity_extractor.pkl

# Add to git
git add models/.gitignore models/nlu_model.tar.gz.dvc
git commit -m "Add NLU model v1.2.0"

# Push to remote storage (S3, GCS, Azure)
dvc remote add -d storage s3://my-bucket/dvc-storage
dvc push
```

**DVC Pipeline:**

```yaml
# dvc.yaml
stages:
  prepare_data:
    cmd: python scripts/prepare_data.py
    deps:
      - data/raw/conversations.json
      - scripts/prepare_data.py
    outs:
      - data/prepared/training_data.yml
      - data/prepared/test_data.yml

  train_nlu:
    cmd: rasa train nlu --data data/prepared/training_data.yml --config config.yml --out models/
    deps:
      - data/prepared/training_data.yml
      - config.yml
      - scripts/train.py
    params:
      - config.yml:
          - pipeline
    outs:
      - models/nlu_model.tar.gz
    metrics:
      - metrics/nlu_metrics.json:
          cache: false

  evaluate:
    cmd: python scripts/evaluate.py
    deps:
      - models/nlu_model.tar.gz
      - data/prepared/test_data.yml
    metrics:
      - metrics/evaluation.json:
          cache: false
    plots:
      - plots/confusion_matrix.png
      - plots/intent_report.json:
          template: confusion
          x: actual
          y: predicted
```

**MLflow Model Registry:**

```python
# train_with_mlflow.py
import mlflow
import mlflow.sklearn
from rasa.train import train_nlu

# Start MLflow run
with mlflow.start_run(run_name="nlu_training_v1.3.0"):

    # Log parameters
    mlflow.log_param("pipeline", "pretrained_embeddings_spacy")
    mlflow.log_param("epochs", 100)
    mlflow.log_param("dropout", 0.2)

    # Train model
    model_path = train_nlu(
        config="config.yml",
        nlu_data="data/nlu.yml",
        output="models/"
    )

    # Evaluate
    results = evaluate_model(model_path, "data/test/")

    # Log metrics
    mlflow.log_metric("intent_accuracy", results['intent_evaluation']['accuracy'])
    mlflow.log_metric("intent_f1", results['intent_evaluation']['f1_score'])
    mlflow.log_metric("entity_f1", results['entity_evaluation']['f1_score'])

    # Log model
    mlflow.log_artifact(model_path, "model")

    # Log plots
    mlflow.log_artifact("plots/confusion_matrix.png")

    # Register model
    mlflow.register_model(
        model_uri=f"runs:/{mlflow.active_run().info.run_id}/model",
        name="nlu_intent_classifier"
    )
```

**Model Registry Management:**

```python
# model_registry.py
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Get latest model version
latest_versions = client.get_latest_versions("nlu_intent_classifier", stages=["Production"])
if latest_versions:
    production_model = latest_versions[0]
    print(f"Production model version: {production_model.version}")

# Transition new model to staging
client.transition_model_version_stage(
    name="nlu_intent_classifier",
    version=5,
    stage="Staging"
)

# After validation, promote to production
client.transition_model_version_stage(
    name="nlu_intent_classifier",
    version=5,
    stage="Production"
)

# Archive old production model
client.transition_model_version_stage(
    name="nlu_intent_classifier",
    version=4,
    stage="Archived"
)

# Add model description
client.update_model_version(
    name="nlu_intent_classifier",
    version=5,
    description="Improved entity extraction with 5% accuracy gain. Trained on 10K new examples."
)
```

### Training Data Versioning

**DVC for Dataset Versioning:**

```bash
# Track training data
dvc add data/training/nlu_data.yml
dvc add data/training/stories.yml
dvc add data/training/rules.yml

git add data/training/.gitignore data/training/*.dvc
git commit -m "Update training data v2.1 - added 500 new intents"
git tag -a data-v2.1 -m "Training data version 2.1"

dvc push

# Checkout specific version
git checkout data-v2.0
dvc checkout
```

**Training Data Manifest:**

```yaml
# data_manifest.yml
version: "2.1.0"
created_at: "2025-01-15T10:30:00Z"
created_by: "data-team@company.com"
description: "Added support for cancellation and rescheduling intents"

datasets:
  nlu_training:
    path: data/training/nlu_data.yml
    hash: md5:a1b2c3d4e5f6g7h8
    size: 524288
    examples: 5432
    intents:
      - book_flight: 523
      - cancel_booking: 412
      - reschedule: 398
      - check_status: 287
      # ... more intents

  stories:
    path: data/training/stories.yml
    hash: md5:h8g7f6e5d4c3b2a1
    size: 102400
    stories: 156

  test_set:
    path: data/test/test_data.yml
    hash: md5:9i8j7k6l5m4n3o2p
    size: 131072
    examples: 1086

metadata:
  annotation_tool: "labelbox"
  annotation_guidelines: "docs/annotation_guidelines.md"
  quality_score: 0.94
  inter_annotator_agreement: 0.89

changes_from_previous:
  - "Added 500 examples for cancel_booking intent"
  - "Added 450 examples for reschedule intent"
  - "Fixed labeling errors in 23 examples"
  - "Removed 15 duplicate examples"
```

**Data Quality Validation:**

```python
# validate_training_data.py
import yaml
from collections import Counter
import hashlib

class TrainingDataValidator:
    """Validate training data quality"""

    def __init__(self, min_examples_per_intent=50):
        self.min_examples_per_intent = min_examples_per_intent
        self.issues = []

    def validate(self, nlu_data_path):
        """Run all validation checks"""

        with open(nlu_data_path) as f:
            data = yaml.safe_load(f)

        self._check_intent_balance(data)
        self._check_duplicates(data)
        self._check_entity_coverage(data)
        self._check_example_quality(data)

        return {
            'valid': len(self.issues) == 0,
            'issues': self.issues
        }

    def _check_intent_balance(self, data):
        """Check if intents have sufficient examples"""

        intent_counts = Counter()
        for intent in data['nlu']:
            intent_name = intent['intent']
            intent_counts[intent_name] += len(intent['examples'])

        for intent, count in intent_counts.items():
            if count < self.min_examples_per_intent:
                self.issues.append({
                    'type': 'insufficient_examples',
                    'severity': 'warning',
                    'intent': intent,
                    'count': count,
                    'message': f"Intent '{intent}' has only {count} examples (min: {self.min_examples_per_intent})"
                })

    def _check_duplicates(self, data):
        """Check for duplicate examples"""

        seen = set()
        for intent in data['nlu']:
            for example in intent['examples'].split('\n'):
                example = example.strip('- ').strip()
                if example in seen:
                    self.issues.append({
                        'type': 'duplicate',
                        'severity': 'error',
                        'example': example,
                        'message': f"Duplicate example: '{example}'"
                    })
                seen.add(example)

    def _check_entity_coverage(self, data):
        """Ensure entities are well-covered"""

        entity_counts = Counter()
        for intent in data['nlu']:
            examples_text = intent['examples']
            # Count entity annotations
            entities = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', examples_text)
            for _, entity_type in entities:
                entity_counts[entity_type] += 1

        for entity, count in entity_counts.items():
            if count < 20:  # Minimum 20 examples per entity
                self.issues.append({
                    'type': 'insufficient_entity_examples',
                    'severity': 'warning',
                    'entity': entity,
                    'count': count,
                    'message': f"Entity '{entity}' has only {count} examples (min: 20)"
                })

    def _check_example_quality(self, data):
        """Check example quality metrics"""

        for intent in data['nlu']:
            examples = [e.strip('- ').strip() for e in intent['examples'].split('\n') if e.strip()]

            # Check for very short examples
            short_examples = [e for e in examples if len(e.split()) < 3]
            if len(short_examples) > 0:
                self.issues.append({
                    'type': 'short_examples',
                    'severity': 'info',
                    'intent': intent['intent'],
                    'count': len(short_examples),
                    'message': f"Intent '{intent['intent']}' has {len(short_examples)} very short examples"
                })

# Usage in CI/CD
validator = TrainingDataValidator(min_examples_per_intent=50)
result = validator.validate('data/nlu.yml')

if not result['valid']:
    print("❌ Data validation failed:")
    for issue in result['issues']:
        print(f"  [{issue['severity']}] {issue['message']}")

    # Fail CI if critical issues
    critical_issues = [i for i in result['issues'] if i['severity'] == 'error']
    if critical_issues:
        sys.exit(1)
```

### Experiment Tracking

**Weights & Biases Integration:**

```python
# train_with_wandb.py
import wandb
from rasa.train import train

# Initialize W&B
wandb.init(
    project="conversational-ai",
    name="nlu-training-run-42",
    config={
        "pipeline": "pretrained_embeddings_spacy",
        "language": "en",
        "epochs": 100,
        "batch_size": 32,
        "dropout": 0.2,
        "learning_rate": 0.001
    }
)

# Train model
model_path = train(
    domain="domain.yml",
    config="config.yml",
    training_files="data/",
    output="models/"
)

# Evaluate
test_results = evaluate_model(model_path)

# Log metrics
wandb.log({
    "intent_accuracy": test_results['intent_evaluation']['accuracy'],
    "intent_f1": test_results['intent_evaluation']['f1_score'],
    "intent_precision": test_results['intent_evaluation']['precision'],
    "intent_recall": test_results['intent_evaluation']['recall'],
    "entity_f1": test_results['entity_evaluation']['f1_score'],
    "entity_precision": test_results['entity_evaluation']['precision'],
    "entity_recall": test_results['entity_evaluation']['recall']
})

# Log confusion matrix
wandb.log({
    "confusion_matrix": wandb.plot.confusion_matrix(
        y_true=test_results['true_labels'],
        preds=test_results['predictions'],
        class_names=test_results['intent_names']
    )
})

# Log model artifact
wandb.save(model_path)

# Log training data metadata
wandb.log({
    "training_examples": count_training_examples(),
    "num_intents": count_intents(),
    "num_entities": count_entities()
})

wandb.finish()
```

**Neptune.ai Integration:**

```python
# train_with_neptune.py
import neptune
from neptune.integrations.sklearn import NeptuneCallback

# Create Neptune run
run = neptune.init_run(
    project="team/conversational-ai",
    api_token=os.environ["NEPTUNE_API_TOKEN"],
    tags=["nlu", "production", "v1.3.0"]
)

# Log hyperparameters
run["parameters"] = {
    "pipeline": "pretrained_embeddings_spacy",
    "epochs": 100,
    "dropout": 0.2,
    "learning_rate": 0.001
}

# Log dataset version
run["dataset/version"] = "v2.1.0"
run["dataset/hash"] = get_dataset_hash()

# Train with logging
for epoch in range(100):
    metrics = train_epoch(epoch)
    run["training/loss"].append(metrics['loss'])
    run["training/accuracy"].append(metrics['accuracy'])

# Log final metrics
run["metrics/intent_accuracy"] = final_intent_accuracy
run["metrics/entity_f1"] = final_entity_f1

# Upload model
run["model/checkpoints"].upload_files(model_path)

# Log confusion matrix as interactive plot
run["evaluation/confusion_matrix"].upload(
    neptune.types.File.as_html(fig)
)

# Compare with baseline
run["comparison/baseline_model"] = "nlu-v1.2.0"
run["comparison/accuracy_improvement"] = improvement_percentage

run.stop()
```

### Model Performance Comparison

**Automated Model Comparison:**

```python
# compare_models.py
import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd

class ModelComparator:
    """Compare multiple model versions"""

    def __init__(self, experiment_name):
        self.client = MlflowClient()
        self.experiment = mlflow.get_experiment_by_name(experiment_name)

    def compare_latest_runs(self, n=5):
        """Compare the latest N runs"""

        runs = self.client.search_runs(
            experiment_ids=[self.experiment.experiment_id],
            order_by=["start_time DESC"],
            max_results=n
        )

        comparison = []
        for run in runs:
            metrics = run.data.metrics
            params = run.data.params

            comparison.append({
                'run_id': run.info.run_id,
                'run_name': run.data.tags.get('mlflow.runName', 'N/A'),
                'start_time': run.info.start_time,
                'intent_accuracy': metrics.get('intent_accuracy', 0),
                'intent_f1': metrics.get('intent_f1', 0),
                'entity_f1': metrics.get('entity_f1', 0),
                'pipeline': params.get('pipeline', 'N/A'),
                'epochs': params.get('epochs', 'N/A')
            })

        df = pd.DataFrame(comparison)
        return df.sort_values('intent_accuracy', ascending=False)

    def compare_production_candidates(self):
        """Compare models tagged for production"""

        # Get current production model
        production_versions = self.client.get_latest_versions(
            "nlu_intent_classifier",
            stages=["Production"]
        )

        if not production_versions:
            return None

        prod_model = production_versions[0]
        prod_run = self.client.get_run(prod_model.run_id)

        # Get staging candidates
        staging_versions = self.client.get_latest_versions(
            "nlu_intent_classifier",
            stages=["Staging"]
        )

        comparison = {
            'production': {
                'version': prod_model.version,
                'run_id': prod_model.run_id,
                'metrics': prod_run.data.metrics
            },
            'staging_candidates': []
        }

        for staging_model in staging_versions:
            staging_run = self.client.get_run(staging_model.run_id)
            comparison['staging_candidates'].append({
                'version': staging_model.version,
                'run_id': staging_model.run_id,
                'metrics': staging_run.data.metrics,
                'improvement': {
                    metric: staging_run.data.metrics.get(metric, 0) - prod_run.data.metrics.get(metric, 0)
                    for metric in ['intent_accuracy', 'intent_f1', 'entity_f1']
                }
            })

        return comparison

    def generate_comparison_report(self, output_path='model_comparison.md'):
        """Generate markdown comparison report"""

        comparison = self.compare_production_candidates()

        report = ["# Model Comparison Report\n"]
        report.append(f"**Date**: {datetime.now().isoformat()}\n")

        # Production model
        report.append("## Current Production Model\n")
        report.append(f"- **Version**: {comparison['production']['version']}")
        report.append(f"- **Run ID**: {comparison['production']['run_id']}")
        report.append(f"- **Intent Accuracy**: {comparison['production']['metrics']['intent_accuracy']:.4f}")
        report.append(f"- **Entity F1**: {comparison['production']['metrics']['entity_f1']:.4f}\n")

        # Staging candidates
        report.append("## Staging Candidates\n")
        for candidate in comparison['staging_candidates']:
            report.append(f"### Version {candidate['version']}\n")
            report.append(f"- **Run ID**: {candidate['run_id']}")
            report.append("\n**Metrics**:")
            report.append(f"- Intent Accuracy: {candidate['metrics']['intent_accuracy']:.4f} ({candidate['improvement']['intent_accuracy']:+.4f})")
            report.append(f"- Entity F1: {candidate['metrics']['entity_f1']:.4f} ({candidate['improvement']['entity_f1']:+.4f})\n")

            # Recommendation
            if all(v > 0 for v in candidate['improvement'].values()):
                report.append("**Recommendation**: ✅ Promote to production")
            else:
                report.append("**Recommendation**: ⚠️ Needs improvement")
            report.append("\n")

        with open(output_path, 'w') as f:
            f.write('\n'.join(report))

        return output_path

# Usage
comparator = ModelComparator(experiment_name="nlu_training")

# Compare latest runs
latest_comparison = comparator.compare_latest_runs(n=10)
print(latest_comparison)

# Generate production comparison report
comparator.generate_comparison_report()
```

### Rollback Strategies

**Automated Rollback System:**

```python
# rollback_system.py
from mlflow.tracking import MlflowClient
import subprocess

class ModelRollbackSystem:
    """Automated model rollback"""

    def __init__(self, model_name):
        self.client = MlflowClient()
        self.model_name = model_name

    def get_production_history(self):
        """Get history of production models"""

        versions = self.client.search_model_versions(f"name='{self.model_name}'")

        production_history = [
            v for v in versions
            if any(stage == 'Production' for stage in v.current_stage.split(','))
        ]

        return sorted(production_history, key=lambda x: x.creation_timestamp, reverse=True)

    def rollback_to_version(self, version_number, reason):
        """Rollback to specific model version"""

        print(f"🔄 Rolling back {self.model_name} to version {version_number}")
        print(f"Reason: {reason}")

        # Get current production version
        current_versions = self.client.get_latest_versions(self.model_name, stages=["Production"])

        if current_versions:
            current_version = current_versions[0]

            # Archive current production
            self.client.transition_model_version_stage(
                name=self.model_name,
                version=current_version.version,
                stage="Archived",
                archive_existing_versions=False
            )

            print(f"Archived current version {current_version.version}")

        # Promote rollback version to production
        self.client.transition_model_version_stage(
            name=self.model_name,
            version=version_number,
            stage="Production"
        )

        # Update model description
        self.client.update_model_version(
            name=self.model_name,
            version=version_number,
            description=f"Rolled back from v{current_version.version}. Reason: {reason}"
        )

        # Trigger deployment
        self._deploy_model(version_number)

        # Send alert
        self._send_rollback_alert(current_version.version, version_number, reason)

        print(f"✅ Rollback complete. Now running version {version_number}")

    def rollback_to_previous(self, reason="Performance degradation"):
        """Rollback to previous production version"""

        history = self.get_production_history()

        if len(history) < 2:
            raise ValueError("No previous production version available")

        current_version = history[0].version
        previous_version = history[1].version

        self.rollback_to_version(previous_version, reason)

    def _deploy_model(self, version_number):
        """Deploy specific model version"""

        # Example: Update Kubernetes deployment
        subprocess.run([
            'kubectl', 'set', 'image',
            'deployment/chatbot',
            f'chatbot=chatbot:model-v{version_number}'
        ])

    def _send_rollback_alert(self, from_version, to_version, reason):
        """Send rollback notification"""

        message = {
            'text': '🔄 Model Rollback',
            'blocks': [
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f'*Model Rollback*\n'
                                f'Model: {self.model_name}\n'
                                f'From: v{from_version}\n'
                                f'To: v{to_version}\n'
                                f'Reason: {reason}'
                    }
                }
            ]
        }

        requests.post(os.environ['SLACK_WEBHOOK_URL'], json=message)

# Usage
rollback_system = ModelRollbackSystem(model_name="nlu_intent_classifier")

# Automatic rollback based on monitoring
if production_metrics['intent_accuracy'] < 0.90:
    rollback_system.rollback_to_previous(
        reason=f"Intent accuracy dropped to {production_metrics['intent_accuracy']:.2%}"
    )

# Manual rollback to specific version
rollback_system.rollback_to_version(
    version_number=23,
    reason="Critical bug in entity extraction"
)
```

---

## Summary & Best Practices

### Key Takeaways

**CI Pipeline Integration:**
- Use GitHub Actions or GitLab CI for automated testing
- Implement matrix strategies for parallel test execution
- Cache dependencies and pre-trained models
- Official Rasa GitHub Action simplifies NLU testing

**Automated Regression Testing:**
- Run nightly regression suites for comprehensive coverage
- Implement PR checks with automated comparison reports
- Track intent accuracy and entity extraction metrics
- Use statistical tests to detect performance degradation

**Test Reporting:**
- JUnit XML for CI/CD integration
- HTML reports with conversation logs for debugging
- Markdown summaries for GitHub Actions
- DataDog/Grafana dashboards for real-time monitoring
- Slack/Teams notifications for immediate feedback

**Continuous Monitoring:**
- Structure conversation logs in JSON format
- Use Langfuse or similar for observability
- Implement real-time quality scoring with LLM-as-a-judge
- Detect drift in embeddings and intent distributions
- Monitor anomalies in conversation patterns

**MLOps:**
- Version models with MLflow or DVC
- Track experiments with Weights & Biases or Neptune
- Version training data alongside models
- Automate model comparison and promotion
- Implement blue-green or canary deployments
- Have automated rollback mechanisms ready

### Recommended Tools by Category

**CI/CD**: GitHub Actions, GitLab CI, Jenkins
**Testing Platforms**: Botium, Rasa, DeepEval, Confident AI
**Observability**: Langfuse, DataDog, Grafana, Prometheus
**MLOps**: MLflow, DVC, Weights & Biases, Neptune.ai
**Deployment**: Kubernetes, Argo Rollouts, Feature flags

---

## Sources

- [How to build a chatbot powered by github actions | Medium](https://medium.com/@shantanutripathi/how-to-build-a-chatbot-powered-by-github-actions-e581224825d3)
- [GitHub - intel/conversational-ai-chatbot](https://github.com/intel/conversational-ai-chatbot)
- [GitLab ChatOps | GitLab Docs](https://docs.gitlab.com/ci/chatops/)
- [Tutorial: Building a CI Pipeline for Chatbot Developers with Rasa X and Botium Box](https://floriantreml.medium.com/tutorial-building-a-ci-pipeline-for-chatbot-developers-with-rasa-x-and-botium-box-a86cfada4fcd)
- [Integrating AI Chatbot AutoTesting With CI/CD Pipeline - NashTech Blog](https://blog.nashtechglobal.com/integrating-ai-chatbot-autotesting-with-ci-cd-pipeline/)
- [Chatbot & Conversational AI Testing Platform | Cyara Botium](https://cyara.com/products/botium/)
- [10 Best Chatbot Testing Platforms in 2025](https://www.cekura.ai/blogs/best-chat-and-voice-testing-platform-for-ai-agents)
- [Testing Conversational AI — Botium documentation](https://botium-docs.readthedocs.io/en/latest/03_testing/01_testing_conversational_ai.html)
- [Write Tests! Make Automated Testing Part of Rasa Workflow](https://rasa.com/blog/rasa-automated-tests)
- [Chatbot Monitoring with Advanced Observability - Langfuse](https://langfuse.com/faq/all/chatbot-analytics)
- [Top LLM Chatbot Evaluation Metrics](https://www.confident-ai.com/blog/llm-chatbot-evaluation-explained-top-chatbot-evaluation-metrics-and-testing-techniques)
- [Evaluating LLM-based chatbots: A comprehensive guide to performance metrics](https://medium.com/data-science-at-microsoft/evaluating-llm-based-chatbots-a-comprehensive-guide-to-performance-metrics-9c2388556d3e)
- [Uploading JUnit test report files to Datadog](https://docs.datadoghq.com/tests/setup/junit_xml/)
- [Custom summary | Grafana k6 documentation](https://grafana.com/docs/k6/latest/results-output/end-of-test/custom-summary/)
- [GitHub - DataDog/junit-upload-github-action](https://github.com/DataDog/junit-upload-github-action)
- [Real Time Test Report Dashboard using Prometheus and Grafana](https://anivaz.medium.com/real-time-test-report-dashboard-using-prometheus-and-grafana-8b47b3dda78)
- [Intro to MLOps: Data and model versioning](https://wandb.ai/site/articles/intro-to-mlops-data-and-model-versioning/)
- [Version Control for ML Models: What It Is and How To Implement It](https://neptune.ai/blog/version-control-for-ml-models)
- [Top Model Versioning Tools for Your ML Workflow](https://neptune.ai/blog/top-model-versioning-tools)
- [25 Top MLOps Tools You Need to Know in 2025](https://www.datacamp.com/blog/top-mlops-tools)
- [Using MLOps to improve AI Training and Bot Performance](https://servisbot.com/mlops-to-improve-bot-performance/)
- [Setting Up CI/CD | Rasa Documentation](https://rasa.com/docs/rasa/setting-up-ci-cd/)
- [RASA - Continuous integration using GitHub Actions](https://dev.to/petr7555/rasa-continuous-integration-using-github-actions-dp7)
- [MLOps for Conversational AI with Rasa, DVC, and CML](https://medium.com/mantisnlp/mlops-for-conversational-ai-with-rasa-dvc-and-cml-part-iii-f56a29c428f3)
- [How to Debug Your Production Chatbot When Accuracy Drops](https://www.sthambh.com/blog/how-to-debug-production-chatbot-when-accuracy-drops-a-comprehensive-diagnostic-framework/)
- [Day 60/100: Canary Deployments and A/B Testing](https://medium.com/@sebuzdugan/day-60-100-canary-deployments-and-a-b-testing-safer-smarter-model-rollouts-d9245042baf9)
- [7 Best LLM Observability Tools](https://www.truefoundry.com/blog/llm-observability-tools)
- [How to Speed Up Your CI/CD Pipeline: Caching, Parallelism, and Test Optimization](https://www.jeeviacademy.com/how-to-speed-up-your-ci-cd-pipeline-caching-parallelism-and-test-optimization/)
- [Tuning Your NLU Model](https://legacy-docs-oss.rasa.com/docs/rasa/tuning-your-model/)
- [Integrating LLM Evaluations into CI/CD Pipelines](https://www.deepchecks.com/llm-evaluation-in-ci-cd-pipelines/)
- [CI/CD Pipeline for Large Language Models (LLMs) and GenAI](https://skphd.medium.com/ci-cd-pipeline-for-large-language-models-llms-7a78799e9d5f)
