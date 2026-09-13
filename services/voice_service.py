"""
Voice intake service ("Agent 0").

Turns a spoken product description into structured intake fields
(part_number, brand, description) that feed unchanged into the existing
4-agent pipeline (Discovery -> Standardization -> Enrichment -> Trust).

Flow:
    raw mic audio (WAV bytes)
        -> AssemblyAI Dictation API (clean transcript)
        -> Gemini structured parse (part_number / brand / description)
        -> existing pipeline, untouched

Design note: AssemblyAI's `llm_instruction` reshapes the transcript's
*prose*, but we still want a hard-structured {part_number, brand,
description} object. So we let AssemblyAI do what it's best at (clean,
accurate transcription with filler removed) and let our own LLM service
do what it's best at (structured extraction) -- same "use the right
tool for the job" principle as the rest of this project.
"""

from __future__ import annotations

import json
import os

import requests

DICTATION_ENDPOINT = "https://dictation.assemblyai.com/v1/transcribe/live"

DICTATION_LLM_INSTRUCTION = (
    "Clean up this spoken product description: remove filler words like "
    "um and uh, fix any self-corrections to what the speaker landed on, "
    "and apply normal punctuation and capitalization. Keep it as natural "
    "spoken-style prose, do not reformat it into a list."
)

PARSE_SYSTEM_PROMPT = """You extract structured product intake fields from a spoken,
possibly informally-phrased product description. Return strict JSON only:
{
  "part_number": "string or empty string if not mentioned",
  "brand": "string or empty string if not mentioned",
  "description": "a short product description in a few words, e.g. 'industrial centrifugal pump'"
}
Do not invent a part number or brand that was not actually said. If genuinely
not mentioned, use an empty string for that field.
"""


class DictationError(Exception):
    pass


def transcribe_dictation(audio_bytes: bytes, api_key: str | None = None) -> dict:
    """Send WAV audio to AssemblyAI's Dictation API. Returns the raw response dict
    with at least `text` (verbatim) and `llm_response` (cleaned, may be None)."""
    key = api_key or os.getenv("ASSEMBLYAI_API_KEY")
    if not key:
        raise DictationError("No ASSEMBLYAI_API_KEY configured.")

    config = {"llm_instruction": DICTATION_LLM_INSTRUCTION}

    try:
        response = requests.post(
            DICTATION_ENDPOINT,
            headers={"Authorization": key},
            files={
                "config": (None, json.dumps(config), "application/json"),
                "audio": ("clip.wav", audio_bytes, "audio/wav"),
            },
            timeout=90,
        )
    except requests.RequestException as e:  # noqa: BLE001
        raise DictationError(f"Network error calling AssemblyAI: {e}") from e

    if response.status_code == 404:
        raise DictationError("Invalid AssemblyAI API key (404 from dictation endpoint).")
    if response.status_code == 415:
        raise DictationError("Unsupported audio format -- must be WAV or raw PCM.")
    if not response.ok:
        raise DictationError(f"AssemblyAI error {response.status_code}: {response.text[:300]}")

    result = response.json()
    if not result.get("text"):
        raise DictationError("No speech detected in the recording.")
    return result


def parse_voice_to_product_fields(transcript: str) -> dict:
    """Use the existing LLM service (Gemini, with mock fallback) to turn a clean
    transcript into {part_number, brand, description}."""
    from services.llm_service import get_llm_client  # local import avoids a circular import

    client = get_llm_client()
    try:
        result = client.json(PARSE_SYSTEM_PROMPT, f"Transcript: {transcript}")
    except Exception:
        result = {}

    if result.get("mock") or not any(result.get(k) for k in ("part_number", "brand", "description")):
        # offline/parse-failure fallback: just drop the whole transcript into description
        # so the user can still edit fields manually rather than losing the input entirely
        return {"part_number": "", "brand": "", "description": transcript.strip()}

    return {
        "part_number": (result.get("part_number") or "").strip(),
        "brand": (result.get("brand") or "").strip(),
        "description": (result.get("description") or transcript).strip(),
    }
