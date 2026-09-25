---
ref_id: REF-002
title: "WizardLM: Empowering Large Language Models to Follow Complex Instructions"
source: ../sources/REF-002.pdf
grade: high
reviewed: 2026-09-25
---

## Executive summary

Evol-Instruct operationalizes difficulty growth through explicit mutations: add constraints, deepen inquiry, concretize, increase reasoning steps, complicate inputs, and broaden topics.

## Method and findings

The study evolves simpler instructions into harder variants and trains on mixed difficulty stages. This supports purposeful curricula instead of asking a teacher for unstructured “hard questions.”

## Relevance and limitations

Use bounded mutation operators whose before/after changes can be validated. Evolution can silently introduce contradictions, unsatisfiable constraints, or teacher-specific style, so every mutation needs constraint and answer checks.

## Implementation implication

Store `parent_record_ids`, `evolution_operator`, `difficulty_before`, and `difficulty_after`; accept only independently verified increases.
