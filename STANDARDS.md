# Coding Standards for this Assignment

These exist so we can read your submission in 10 minutes instead of 30. They
are not gatekeeping — they are basic professional habits. If you skip them,
your code looks indistinguishable from a stack of AI-generated snippets
glued together, and we can't tell what *you* did.

Most of this is mechanical and takes <30 minutes total to set up.

---

## 1. Project hygiene

- **`README.md`** in your submission root. Sections: *Setup, How to run, How to
  test, Known limitations*. Written by you, in plain English. Not generated.
- **`requirements.txt`** (or `pyproject.toml`) pinned to specific versions.
  `pip install -r requirements.txt` must work from a clean Python 3.10+ env.
- **`.gitignore`** that excludes `__pycache__/`, `.venv/`, `*.db`, `.env`,
  `.pytest_cache/`, `node_modules/`, etc.
- **No committed secrets.** Use a `.env` file and a `.env.example`. Never hard-code
  API keys.
- **No 200MB binaries.** Don't commit virtualenvs, models, or `.db` files.

## 2. Python style

- **Python 3.10+**. Use modern syntax (`x: list[str]`, `match` if helpful).
- **Type hints on every function signature.** Not on every internal variable —
  just on functions. We're not type-Nazis but if your code has zero hints we
  can't tell what shape your data has.
- **Docstrings** on every function that does something non-trivial. One line
  is fine. We don't want essays — we want to know *what it returns and why
  it exists*. Skip docstrings on obvious one-liners.
- **No `print()` for application output.** Use the `logging` module. Print is
  fine for the one-off summary at the end of `ingest.py`.
- **Run [`ruff`](https://docs.astral.sh/ruff/) or `black`** before submitting.
  We don't care which; we care that the file isn't a stylistic mess.
- **Imports sorted** (`ruff check --select I --fix .` or `isort`).

## 3. Code structure

- **One responsibility per function.** A function that loads, cleans, transforms,
  and writes is four functions. Hard limit: if a function is longer than ~50 lines,
  it's probably doing too much.
- **No god-files.** If `main.py` is 600 lines, split it.
- **Named constants, not magic numbers.** `CHUNK_SIZE = 500` at the top of the
  file, not `500` scattered through the code.
- **Keep configuration outside code.** API keys, model names, paths — read
  from env vars or a small config file.

## 4. Errors and edge cases

- **Don't swallow exceptions.** `except: pass` is an automatic red flag.
  Catch specific exceptions and log them at minimum.
- **Validate at the boundary.** Your API endpoints should reject bad input
  with a clear 400 error, not crash with a 500.
- **Don't add error handling for things that can't happen.** Trust your own
  internal calls. Validate user input, not internal function arguments.

## 5. Testing

- **At least 5 real tests.** Not 50 — five. Pick the most important behaviours
  and test them. Use `pytest`.
- Examples of good tests:
  - "Ingestion drops rows with no title" — feed a tiny CSV in, assert the row
    count.
  - "Filtering by country=India returns only Indian titles" — call the endpoint
    on a small fixture, assert.
  - "/ask returns at least one source for any non-empty answer" — invariant test.
- **A test that doesn't test anything** (e.g., `assert True`) is worse than no
  test. We will check.

## 6. Git hygiene

- **Real commit history.** As you work, commit small chunks with messages like
  *"trying smaller chunks for RAG"*, *"this didn't work, reverting"*, *"got
  filter endpoint working"*. We want to see the journey.
- **Do NOT squash before submitting.** Two commits called "initial commit" and
  "final" tell us you only ever committed the AI's final answer. That's a
  strong negative signal.
- Commit messages in present tense, lowercase first letter is fine. Be honest.

## 7. AI tool use — the rules

- You can use any AI tool. We use them too.
- **You must understand every line you submit.** During the live round we
  will pick a line at random and ask "why is this here, what breaks if I
  delete it." If you can't answer, that line counts against you.
- **Document your AI usage in NOTES.md (Question 5).** Honest "I prompted
  Cursor to write the FastAPI scaffolding and accepted it as-is" is fine.
  Pretending you wrote everything when you didn't is not.
- **Don't paste AI output you don't understand.** If you don't know what a
  line does, either learn it or delete it. We will catch this.

## 8. README in your submission

Your submission's `README.md` must contain (at minimum):

```
# <project name>

## Setup
<exact commands to set up from a clean environment>

## How to run
<exact commands to run ingest.py and start the API>

## How to test
<exact commands to run tests>

## Known limitations
<honest list of things that don't work or are half-finished>
```

The "Known limitations" section is one of the most useful things you can
write. Acknowledging what's broken is much better than pretending it isn't.

---

## TL;DR

- Type hints, docstrings, real commit history, real tests.
- No print spam, no swallowed exceptions, no committed secrets.
- A clear README with exact commands.
- An honest NOTES.md.

If you do this much, your submission already looks like a 75th-percentile
intern. Most candidates skip half of these and it's the first thing we
notice.
