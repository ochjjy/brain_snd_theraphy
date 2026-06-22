#!/usr/bin/env python3
"""
Generate 5-minute AM WAV files for browser playback.

The generated files use a soft audible carrier and a sine-shaped amplitude
envelope at the target stimulation frequency. Brainwave targets change the
modulation rate, while resonance presets change the audible carrier. The
modulation depth stays below 100% so the sound feels less buzzy while
preserving the target rhythm.
"""

from __future__ import annotations

import math
import wave
from array import array
from pathlib import Path


SAMPLE_RATE = 44_100
DURATION_SECONDS = 5 * 60
DEFAULT_CARRIER_FREQ = 220.0
DEFAULT_RESONANCE_MOD_FREQ = 8.0
MODULATION_DEPTH = 0.45
PEAK_AMPLITUDE = 0.50
BITS_PER_SAMPLE = 16
CHANNELS = 1
CHUNK_SECONDS = 1

OUTPUT_DIR = Path("wave")

TARGETS = (
    ("gamma_40hz_5m.wav", 40.0, DEFAULT_CARRIER_FREQ),
    ("alpha_theta_8hz_5m.wav", 8.0, DEFAULT_CARRIER_FREQ),
    ("delta_2hz_5m.wav", 2.0, DEFAULT_CARRIER_FREQ),
    ("low_alpha_9_5hz_5m.wav", 9.5, DEFAULT_CARRIER_FREQ),
    ("smr_13_5hz_5m.wav", 13.5, DEFAULT_CARRIER_FREQ),
    ("schumann_7_83hz_5m.wav", 7.83, DEFAULT_CARRIER_FREQ),
    ("solfeggio_396hz_5m.wav", DEFAULT_RESONANCE_MOD_FREQ, 396.0),
    ("natural_432hz_5m.wav", DEFAULT_RESONANCE_MOD_FREQ, 432.0),
    ("healing_528hz_5m.wav", DEFAULT_RESONANCE_MOD_FREQ, 528.0),
)


def is_integer_cycle(freq: float) -> bool:
    """Return whether a frequency completes whole cycles in one segment."""
    cycles = freq * DURATION_SECONDS
    return math.isclose(cycles, round(cycles), abs_tol=1e-9)


def validate_target_alignment(filename: str, mod_freq: float, carrier_freq: float) -> None:
    """Reject targets that would click or drift when 5-minute files are joined."""
    if not is_integer_cycle(mod_freq):
        raise ValueError(f"{filename}: {mod_freq:g}Hz modulation does not align")

    if not is_integer_cycle(carrier_freq):
        raise ValueError(f"{filename}: {carrier_freq:g}Hz carrier does not align")


def generate_am_wav(path: Path, mod_freq: float, carrier_freq: float) -> None:
    """Generate a seamless-loop 16-bit mono PCM WAV file."""
    total_frames = SAMPLE_RATE * DURATION_SECONDS
    chunk_frames = SAMPLE_RATE * CHUNK_SECONDS
    carrier_step = 2 * math.pi * carrier_freq / SAMPLE_RATE
    mod_step = 2 * math.pi * mod_freq / SAMPLE_RATE
    carrier_phase = 0.0
    mod_phase = 0.0
    max_int16 = (2 ** (BITS_PER_SAMPLE - 1)) - 1

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(BITS_PER_SAMPLE // 8)
        wav_file.setframerate(SAMPLE_RATE)

        frames_written = 0
        while frames_written < total_frames:
            frames_this_chunk = min(chunk_frames, total_frames - frames_written)
            samples = array("h")

            for _ in range(frames_this_chunk):
                carrier = math.sin(carrier_phase)
                mod_shape = 0.5 * (1 - math.cos(mod_phase))
                envelope = (1 - MODULATION_DEPTH) + (MODULATION_DEPTH * mod_shape)
                sample = carrier * envelope * PEAK_AMPLITUDE
                samples.append(round(sample * max_int16))

                carrier_phase += carrier_step
                mod_phase += mod_step

                if carrier_phase >= 2 * math.pi:
                    carrier_phase -= 2 * math.pi

                if mod_phase >= 2 * math.pi:
                    mod_phase -= 2 * math.pi

            wav_file.writeframes(samples.tobytes())
            frames_written += frames_this_chunk


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    for filename, mod_freq, carrier_freq in TARGETS:
        validate_target_alignment(filename, mod_freq, carrier_freq)
        path = OUTPUT_DIR / filename
        print(
            f"Generating {path} "
            f"({mod_freq:g}Hz modulation, {carrier_freq:g}Hz carrier)..."
        )
        generate_am_wav(path, mod_freq, carrier_freq)

    print("Done.")


if __name__ == "__main__":
    main()
