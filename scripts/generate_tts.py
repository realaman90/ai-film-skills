"""Generate text-to-speech audio using ElevenLabs.

Usage:
    # Basic narration
    python scripts/generate_tts.py --text "Hello world" --output hello.mp3

    # With specific voice
    python scripts/generate_tts.py --text "..." --voice onwK4e9ZLuTAKqWW03F9 --output narration.mp3

    # Dramatic style with slow speed
    python scripts/generate_tts.py --text "..." --output vo.mp3 --stability 0.3 --style 0.15 --speed 0.9

    # From a text file
    python scripts/generate_tts.py --file script.txt --output narration.mp3

    # With timestamps for subtitles
    python scripts/generate_tts.py --text "..." --output vo.mp3 --timestamps timestamps.json
"""
import os, sys, json, argparse, requests

def main():
    parser = argparse.ArgumentParser(description="Generate TTS with ElevenLabs")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Text to speak")
    group.add_argument("--file", help="Read text from file")
    parser.add_argument("--output", required=True, help="Output audio file (.mp3)")
    parser.add_argument("--voice", default=None, help="Voice ID (default: $ELEVENLABS_VOICE)")
    parser.add_argument("--model", default="eleven_v3", help="TTS model (default: eleven_v3)")
    parser.add_argument("--stability", type=float, default=0.50, help="Stability 0-1 (default: 0.50)")
    parser.add_argument("--similarity", type=float, default=0.75, help="Similarity boost 0-1 (default: 0.75)")
    parser.add_argument("--style", type=float, default=0.0, help="Style exaggeration 0-1 (default: 0.0)")
    parser.add_argument("--speed", type=float, default=1.0, help="Speech speed 0.7-1.2 (default: 1.0)")
    parser.add_argument("--format", default="mp3_44100_192", help="Output format")
    parser.add_argument("--timestamps", default=None, help="Save word timestamps to JSON file")
    parser.add_argument("--skip-existing", action="store_true", help="Skip if output exists")
    args = parser.parse_args()

    if args.skip_existing and os.path.exists(args.output):
        print(f"SKIP {args.output} (exists)")
        return

    text = args.text if args.text else open(args.file).read()
    voice_id = args.voice or os.environ.get("ELEVENLABS_VOICE", "onwK4e9ZLuTAKqWW03F9")
    api_key = os.environ["ELEVENLABS_KEY"]

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "text": text,
        "model_id": args.model,
        "voice_settings": {
            "stability": args.stability,
            "similarity_boost": args.similarity,
            "style": args.style,
            "speed": args.speed,
        },
    }

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    # With or without timestamps
    if args.timestamps:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
        print(f"Generating TTS with timestamps...")
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            # Save audio
            import base64
            audio_bytes = base64.b64decode(data.get("audio_base64") or data.get("audio_base_64") or (_ for _ in ()).throw(KeyError(f"no audio in response: {list(data.keys())} {str(data)[:300]}")))
            with open(args.output, "wb") as f:
                f.write(audio_bytes)
            # Save timestamps
            with open(args.timestamps, "w") as f:
                json.dump(data["alignment"], f, indent=2)
            print(f"SAVED {args.output} ({len(audio_bytes)/1024:.0f}KB)")
            print(f"SAVED {args.timestamps}")
        else:
            print(f"ERROR {response.status_code}: {response.text[:200]}")
            sys.exit(1)
    else:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format={args.format}"
        print(f"Generating TTS...")
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            with open(args.output, "wb") as f:
                f.write(response.content)
            print(f"SAVED {args.output} ({len(response.content)/1024:.0f}KB)")
        else:
            print(f"ERROR {response.status_code}: {response.text[:200]}")
            sys.exit(1)

if __name__ == "__main__":
    main()
