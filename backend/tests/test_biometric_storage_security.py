from __future__ import annotations

import json

import numpy as np
import pytest

from app.core.config import settings
from app.security.crypto import (
    encrypt_embedding,
    initialize_encryption,
    migrate_plaintext_embeddings,
)
from app.services import recognition


def test_production_rejects_legacy_plaintext_embedding(monkeypatch):
    monkeypatch.setattr(settings, "environment", "production")

    result = recognition._get_stored_embedding({"embedding": [0.1, 0.2]})

    assert result is None


def test_development_keeps_legacy_plaintext_compatibility(monkeypatch):
    monkeypatch.setattr(settings, "environment", "development")
    expected = np.array([0.1, 0.2], dtype=np.float64)

    result = recognition._get_stored_embedding({"embedding": expected.tolist()})

    assert np.array_equal(result, expected)


def test_valid_encrypted_embedding_loads_in_production(monkeypatch):
    monkeypatch.setattr(settings, "environment", "production")
    initialize_encryption(bytes(range(32)), bytes(range(32, 64)))
    encrypted = encrypt_embedding([0.1, 0.2])

    result = recognition._get_stored_embedding(
        {"embedding": None, "embedding_encrypted": encrypted.to_dict()}
    )

    assert np.array_equal(result, np.array([0.1, 0.2], dtype=np.float64))


def test_decryption_failure_fails_closed(monkeypatch):
    monkeypatch.setattr(settings, "environment", "production")
    initialize_encryption(bytes(range(32)), bytes(range(32, 64)))
    encrypted = encrypt_embedding([0.1, 0.2])
    initialize_encryption(bytes(range(64, 96)), bytes(range(96, 128)))

    result = recognition._get_stored_embedding(
        {"embedding": None, "embedding_encrypted": encrypted.to_dict()}
    )

    assert result is None


def test_encryption_failure_fails_closed(monkeypatch):
    monkeypatch.setattr(settings, "environment", "production")
    monkeypatch.setattr(recognition, "_get_encryption_enabled", lambda: True)

    def fail_encryption(_embedding):
        raise ValueError("encryption failure")

    monkeypatch.setattr("app.security.crypto.encrypt_embedding", fail_encryption)

    with pytest.raises(RuntimeError, match="encryption failed"):
        recognition._encrypt_and_store_embedding(np.zeros(2, dtype=np.float64))


def test_production_migration_does_not_create_plaintext_backup(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "environment", "production")
    index_path = tmp_path / "index.json"
    backup_path = tmp_path / "plaintext-backup.json"
    index_path.write_text(json.dumps({"face": {"embedding": [0.1, 0.2]}}))

    with pytest.raises(RuntimeError, match="disabled in production"):
        recognition._backup_and_migrate_embeddings(
            {"face": {"embedding": [0.1, 0.2]}}
        )
    assert not backup_path.exists()

    with pytest.raises(RuntimeError, match="disabled in production"):
        migrate_plaintext_embeddings(str(index_path), str(backup_path))
    assert not backup_path.exists()
