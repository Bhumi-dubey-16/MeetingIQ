import os
import PyPDF2
import docx
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SUPPORTED_AUDIO = {".mp3", ".mp4", ".wav", ".m4a", ".ogg", ".webm"}
SUPPORTED_DOCS  = {".pdf", ".docx", ".txt"}
ALL_SUPPORTED   = SUPPORTED_AUDIO | SUPPORTED_DOCS


def parse_input(file_path: str = None, text: str = None) -> str:
    """
    Master function — accepts ANY input, always returns plain text.
    Raises ValueError with a clean message for unsupported file types.
    Never crashes with a 500 — all errors are caught and re-raised cleanly.
    """

    # ── Direct text input ──────────────────────────────────────────────────────
    if text and text.strip():
        return text.strip()

    # ── No input at all ────────────────────────────────────────────────────────
    if not file_path:
        raise ValueError("Please provide either a file or paste your transcript as text.")

    ext = Path(file_path).suffix.lower()

    # ── Unsupported file type — clean error, no 500 ───────────────────────────
    if ext not in ALL_SUPPORTED:
        supported_list = ", ".join(sorted(ALL_SUPPORTED))
        raise ValueError(
            f"Unsupported file type '{ext}'. "
            f"MeetingIQ supports: {supported_list}"
        )

    # ── Audio ──────────────────────────────────────────────────────────────────
    if ext in SUPPORTED_AUDIO:
        return _parse_audio(file_path)

    # ── Documents ──────────────────────────────────────────────────────────────
    if ext == ".pdf":
        return _parse_pdf(file_path)
    if ext == ".docx":
        return _parse_docx(file_path)
    if ext == ".txt":
        return _parse_txt(file_path)


# ── Diarization helper ────────────────────────────────────────────────────────

def _build_diarized_transcript(response) -> str:
    """
    Takes a verbose_json Whisper response and assembles a transcript
    with speaker labels like:

        [Speaker 1] Let's kick off with the Q3 roadmap.
        [Speaker 2] Agreed. Our primary concern is the vendor delay.
        [Speaker 1] Right, so we need to lock that down by Friday.

    How it works:
    - Whisper returns a list of segments, each with a 'speaker' field
      (e.g. "SPEAKER_00", "SPEAKER_01") and a 'text' field.
    - We rename them to "Speaker 1", "Speaker 2" etc. for readability.
    - Consecutive segments from the same speaker are merged into one line
      so the transcript doesn't fragment into tiny one-word chunks.

    Falls back to plain text if diarization data is missing — so this
    never crashes even if Groq changes its response format.
    """
    segments = getattr(response, "segments", None)

    # No segments at all — fall back to plain text
    if not segments:
        return getattr(response, "text", "").strip()

    # Check if any segment has speaker info
    has_speaker = any(getattr(seg, "speaker", None) for seg in segments)

    if not has_speaker:
        # Diarization wasn't returned — join segments as plain text
        return " ".join(
            getattr(seg, "text", "").strip()
            for seg in segments
            if getattr(seg, "text", "").strip()
        )

    # Map raw Groq speaker IDs → human-readable labels
    # e.g. "SPEAKER_00" → "Speaker 1", "SPEAKER_01" → "Speaker 2"
    speaker_map: dict[str, str] = {}

    def _label(raw_speaker: str) -> str:
        if raw_speaker not in speaker_map:
            speaker_map[raw_speaker] = f"Speaker {len(speaker_map) + 1}"
        return speaker_map[raw_speaker]

    # Merge consecutive segments from the same speaker into one line
    lines = []
    current_speaker = None
    current_text_parts = []

    for seg in segments:
        raw_speaker = getattr(seg, "speaker", None) or "SPEAKER_UNKNOWN"
        text        = getattr(seg, "text", "").strip()
        if not text:
            continue

        if raw_speaker == current_speaker:
            # Same speaker continuing — append to current line
            current_text_parts.append(text)
        else:
            # Speaker changed — flush previous line
            if current_speaker is not None and current_text_parts:
                label = _label(current_speaker)
                lines.append(f"[{label}] {' '.join(current_text_parts)}")
            # Start new speaker
            current_speaker    = raw_speaker
            current_text_parts = [text]

    # Flush the last speaker's line
    if current_speaker is not None and current_text_parts:
        label = _label(current_speaker)
        lines.append(f"[{label}] {' '.join(current_text_parts)}")

    return "\n".join(lines)


# ── Audio parsing ─────────────────────────────────────────────────────────────

def _parse_audio(file_path: str) -> str:
    """
    Audio → diarized transcript via Groq Whisper API (whisper-large-v3).

    Uses verbose_json response format to get per-segment speaker labels.
    Falls back gracefully to plain text if diarization is unavailable.
    Handles files over 25MB by splitting into chunks automatically.
    """
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

    if file_size_mb > 25:
        return _parse_audio_chunked(file_path)

    try:
        with open(file_path, "rb") as f:
            response = client.audio.transcriptions.create(
                file            = (Path(file_path).name, f),
                model           = "whisper-large-v3",
                response_format = "verbose_json",  # ← gives us segments + speaker
                language        = "en",
                # diarization is enabled by default in verbose_json on Groq;
                # no extra parameter needed — speaker labels come in segments
            )

        transcript = _build_diarized_transcript(response)

        if not transcript.strip():
            raise ValueError("Transcription returned empty text.")

        print(f"[Parser] Transcribed audio — {len(transcript)} chars, "
              f"{len(getattr(response, 'segments', []))} segments")
        return transcript

    except Exception as e:
        raise ValueError(f"Audio transcription failed: {str(e)}")


def _parse_audio_chunked(file_path: str) -> str:
    """
    For audio files over 25MB — splits into 10-minute chunks,
    transcribes each with diarization, joins the results.
    Requires ffmpeg installed: brew install ffmpeg

    Note: speaker numbering resets per chunk (each chunk is a separate
    Whisper call). Labels are offset per chunk so Speaker 1 in chunk 2
    doesn't collide with Speaker 1 in chunk 1.
    """
    import subprocess
    import tempfile
    import glob

    with tempfile.TemporaryDirectory() as tmp_dir:
        chunk_pattern = os.path.join(tmp_dir, "chunk_%03d.mp3")

        split_cmd = [
            "ffmpeg", "-i", file_path,
            "-f", "segment",
            "-segment_time", "600",
            "-c", "copy",
            "-y",
            chunk_pattern
        ]

        try:
            subprocess.run(split_cmd, check=True, capture_output=True)
        except FileNotFoundError:
            raise ValueError(
                "ffmpeg is not installed. For large audio files, install it: brew install ffmpeg"
            )
        except subprocess.CalledProcessError as e:
            raise ValueError(f"Failed to split audio file: {e.stderr.decode()}")

        chunks = sorted(glob.glob(os.path.join(tmp_dir, "chunk_*.mp3")))
        if not chunks:
            raise ValueError("Audio splitting produced no chunks — file may be corrupted.")

        all_parts = []
        # Track how many unique speakers we've seen so far across chunks
        # so we can offset labels: chunk 0 has Speaker 1/2, chunk 1 gets 3/4, etc.
        global_speaker_offset = 0

        for i, chunk_path in enumerate(chunks):
            print(f"[Parser] Transcribing chunk {i+1}/{len(chunks)}...")
            try:
                with open(chunk_path, "rb") as f:
                    response = client.audio.transcriptions.create(
                        file            = (f"chunk_{i}.mp3", f),
                        model           = "whisper-large-v3",
                        response_format = "verbose_json",
                        language        = "en",
                    )

                # Build diarized text for this chunk, then offset speaker numbers
                chunk_text = _build_diarized_transcript(response)

                # Count how many unique speakers appeared in this chunk
                segments = getattr(response, "segments", [])
                unique_speakers_in_chunk = len({
                    getattr(seg, "speaker", "SPEAKER_UNKNOWN")
                    for seg in segments
                    if getattr(seg, "speaker", None)
                })

                # Offset: replace "Speaker N" with "Speaker N+offset"
                if global_speaker_offset > 0:
                    for n in range(unique_speakers_in_chunk, 0, -1):
                        chunk_text = chunk_text.replace(
                            f"[Speaker {n}]",
                            f"[Speaker {n + global_speaker_offset}]"
                        )

                global_speaker_offset += unique_speakers_in_chunk
                all_parts.append(chunk_text)

            except Exception as e:
                print(f"[Parser] Warning: chunk {i+1} failed — {e}")
                continue

        if not all_parts:
            raise ValueError("Transcription failed for all audio chunks.")

        return "\n".join(all_parts)


# ── Document parsing (unchanged) ──────────────────────────────────────────────

def _parse_pdf(file_path: str) -> str:
    """PDF → text via PyPDF2"""
    try:
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        if not text.strip():
            raise ValueError("PDF appears to be empty or is a scanned image — no text could be extracted.")
        return text.strip()
    except PyPDF2.errors.PdfReadError:
        raise ValueError("Could not read PDF — file may be corrupted or password-protected.")


def _parse_docx(file_path: str) -> str:
    """Word doc → text via python-docx"""
    try:
        doc = docx.Document(file_path)
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        if not text.strip():
            raise ValueError("Word document appears to be empty.")
        return text.strip()
    except Exception as e:
        raise ValueError(f"Could not read Word document: {str(e)}")


def _parse_txt(file_path: str) -> str:
    """Plain text file → text"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read().strip()
        if not text:
            raise ValueError("Text file is empty.")
        return text
    except UnicodeDecodeError:
        raise ValueError("Could not read text file — try saving it as UTF-8.")