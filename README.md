# Practical AI Training for Her Second Innings (HSI)

Hands-on training for HSI management and staff on using AI in daily work, with a local, private RAG assistant built on Ollama.

## Audience
- Management (founder, leadership)
- Resourcing, career coaching, community, marketing, IT

## Principles
1. Practical over theory: every module ends with a working output.
2. Private by default: local models, no candidate data in public tools.
3. AI drafts, humans decide: especially for anything about a person.
4. Use HSI's real (anonymized) material.

## Repo map
| Path | Purpose |
|---|---|
| `TOC.md` | Draft table of contents (for discussion) |
| `docs/use-cases.md` | Use-case catalogue and priorities |
| `docs/policy-draft.md` | One-page AI usage and data rules (to be agreed) |
| `modules/` | One folder per training module (slides, lab guide, handouts) |
| `rag-lab/` | The workshop lab developers clone: skeleton code, failing tests, synthetic KB, instructions (start at `rag-lab/README.md`). `rag-lab/facilitator/` is the private answer key and is gitignored. |
| `slides/` | Decks: `HSI_RAG_Dev_Workshop.pptx` (developers, main) and `HSI_AI_Training.pptx` (staff hand-over) |
| `ARCHITECTURE.md` | System design and contracts overview |
| `templates/` | Reusable prompt templates for staff |

## Status
Draft. ToC v4: full-day developer workshop (concepts, code-alongs, squad build), 14 developers, shared AWS EC2 server, deployed assistant for HSI. Deck built (`slides/HSI_RAG_Dev_Workshop.pptx`, NASSCOM-style colors). Repo skeleton, reference implementation and synthetic knowledge base not built yet.
