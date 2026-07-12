"""Tests for sublime_llm.providers.omlx."""
import io
import json
import threading
import urllib.error
from unittest import mock

from unittesting import DeferrableTestCase

from LLM.sublime_llm.providers import ChatMessage, ProviderError
from LLM.sublime_llm.providers.omlx import OMLXProvider


class MockResponse:
    def __init__(self, body: bytes = b"", status: int = 200, headers=None) -> None:
        self._buf = io.BytesIO(body)
        self._status = status
        self.headers = headers or {}
        self.closed = False

    def read(self) -> bytes:
        return self._buf.read()

    def readline(self) -> bytes:
        if self.closed:
            return b""
        return self._buf.readline()

    def getcode(self) -> int:
        return self._status

    def close(self) -> None:
        self.closed = True


def _patch_no_secret_file():
    return mock.patch(
        "LLM.sublime_llm.secrets._read_secrets_file",
        return_value={},
    )


def _omlx_key():
    return mock.patch.dict(
        "os.environ", {"OMLX_API_KEY": "test-key-12345"}, clear=False
    )


def _no_omlx_key():
    return mock.patch.dict("os.environ", {"OMLX_API_KEY": ""}, clear=False)


class BaseUrlTests(DeferrableTestCase):
    def test_default_base_url(self) -> None:
        p = OMLXProvider({})
        self.assertEqual(p.base_url, "http://127.0.0.1:8000/v1")


class KeyResolutionTests(DeferrableTestCase):
    def test_key_resolved_via_omlx_env(self) -> None:
        body = json.dumps(
            {"choices": [{"message": {"role": "assistant", "content": "ok"}}]}
        ).encode("utf-8")
        captured = {}

        def fake_urlopen(req, timeout=None, context=None):
            captured["headers"] = dict(req.header_items())
            return MockResponse(body=body, status=200)

        with _omlx_key(), _patch_no_secret_file(), mock.patch(
            "LLM.sublime_llm.providers.openai.urllib.request.urlopen",
            side_effect=fake_urlopen,
        ):
            p = OMLXProvider({})
            p.complete(
                [ChatMessage("user", "hi")],
                "Qwen2.5-Coder-1.5B-Instruct-MLX-8bit",
                {},
                threading.Event(),
            )

        lowered = {k.lower(): v for k, v in captured["headers"].items()}
        self.assertEqual(lowered.get("authorization"), "Bearer test-key-12345")


class ListModelsTests(DeferrableTestCase):
    def test_list_models_success(self) -> None:
        body = json.dumps(
            {
                "data": [
                    {"id": "Qwen2.5-Coder-1.5B-Instruct-MLX-8bit"},
                    {"id": "Qwen2.5-Coder-14B-Instruct-MLX-4bit"},
                ]
            }
        ).encode("utf-8")
        with _omlx_key(), _patch_no_secret_file(), mock.patch(
            "LLM.sublime_llm.providers.openai.urllib.request.urlopen",
            return_value=MockResponse(body=body, status=200),
        ):
            p = OMLXProvider({})
            self.assertEqual(
                p.list_models(),
                [
                    "Qwen2.5-Coder-14B-Instruct-MLX-4bit",
                    "Qwen2.5-Coder-1.5B-Instruct-MLX-8bit",
                ],
            )

    def test_list_models_falls_back_on_404(self) -> None:
        err = urllib.error.HTTPError(
            url="http://127.0.0.1:8000/v1/models",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=io.BytesIO(b"nope"),
        )
        with _omlx_key(), _patch_no_secret_file(), mock.patch(
            "LLM.sublime_llm.providers.openai.urllib.request.urlopen",
            side_effect=err,
        ):
            p = OMLXProvider({})
            self.assertEqual(p.list_models(), [])

        self.assertTrue(err.closed)

    def test_list_models_falls_back_on_connection_error(self) -> None:
        with _omlx_key(), _patch_no_secret_file(), mock.patch(
            "LLM.sublime_llm.providers.openai.urllib.request.urlopen",
            side_effect=ConnectionRefusedError(),
        ):
            p = OMLXProvider({})
            self.assertEqual(p.list_models(), [])

    def test_list_models_custom_fallback(self) -> None:
        err = urllib.error.HTTPError(
            url="http://127.0.0.1:8000/v1/models",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=io.BytesIO(b"nope"),
        )
        with _omlx_key(), _patch_no_secret_file(), mock.patch(
            "LLM.sublime_llm.providers.openai.urllib.request.urlopen",
            side_effect=err,
        ):
            p = OMLXProvider(
                {
                    "omlx_models": [
                        "Qwen2.5-Coder-1.5B-Instruct-MLX-8bit",
                        "Qwen2.5-Coder-14B-Instruct-MLX-4bit",
                    ]
                }
            )
            self.assertEqual(
                p.list_models(),
                [
                    "Qwen2.5-Coder-1.5B-Instruct-MLX-8bit",
                    "Qwen2.5-Coder-14B-Instruct-MLX-4bit",
                ],
            )

    def test_list_models_no_key_uses_fallback(self) -> None:
        with _no_omlx_key(), _patch_no_secret_file(), mock.patch(
            "LLM.sublime_llm.providers.openai.urllib.request.urlopen"
        ) as urlopen:
            p = OMLXProvider({})
            self.assertEqual(p.list_models(), [])
            urlopen.assert_not_called()


class ErrorMessageTests(DeferrableTestCase):
    def test_missing_credential_says_omlx(self) -> None:
        with _no_omlx_key(), _patch_no_secret_file():
            p = OMLXProvider({})
            with self.assertRaises(ProviderError) as cm:
                p.complete(
                    [ChatMessage("user", "hi")],
                    "Qwen2.5-Coder-1.5B-Instruct-MLX-8bit",
                    {},
                    threading.Event(),
                )
            self.assertEqual(cm.exception.code, "MISSING_CREDENTIAL")
            self.assertIn("oMLX", cm.exception.message)
