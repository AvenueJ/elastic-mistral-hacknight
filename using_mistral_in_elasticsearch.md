# 🤖 Using Mistral in Elasticsearch


> This guide covers one way to use Mistral: from inside Elasticsearch. To call Mistral directly — agents, OCR, Voxtral audio, vision, moderation, the Vibe coding CLI, and more — see the [Mistral guide](mistral_guide.md).

This hack night pairs **Elasticsearch** with **Mistral** tech. If you want to use Mistral through Elasticsearch's **Inference API**: you create an *inference endpoint* backed by Mistral once, and then everything in Elastic — `semantic_text` fields, your own queries, and (optionally) Agent Builder — can use it. Auth is handled for you: the Mistral API key lives inside the endpoint, so your app only ever talks to Elasticsearch.
You'll typically create **two** endpoints:

1. a **`text_embedding`** endpoint (for semantic/vector search), and
2. a **`chat_completion`** endpoint (the LLM for RAG, generation, or an agent).

> **You'll be given a Mistral API key at the event.** Wherever you see `<MISTRAL_API_KEY>` below, paste it in.

All the API calls below run in Kibana's **Dev Tools Console** (hamburger menu → **Management → Dev Tools**). Dev Tools uses your current session — no endpoint URL or auth headers to set.

---

## 1. Embeddings — semantic & vector search

Create a Mistral embedding endpoint:

```
PUT _inference/text_embedding/mistral-embeddings
{
  "service": "mistral",
  "service_settings": {
    "api_key": "<MISTRAL_API_KEY>",
    "model": "mistral-embed"
  }
}
```

### The fast path: `semantic_text`

Point a `semantic_text` field at your Mistral endpoint and Elasticsearch embeds documents automatically at index time — no manual vector handling:

```
PUT nyc_notes
{
  "mappings": {
    "properties": {
      "text": {
        "type": "semantic_text",
        "inference_id": "mistral-embeddings"
      }
    }
  }
}
```

Index a few documents normally — Elasticsearch calls Mistral to embed them:

```
POST nyc_notes/_doc
{ "text": "Mouse droppings found in the kitchen near the food prep area." }
```
```
POST nyc_notes/_doc
{ "text": "Cold food held above 41F; no thermometer available on site." }
```

Then search with natural language — no keywords, no vectors in your query:

```
GET nyc_notes/_search
{
  "query": {
    "semantic": {
      "field": "text",
      "query": "rodent problems in the food area"
    }
  }
}
```

The "mouse droppings" document comes back top, even though it never says *rodent*. That's Mistral embeddings doing the work.

> **Applying it to real data:** the restaurant `violation_description` field is perfect for this. Add a `semantic_text` field to the index (or reindex into a new one with `inference_id: "mistral-embeddings"`) and you can search inspections by meaning — "unsafe food temperatures", "pest problems", "dirty equipment" — instead of exact violation codes. The same trick works on squirrel stories, 311 messages, or OCR'd tax-photo captions.

### Raw vectors (bring-your-own kNN)

Want the vectors yourself for a custom `dense_vector` / kNN setup? Call the inference API directly:

```
POST _inference/text_embedding/mistral-embeddings
{
  "input": ["best pizza in Brooklyn", "cleanest ramen in Manhattan"]
}
```

---

## 2. Chat & generation — a Mistral chat model

Create a **`chat_completion`** endpoint backed by a Mistral general-purpose model. This is the LLM for a RAG answer, a generation step, or — if you choose — an Agent Builder agent:

```
PUT _inference/chat_completion/mistral-chat
{
  "service": "mistral",
  "service_settings": {
    "api_key": "<MISTRAL_API_KEY>",
    "model": "mistral-large-latest"
  }
}
```

Swap `model` for whatever fits your project:
- `mistral-large-latest` — most capable general-purpose model, also strong at reasoning and multi-step analysis
- `mistral-small-latest` — faster and cheaper, great for high-volume tools

> Check [Mistral's model overview](https://docs.mistral.ai/getting-started/models/models_overview/) for the current model IDs.

### Test it

```
POST _inference/chat_completion/mistral-chat
{
  "messages": [
    { "role": "user", "content": "In one sentence, what makes a NYC restaurant get a grade of C?" }
  ]
}
```

### (Optional) Point Agent Builder at it

If you choose to build an agent, Agent Builder uses the Elastic Managed LLM by default. To make it think with Mistral instead:

1. Open **Kibana → Agents** and start (or open) your agent's chat.
2. Use the **model selector** in the chat interface and pick your **`mistral-chat`** endpoint.

Prefer to set it globally? Search **GenAI Settings** in Kibana's global search bar and choose your Mistral connector/endpoint as the **Default AI Connector**. Either way, the only requirement is that the endpoint supports the **`chat_completion`** task type — which the one above does.

> **UI alternative — connector route.** You can also add Mistral as a Kibana **Connector** (global search → **Connectors → Create connector**). Because Mistral's API is OpenAI-compatible, pick the **OpenAI** connector type, choose the *OpenAI-compatible / Other* provider, set the URL to `https://api.mistral.ai/v1/chat/completions`, the model to e.g. `mistral-large-latest`, and paste your key. The inference-endpoint route above is simpler and keeps everything in Dev Tools, so prefer it unless you need the connector UI.

---

## 3. Calling Mistral through Elasticsearch from your own app

Building a backend, script, or custom chatbot? You can call Mistral directly with the `mistralai` SDK (see the [Mistral guide](mistral_guide.md)), or talk to the **inference API** on your Elasticsearch endpoint — your Elasticsearch API key is the only credential you need; the Mistral key stays inside the endpoint.

```bash
curl "$ELASTICSEARCH_URL/_inference/chat_completion/mistral-chat/_stream" \
  -H "Authorization: ApiKey $ELASTIC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      { "role": "system", "content": "You are a NYC restaurant inspector." },
      { "role": "user",   "content": "Summarize the health risks of cold-holding violations." }
    ]
  }'
```

Same thing from Python with the official client:

```python
from elasticsearch import Elasticsearch

es = Elasticsearch(ELASTIC_ENDPOINT, api_key=ELASTIC_API_KEY)

resp = es.inference.chat_completion_unified(
    inference_id="mistral-chat",
    messages=[
        {"role": "system", "content": "You are a NYC restaurant inspector."},
        {"role": "user",   "content": "Summarize the health risks of cold-holding violations."},
    ],
)
# response streams as SSE chunks — concatenate the delta.content fields
```

**This is the core of a RAG app:** query Elasticsearch for relevant context (keyword, `semantic`, or kNN), drop it into the messages, then call the Mistral chat endpoint for a grounded answer.

Need raw embeddings in Python?

```python
resp = es.inference.inference(
    inference_id="mistral-embeddings",
    task_type="text_embedding",
    input=["Lower East Side", "Astoria", "Flushing"],
)
print(resp["text_embedding"][0]["embedding"][:5])
```

---

## Reference

- [Create a Mistral inference endpoint (API)](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-inference-put-mistral)
- [Inference API overview](https://www.elastic.co/docs/explore-analyze/elastic-inference/inference-api)
- [Using different models in Agent Builder](https://www.elastic.co/docs/solutions/search/agent-builder/models)
- [Using OpenAI-compatible models](https://www.elastic.co/docs/solutions/search/using-openai-compatible-models)
- [Semantic search with `semantic_text`](https://www.elastic.co/docs/solutions/search/semantic-search/semantic-search-semantic-text)
- [Mistral API docs](https://docs.mistral.ai/) · [model overview](https://docs.mistral.ai/getting-started/models/models_overview/)
