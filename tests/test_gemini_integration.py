"""Configuration/provider regressions. All credentials and responses are synthetic."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from google.genai import errors, types

import ai_service
import app as application


@pytest.mark.parametrize('encoding', ['utf-8', 'utf-8-sig'])
def test_factory_loads_project_dotenv_including_windows_bom(monkeypatch, tmp_path, encoding):
    (tmp_path / '.env').write_text('GEMINI_API_KEY=dummy-file-key\nGEMINI_MODEL=test-text\n', encoding=encoding)
    monkeypatch.setattr(application, 'BASE_DIR', tmp_path)
    monkeypatch.delenv('PYTHON_DOTENV_DISABLED', raising=False)
    # Register restoration even when dotenv adds previously absent variables.
    monkeypatch.setenv('GEMINI_API_KEY', 'dummy-before-load')
    monkeypatch.setenv('GEMINI_MODEL', 'dummy-before-load')
    monkeypatch.delenv('GEMINI_API_KEY')
    monkeypatch.delenv('GEMINI_MODEL')
    application.create_app({'TESTING': True})
    assert ai_service.is_ai_configured()
    assert ai_service.get_configured_model_name() == 'test-text'


def test_dotenv_preserves_exported_configuration(monkeypatch, tmp_path):
    (tmp_path / '.env').write_text('GEMINI_API_KEY=dummy-file-key\nGEMINI_MODEL=file-model\n')
    monkeypatch.setattr(application, 'BASE_DIR', tmp_path)
    monkeypatch.delenv('PYTHON_DOTENV_DISABLED', raising=False)
    monkeypatch.setenv('GEMINI_API_KEY', 'dummy-exported-key')
    monkeypatch.setenv('GEMINI_MODEL', 'exported-model')
    application.create_app({'TESTING': True})
    client = Mock()
    monkeypatch.setattr(ai_service.genai, 'Client', client)
    ai_service._get_genai_client()
    assert client.call_args.kwargs['api_key'] == 'dummy-exported-key'
    assert ai_service.get_configured_model_name() == 'exported-model'


@pytest.mark.parametrize('key', ['', ' ', 'replace_with_your_own_key_locally', 'your_actual_gemini_api_key_here', 'YOUR_API_KEY', '<your-api-key>'])
def test_placeholder_keys_are_not_configured(monkeypatch, key):
    monkeypatch.setenv('GEMINI_API_KEY', key)
    assert not ai_service.is_ai_configured()


def test_client_uses_gemini_api_despite_vertex_environment(monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY', '  dummy-key  ')
    monkeypatch.setenv('GOOGLE_GENAI_USE_VERTEXAI', 'true')
    client = Mock()
    monkeypatch.setattr(ai_service.genai, 'Client', client)
    ai_service._get_genai_client()
    assert client.call_args.kwargs['api_key'] == 'dummy-key'
    assert client.call_args.kwargs['vertexai'] is False


@pytest.mark.parametrize('model', ['', 'replace_with_a_model_verified_for_your_account'])
def test_model_must_be_selected_explicitly(monkeypatch, model):
    monkeypatch.setenv('GEMINI_MODEL', model)
    with pytest.raises(ai_service.AIServiceError) as exc:
        ai_service.get_configured_model_name()
    assert exc.value.code == 'AI_MODEL_NOT_CONFIGURED'


@pytest.mark.parametrize('stage', ['metadata', 'generation'])
@pytest.mark.parametrize('route', ['/api/explain', '/api/ask'])
@pytest.mark.parametrize('status,reason,expected', [
    (400, 'API_KEY_INVALID', 'AI_AUTH_FAILED'),
    (401, 'UNAUTHENTICATED', 'AI_AUTH_FAILED'),
    (403, 'PERMISSION_DENIED', 'AI_ACCESS_DENIED'),
    (404, 'NOT_FOUND', 'AI_MODEL_UNAVAILABLE'),
    (429, 'RESOURCE_EXHAUSTED', 'AI_RATE_LIMITED'),
    (400, 'INVALID_ARGUMENT', 'AI_REQUEST_REJECTED'),
    (503, 'UNAVAILABLE', 'AI_UNAVAILABLE'),
])
def test_provider_errors_are_actionable_and_redacted(monkeypatch, route, status, reason, expected, stage):
    monkeypatch.setenv('GEMINI_MODEL', 'test-text')
    error = errors.APIError(status, {'error': {
        'code': status, 'message': 'Sensitive dummy-key and provider details',
        'details': [{'reason': reason}],
    }})
    models = SimpleNamespace(
        get=Mock(side_effect=error) if stage == 'metadata' else Mock(return_value=types.Model(name='models/test-text', supported_actions=['generateContent'])),
        generate_content=Mock(side_effect=error),
    )
    monkeypatch.setattr(ai_service, '_get_genai_client', lambda: SimpleNamespace(models=models))
    client = application.create_app({'TESTING': True}).test_client()
    response = client.post(route, json={'topic_id': 'handwashing', 'language': 'en', 'question': 'How long should I scrub?'})
    assert response.status_code == 503
    assert response.json['error']['code'] == expected
    assert response.json['live_ai'] is False
    assert 'dummy-key' not in response.text
    assert 'Sensitive' not in response.text


def test_embedding_model_is_rejected_before_generation(monkeypatch):
    monkeypatch.setenv('GEMINI_MODEL', 'test-embedding')
    generate = Mock()
    models = SimpleNamespace(get=lambda **kw: types.Model(name='models/test-embedding', supported_actions=['embedContent']), generate_content=generate)
    monkeypatch.setattr(ai_service, '_get_genai_client', lambda: SimpleNamespace(models=models))
    response = application.create_app({'TESTING': True}).test_client().post('/api/explain', json={'topic_id': 'sleep', 'language': 'en'})
    assert response.json['error']['code'] == 'AI_MODEL_UNSUPPORTED'
    generate.assert_not_called()


def test_model_discovery_uses_official_api_and_filters_generation(monkeypatch):
    models = [types.Model(name='models/account-text', supported_actions=['generateContent']), types.Model(name='models/embed-only', supported_actions=['embedContent'])]
    monkeypatch.setattr(ai_service, '_get_genai_client', lambda: SimpleNamespace(models=SimpleNamespace(list=lambda: iter(models))))
    result = application.create_app({'TESTING': True}).test_cli_runner().invoke(args=['list-gemini-models'])
    assert result.exit_code == 0
    assert result.output.strip() == 'models/account-text'


def test_model_discovery_redacts_errors(monkeypatch):
    error = errors.ClientError(403, {'error': {'message': 'Sensitive dummy-key'}})
    models = SimpleNamespace(list=Mock(side_effect=error))
    monkeypatch.setattr(ai_service, '_get_genai_client', lambda: SimpleNamespace(models=models))
    result = application.create_app({'TESTING': True}).test_cli_runner().invoke(args=['list-gemini-models'])
    assert result.exit_code != 0
    assert 'AI_ACCESS_DENIED' in result.output
    assert 'dummy-key' not in result.output


def test_client_initialization_error_is_redacted(monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY', 'dummy-key')
    monkeypatch.setattr(ai_service.genai, 'Client', Mock(side_effect=ValueError('Sensitive dummy-key')))
    with pytest.raises(ai_service.AIServiceError) as exc:
        ai_service._get_genai_client()
    assert exc.value.code == 'AI_UNAVAILABLE'
    assert 'dummy-key' not in str(exc.value)


def test_selected_model_is_verified_then_used_without_fallback(monkeypatch):
    monkeypatch.setenv('GEMINI_MODEL', ' models/account-text ')
    models = SimpleNamespace(
        get=Mock(return_value=types.Model(name='models/account-text', supported_actions=['generateContent'])),
        generate_content=Mock(return_value=SimpleNamespace(text='{"answer":"Scrub for at least 20 seconds.","supported_by_source":true}')),
    )
    monkeypatch.setattr(ai_service, '_get_genai_client', lambda: SimpleNamespace(models=models))
    response = application.create_app({'TESTING': True}).test_client().post('/api/ask', json={
        'topic_id': 'handwashing', 'language': 'en', 'question': 'How long should I scrub?',
    })
    assert response.status_code == 200
    assert response.json['answer'] == 'Scrub for at least 20 seconds.'
    models.get.assert_called_once_with(model='models/account-text')
    assert models.generate_content.call_args.kwargs['model'] == 'models/account-text'


def test_model_discovery_paginates_with_real_sdk_and_mock_http(monkeypatch):
    import httpx2
    from google import genai

    def respond(request):
        assert request.url.host == 'generativelanguage.googleapis.com'
        assert request.url.path == '/v1beta/models'
        if request.url.params.get('pageToken') == 'next-page':
            return httpx2.Response(200, json={'models': [
                {'name': 'models/page-two', 'supportedGenerationMethods': ['generateContent']},
                {'name': 'models/embed', 'supportedGenerationMethods': ['embedContent']},
            ]})
        return httpx2.Response(200, json={'models': [
            {'name': 'models/page-one', 'supportedGenerationMethods': ['generateContent']},
        ], 'nextPageToken': 'next-page'})

    with genai.Client(api_key='dummy-key', vertexai=False, http_options=types.HttpOptions(
        base_url='https://generativelanguage.googleapis.com', api_version='v1beta',
        client_args={'transport': httpx2.MockTransport(respond), 'trust_env': False},
    )) as client:
        monkeypatch.setattr(ai_service, '_get_genai_client', lambda: client)
        assert ai_service.list_generation_models() == ['models/page-one', 'models/page-two']
