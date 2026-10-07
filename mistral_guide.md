# 🧡 Building with Mistral 😼

![Le chonk: Introducing Mistral Large 4](img/le_chonk.jpg)

This guide covers what Mistral offers and how to start building with it tonight. To use Mistral models from inside Elasticsearch (inference endpoints, `semantic_text`, Agent Builder), see [Using Mistral in Elasticsearch](using_mistral_in_elasticsearch.md).

---

# What does Mistral make?

* **[Lots of models](https://mistral.ai/research/)**, including the new [Mistral Large 4](https://mistral.ai/news/mistral-large-4/)
* **[Mistral Studio](https://console.mistral.ai/)**, to create agents, work with audio, build agents, and more
* **[Vibe Work](https://chat.mistral.ai/work)**, to accomplish agentic tasks via chat, with connectors, skills, [workflows](https://docs.mistral.ai/vibe/work/workflows), knowledge store, and more
* **[Vibe CLI](https://mistral.ai/products/vibe/code/)**, for LLM-driven coding with the model(s) of your choice
* Mistral Cloud, Mistral Compute, and more things you won't use today

## More about those models

* Just yesterday, we released [Mistral Large 4](https://mistral.ai/news/mistral-large-4/), our new flagship model. You can use that to power agents, write code, and more.
* For more popular models, there's a pretty guide at [mistral.ai/research](https://mistral.ai/research/)
* [OCR 4.1](https://docs.mistral.ai/models/ocr-4-1), a top model for recognizing text in images
* [Audio models](https://docs.mistral.ai/studio/audio/overview) for text-to-speech and speech-to-text
* Small open models that can fit on your laptop, like [Ministral](https://docs.mistral.ai/models/ministral-3-8b-25-12) and the Voxtral mini family, like [Mini Transcribe Realtime](https://docs.mistral.ai/models/voxtral-mini-transcribe-26-02)
* [Shieldstral](https://docs.mistral.ai/models/shieldstral-1-0), for content moderation
* [Embeddings](https://docs.mistral.ai/models/mistral-embed-23-12)
* plus [more here](https://docs.mistral.ai/models)!


---

# Getting started

First, you'll need to sign up for a Mistral account.

To get credits to use the API, [go here](https://admin.mistral.ai/subscription/upgrade/redeem?redeem_code=MIST-ELAST-NYC) or scan this QR code:

<img src="img/mistral_api_qr_code.svg" width="220" alt="QR code linking to the Mistral API credit redemption page"/>

Once you have an account, you can use [Vibe Work](https://chat.mistral.ai/work) in the browser. You can also install the [Mistral Vibe](https://docs.mistral.ai/mistral-vibe/introduction) coding CLI with:

```bash
curl -LsSf https://mistral.ai/vibe/install.sh | bash
```

# Resources

* [Mistral docs](https://docs.mistral.ai/) · [all models](https://docs.mistral.ai/models)
* [Cookbooks](https://docs.mistral.ai/resources/cookbooks) · [on GitHub](https://github.com/mistralai/cookbook)
* [Python and TypeScript SDKs](https://docs.mistral.ai/resources/sdks)
* [Mistral Discord](https://discord.gg/mistralai)

## Quickstarts

* [Install and use Vibe CLI for coding](https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli)
* [API Quickstart](https://docs.mistral.ai/getting-started/quickstarts/developer/first-api-request)
* [Build an agent with tools](https://docs.mistral.ai/getting-started/quickstarts/developer/build-an-agent)
* [Build a Workflow](https://docs.mistral.ai/getting-started/quickstarts/developer/build-a-workflow)
* [More quickstarts](https://docs.mistral.ai/#quickstarts)
* [Using the Python and TypeScript SDKs](https://docs.mistral.ai/resources/sdks)

# A bunch of stuff Claude wrote about coding with Mistral

It might have gone a little crazy here with detail, but I'm keeping this because it took the trouble to write it up. And you might find it useful!

## Coding with Mistral

* **[Vibe CLI](https://docs.mistral.ai/getting-started/quickstarts/vibe-code/install-cli):** an agentic coding assistant in your terminal. Install it with `curl -LsSf https://mistral.ai/vibe/install.sh | bash`, point it at your project, and have it write your ingest scripts, Elasticsearch queries, and app code.
* **Vibe in your IDE:** Vibe also runs as a VS Code extension, and in JetBrains IDEs and other ACP-compatible clients. See [Use Vibe in other IDEs](https://docs.mistral.ai/vibe/code/use-vibe-in-other-ides).
* **Mistral models in other coding tools:** tools such as [OpenCode](https://opencode.ai/docs/providers/) let you plug in Mistral models with your API key.

To call the API from code, [create an API key in Mistral Studio](https://docs.mistral.ai/getting-started/quickstarts/studio/activate-and-generate-api-key), then:

```bash
export MISTRAL_API_KEY="your_api_key_here"
pip install mistralai          # or: npm i @mistralai/mistralai
```

```python
import os
from mistralai.client import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

response = client.chat.complete(
    model="mistral-large-4",
    messages=[{"role": "user", "content": "In one sentence, what makes a NYC restaurant get a grade of C?"}],
)
print(response.choices[0].message.content)
```

All the snippets below reuse this `client`.

### Names for some popular models in the API

| Model | API name | Good for |
|---|---|---|
| Mistral Large 4 (public preview) | `mistral-large-4` | Agents, reasoning, coding, images |
| Mistral Small | `mistral-small-latest` | Fast, cheap, high-volume calls |
| Ministral 8B | `ministral-8b-latest` | Small and fast; open weights you can run locally |
| OCR 4.1 | `mistral-ocr-latest` | Reading text from images and PDFs |
| Voxtral Mini Transcribe | `voxtral-mini-latest` | Speech-to-text from audio files |
| Voxtral Mini Transcribe Realtime | `voxtral-mini-realtime-latest` | Live speech-to-text |
| Voxtral TTS | `voxtral-mini-tts-latest` | Text-to-speech and voice cloning |
| Mistral Embed | `mistral-embed` | Embeddings for semantic search and RAG |
| Mistral Moderation | `mistral-moderation-2603` | Hosted content moderation API |
| Shieldstral 1.0 | [open weights](https://docs.mistral.ai/models/shieldstral-1-0) | Policy-based moderation you run yourself |



## Core APIs, on NYC data

Short Python examples. Each one links to the full docs.

### Structured outputs: messy text → clean JSON

Turn free-text 311 feedback into fields you can index and aggregate in Elasticsearch. [Docs](https://docs.mistral.ai/studio/conversations/structured-output/custom)

```python
from pydantic import BaseModel

class Complaint(BaseModel):
    topic: str
    borough: str | None
    urgency: str  # "low", "medium", or "high"

response = client.chat.parse(
    model="mistral-large-4",
    messages=[
        {"role": "system", "content": "Extract the complaint details."},
        {"role": "user", "content": "There's been a broken streetlight on my block in Astoria for three weeks and it's not safe at night."},
    ],
    response_format=Complaint,
)
print(response.choices[0].message.parsed)
```

### Function calling: let the model decide what to look up

Describe a tool, and the model tells you when to call it and with which arguments. The function can be anything, including an Elasticsearch query. [Docs](https://docs.mistral.ai/studio/conversations/function-calling)

```python
import json

tools = [{
    "type": "function",
    "function": {
        "name": "search_inspections",
        "description": "Search NYC restaurant inspections by restaurant name or cuisine.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}, "borough": {"type": "string"}},
            "required": ["query"],
        },
    },
}]

messages = [{"role": "user", "content": "Any recent rodent violations at pizza places in Brooklyn?"}]
response = client.chat.complete(model="mistral-large-4", messages=messages, tools=tools)

tool_call = response.choices[0].message.tool_calls[0]
args = json.loads(tool_call.function.arguments)  # e.g. {"query": "pizza rodent", "borough": "Brooklyn"}

# Run your search with args, then send the result back as a "tool" message for the final answer.
results = {"hits": []}  # replace with a real search
messages.append(response.choices[0].message)
messages.append({"role": "tool", "name": tool_call.function.name,
                 "content": json.dumps(results), "tool_call_id": tool_call.id})
final = client.chat.complete(model="mistral-large-4", messages=messages, tools=tools)
print(final.choices[0].message.content)
```

### Embeddings: search by meaning

Embed text yourself, then index the vectors into an Elasticsearch `dense_vector` field for kNN search. [Docs](https://docs.mistral.ai/studio/knowledge-rag/embeddings/text_embeddings)

```python
response = client.embeddings.create(
    model="mistral-embed",
    inputs=["Squirrel chased a jogger near the reservoir.", "Squirrel eating a bagel on a bench."],
)
vector = response.data[0].embedding  # 1024 floats
```

### Vision: understand a photo

Ask about a City Nature Challenge observation photo. [Docs](https://docs.mistral.ai/studio/conversations/vision)

```python
photo_url = "https://..."  # an observation's photo_url field from the City Nature Challenge notebook

response = client.chat.complete(
    model="mistral-large-4",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "What species is this? Answer with the common and scientific name."},
            {"type": "image_url", "image_url": photo_url},  # or "data:image/jpeg;base64,..."
        ],
    }],
)
print(response.choices[0].message.content)
```

### OCR: read text from images and documents

Read the block/lot signboard in a 1940s tax photo. [Docs](https://docs.mistral.ai/studio/document-processing/basic_ocr)

```python
import base64

with open("tax_photo.jpg", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

ocr = client.ocr.process(
    model="mistral-ocr-latest",
    document={"type": "image_url", "image_url": f"data:image/jpeg;base64,{b64}"},
)
print(ocr.pages[0].markdown)
```

### Audio: speech-to-text and text-to-speech

Some audio and document tools can be tried in Mistral Studio without code:

| | In Studio | Via API |
|---|---|---|
| [OCR](https://docs.mistral.ai/studio/document-processing/basic_ocr) | ✅ | ✅ |
| [Text-to-speech](https://docs.mistral.ai/studio/audio/text_to_speech/speech) | ✅ | ✅ |
| [Speech-to-text](https://docs.mistral.ai/studio/audio/speech_to_text/offline_transcription) | | ✅ |

Transcribe a street recording from the SONYC dataset. [Docs](https://docs.mistral.ai/studio/audio/speech_to_text/offline_transcription)

```python
with open("sonyc_clip.wav", "rb") as f:
    transcription = client.audio.transcriptions.complete(
        model="voxtral-mini-latest",
        file={"content": f, "file_name": "sonyc_clip.wav"},
    )
print(transcription.text)
```

Speak an answer out loud. You'll need a `voice_id`; [create or pick a voice](https://docs.mistral.ai/studio/audio/text_to_speech/voices) first. [Docs](https://docs.mistral.ai/studio/audio/text_to_speech/speech)

```python
import base64
from pathlib import Path

speech = client.audio.speech.complete(
    model="voxtral-mini-tts-latest",
    input="The L train is running with delays at Bedford Avenue.",
    voice_id="your-voice-id",
    response_format="mp3",
)
Path("answer.mp3").write_bytes(base64.b64decode(speech.audio_data))
```

### Moderation: flag unsafe text

Screen 311 feedback before you index it. [Docs](https://docs.mistral.ai/studio/safety-moderation)

```python
response = client.classifiers.moderate(
    model="mistral-moderation-2603",
    inputs=["The noise from the construction site starts at 5am every day."],
)
print(response.results[0].categories)
```

Want to run moderation yourself, with your own policies? [Shieldstral](https://docs.mistral.ai/models/shieldstral-1-0) is an open-weights moderation model you can host. See the [Shieldstral cookbook](https://docs.mistral.ai/resources/cookbooks/mistral-moderation-shieldstral_policy_moderation).

---

## Agents

The [Agents API](https://docs.mistral.ai/studio/agents/introduction) gives you agents that keep conversation state and come with [built-in tools](https://docs.mistral.ai/studio/agents/agent-tools):

* **Web search** for up-to-date information
* **Code interpreter** for running code and making plots
* **Image generation**
* **Document library** for RAG over files you upload
* **Function calling**, to add your own tools (like an Elasticsearch search)
* **[Handoffs](https://docs.mistral.ai/studio/agents/handoffs)**, so agents can pass work to each other

```python
agent = client.beta.agents.create(
    model="mistral-large-4",
    name="NYC Guide",
    description="Answers questions about New York City.",
    instructions="You help people explore NYC. Use web search for anything current.",
    tools=[{"type": "web_search"}],
)

response = client.beta.conversations.start(
    agent_id=agent.id,
    inputs="What's happening in Central Park this weekend?",
)
print(response.outputs[-1].content)
```

For longer, multi-step jobs, see [Build a Workflow](https://docs.mistral.ai/getting-started/quickstarts/developer/build-a-workflow).

You can also build agentic tasks without code in [Vibe Work](https://docs.mistral.ai/vibe/work/get-started), which supports [MCP connectors](https://docs.mistral.ai/vibe/work/connectors/mcp-connectors), skills, and workflows.

---
