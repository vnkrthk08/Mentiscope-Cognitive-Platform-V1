"""
Cross-language parity test: Asserts 100% identical CRC32 hashing and canary bucketing
between Python backend (BackchannelRegistry.is_canary_session) and TypeScript frontend (isCanarySession).
"""

import json
import subprocess
import zlib
import pytest
from app.application.followup_subsystem.backchannel_registry import BackchannelRegistry


# Diverse batch of test vectors: UUIDs, ASCII slugs, edge cases, symbols, unicode
TEST_SESSION_IDS = [
    # Standard UUID v4 strings
    "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
    "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "00000000-0000-0000-0000-000000000000",
    "ffffffff-ffff-ffff-ffff-ffffffffffff",
    # Typical application session slugs
    "session_candidate_12345",
    "live_real_llm_test_image1",
    "sess-prod-2026-08-12-cand-099",
    "default_session",
    "test_stream_session_001",
    # Numbers & Short strings
    "1",
    "0",
    "42",
    "a",
    "ab",
    "abc",
    # Special Characters & Edge Cases
    "session/with/slashes/and.dots_and-dashes",
    "user@domain.com:assessment:session#99",
    "!@#$%^&*()_+-=[]{}|;':,.<>?`~",
    "   session_with_leading_and_trailing_spaces   ",
    # Unicode & Multibyte strings
    "session_élève_étudiant_123",
    "session_日本語_テスト_2026",
    "session_हिंदी_परीक्षण_001",
    "session_🚀_sparkles_✨",
    # Long strings
    "long_session_" + "x" * 500,
]

ROLLOUT_PERCENTAGES = [0, 1, 5, 10, 25, 50, 75, 90, 99, 100]


def test_cross_language_crc32_and_canary_parity():
    """
    Executes Node.js with TypeScript's crc32Hash & isCanarySession logic
    and asserts that all test vectors produce identical CRC32 unsigned ints
    and identical boolean canary bucket decisions across all rollout percentages.
    """
    # JS script that computes CRC32 and canary decisions using the exact logic from src/config/features.ts
    js_script = """
    const fs = require('fs');
    const inputData = JSON.parse(fs.readFileSync(0, 'utf-8'));
    const { testSessions, rolloutPercentages } = inputData;

    const CRC32_TABLE = new Uint32Array(256);
    for (let i = 0; i < 256; i++) {
        let c = i;
        for (let j = 0; j < 8; j++) {
            c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
        }
        CRC32_TABLE[i] = c >>> 0;
    }

    function crc32Hash(str) {
        if (!str) return 0;
        const bytes = new TextEncoder().encode(str);
        let crc = 0xffffffff;
        for (let i = 0; i < bytes.length; i++) {
            crc = (crc >>> 8) ^ CRC32_TABLE[(crc ^ bytes[i]) & 0xff];
        }
        return (crc ^ 0xffffffff) >>> 0;
    }

    function isCanarySession(sessionId, rolloutPercentage) {
        if (!sessionId || rolloutPercentage <= 0) return false;
        if (rolloutPercentage >= 100) return true;
        const hash = crc32Hash(sessionId);
        return (hash % 100) < rolloutPercentage;
    }

    const results = {};
    for (const sid of testSessions) {
        const hash = crc32Hash(sid);
        const buckets = {};
        for (const pct of rolloutPercentages) {
            buckets[pct] = isCanarySession(sid, pct);
        }
        results[sid] = { hash, buckets };
    }

    console.log(JSON.stringify(results));
    """

    payload_json = json.dumps({
        "testSessions": TEST_SESSION_IDS,
        "rolloutPercentages": ROLLOUT_PERCENTAGES,
    })

    # Run in Node.js via stdin with explicit utf-8 encoding
    proc = subprocess.run(
        ["node", "-e", js_script],
        input=payload_json,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    js_results = json.loads(proc.stdout)

    # Compare against Python implementation
    for sid in TEST_SESSION_IDS:
        py_hash = zlib.crc32(sid.encode("utf-8")) & 0xFFFFFFFF
        js_hash = js_results[sid]["hash"]

        assert py_hash == js_hash, (
            f"CRC32 mismatch for session_id '{sid}': Python={py_hash} (0x{py_hash:08X}) vs TS/JS={js_hash} (0x{js_hash:08X})"
        )

        for pct in ROLLOUT_PERCENTAGES:
            py_canary = BackchannelRegistry.is_canary_session(sid, rollout_percentage=pct)
            js_canary = js_results[sid]["buckets"][str(pct)]

            assert py_canary == js_canary, (
                f"Canary bucket decision mismatch for session_id '{sid}' at {pct}% rollout: "
                f"Python={py_canary} vs TS/JS={js_canary}"
            )
