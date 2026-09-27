# ElevenLabs -- Complete Audio Production Guide

## Voice Selection

### List Voices API

```bash
# All premade voices
curl -X GET "https://api.elevenlabs.io/v2/voices?category=premade&page_size=50" \
  -H "xi-api-key: $ELEVENLABS_KEY"

# Search by keyword
curl -X GET "https://api.elevenlabs.io/v2/voices?search=british+male&category=premade" \
  -H "xi-api-key: $ELEVENLABS_KEY"

# Filter by category: premade, cloned, generated, professional
# Filter by type: personal, community, default, workspace
# Sort: created_at_unix or name, asc or desc
```

### Python Voice Listing

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(api_key=os.environ["ELEVENLABS_KEY"])

voices = client.voices.search(
    search="narrator",
    category="premade",
    page_size=50,
    sort="name",
    sort_direction="asc"
)

for voice in voices.voices:
    print(f"{voice.name:15} {voice.voice_id:25} {voice.labels}")
```

### Find Similar Voices (by audio)

```bash
curl -X POST "https://api.elevenlabs.io/v1/similar-voices" \
  -H "xi-api-key: $ELEVENLABS_KEY" \
  -F "audio_file=@reference_voice.mp3" \
  -F "similarity_threshold=0.5" \
  -F "top_k=10"
```

### Preview a Voice

```bash
# Quick test any voice (2 free regenerations of identical text)
curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM?output_format=mp3_44100_128" \
  -H "xi-api-key: $ELEVENLABS_KEY" -H "Content-Type: application/json" \
  -d '{"text": "Hello! This is a preview of how this voice sounds.", "model_id": "eleven_multilingual_v2"}' \
  --output preview.mp3
```

---

## Complete Premade Voice IDs

| Name | Voice ID | Gender | Age | Accent | Style |
|------|----------|--------|-----|--------|-------|
| Rachel | `21m00Tcm4TlvDq8ikWAM` | F | Young | American | Calm |
| Adam | `pNInz6obpgDQGcFmaJgB` | M | Mid | American | Deep |
| Alice | `Xb7hH8MSUJpSbSDYk0k2` | F | Mid | British | Confident |
| Antoni | `ErXwobaYiN019PkySvjV` | M | Young | American | Well-rounded |
| Arnold | `VR6AewLTigWG4xSOukaG` | M | Mid | American | Crisp |
| Bill | `pqHfZKP75CvOlQylNhV4` | M | Mid | American | Strong |
| Brian | `nPczCjzI2devNBz1zQrb` | M | Mid | American | Deep |
| Callum | `N2lVS1w4EtoT3dr4eOWO` | M | Mid | American | Hoarse |
| Charlie | `IKne3meq5aSn9XLyUdCD` | M | Mid | Australian | Casual |
| Charlotte | `XB0fDUnXU5powFXDhCwa` | F | Mid | Eng-Swedish | Seductive |
| Chris | `iP95p4xoKVk53GoZ742B` | M | Mid | American | Casual |
| Clyde | `2EiwWnXFnvU5JabPnv8n` | M | Mid | American | War veteran |
| Daniel | `onwK4e9ZLuTAKqWW03F9` | M | Mid | British | Deep |
| Dave | `CYw3kZ02Hs0563khs1Fj` | M | Young | British-Essex | Conversational |
| Domi | `AZnzlk1XvdvUeBnXmlld` | F | Young | American | Strong |
| Dorothy | `ThT5KcBeYPX3keUQqHPh` | F | Young | British | Pleasant |
| Drew | `29vD33N1CtxCmqQRPOHJ` | M | Mid | American | Well-rounded |
| Emily | `LcfcDJNUP1GQjkzn1xUU` | F | Young | American | Calm |
| Fin | `D38z5RcWu1voky8WS1ja` | M | Old | Irish | Sailor |
| Freya | `jsCqWAovK2LkecY7zXl4` | F | Young | American | -- |
| George | `JBFqnCBsd6RMkjVDRZzb` | M | Mid | British | Raspy |
| Gigi | `jBpfuIE2acCO8z3wKNLl` | F | Young | American | Childish |
| Giovanni | `zcAOhNBS3c14rBihAFp1` | M | Young | Eng-Italian | Foreigner |
| Glinda | `z9fAnlkpzviPz146aGWa` | F | Mid | American | Witch |
| Grace | `oWAxZDx7w5VEj9dCyTzz` | F | Young | American-Southern | -- |
| Harry | `SOYHLrjzK2X1ezoPC6cr` | M | Young | American | Anxious |
| James | `ZQe5CZNOzWyzPSCn5a3c` | M | Old | Australian | Calm |
| Jeremy | `bVMeCyTHy58xNoL34h3p` | M | Young | American-Irish | Excited |
| Jessie | `t0jbNlBVZ17f02VDIeMI` | M | Old | American | Raspy |
| Joseph | `Zlb1dXrM653N07WRdFW3` | M | Mid | British | -- |
| Josh | `TxGEqnHWrfWFTfGW9XjX` | M | Young | American | Deep |
| Liam | `TX3LPaxmHKxFdv7VOQHJ` | M | Young | American | -- |
| Lily | `pFZP5JQG7iQjIQuC4Bku` | F | Mid | British | Raspy |
| Matilda | `XrExE9yKIg1WjnnlVkGX` | F | Young | American | Warm |
| Michael | `flq6f7yk4E4fJM5XTYuZ` | M | Old | American | -- |
| Mimi | `zrHiDhphv9ZnVXBqCLjz` | F | Young | Eng-Swedish | Childish |
| Nicole | `piTKgcLEGmPE4e6mEKli` | F | Young | American | Whisper |
| Patrick | `ODq5zmih8GrVes37Dizd` | M | Mid | American | Shouty |
| Paul | `5Q0t7uMcjvnagumLfvZi` | M | Mid | American | Ground reporter |
| Sam | `yoZ06aMxZJJ28mfd3POQ` | M | Young | American | Raspy |
| Sarah | `EXAVITQu4vr4xnSDxMaL` | F | Young | American | Soft |
| Serena | `pMsXgVXv3BLzUgSXRplE` | F | Mid | American | Pleasant |
| Thomas | `GBv7mTt0atIp3Br8iCZE` | M | Young | American | Calm |

### Voices by Use Case

| Use Case | Best Voices |
|----------|-------------|
| Narration / Audiobook | Rachel, Daniel, Matilda, Sarah |
| Conversational / Chatbot | Brian, Charlotte, Dave, Chris |
| Deep Male Narrator | Adam, Brian, Josh, Daniel |
| Calm Female | Rachel, Emily, Sarah |
| British Accent | Alice, Daniel, Dorothy, George, Lily |
| Character / Acting | Clyde, Fin, Glinda, Giovanni, Gigi |
| News / Reporter | Paul, Bill, Arnold |
| Whisper / ASMR | Nicole |

---

## Voice Settings

| Setting | Range | Default | What it does |
|---------|-------|---------|-------------|
| `stability` | 0-1 | 0.5 | Low = expressive/variable. High = consistent/monotone |
| `similarity_boost` | 0-1 | 0.75 | How close to original voice. >0.9 may cause artifacts |
| `style` | 0-1 | 0.0 | Exaggerates voice character. Keep 0 unless needed (adds latency) |
| `speed` | 0.7-1.2 | 1.0 | Speech rate. Natural: 0.9-1.1 |
| `use_speaker_boost` | bool | true | Enhanced similarity processing |

### Presets by Use Case

| Use Case | Stability | Similarity | Style | Speed |
|----------|-----------|------------|-------|-------|
| Audiobook | 0.50 | 0.75 | 0.00 | 0.95 |
| Conversational AI | 0.50 | 0.75 | 0.00 | 1.00 |
| Dramatic / emotional | 0.30 | 0.75 | 0.15 | 1.00 |
| News / professional | 0.70 | 0.80 | 0.00 | 1.00 |
| Character acting | 0.25 | 0.70 | 0.20 | 1.00 |
| E-learning | 0.60 | 0.75 | 0.00 | 0.90 |

---

## TTS Models

| Model | Languages | Char Limit | Best For |
|-------|-----------|------------|----------|
| `eleven_v3` | 70+ | 5,000 | Newest, most natural, best quality |
| `eleven_multilingual_v2` | 29 | 10,000 | Reliable multilingual, longer text |
| `eleven_flash_v2_5` | 32 | 40,000 | Low latency (~75ms), very long text |
| `eleven_flash_v2` | English | 40,000 | English-only fast |

---

## TTS API

```bash
curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}" \
  -H "xi-api-key: $ELEVENLABS_KEY" \
  -H "Content-Type: application/json" \
  -o output.mp3 \
  -d '{
    "text": "Your text here.",
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
      "stability": 0.50,
      "similarity_boost": 0.75,
      "style": 0.0,
      "speed": 1.0
    }
  }'
```

### With Timestamps (for subtitles)

```bash
curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps" \
  -H "xi-api-key: $ELEVENLABS_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here.", "model_id": "eleven_multilingual_v2"}'
```

---

## Music Generation

```bash
curl -X POST "https://api.elevenlabs.io/v1/music" \
  -H "xi-api-key: $ELEVENLABS_KEY" \
  -H "Content-Type: application/json" \
  -o music.mp3 \
  -d '{
    "prompt": "Atmospheric Nordic ambient, slow building, dark cinematic pads, minimal piano",
    "music_length_ms": 60000,
    "model_id": "music_v1",
    "force_instrumental": true
  }'
```

### Structured Composition

```bash
curl -X POST "https://api.elevenlabs.io/v1/music" \
  -H "xi-api-key: $ELEVENLABS_KEY" \
  -H "Content-Type: application/json" \
  -o music.mp3 \
  -d '{
    "composition_plan": {
      "positive_global_styles": ["cinematic", "orchestral"],
      "negative_global_styles": ["lo-fi", "distorted"],
      "sections": [
        {"section_name": "intro", "positive_local_styles": ["soft", "building"], "duration_ms": 5000},
        {"section_name": "main", "positive_local_styles": ["powerful", "driving"], "duration_ms": 50000},
        {"section_name": "outro", "positive_local_styles": ["resolving", "fade"], "duration_ms": 5000}
      ]
    },
    "model_id": "music_v1",
    "force_instrumental": true
  }'
```

**Do NOT mention artist names** -- triggers TOS violation. Describe style instead.

### Songs with lyrics (Music v2.5 composition plan) — `scripts/generate_song.py`

`generate_music.py` forces `force_instrumental: true`. For sung words, use the **detailed** endpoint with a v2.5
composition plan. Lyrics live in each chunk's `text` (verified 2026-09-27):

```bash
curl -X POST "https://api.elevenlabs.io/v1/music/detailed" -H "xi-api-key: $ELEVENLABS_KEY" -H "Content-Type: application/json" \
  -d '{"model_id": "music_v2_5", "with_timestamps": true, "output_format": "mp3_44100_192", "seed": 11,
       "composition_plan": {"chunks": [
         {"text": "[Intro]\n{instrumental intro: pulsing synth arpeggio, kick enters on bar three}", "duration_ms": 7600,
          "positive_styles": ["minimal synthpop", "126 bpm", "deadpan female vocal", "four-on-the-floor kick"],
          "negative_styles": ["male vocals", "rock", "rap"], "context_adherence": "high"},
         {"text": "[Chorus]\nEvery message gets a score\nOnly the sure ones move", "duration_ms": 15200,
          "positive_styles": ["catchy chorus", "bright synth stabs"], "negative_styles": ["ballad"]}]}}'
```

- **Response:** `multipart/mixed`. A JSON part holds `composition_plan`, `song_metadata`, `waveform_visual` and
  **`words_timestamps`** (`[{word, start_ms, end_ms}]`, sung words only; `{direction}` words come back 0-length).
  The other part is the audio. The script splits them into `<out>.mp3` and `<out>.json`.
- **Chunks:** up to 30 chunks, 3–120 s each, 3 s–10 min in total. On v2 and v2.5, chunk durations are always enforced.
  Size them in bars: `bars × 4 × 60000 / BPM`.
- **Cues:** `[Section]` labels, `{instrumental break}`, `{spoken, deadpan}` and `{ends abruptly on the last word}` all
  steer the take. The first chunk's styles set the whole song.
- **Delivery:** ~80 s songs came back in under 2 minutes, with the line timing tracking the plan to ~0.5 s. Make two
  takes (different `seed`) and keep the one Whisper understands best (`song_lyrics.py score`).
- **Endings:** the model doesn't produce trailing silence reliably. Add the cold stop in the file
  (`ffmpeg -af apad=pad_dur=2.5`).


---

## Sound Effects

```bash
curl -X POST "https://api.elevenlabs.io/v1/sound-generation" \
  -H "xi-api-key: $ELEVENLABS_KEY" \
  -H "Content-Type: application/json" \
  -o sfx.mp3 \
  -d '{
    "text": "Old wooden desk drawer creaking open slowly",
    "duration_seconds": 2,
    "prompt_influence": 0.5
  }'
```

| Parameter | Range | Description |
|-----------|-------|-------------|
| `text` | required | Description of the sound |
| `duration_seconds` | 0.5-30 | Length. Auto if omitted |
| `prompt_influence` | 0-1 | How closely to follow prompt |
| `loop` | bool | Seamless looping |

---

## Voice Cloning (Instant)

```bash
curl -X POST "https://api.elevenlabs.io/v1/voices/add" \
  -H "xi-api-key: $ELEVENLABS_KEY" \
  -F "name=My Custom Voice" \
  -F "description=A warm narrator voice" \
  -F "files=@sample1.mp3" \
  -F "files=@sample2.mp3" \
  -F "remove_background_noise=true" \
  -F 'labels={"accent":"american","gender":"male","age":"middle_aged"}'
```

**Audio requirements:** 1-3 min clean audio, no reverb/noise, MP3 128kbps+, -23 to -18 dB RMS.

---

## Voice Design (Generate New Voice)

```python
result = client.text_to_voice.design(
    voice_description="A warm, friendly narrator with a slight British accent"
)

# Preview generated voices
for preview in result.previews:
    audio_bytes = base64.b64decode(preview.audio_base_64)
    with open(f"preview_{preview.generated_voice_id}.mp3", "wb") as f:
        f.write(audio_bytes)

# Save the one you like
client.text_to_voice.save(
    voice_id=result.previews[0].generated_voice_id,
    voice_name="My Designed Voice",
    voice_description="Warm British narrator"
)
```

---

## Output Formats

| Format | Code | Use Case |
|--------|------|----------|
| MP3 128k | `mp3_44100_128` | Default, good quality |
| MP3 192k | `mp3_44100_192` | Higher quality |
| WAV 44.1k | `pcm_44100` | Lossless, editing |
| Opus | `opus_48000_128` | Web streaming |
