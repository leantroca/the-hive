from sounddevice import OutputStream
import numpy as np
from piper import PiperVoice, SynthesisConfig
from strands import tool

DEFAULT_ONNX = "tools/piper_resources/en_US-lessac-medium.onnx"


@tool
def piper_speak(text: str, model_path: str = DEFAULT_ONNX) -> str:
    """
    Converts text to speech and plays it aloud through the system's audio output in real-time.

    Uses the Piper neural text-to-speech engine to synthesize natural-sounding speech
    from the provided text. Audio is streamed and played immediately as it's generated,
    providing low-latency playback suitable for interactive applications.

    Args:
        text: The text content to be spoken aloud. Can be any length, from single words
              to long paragraphs. Supports standard punctuation for natural phrasing.
        model_path: Path to the Piper ONNX voice model file (.onnx). Defaults to
                    'voice/en_US-lessac-medium.onnx'. Different models provide different
                    voices and languages.

    Returns:
        str: A confirmation message indicating successful playback, an interruption message
             if stopped by user (Ctrl+C), or an error message if the operation failed.
             Blocks until speech playback completes or is interrupted.

    Example:
        piper_speak("Hello, this is a test of the text to speech system.")
        piper_speak("Bonjour!", model_path="voice/fr_FR-siwis-medium.onnx")
    """
    stream = None

    try:
        voice = PiperVoice.load(
            model_path,
            use_cuda=False,
        )

        # Stream audio chunks from Piper
        for chunk in voice.synthesize(text):
            # Initialize stream on first chunk
            if stream is None:
                stream = OutputStream(
                    samplerate=chunk.sample_rate,
                    channels=chunk.sample_channels,
                    dtype=np.int16
                )
                stream.start()

            # Convert bytes to numpy array and write to stream
            audio_data = np.frombuffer(chunk.audio_int16_bytes, dtype=np.int16)

            # Reshape for stereo if needed
            if chunk.sample_channels == 2:
                audio_data = audio_data.reshape(-1, 2)

            stream.write(audio_data)

        # Clean up
        if stream:
            stream.stop()
            stream.close()

        return f"Successfully spoke: {text[:100]}{'...' if len(text) > 100 else ''}"

    except KeyboardInterrupt:
        # Handle user interruption (Ctrl+C)
        if stream:
            stream.abort()  # Immediately stop playback
            stream.close()
        return "Speech interrupted by user"

    except Exception as e:
        # Handle other errors
        if stream:
            stream.stop()
            stream.close()
        return f"Error speaking text: {str(e)}"


####################################################################################################################
#"""Agent tools to download and manage Piper voice models from Hugging Face."""
# import json
# import hashlib
# from pathlib import Path
# from urllib.request import urlopen, Request
# from strands import tool


# VOICES_JSON_URL = "https://huggingface.co/rhasspy/piper-voices/raw/main/voices.json"
# HF_BASE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main"
# DEFAULT_OUTPUT_DIR = "voice"

# # Language code mappings for common language names
# LANGUAGE_MAP = {
#     "english": "en_US",
#     "spanish": "es_ES",
#     "french": "fr_FR",
#     "german": "de_DE",
#     "italian": "it_IT",
#     "portuguese": "pt_BR",
#     "russian": "ru_RU",
#     "chinese": "zh_CN",
#     "japanese": "ja_JP",
#     "korean": "ko_KR",
#     "arabic": "ar_JO",
#     "hindi": "hi_IN",
# }


# def _fetch_voices_list() -> dict:
#     """Internal helper to fetch the list of available voices."""
#     with urlopen(VOICES_JSON_URL) as response:
#         return json.loads(response.read().decode())


# def _verify_md5(file_path: Path, expected_md5: str) -> bool:
#     """Internal helper to verify MD5 checksum."""
#     md5_hash = hashlib.md5()
#     with open(file_path, "rb") as f:
#         for chunk in iter(lambda: f.read(4096), b""):
#             md5_hash.update(chunk)
#     return md5_hash.hexdigest() == expected_md5


# def _get_best_voice(language_code: str, quality: str = "medium") -> str:
#     """Internal helper to find the best voice for a language."""
#     voices = _fetch_voices_list()

#     # Find voices matching language and quality
#     matches = []
#     for key, info in voices.items():
#         if info['language']['code'].startswith(language_code[:2]) and info['quality'] == quality:
#             matches.append(key)

#     if not matches:
#         # Fallback to any quality
#         for key, info in voices.items():
#             if info['language']['code'].startswith(language_code[:2]):
#                 matches.append(key)

#     return matches[0] if matches else None


# @tool
# def list_piper_voices(language: str = "", quality: str = "") -> str:
#     """
#     Lists all available Piper text-to-speech voice models with optional filtering.

#     Fetches the complete catalog of voice models from the Piper repository,
#     displaying information about each voice including language, quality level,
#     number of speakers, and file size. Results can be filtered by language
#     code or quality level.

#     Args:
#         language: Optional language code filter (e.g., "en_US", "fr_FR", "es_ES").
#                   Use just the language part (e.g., "en") to see all English voices.
#                   Leave empty to show all languages.
#         quality: Optional quality level filter. Valid values are "x_low", "low",
#                  "medium", or "high". Leave empty to show all quality levels.

#     Returns:
#         str: A formatted table showing available voices with their details including
#              voice key, language, quality, speaker count, and size in MB.

#     Example:
#         list_piper_voices()  # Show all voices
#         list_piper_voices(language="en_US")  # Show only US English voices
#         list_piper_voices(quality="medium")  # Show only medium quality voices
#         list_piper_voices(language="fr", quality="high")  # French high-quality voices
#     """
#     try:
#         voices = _fetch_voices_list()

#         output_lines = []
#         output_lines.append(f"\n{'Key':<30} {'Language':<15} {'Quality':<10} {'Speakers':<10} {'Size (MB)':<12}")
#         output_lines.append("-" * 85)

#         count = 0
#         for key, info in sorted(voices.items()):
#             # Apply filters
#             if language and not info['language']['code'].startswith(language):
#                 continue
#             if quality and info['quality'] != quality:
#                 continue

#             # Get size of main .onnx file
#             onnx_files = [f for f in info['files'].keys() if f.endswith('.onnx')]
#             size_mb = info['files'][onnx_files[0]]['size_bytes'] / (1024 * 1024) if onnx_files else 0

#             # Get speaker info
#             speakers = info['num_speakers']
#             speaker_info = f"{speakers} speaker{'s' if speakers > 1 else ''}"

#             output_lines.append(
#                 f"{key:<30} {info['language']['code']:<15} {info['quality']:<10} {speaker_info:<10} {size_mb:>10.1f} MB"
#             )
#             count += 1

#         output_lines.append(f"\nTotal: {count} voice(s) found")

#         if count == 0:
#             return f"No voices found matching filters (language='{language}', quality='{quality}')"

#         return "\n".join(output_lines)

#     except Exception as e:
#         return f"Error fetching voice list: {str(e)}"


# @tool
# def download_piper_voice(voice_key: str, output_dir: str = "voice") -> str:
#     """
#     Downloads a specific Piper voice model from Hugging Face to local storage.

#     Fetches the voice model files (.onnx neural network and .json config) from
#     the Piper voices repository, verifies file integrity using MD5 checksums,
#     and saves them to the specified directory for use with text-to-speech synthesis.

#     Args:
#         voice_key: Unique identifier for the voice model to download. Format is
#                    typically "language_REGION-name-quality" (e.g., "en_US-lessac-medium",
#                    "fr_FR-siwis-high"). Use list_piper_voices() to see available keys.
#         output_dir: Directory path where voice files will be saved. Defaults to "voice".
#                     Directory will be created if it doesn't exist.

#     Returns:
#         str: Status message indicating success with usage instructions, or error details
#              if the download failed. Includes file verification results and the path
#              to use in piper_speak() calls.

#     Example:
#         download_piper_voice("en_US-lessac-medium")
#         download_piper_voice("fr_FR-siwis-high", output_dir="voices/french")
#         download_piper_voice("es_ES-davefx-medium", output_dir="voice")
#     """
#     try:
#         # Fetch voice metadata
#         voices = _fetch_voices_list()

#         if voice_key not in voices:
#             available = ', '.join(sorted(voices.keys())[:10])
#             return (
#                 f"Error: Voice '{voice_key}' not found.\n"
#                 f"Use list_piper_voices() to see all available voices.\n"
#                 f"First 10 available: {available}..."
#             )

#         voice_info = voices[voice_key]
#         output_path = Path(output_dir)
#         output_path.mkdir(parents=True, exist_ok=True)

#         output_lines = []
#         output_lines.append(f"Downloading voice: {voice_key}")
#         output_lines.append(f"Language: {voice_info['language']['name_english']} ({voice_info['language']['code']})")
#         output_lines.append(f"Quality: {voice_info['quality']}")
#         output_lines.append(f"Speakers: {voice_info['num_speakers']}")

#         # Download all files for this voice
#         success = True
#         for file_path, file_info in voice_info['files'].items():
#             filename = Path(file_path).name
#             output_file = output_path / filename
#             file_url = f"{HF_BASE_URL}/{file_path}"
#             size_mb = file_info['size_bytes'] / (1024 * 1024)

#             output_lines.append(f"\nDownloading {filename} ({size_mb:.1f} MB)...")

#             try:
#                 # Download file
#                 req = Request(file_url, headers={'User-Agent': 'Mozilla/5.0'})
#                 with urlopen(req) as response:
#                     with open(output_file, 'wb') as f:
#                         downloaded = 0
#                         chunk_size = 8192
#                         total_size = file_info['size_bytes']
#                         while True:
#                             chunk = response.read(chunk_size)
#                             if not chunk:
#                                 break
#                             f.write(chunk)
#                             downloaded += len(chunk)
#                             # Progress every 10%
#                             progress = int(downloaded / total_size * 10)
#                             if downloaded % (total_size // 10) < chunk_size:
#                                 output_lines.append(f"  {progress * 10}% complete...")

#                 # Verify checksum
#                 if 'md5_digest' in file_info:
#                     if _verify_md5(output_file, file_info['md5_digest']):
#                         output_lines.append(f"✓ {filename} verified successfully")
#                     else:
#                         output_lines.append(f"✗ Checksum mismatch for {filename}")
#                         success = False
#                 else:
#                     output_lines.append(f"✓ {filename} downloaded (no checksum available)")

#             except Exception as e:
#                 output_lines.append(f"✗ Failed to download {filename}: {e}")
#                 success = False

#         if success:
#             onnx_file = output_path / f"{voice_key}.onnx"
#             output_lines.append(f"\n✓ Voice '{voice_key}' downloaded successfully!")
#             output_lines.append(f"\nUsage:")
#             output_lines.append(f'  piper_speak("Hello world", model_path="{onnx_file}")')
#         else:
#             output_lines.append(f"\n✗ Some files failed to download")

#         return "\n".join(output_lines)

#     except Exception as e:
#         return f"Error downloading voice: {str(e)}"


# @tool
# def get_voice_info(voice_key: str) -> str:
#     """
#     Retrieves detailed information about a specific Piper voice model.

#     Fetches and displays comprehensive metadata for a voice including language details,
#     quality level, speaker information, file sizes, and available speaker names for
#     multi-speaker models.

#     Args:
#         voice_key: Unique identifier for the voice model (e.g., "en_US-lessac-medium").
#                    Use list_piper_voices() to discover available voice keys.

#     Returns:
#         str: Detailed information about the voice model including language, quality,
#              speakers, file details, and speaker IDs if applicable. Returns error
#              message if voice key is not found.

#     Example:
#         get_voice_info("en_US-lessac-medium")
#         get_voice_info("cy_GB-bu_tts-medium")  # Multi-speaker voice
#     """
#     try:
#         voices = _fetch_voices_list()

#         if voice_key not in voices:
#             return f"Error: Voice '{voice_key}' not found. Use list_piper_voices() to see available voices."

#         voice_info = voices[voice_key]
#         output_lines = []

#         output_lines.append(f"Voice: {voice_key}")
#         output_lines.append(f"Name: {voice_info['name']}")
#         output_lines.append(f"\nLanguage:")
#         output_lines.append(f"  Code: {voice_info['language']['code']}")
#         output_lines.append(f"  Family: {voice_info['language']['family']}")
#         output_lines.append(f"  Region: {voice_info['language']['region']}")
#         output_lines.append(f"  Native: {voice_info['language']['name_native']}")
#         output_lines.append(f"  English: {voice_info['language']['name_english']}")
#         output_lines.append(f"  Country: {voice_info['language']['country_english']}")

#         output_lines.append(f"\nQuality: {voice_info['quality']}")
#         output_lines.append(f"Number of Speakers: {voice_info['num_speakers']}")

#         if voice_info['speaker_id_map']:
#             output_lines.append(f"\nAvailable Speakers:")
#             for speaker_name, speaker_id in voice_info['speaker_id_map'].items():
#                 output_lines.append(f"  {speaker_id}: {speaker_name}")

#         output_lines.append(f"\nFiles:")
#         for file_path, file_info in voice_info['files'].items():
#             size_mb = file_info['size_bytes'] / (1024 * 1024)
#             output_lines.append(f"  {Path(file_path).name}: {size_mb:.1f} MB")

#         if voice_info.get('aliases'):
#             output_lines.append(f"\nAliases: {', '.join(voice_info['aliases'])}")

#         return "\n".join(output_lines)

#     except Exception as e:
#         return f"Error fetching voice info: {str(e)}"


# @tool
# def find_voice_for_language(language: str, quality: str = "medium") -> str:
#     """
#     Finds the best available Piper voice model for a given language.

#     Searches the voice catalog to identify a suitable voice model based on language
#     name or code. This tool helps the agent automatically select an appropriate voice
#     without needing to browse the full catalog.

#     Args:
#         language: Language name (e.g., "english", "spanish", "french") or language code
#                   (e.g., "en_US", "es_ES", "fr_FR"). Case-insensitive.
#         quality: Preferred quality level ("x_low", "low", "medium", "high").
#                  Defaults to "medium". Will fallback to other qualities if preferred
#                  quality is not available for the language.

#     Returns:
#         str: The voice key for the best matching voice model, along with basic info.
#              If no match is found, returns an error message with suggestions.

#     Example:
#         find_voice_for_language("english")
#         find_voice_for_language("french", quality="high")
#         find_voice_for_language("es_ES")
#     """
#     try:
#         language_lower = language.lower()

#         # Map common language names to codes
#         language_code = LANGUAGE_MAP.get(language_lower, language)

#         # Find best voice
#         voice_key = _get_best_voice(language_code, quality)

#         if not voice_key:
#             return f"No voice found for language '{language}'. Use list_piper_voices() to see available languages."

#         voices = _fetch_voices_list()
#         voice_info = voices[voice_key]

#         size_mb = 0
#         onnx_files = [f for f in voice_info['files'].keys() if f.endswith('.onnx')]
#         if onnx_files:
#             size_mb = voice_info['files'][onnx_files[0]]['size_bytes'] / (1024 * 1024)

#         return (
#             f"Best match for '{language}':\n"
#             f"Voice Key: {voice_key}\n"
#             f"Language: {voice_info['language']['name_english']} ({voice_info['language']['code']})\n"
#             f"Quality: {voice_info['quality']}\n"
#             f"Size: {size_mb:.1f} MB\n"
#             f"\nTo download: download_piper_voice('{voice_key}')"
#         )

#     except Exception as e:
#         return f"Error finding voice: {str(e)}"


# @tool
# def auto_setup_voice(language: str, quality: str = "medium") -> str:
#     """
#     Automatically finds, downloads, and sets up a voice model for the specified language.

#     This is a convenience tool that combines finding and downloading in one step.
#     Use this when you need to quickly set up a voice for a specific language without
#     manually browsing and selecting from the catalog.

#     Args:
#         language: Language name (e.g., "english", "french") or code (e.g., "en_US").
#         quality: Preferred quality level ("x_low", "low", "medium", "high").
#                  Defaults to "medium".

#     Returns:
#         str: Status message with the path to the downloaded voice model file, ready
#              to use with piper_speak(). Returns error if language not found or download fails.

#     Example:
#         auto_setup_voice("english")
#         auto_setup_voice("french", quality="high")
#     """
#     try:
#         language_lower = language.lower()
#         language_code = LANGUAGE_MAP.get(language_lower, language)

#         # Check if voice already exists
#         voice_key = _get_best_voice(language_code, quality)
#         if not voice_key:
#             return f"No voice available for language '{language}'."

#         output_path = Path(DEFAULT_OUTPUT_DIR)
#         onnx_file = output_path / f"{voice_key}.onnx"

#         # Check if already downloaded
#         if onnx_file.exists():
#             return f"Voice already available: {voice_key}\nModel path: {onnx_file}"

#         # Download the voice
#         voices = _fetch_voices_list()
#         voice_info = voices[voice_key]
#         output_path.mkdir(parents=True, exist_ok=True)

#         # Download files silently
#         for file_path, file_info in voice_info['files'].items():
#             filename = Path(file_path).name
#             output_file = output_path / filename
#             file_url = f"{HF_BASE_URL}/{file_path}"

#             req = Request(file_url, headers={'User-Agent': 'Mozilla/5.0'})
#             with urlopen(req) as response:
#                 with open(output_file, 'wb') as f:
#                     f.write(response.read())

#             # Verify if MD5 available
#             if 'md5_digest' in file_info:
#                 if not _verify_md5(output_file, file_info['md5_digest']):
#                     return f"Download verification failed for {filename}"

#         return (
#             f"✓ Voice '{voice_key}' ready for use\n"
#             f"Language: {voice_info['language']['name_english']}\n"
#             f"Model path: {onnx_file}"
#         )

#     except Exception as e:
#         return f"Error setting up voice: {str(e)}"


# @tool
# def get_downloaded_voices() -> str:
#     """
#     Lists all Piper voice models that have been downloaded locally.

#     Scans the local voice directory to find all .onnx model files that are ready
#     to use with piper_speak(). This helps the agent know which voices are already
#     available without needing to download them again.

#     Returns:
#         str: List of downloaded voices with their file paths, or a message indicating
#              no voices have been downloaded yet.

#     Example:
#         get_downloaded_voices()
#     """
#     try:
#         output_path = Path(DEFAULT_OUTPUT_DIR)

#         if not output_path.exists():
#             return f"No voices downloaded yet. Use auto_setup_voice() to download a voice."

#         onnx_files = list(output_path.glob("*.onnx"))

#         if not onnx_files:
#             return f"No voices found in {output_path}/. Use auto_setup_voice() to download a voice."

#         output_lines = ["Downloaded voices:"]
#         for onnx_file in sorted(onnx_files):
#             voice_key = onnx_file.stem
#             size_mb = onnx_file.stat().st_size / (1024 * 1024)
#             output_lines.append(f"  {voice_key} ({size_mb:.1f} MB) - Path: {onnx_file}")

#         output_lines.append(f"\nTotal: {len(onnx_files)} voice(s) available locally")
#         return "\n".join(output_lines)

#     except Exception as e:
#         return f"Error listing downloaded voices: {str(e)}"
