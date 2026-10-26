# Progress Tracker

## Goal
Make every declassified document readable in full verbatim inside this repository, without
needing to visit external links. This is a long-running task; resume across sessions.

## Completed
- [x] README.md: comprehensive global reference (overview, timeline, programs, techniques, figures, works, sessions, evaluations, legacy, methodology, sources, disclaimer)
- [x] README.md: full index of 1,809 CIA STARGATE/remote-viewing documents (title, id, short description, links)
- [x] collections/mkultra.md: 524 MKULTRA records (title, id, short description, links)
- [x] collections/nsa-psychokinesis.md: NSA psychokinesis/SIGINT threat summary
- [x] collections/gwu-stargate-doc57.md: GWU STARGATE doc 57 summary
- [x] Clean formatting: no em dashes, backticks, or non-ASCII characters
- [x] Committed and pushed to https://github.com/hernanda-git/cia-remote-viewing

## In progress / next (resumable)
- [ ] Fetch full verbatim OCR text for each of the 1,809 STARGATE/remote-viewing documents into documents/stargate/ (5 done, 1,804 remaining)
- [ ] Fetch full verbatim OCR text for each of the 524 MKULTRA documents into documents/mkultra/
- [ ] Fetch full text for NSA psychokinesis document
- [ ] Fetch full text for GWU STARGATE doc 57
- [ ] Update README and collection indexes to point to in-repo full-text files
- [ ] Verify all files present and links resolve

## How to resume
Run the provided script to fetch full text with resume support:
  python tools/fetch_full_text.py --collection stargate
  python tools/fetch_full_text.py --collection mkultra

The script skips already-fetched files and saves progress to a log. Re-run safely at any time.

## Notes
- Index scope: CREST items mentioning remote viewing or stargate (1,809 docs).
- MKULTRA index: 524 docs.
- Total in-repo collection records: 2,333+
- Full verbatim text is large; expect hours of fetching and hundreds of MB of storage.
"