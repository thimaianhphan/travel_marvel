from typing import List, Dict, Tuple
from faster_whisper import WhisperModel, BatchedInferencePipeline
from tqdm import tqdm
import os

# Keep CPU usage modest
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

_MODEL: WhisperModel | None = None
_PIPELINE: BatchedInferencePipeline | None = None
GPU: bool | None = None

MAX_WORKERS = max(1, os.cpu_count() or 4)
try:
    if "ASR_MAX_WORKERS" in os.environ:
        MAX_WORKERS = max(1, int(os.environ["ASR_MAX_WORKERS"]))
except ValueError:
    pass


def _ensure_pipeline(model_size: str = "small.en") -> BatchedInferencePipeline:
    """Lazy-init a single pipeline (GPU first, CPU fallback)."""
    global _PIPELINE, GPU
    if _PIPELINE is not None:
        return _PIPELINE

    try:
        print(f"[faster-whisper] init device=cuda, compute_type=float16, model={model_size}")
        model = WhisperModel(model_size, device="cuda", compute_type="float16")
        GPU = True
    except Exception as e:
        print(f"[faster-whisper] CUDA not available ({e}); falling back to CPU")
        GPU = False
        print(f"[faster-whisper] init device=cpu, compute_type=int8, cpu_threads={MAX_WORKERS}, model={model_size}")
        model = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=MAX_WORKERS)

    _PIPELINE = BatchedInferencePipeline(model=model)
    print(f"[faster-whisper] Batched pipeline ready (runtime={'GPU' if GPU else 'CPU'})")
    return _PIPELINE


def transcribe_to_segments(
    audio_path: str,
    model_size: str,
    chunk_length: int,
    show_progress: bool = True,
) -> Tuple[List[Dict], Dict]:
    """
    Returns (segments_list, info_dict)

    segments_list is a SINGLE item:
      [{"start": float, "end": float, "text": "<full transcript>"}]

    We let Whisper produce its usual segments (efficient) and then merge
    into one full-text transcript — ideal for ~1 minute YouTube Shorts.
    """
    pipe = _ensure_pipeline(model_size)

    # Small batch is fine for Shorts; keep CPU very light
    if GPU:
        batch_size = min(4, MAX_WORKERS)
    else:
        batch_size = 1

    pbar = None
    if show_progress:
        pbar = tqdm(desc="Transcribing", unit="seg", dynamic_ncols=True)

    # Keep settings simple & fast
    common = dict(
        language="en",
        beam_size=1,
        best_of=1,
        word_timestamps=False,
        vad_filter=True,
        vad_parameters=dict(
            min_silence_duration_ms=600,
            min_speech_duration_ms=250,
            speech_pad_ms=100,
        ),
        # We still pass chunk_length (no extra cost) but we merge afterward.
        chunk_length=chunk_length,
        condition_on_previous_text=False,
        temperature=0.0,
        no_speech_threshold=0.45,
        log_prob_threshold=-1.0,
        compression_ratio_threshold=2.4,
        hallucination_silence_threshold=0.5,
    )

    segments, info = pipe.transcribe(audio_path, batch_size=batch_size, **common)

    # ---- Merge to full text (single record) ----
    texts: List[str] = []
    first_start: float | None = None
    last_end: float | None = None

    for s in segments:
        if pbar is not None:
            pbar.update(1)
            pbar.set_postfix({"time": f"{s.end:.1f}s"})
        if first_start is None:
            first_start = float(s.start)
        last_end = float(s.end)
        t = (s.text or "").strip()
        if t:
            texts.append(t)

    if pbar is not None:
        pbar.close()

    full_text = " ".join(texts).strip()
    # Robust defaults if timing missing
    if first_start is None:
        first_start = 0.0
    if last_end is None:
        last_end = float(info.duration) if getattr(info, "duration", None) else 0.0

    out_segments: List[Dict] = [{
        "start": float(first_start),
        "end": float(last_end),
        "text": full_text,
    }]

    info_dict = {
        "duration": float(info.duration) if getattr(info, "duration", None) else None,
        "language": getattr(info, "language", None),
        "language_probability": float(info.language_probability) if getattr(info, "language_probability", None) else None,
        "model_size": model_size,
        "gpu": bool(GPU),
        "max_workers": MAX_WORKERS,
        "batch_size": batch_size,
        "chunk_length": chunk_length,
    }
    return out_segments, info_dict
