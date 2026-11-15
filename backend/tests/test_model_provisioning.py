from __future__ import annotations

import hashlib
import json

from scripts.download_models import verify_manifest_assets


def _write_manifest(path, filename: str, data: bytes, required: bool = True) -> None:
    path.write_text(
        json.dumps(
            {
                "models": {
                    filename: {
                        "filename": filename,
                        "sha256": hashlib.sha256(data).hexdigest(),
                        "size": len(data),
                        "purpose": "test",
                        "required": required,
                    }
                }
            }
        ),
        encoding="utf-8",
    )


def test_manifest_verification_accepts_valid_required_asset(tmp_path):
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    payload = b"valid model bytes"
    (models_dir / "model.onnx").write_bytes(payload)
    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest, "model.onnx", payload)

    assert verify_manifest_assets(manifest, models_dir) == (True, [])


def test_manifest_verification_rejects_missing_required_asset(tmp_path):
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest, "model.onnx", b"required model")

    ok, issues = verify_manifest_assets(manifest, models_dir)

    assert not ok
    assert issues == ["Required model missing: model.onnx"]


def test_manifest_verification_rejects_hash_mismatch(tmp_path):
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    (models_dir / "model.onnx").write_bytes(b"tamperedmodel")
    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest, "model.onnx", b"trusted model")

    ok, issues = verify_manifest_assets(manifest, models_dir)

    assert not ok
    assert issues == ["SHA-256 mismatch for model.onnx"]
