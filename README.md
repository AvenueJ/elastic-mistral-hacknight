# Elastic × Mistral NYC Hack Night

Welcome to the **Elastic × Mistral NYC Hack Night**! Tonight you'll build something that leverages **Elasticsearch** and **Mistral** models on top of **open NYC data** — a search experience, a RAG app, an analytics pipeline, an agent, whatever your idea calls for.

The theme is **New York City**. The city publishes an enormous amount of open data — restaurant inspections, 311 complaints, a squirrel census, live transit feeds, and much more. Your job is to turn some slice of it into something that reasons, answers, and surprises. Semantic search, a RAG chatbot, a conversational analyst, a moderation pipeline — if it runs on Elasticsearch and Mistral, we want to see it.

**Date:** October 7, 2026
**Location:** Elastic NYC Office
**Hack time:** ~3 hours

> **This is a hack about ideas, not interfaces.** We are judging how creatively and effectively you combine **Elastic** and **Mistral** — not how your project looks. You do **not** need a polished front-end, and fancy JavaScript or slick animations win you nothing. A notebook, a Dev Tools session, a terminal script, or Kibana itself is a perfectly good way to demo. Spend your three hours on the data and the models.

---

## Judging Criteria and Presentations

Projects will be evaluated on:

| Criteria | Description |
|---|---|
| **Novelty** | A unique idea, a novel use of the data, or an interesting technical approach. |
| **Use of Elastic** | Meaningful use of Elasticsearch — search, aggregations, vector/semantic search. Agent Builder is a bonus, not a requirement. |
| **Use of Mistral** | Meaningful use of Mistral models — embeddings, general-purpose/reasoning chat, moderation, audio, or coding. |
| **Use of MCP and other tools** | Optional: connecting to Claude, an IDE, or your own app via MCP, or wiring in other tooling. |

At the end you'll present what you built — no matter how finished it is. Show it off even if it's rough; that's the spirit of the night.

Some presentation guidelines:
- **3-minute demo** of what you built. No polished UI expected — a notebook, Dev Tools, a script, or Kibana is fine.
- Show the **Elastic** portion (your queries, mappings, or tools) and the **Mistral** portion (which models you used and where). Those two, plus any accompanying tech, must be part of the demo.

**Submission:** Post on DevPost (link pending).

**Recommended team size:** Individuals or small teams of 2–4.

---

## What you can build

Anything that puts **Elasticsearch** and **Mistral** to work on NYC data. To get moving fast:

1. **Pick a dataset** from the table below — each one has a ready-to-run ingest notebook that loads it into Elasticsearch.
2. **Add Mistral** — embeddings for semantic search, a chat model for a RAG answer, moderation, OCR, audio, whatever fits your idea. The [Mistral guide](mistral_guide.md) shows how.
3. **Build your thing** — a search experience, a RAG app, an analytics pipeline, a classifier, an agent. See [open_challenge.md](open_challenge.md) for ideas and a generic ingest example.

You'll use a serverless Elastic deployment: [Elastic Cloud Serverless free trial](https://www.elastic.co/cloud/cloud-trial-overview).

**Need an LLM, embeddings, moderation, or speech?** Use **Mistral** through Elasticsearch. The [Mistral guide](mistral_guide.md) shows how to create Mistral inference endpoints for embeddings and chat, and how to tap Mistral's other capabilities.

> **Agent Builder is optional.** Elastic [Agent Builder](https://www.elastic.co/docs/explore-analyze/ai-features/elastic-agent-builder) is a slick, no-code way to stand up a conversational agent with Mistral as its brain, and it's a great fit for some ideas — but it is **not** required. A RAG script, a semantic-search demo, or an analytics notebook counts just as much.

---

## Technical setup

You'll need two things:

1. **Elasticsearch Serverless (9.4+)** — [free trial](https://www.elastic.co/cloud/cloud-trial-overview). This is the home for your data and where Agent Builder lives.
2. **Mistral API key(s)** — for the embedding and general-purpose models. We'll hand these out at the event. You'll plug them into Elastic inference endpoints (see the [Mistral guide](mistral_guide.md)).

**How Elasticsearch is used:** Elasticsearch is the main data store. You ingest an NYC dataset and query it — full-text, aggregations, vector/semantic search — from a notebook, Dev Tools, your own app, or (optionally) Agent Builder. If you build an agent, you can expose it over the built-in **MCP server** to drive it from Claude or your own app.

**How Mistral is used:** Mistral provides the intelligence. A common pairing is a Mistral **embedding** model for semantic/vector search plus a Mistral **general-purpose** model for generation — both wired in as Elasticsearch inference endpoints. Beyond that, Mistral is open for you to explore (see below).

---

## Mistral capabilities to explore

Keep it open — these are prompts, not requirements. Any of these can anchor a project:

| Capability | Where it shines | Models |
|---|---|---|
| **Embeddings** | Semantic search and RAG over NYC text (violations, 311 complaints, squirrel sightings) | `mistral-embed` |
| **General-purpose chat** | The reasoning brain behind a RAG answer, an agent, or any generation step | `mistral-large-latest`, `mistral-small-latest` |
| **Reasoning models** | Multi-step analysis, planning, harder questions | `magistral-medium-latest`, `magistral-small-latest` |
| **Content moderation** | Flag or filter user input and dataset text | `mistral-moderation-latest` |
| **Speech-to-text & text-to-speech** | Voice-driven NYC assistants; transcribe audio into Elasticsearch | Voxtral (audio) |
| **Vibe-coding & CLI** | Build faster with Mistral's coding models and CLI/IDE tooling | `codestral-latest` |

See the [Mistral guide](mistral_guide.md) for how to reach these from Elasticsearch, and [Mistral's model docs](https://docs.mistral.ai/getting-started/models/models_overview/) for the current list of model IDs.

---

## Public NYC Datasets

Suggested starting points — **you are not restricted to these, use any NYC dataset you find.** Most [NYC Open Data](https://opendata.cityofnewyork.us/) sets have a direct JSON/CSV API (Socrata), so they're easy to ingest (see [open_challenge.md](open_challenge.md)).

Each dataset ships with a ready-to-run ingest notebook in this repo — connect your Elastic project, run all cells, done.

| Dataset | Description | Ingest notebook |
|---|---|---|
| **[DOHMH Restaurant Inspection Results](https://data.cityofnewyork.us/Health/DOHMH-New-York-City-Restaurant-Inspection-Results/43nn-pn8j/data_preview)** | Every NYC restaurant inspection: grades, scores, violations, cuisine, borough, location. Rich text + categories + geo — great for aggregations and semantic search alike. | [nyc_restaurant_analyst.ipynb](nyc_restaurant_analyst.ipynb) |
| **[2018 Central Park Squirrel Census](https://data.cityofnewyork.us/Environment/2018-Central-Park-Squirrel-Census-Stories/gfqj-f768/about_data)** | Field notes and stories from an actual census of Central Park's squirrels. Delightfully weird narrative text, perfect for embeddings. | [nyc_squirrel_census.ipynb](nyc_squirrel_census.ipynb) |
| **[311 Public Feedback / complaint types](https://data.cityofnewyork.us/City-Government/Public-feedback-on-311-request-complaint-types/7ffd-6gs9/about_data)** | Free-text feedback New Yorkers submit to 311. Ideal for embeddings and Mistral moderation (plus a pointer to the giant 311 Service Requests set). | [nyc_311_feedback.ipynb](nyc_311_feedback.ipynb) |
| **[MTA Subway Real-Time Feeds](https://api.mta.info/#/subwayRealTimeFeeds)** | Live train positions and arrival predictions (GTFS-Realtime). Real-time data for a live agent. | [mta_subway_realtime.ipynb](mta_subway_realtime.ipynb) |
| **[MTA Subway Schedule](https://www.mta.info/developers)** | Static GTFS schedule — routes, stops (with geo), timetables. Pairs with the live feed. | [mta_subway_schedule.ipynb](mta_subway_schedule.ipynb) |
| **[NYC 1940s Tax Photos](https://nycrecords.access.preservica.com/uncategorized/SO_d501be84-e09a-4023-bb8a-263aa8b0e04f/)** | ~720,000 WPA photographs of every NYC building (1939–1941), with block/lot signboards. A real-world **Mistral OCR** stress test. | [nyc_tax_photos.ipynb](nyc_tax_photos.ipynb) + [tax_photos_scraper.py](tax_photos_scraper.py) |
| **[SONYC Urban Sound Tagging](https://zenodo.org/records/2590742)** | Thousands of 10-second street recordings from NYC's acoustic sensor network, tagged across 23 sound classes. Great for **Mistral Voxtral** speech-to-text. | [nyc_sonyc_sound.ipynb](nyc_sonyc_sound.ipynb) |
| **[City Nature Challenge: NYC](https://www.inaturalist.org/projects/city-nature-challenge-2025-new-york-city)** | ~22,000 geo-tagged iNaturalist observations of NYC's wild plants, birds, bugs and fungi — each with a **photo** (and sometimes **audio**). The most multimodal set here: Mistral vision + Voxtral + embeddings. | [nyc_city_nature_challenge.ipynb](nyc_city_nature_challenge.ipynb) |

Mix datasets freely — e.g., join 311 rat complaints with restaurant rodent violations by neighborhood, overlay the squirrel census (or City Nature Challenge sightings) on subway stops, or OCR a block's 1940s photos and cross-reference today's inspection grades.

> **Tax photos need a scraper first.** Images live in the NYC Municipal Archives (Preservica), not a flat API. Run `python tax_photos_scraper.py --borough richmond --max 50` to pull a batch (images + `metadata.csv`), then run the notebook to OCR and index them. The scraper is rate-limited and sends a descriptive User-Agent — it's a city-government server, so be a good citizen. Non-commercial use is exempt from licensing; credit published output as *1940s Tax Department photographs, Courtesy of the Municipal Archives, City of New York.*

---

## Prizes

The **top three projects** win — a unique Lego set!

Good luck, have fun, and happy hacking! 🗽

---

## Resources

Handy documentation and references for tonight.

### Getting started
- [Elasticsearch quickstart](https://www.elastic.co/docs/solutions/search/get-started) — your first index and query
- [Connecting to Elasticsearch](https://www.elastic.co/docs/reference/elasticsearch/clients) — endpoints, API keys, and client setup

### Mistral on Elastic
- [Mistral guide (this repo)](mistral_guide.md) — embeddings, chat, and the rest of Mistral's lineup through Elasticsearch
- [Create a Mistral inference endpoint (API)](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-inference-put-mistral)
- [Mistral model overview](https://docs.mistral.ai/getting-started/models/models_overview/)

### Agent Builder (optional)
- [Agent Builder overview](https://www.elastic.co/docs/explore-analyze/ai-features/elastic-agent-builder)
- [Building custom tools](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/tools/custom-tools)
- [Building custom agents](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/custom-agents)
- [Using different models in Agent Builder](https://www.elastic.co/docs/solutions/search/agent-builder/models)
- [Expose agents over MCP](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/mcp-server) — connect to Claude or your own app

### Search & querying
- [ES|QL reference](https://www.elastic.co/docs/explore-analyze/query-filter/languages/esql) — a concise query language for search and aggregations
- [Query DSL](https://www.elastic.co/docs/explore-analyze/query-filter/languages/querydsl) — full-text, filters, and boolean queries
- [Aggregations](https://www.elastic.co/docs/explore-analyze/query-filter/aggregations) — stats, terms, and metrics

### Vector & semantic search (great for RAG)
- [Semantic search with `semantic_text`](https://www.elastic.co/docs/solutions/search/semantic-search/semantic-search-semantic-text) — the fastest path to semantic search
- [kNN / dense vector search](https://www.elastic.co/docs/solutions/search/vector/knn)
- [Bringing your own embeddings](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/dense-vector)

### Ingesting data
- [Python Elasticsearch client](https://www.elastic.co/docs/reference/elasticsearch/clients/python) — what the notebook uses
- [Bulk API](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-bulk) — efficient batch indexing
- [Upload a file in Kibana](https://www.elastic.co/docs/manage-data/ingest/upload-data-files) — no-code CSV/JSON ingest
