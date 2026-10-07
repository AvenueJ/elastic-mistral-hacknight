# Hack Night Open Challenge

Build anything you like on NYC data using tech from **Elasticsearch** and **Mistral**. This page has project ideas across the suggested datasets and a ready-to-run ingest example you can point at *any* NYC Open Data set.

> No polished UI required — a notebook, Dev Tools, a script, or Kibana is a perfectly good demo. We care about how you combine Elastic and Mistral, not how it looks. Agent frameworks (Elastic Agent Builder, Mistral's Agents API) are optional, not requirements.

## Example Projects

| Project | Dataset | Elastic + Mistral features |
|---|---|---|
| **NYC Complaint Analyst** | [311 requests](https://data.cityofnewyork.us/City-Government/Public-feedback-on-311-request-complaint-types/7ffd-6gs9/about_data) | Aggregations + a Mistral agent: "What is my neighborhood complaining about this month?" |
| **Squirrel Spotter** | [Central Park Squirrel Census](https://data.cityofnewyork.us/Environment/2018-Central-Park-Squirrel-Census-Stories/gfqj-f768/about_data) | Semantic search over field notes with Mistral embeddings: "Find sightings of a squirrel that seemed annoyed at a jogger." |
| **Where Should I Eat?** | [Restaurant inspections](https://data.cityofnewyork.us/Health/DOHMH-New-York-City-Restaurant-Inspection-Results/43nn-pn8j/data_preview) | RAG chatbot combining grades + semantic violation search for a trustworthy recommendation. |
| **Complaint Moderator** | [311 requests](https://data.cityofnewyork.us/City-Government/Public-feedback-on-311-request-complaint-types/7ffd-6gs9/about_data) | Run free-text through Mistral moderation before indexing; dashboard what gets flagged. |
| **Live Subway Companion** | [MTA real-time feeds](https://api.mta.info/#/subwayRealTimeFeeds) + [schedule](https://www.mta.info/developers) | Ingest live positions, let a Mistral agent reason over current service status. |
| **Voice of the City** | any + [Voxtral](https://docs.mistral.ai/) | Transcribe a spoken question with Mistral speech-to-text, answer it from Elasticsearch. |
| **Time Machine Block Explorer** | [1940s Tax Photos](https://nycrecords.access.preservica.com/) | OCR the block/lot signboards with **Mistral OCR**, index them, and ask "show me what this block looked like in 1940." |
| **City Soundscape** | [SONYC Urban Sound](https://zenodo.org/records/2590742) | Aggregate which sensors hear the most jackhammers/sirens; transcribe human-voice clips with **Voxtral**. |
| **Pocket Naturalist** | [City Nature Challenge](https://www.inaturalist.org/projects/city-nature-challenge-2025-new-york-city) | Send an observation photo to a vision-capable **Mistral** model, guess the species, and check it against the crowd ID — then map where it was found. |
| **Invasive Species Tracker** | [City Nature Challenge](https://www.inaturalist.org/projects/city-nature-challenge-2025-new-york-city) | Aggregate + map the spread of spotted lanternfly or other invasives across boroughs, and summarize the hotspots with a Mistral chat model. |
| **Borough Concierge** | any | A **Mistral agent** (Agents API) with an Elasticsearch search function as one of its tools, plus built-in web search for anything the index doesn't cover. |
| **Chat With the City** | any | Connect **Le Chat** or **Mistral Vibe** to Elastic Agent Builder's MCP server, and query your NYC indices in plain language. |
| **Archive Digitizer** | [1940s Tax Photos](https://nycrecords.access.preservica.com/) | A **Mistral Document AI** pipeline extracts structured JSON (block, lot, signage, building type) from each photo, and Elasticsearch makes the whole archive searchable and aggregatable. |

> **Two ways to use Mistral.** Call Mistral directly with the `mistralai` SDK or API: chat and reasoning, agents, function calling, OCR, vision, Voxtral audio, moderation, and more. Then index whatever it produces into Elasticsearch. Or register Mistral models as **Elasticsearch inference endpoints**, so `semantic_text`, Agent Builder, and your own queries can use them. Mix both freely. See the [Mistral guide](mistral_guide.md) for the direct route and [Using Mistral in Elasticsearch](using_mistral_in_elasticsearch.md) for the inference-endpoint route.

## Stretch Ideas

- **Semantic search** over squirrel census stories or 311 complaints using Mistral embeddings - search by meaning, not keywords.
- **Cross-dataset mashup** - join 311 rodent complaints with restaurant rodent violations by neighborhood and map the overlap.
- **A reasoning agent** on `mistral-large-latest` that plans multi-step answers ("Which blocks have both the most noise complaints *and* the lowest restaurant grades?").
- **Natural-language dashboard** - users ask questions in plain English; Elasticsearch retrieves, Mistral explains.
- **An MCP-connected agent** you drive from Claude, Mistral Vibe, or your own app via Agent Builder's MCP server.
- **OCR → structured data** - OCR a batch of 1940s tax photos with Mistral, extract the block/lot, and reconcile it against the metadata to measure OCR accuracy on real handwriting.
- **Then vs. now** - OCR a block's 1940s photos and join to today's restaurant grades or 311 complaints for the same block, telling an 80-year story of a NYC street.

---

## Example: Ingesting any NYC Open Data set

Almost every dataset on [NYC Open Data](https://opendata.cityofnewyork.us/) is served by **Socrata**, which gives you a direct JSON API - no key, no download, no CSV wrangling. The pattern below works for any of them; just change the dataset id.

Run it in a Jupyter/Colab notebook or as a plain Python script. If you'd rather not script it, you can also use the **Upload file** option in the Elasticsearch UI with a downloaded CSV.

### 1. Install dependencies

```bash
pip install elasticsearch requests
```

### 2. Find the dataset id

On any NYC Open Data page, the id is the code in the URL (e.g. the squirrel census is `gfqj-f768`). The JSON API for a dataset is:

```
https://data.cityofnewyork.us/resource/<dataset-id>.json
```

You can append [Socrata query params](https://dev.socrata.com/docs/queries/): `$limit`, `$where`, `$order`, `$select`.

### 3. Fetch the data

```python
import requests

DATASET_ID = 'gfqj-f768'  # 2018 Central Park Squirrel Census Stories
url = f'https://data.cityofnewyork.us/resource/{DATASET_ID}.json'

resp = requests.get(url, params={'$limit': 5000}, timeout=60)
resp.raise_for_status()
rows = resp.json()

print(f'{len(rows)} rows')
print('Columns:', list(rows[0].keys()))
```

### 4. Connect to Elastic Serverless

```python
from elasticsearch import Elasticsearch, helpers

# 🔑 Fill these in - Elastic Cloud Console → Your Project → Connection Details
ELASTIC_ENDPOINT = 'https://your-project.es.region.aws.elastic.cloud'
ELASTIC_API_KEY  = 'your-elastic-api-key'

es = Elasticsearch(ELASTIC_ENDPOINT, api_key=ELASTIC_API_KEY)
print(f'✅ Connected to Elasticsearch {es.info()["version"]["number"]}')
```

### 5. Bulk-index into Elasticsearch

Let Elasticsearch infer field types (dynamic mapping) - fine for exploration. Define an explicit mapping later if you want `keyword` fields for exact filtering, `geo_point` for maps, or `semantic_text` for Mistral-powered semantic search.

```python
INDEX = 'nyc_squirrels'

# Recreate the index each run so there are no duplicates
if es.indices.exists(index=INDEX):
    es.indices.delete(index=INDEX)
es.indices.create(index=INDEX)

actions = [{'_index': INDEX, '_source': r} for r in rows]
success, errors = helpers.bulk(es, actions, raise_on_error=False)
es.indices.refresh(index=INDEX)
print(f'✅ Indexed {success} documents ({len(errors)} errors)')
```

### 6. Verify

```python
resp = es.search(index=INDEX, size=3)
print(f"Total documents: {resp['hits']['total']['value']}\n")
for hit in resp['hits']['hits']:
    print(hit['_source'])
```

That's it - you now have an index you can search, aggregate, or layer AI on top of. From here, add an explicit mapping, wire up a `semantic_text` field with a **Mistral embedding endpoint** for meaning-based search ([Using Mistral in Elasticsearch](using_mistral_in_elasticsearch.md)), or call **Mistral** directly with the `mistralai` SDK: a chat model for a RAG answer, an agent that queries this index as a tool, moderation, OCR, or Voxtral audio ([Mistral guide](mistral_guide.md)).

---

## Add Mistral semantic search in 3 steps

Turn any text field into meaning-aware search:

```
# 1. Create a Mistral embedding endpoint (once)
PUT _inference/text_embedding/mistral-embeddings
{ "service": "mistral", "service_settings": { "api_key": "<MISTRAL_API_KEY>", "model": "mistral-embed" } }

# 2. Create an index with a semantic_text field pointed at it
PUT nyc_squirrels_semantic
{ "mappings": { "properties": { "story": { "type": "semantic_text", "inference_id": "mistral-embeddings" } } } }

# 3. Index docs normally, then search by meaning
GET nyc_squirrels_semantic/_search
{ "query": { "semantic": { "field": "story", "query": "a squirrel acting suspicious near the reservoir" } } }
```

See [using_mistral_in_elasticsearch.md](using_mistral_in_elasticsearch.md) for details, raw-vector kNN, and the full Mistral model lineup.
