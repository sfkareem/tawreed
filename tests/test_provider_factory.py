"""Provider factory tests.

These are pure-Python unit tests — no GUI, no API calls, no DB writes.
Run with `pytest tests/` from the project root.
"""
import os

import pytest

# conftest.py handles the project-root sys.path insertion and the
# Qt offscreen platform setup. See tests/conftest.py.

from core.ai import (  # noqa: E402
    PROVIDERS,
    get_provider_names,
    get_provider_config,
    is_valid_provider,
    get_default_settings,
)


def test_provider_names_returns_all_keys():
    names = get_provider_names()
    assert isinstance(names, list)
    assert set(names) == set(PROVIDERS.keys())


def test_provider_names_order_matches_dict_order():
    # The UI dropdown relies on the order returned by get_provider_names.
    # This guards against accidental ordering changes (e.g. sorting) that
    # would shift the dropdown's default selection.
    assert get_provider_names() == list(PROVIDERS.keys())


@pytest.mark.parametrize("name", list(PROVIDERS.keys()))
def test_every_provider_has_required_fields(name):
    cfg = get_provider_config(name)
    for key in ("base_url", "models", "default_model", "requires_base_url", "transport", "label"):
        assert key in cfg, f"provider {name!r} missing field {key!r}"


@pytest.mark.parametrize("name", list(PROVIDERS.keys()))
def test_every_provider_default_model_is_in_its_models_list(name):
    cfg = get_provider_config(name)
    # OpenAI-Compatible is allowed to have an empty default model because
    # the user is expected to type a model name manually.
    if cfg["default_model"] == "" and cfg["models"] == []:
        return
    assert cfg["default_model"] in cfg["models"], (
        f"provider {name!r}: default_model {cfg['default_model']!r} "
        f"not present in models {cfg['models']!r}"
    )


def test_is_valid_provider_known():
    assert is_valid_provider("OpenAI") is True
    assert is_valid_provider("Google") is True
    assert is_valid_provider("Claude") is True
    assert is_valid_provider("OpenAI Compatible") is True


def test_is_valid_provider_unknown():
    assert is_valid_provider("") is False
    assert is_valid_provider("openai") is False  # case-sensitive
    assert is_valid_provider("Anthropic") is False  # the dict key is "Claude"


def test_get_provider_config_unknown_raises_keyerror():
    with pytest.raises(KeyError):
        get_provider_config("NotARealProvider")


def test_get_default_settings_has_all_required_keys():
    s = get_default_settings()
    for key in ("provider", "api_key", "model", "base_url"):
        assert key in s, f"default settings missing {key!r}"


def test_get_default_settings_provider_is_valid():
    s = get_default_settings()
    assert is_valid_provider(s["provider"])


def test_get_default_settings_model_matches_provider_default():
    s = get_default_settings()
    cfg = get_provider_config(s["provider"])
    assert s["model"] == cfg["default_model"]
    assert s["base_url"] == cfg["base_url"]


def test_get_default_settings_api_key_blank():
    # We must never ship with a default API key.
    assert get_default_settings()["api_key"] == ""
