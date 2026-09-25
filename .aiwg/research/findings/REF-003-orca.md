---
ref_id: REF-003
title: "Orca: Progressive Learning from Complex Explanation Traces of GPT-4"
source: ../sources/REF-003.pdf
grade: moderate
reviewed: 2026-09-25
---

## Executive summary

Orca argues that student models benefit from richer teacher signals, varied system instructions, and progressive learning rather than bare answers alone.

## Method and findings

Its reported process uses a large first-stage corpus from one teacher and a smaller, stronger-teacher stage, while varying system messages that elicit explanation behavior.

## Relevance and limitations

Preserve system, user, teacher, and verification fields separately. Explanations may improve learning, but proprietary-teacher dependence and limited reproducibility lower confidence, and verbose rationales are not automatically correct.

## Implementation implication

Support concise answers, structured explanations, and worked solutions as distinct answer forms; do not force chain-of-thought into every row.
