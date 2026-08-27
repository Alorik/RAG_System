# Intern Assignment — Netflix Catalog Q&A System

Welcome. This is a take-home assignment to help us understand how you think about
data, backend, and AI/LLM problems. We're not looking for a perfect product —
we're looking for the **reasoning behind your choices**.

**Time expectation:** ~5–7 hours. Stop at 8 hours regardless of where you are.
We'd rather see a smaller scope done thoughtfully than a large scope half-done.

**You can use AI tools** (ChatGPT, Cursor, Copilot, Claude, etc.). We expect you
to. But you must understand every line you submit and be able to explain it.
There is a live walkthrough after submission where we will ask you to defend
specific lines, modify code on the spot, and debug something you didn't write.
If you can't, the assignment counts for very little.

---

## What you're building

A small system that lets a user query the Netflix catalogue in two ways:
1. **Structured search** — filter shows by country, year, type, rating.
2. **Natural-language Q&A** — ask questions like *"Suggest me a comedy movie from
   India with a strong female lead"* and get an answer grounded in the catalogue.

You will also write up your reasoning. The write-up matters as much as the code.

---

## Provided data

`data/netflix_titles.csv` — ~6,200 rows of Netflix titles as of 2019. Real,
public, and **deliberately not cleaned for you**. Treat it as you'd treat any
data you receive in the real world.

Columns: `show_id, type, title, director, cast, country, date_added,
release_year, rating, duration, listed_in, description`

You will discover problems with this data as you work. Document what you find.

---

## The four parts

### Part 1 — Data ingestion (scripting + data)

Write a Python script `ingest.py` that:
- Loads `data/netflix_titles.csv`
- Cleans/normalises the data (your judgement call — explain in NOTES.md)
- Writes the cleaned data into a SQLite database `data/netflix.db`
- Prints a clear summary report when it finishes (rows loaded, rows dropped/fixed,
  any anomalies you found)

You should be able to run `python ingest.py` from a fresh checkout and have it
work end-to-end.

### Part 2 — Backend API (backend)

Build a small HTTP API using **FastAPI** (preferred) or Flask, with these
endpoints:

- `GET /titles` — list titles, with query params for filtering by `country`,
  `release_year`, `type` (Movie / TV Show), and `rating`. Support pagination.
- `GET /titles/{show_id}` — fetch a single title by id.
- `GET /stats` — return small summary stats (total titles, count by type,
  count by country — top 10).

Run it locally with one command. Document that command in your README.

### Part 3 — RAG-based Q&A (AI / LLM)

Add an endpoint:
- `POST /ask` — body: `{ "question": "..." }`. Returns an answer grounded in
  the catalogue, plus the `show_id`s of the titles your answer was based on.

Build a basic RAG pipeline:
1. Embed the catalogue (you decide what text to embed — that's a real design
   choice, document it).
2. On a question, retrieve the most relevant titles.
3. Pass them to an LLM with a prompt and return the answer + sources.

You can use **any** LLM — OpenAI, Groq (free tier), Gemini (free tier), Ollama
locally, anything. You can use any embedding model (sentence-transformers
locally is free and fine). You can use any vector store (FAISS, Chroma, or even
just numpy + cosine similarity — for 6k rows you don't need a real vector DB).

The answer must cite which titles it used. Hallucinated answers without sources
will be penalised heavily.

### Part 4 — NOTES.md (the most important file)

A single markdown file in the project root, **maximum 2 pages**, answering:

1. **What problems did you find in the CSV?** What did you fix, what did you
   leave, and why?
2. **Schema decisions.** How did you store multi-value fields like `country`,
   `cast`, `listed_in`? Why?
3. **RAG choices.** What text did you embed for each title? What chunk size /
   model did you pick? Why?
4. **What would break at 100,000 titles instead of 6,000?** Be concrete.
5. **AI usage — be honest.** What did you ask AI tools to write? Where did you
   override or rewrite their output, and why? Where did you accept their output
   without fully understanding it?
6. **What would you do with another 4 hours?**

We read this **first**, before looking at your code. Don't bullshit it. Honest
"I don't know why I picked this" beats a confident-sounding lie. We will ask
follow-up questions on every answer in the live round.

---

## Coding standards (read STANDARDS.md before you start)

You must follow `STANDARDS.md` — it lists the conventions we use so we can
read your code quickly. It's short. Skipping it makes your submission look
like vibe-coded output we can't review.

---

## What to submit

A single zip file (or a public git repo link) containing:

```
your_submission/
├── README.md           # how to install + run, in your own words
├── NOTES.md            # the write-up (Part 4)
├── STANDARDS.md        # (optional — copy ours, or write your own and tell us why)
├── requirements.txt    # or pyproject.toml
├── .gitignore
├── ingest.py
├── api/                # your FastAPI / Flask app
│   └── ...
├── rag/                # your RAG code
│   └── ...
├── tests/              # at least a few real tests, see STANDARDS.md
│   └── ...
└── data/
    └── netflix_titles.csv   # leave the original here for reproducibility
```

If you use git: **do not squash your commits**. We want to see the messy
history — failed attempts, reverts, "trying X" commits. That's the most
honest signal of how you actually worked. A repo with two commits ("initial",
"final") tells us you only committed the AI's output.

---

## What happens next

1. You submit the assignment.
2. We read NOTES.md and skim the code.
3. **60–90 minute live walkthrough**, screen-share. We will:
   - Ask you to walk through one part of your code we pick at random
   - Ask "why" on specific lines
   - Ask you to add a small feature live, in 15 minutes (no new prompting to
     ChatGPT during this — you can google syntax, that's it)
   - Hand you a 30-line Python script we wrote that's broken, and ask you to
     debug it in 10 minutes

The live round is where the assignment is actually graded. The code you
submit is the artifact we will discuss; the discussion is what we evaluate.

---

## Questions before you start

If anything is unclear, ask. We'd rather answer a question than receive a
submission built on a wrong assumption. Asking good clarifying questions is
itself a positive signal.

Good luck.
