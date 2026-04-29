## ADDED Requirements

### Requirement: setup_state.py MUST accept multi-PDF manual sources

When a `tools/manual_urls.json` entry contains a non-empty `urls` array, `setup_state.py` SHALL download each URL in declared order, extract text from each, and concatenate the results into a single text file before invoking question generation. The order in `urls` is the canonical chapter order for the resulting concatenation.

#### Scenario: Multi-PDF state is onboarded end-to-end
- **WHEN** `setup_state.py` runs on a state whose catalog entry contains 5 chapter PDF URLs
- **THEN** the resulting `/tmp/<code>_manual_text.txt` contains the extracted text of all 5 PDFs in order, each preceded by a `=== chapter <n> ===` separator, and `generate_questions.py` produces a question bank that cites multiple chapters

#### Scenario: Backward compatibility for single-URL entries
- **WHEN** `setup_state.py` runs on a state whose catalog entry has only `manual_url` (no `urls` field)
- **THEN** the behavior is identical to the pre-change pipeline: one PDF downloaded, one text file extracted, one question bank generated

### Requirement: setup_state.py MUST accept HTML-index manual sources

When a state's manual is published only as a chapter-by-chapter HTML index (no PDF available), `setup_state.py` SHALL accept an HTML index URL, scrape the linked chapter pages, strip site navigation/footer, and produce a single text file equivalent to the PDF-extraction path.

#### Scenario: HTML-index state is onboarded
- **WHEN** `setup_state.py` runs on a state whose `manual_url` points to an HTML index page (content-type `text/html`) and `urls` is absent
- **THEN** the helper fetches the index, identifies chapter `<a href>` links, fetches each, extracts main-content text, concatenates, and writes the combined text file
