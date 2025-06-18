import os
import json
import tempfile
from unittest.mock import patch

import pytest

from src.product_scrapers.scrapers.mixins.rotating_user_agent_mixin import RotatingUserAgentMixin

class DummyRotatingUserAgent(RotatingUserAgentMixin):
    def __init__(self, user_agents_file=None):
        if user_agents_file:
            self._default_user_agents_file = user_agents_file
        super().__init__()

def test_load_user_agents_success(tmp_path):
    user_agents = ["UA1", "UA2", "UA3"]
    resources_dir = tmp_path / "resources"
    resources_dir.mkdir()
    file_path = resources_dir / "user-agents.json"
    file_path.write_text(json.dumps(user_agents))

    with patch.object(RotatingUserAgentMixin, "_get_user_agents_file_path", return_value=str(file_path)):
        dummy = DummyRotatingUserAgent()
        assert dummy._user_agents == user_agents
        assert dummy.get_random_user_agent() in user_agents

def test_load_user_agents_file_not_found():
    with patch.object(RotatingUserAgentMixin, "_get_user_agents_file_path", return_value="/non/existent/file.json"):
        dummy = DummyRotatingUserAgent()
        assert dummy._user_agents == []
        assert dummy.get_random_user_agent() is None

def test_load_user_agents_invalid_json(tmp_path):
    resources_dir = tmp_path / "resources"
    resources_dir.mkdir()
    file_path = resources_dir / "user-agents.json"
    file_path.write_text("{invalid json}")

    with patch.object(RotatingUserAgentMixin, "_get_user_agents_file_path", return_value=str(file_path)):
        dummy = DummyRotatingUserAgent()
        assert dummy._user_agents == []
        assert dummy.get_random_user_agent() is None

def test_get_random_user_agent_empty():
    dummy = DummyRotatingUserAgent()
    dummy._user_agents = []
    assert dummy.get_random_user_agent() is None
