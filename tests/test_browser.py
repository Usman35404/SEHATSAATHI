"""Optional Chromium integration tests; see requirements-dev.txt and README."""
import json
import os
import threading
from types import SimpleNamespace

import pytest

playwright = pytest.importorskip('playwright.sync_api')
from werkzeug.serving import make_server

import ai_service
from app import create_app


@pytest.fixture
def site(monkeypatch):
    entered, release = threading.Event(), threading.Event()
    control = {'delay': False}

    def generate_content(*, contents, **kwargs):
        if control['delay']:
            entered.set()
            assert release.wait(10), 'Test did not release delayed Gemini response'
        if 'User Question:' in contents:
            data = {'answer': 'Scrub with soap for at least 20 seconds.', 'supported_by_source': True}
        else:
            data = {
                'explanation': 'Wash your hands with soap and clean water. Scrub for at least 20 seconds.',
                'key_points': ['Wet your hands.', 'Scrub for 20 seconds.', 'Rinse and dry your hands.'],
                'quiz': {'question': 'How long should you scrub?', 'options': ['5 seconds', '20 seconds', '60 seconds'],
                         'correct_index': 1, 'feedback': 'Scrub for at least 20 seconds to remove germs.'},
            }
        return SimpleNamespace(text=json.dumps(data))

    monkeypatch.setattr(ai_service, '_get_genai_client', lambda: SimpleNamespace(
        models=SimpleNamespace(generate_content=generate_content)))
    server = make_server('127.0.0.1', 0, create_app(), threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_port}', control, entered, release
    release.set()
    server.shutdown()
    thread.join()


@pytest.fixture
def page(site):
    with playwright.sync_playwright() as p:
        executable = os.environ.get('CHROMIUM_EXECUTABLE_PATH')
        browser = p.chromium.launch(headless=True, executable_path=executable)
        page = browser.new_page()
        page.add_init_script('''
          window.spoken = [];
          window.completedRequests = [];
          window.completedFetches = [];
          const originalFetch = window.fetch.bind(window);
          window.fetch = async (...args) => {
            const response = await originalFetch(...args);
            setTimeout(() => completedFetches.push(args[0]), 0);
            const originalJson = response.json.bind(response);
            response.json = async () => {
              const data = await originalJson();
              if (window.delayJson) {
                window.jsonWaiting = true;
                await new Promise(resolve => window.releaseJson = resolve);
              }
              setTimeout(() => completedRequests.push(args[0]), 0);
              return data;
            };
            return response;
          };
          window.SpeechSynthesisUtterance = class { constructor(text) { this.text = text; } };
          Object.defineProperty(window, 'speechSynthesis', {configurable: true, value: {
            getVoices: () => [{lang: 'en-US'}, {lang: 'ur-PK'}],
            cancel: () => {}, speak: u => window.spoken.push(u)
          }});
        ''')
        page.goto(site[0])
        yield page
        browser.close()


@pytest.mark.parametrize('language', ['en', 'ur'])
def test_explain_listen_quiz(page, language):
    page.locator(f'#lang-{language}-btn').click()
    page.locator('#explain-btn').click()
    playwright.expect(page.locator('#result-container')).to_be_visible()
    playwright.expect(page.locator('#localized-explanation-region')).to_have_attribute('dir', 'rtl' if language == 'ur' else 'ltr')
    playwright.expect(page.locator('#result-key-points li')).to_have_count(3)
    playwright.expect(page.locator('#source-url-link')).to_have_attribute('href', 'https://www.cdc.gov/clean-hands/about/')
    page.locator('#listen-btn').click()
    assert page.evaluate('spoken[0].text') == 'Wash your hands with soap and clean water. Scrub for at least 20 seconds.. Wet your hands.. Scrub for 20 seconds.. Rinse and dry your hands.'
    assert page.evaluate('spoken[0].lang') == ('ur-PK' if language == 'ur' else 'en-US')
    playwright.expect(page.locator('#stop-audio-btn')).to_be_visible()
    page.evaluate('spoken[0].onend()')
    playwright.expect(page.locator('#stop-audio-btn')).to_be_hidden()
    page.locator('input[value="0"]').check()
    page.locator('#submit-quiz-btn').click()
    playwright.expect(page.locator('#quiz-feedback-box')).to_have_class('quiz-feedback is-incorrect')
    page.locator('input[value="1"]').check()
    page.locator('#submit-quiz-btn').click()
    playwright.expect(page.locator('#quiz-feedback-box')).to_have_class('quiz-feedback is-correct')
    playwright.expect(page.locator('#quiz-feedback-text')).to_contain_text('at least 20 seconds')


def test_selection_change_invalidates_pending_explanation(page, site):
    _, control, entered, release = site
    control['delay'] = True
    page.locator('#explain-btn').click()
    assert entered.wait(3)
    page.locator('#lang-ur-btn').click()
    try:
        playwright.expect(page.locator('#explain-btn')).to_be_enabled(timeout=1000)
    finally:
        release.set()
    page.wait_for_function("completedFetches.includes('/api/explain')")
    playwright.expect(page.locator('#result-container')).to_be_hidden()
    playwright.expect(page.locator('#error-state')).to_be_hidden()
    control['delay'] = False
    page.locator('#explain-btn').click()
    playwright.expect(page.locator('#result-lang-badge')).to_have_text('اردو (Urdu)')


def test_followup_does_not_restore_old_topic_answer(page, site):
    _, control, entered, release = site
    page.locator('#explain-btn').click()
    playwright.expect(page.locator('#result-container')).to_be_visible()
    control['delay'] = True
    page.locator('#followup-input').fill('How long should I scrub?')
    page.locator('#followup-submit-btn').click()
    assert entered.wait(3)
    page.locator('[data-topic-id="sleep"]').click()
    control['delay'] = False
    page.locator('#explain-btn').click()
    playwright.expect(page.locator('#result-topic-heading')).to_have_text('Healthy Sleep Basics')
    try:
        playwright.expect(page.locator('#followup-submit-btn')).to_be_enabled(timeout=1000)
    finally:
        with page.expect_response('**/api/ask'):
            release.set()
    page.wait_for_function("completedRequests.includes('/api/ask')")
    playwright.expect(page.locator('#followup-result')).to_be_hidden()


@pytest.mark.parametrize('language, label', [('en', 'English'), ('ur', 'Urdu')])
def test_missing_voice_disables_listen(page, language, label):
    page.locator(f'#lang-{language}-btn').click()
    page.evaluate('speechSynthesis.getVoices = () => []')
    page.locator('#explain-btn').click()
    playwright.expect(page.locator('#result-container')).to_be_visible()
    playwright.expect(page.locator('#listen-btn')).to_be_disabled()
    playwright.expect(page.locator('#speech-status-note')).to_contain_text(f'{label} voice')
    page.evaluate("speechSynthesis.getVoices = () => [{lang: 'en-US'}, {lang: 'ur-PK'}]; speechSynthesis.onvoiceschanged()")
    playwright.expect(page.locator('#listen-btn')).to_be_enabled()


def test_quiz_remains_available_without_speech_support(page):
    page.evaluate("delete window.speechSynthesis")
    page.locator('#explain-btn').click()
    playwright.expect(page.locator('#result-container')).to_be_visible()
    playwright.expect(page.locator('#listen-btn')).to_be_disabled()
    playwright.expect(page.locator('#speech-status-note')).to_contain_text('not supported')
    page.locator('input[value="1"]').check()
    page.locator('#submit-quiz-btn').click()
    playwright.expect(page.locator('#quiz-feedback-box')).to_have_class('quiz-feedback is-correct')


def test_selection_change_while_response_body_is_pending(page):
    page.evaluate('window.delayJson = true')
    page.locator('#explain-btn').click()
    page.wait_for_function('window.jsonWaiting')
    page.locator('#lang-ur-btn').click()
    page.evaluate('window.releaseJson()')
    page.wait_for_function("completedRequests.includes('/api/explain')")
    playwright.expect(page.locator('#result-container')).to_be_hidden()
    playwright.expect(page.locator('#explain-btn')).to_be_enabled()
