"""Tests for API endpoints — webhook signature, reject, compliance."""

import hashlib
import hmac

from api.routes.webhooks import _verify_signature


def test_verify_signature_valid():
    payload = b'{"action": "created"}'
    secret = "test-secret"
    sig = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    assert _verify_signature(payload, sig, secret) is True


def test_verify_signature_invalid():
    payload = b'{"action": "created"}'
    assert _verify_signature(payload, "sha256=bad", "test-secret") is False


def test_verify_signature_empty_secret():
    assert _verify_signature(b"data", "sha256=abc", "") is False


def test_verify_signature_empty_sig():
    assert _verify_signature(b"data", "", "secret") is False
