# Libraries and AI (7/2025)

> 2025-07-17, 13:00, Martin Czygan -- UBL KI MEETUP #4, "Document Chat" / [BIDC]() review

## Summaries

* Navigating AI ...
* Bibliothekskongress 2025 / AI TRACK, https://pdf-program.abstractserver.com/?congress=bid2025

## Demos

### Chat with your local documents (PDF)

#### Requirements

* [ ] A desktop application
* [ ] Either a GPU or an API to access a remote model (available through GWDG, Leibniz, etc.)


#### Options

Numerous applications to run chat with your documents locally:

* [x] [GPT4ALL](https://www.nomic.ai/gpt4all) ([$17M](https://www.reuters.com/technology/open-source-ai-model-creator-nomic-raises-17-million-led-by-coatue-2023-07-13/), ...)
* [x] [ChatRTX](https://www.nvidia.com/en-us/ai-on-rtx/chatrtx/)
* [x] [AnythingLLM](https://anythingllm.com/desktop), [GitHub](https://github.com/Mintplex-Labs/anything-llm)
* [x] [LMStudio](https://lmstudio.ai/)

```
$ ./gpt4all/bin/chat
```

Index a folder of PDFs.

![](static/screenshot-2025-07-17-122222-gpt4all-embedding.png)

Start dialogue.

![](static/screenshot-2025-07-17-123154-dialogue.png)


### Chat/Search over a FT (wip)

> Exploring a set of 22K docs and 500K pages with the help of AI

What can the machine learn from this corpus?

* let's cluster it into 2, 3, ..., 10 categories, what do we get?
* let's embed the documents into a vector database and see which records are similar
* let's embed paragraphs and see which documents are similar

Matching queries against documents.

* full text search
* natural language query; LLM and RAG
* natural language query to document query; fuzzy text, but exact query
* query in images

You can do this with any document set.

### MCP server for catalogs (wip)

* expose a library catalog to a chat interface
* make it so that we can find books, text, new items, but also images, digitized pages, and more

## BID CONGRESS 2025 Review

![](static/open-bid-2025-ki-keyword-rga-screenie.png)


### Ideation

![](static/screenshot-2025-07-17-123447-bid-2025-ideation.png)

### Beratung (FAIR)

![](static/screenshot-2025-07-17-123620-fair-chatbot.png)

* conventient, fast
* dependent of third party infra

### KI Schulungen

![](static/screenshot-2025-07-17-123754-ki-schulungen.png)

* dynamische Entwicklung


### Future

![](static/screenshot-2025-07-17-123950-bib-2030-1.png)

![](static/screenshot-2025-07-17-124156-bib-2030-2.png)

* does GLAM not have enough images?

### AI at a small social science university

![](static/screenshot-2025-07-17-124340-hertie-1.png)


### Survey

![](static/screenshot-2025-07-17-124455-survey-1.png)

### OER

![](static/screenshot-2025-07-17-124627-oer.png)

### YAAK - Yet another Arbeitskreis

![](static/screenshot-2025-07-17-124837-yaak.png)


### Writing Project

![](static/screenshot-2025-07-17-125027-writing.png)



## References

* [](https://discovery.ucl.ac.uk/id/eprint/10209236/1/Navigating-Artificial-Intelligence-for-Cultural-Heritage-Organisations.pdf)


