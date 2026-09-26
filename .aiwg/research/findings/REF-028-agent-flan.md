---
ref_id: REF-028
title: "Agent-FLAN: Designing Data and Methods of Effective Agent Tuning for Large Language Models"
authors: "Zehui Chen et al."
year: 2024
source: ../sources/REF-028.pdf
source_url: https://arxiv.org/abs/2403.12881
source_type: preprint
full_text: ../working/fulltext/REF-028.txt
sha256: a7ae31d03dd631db964406bc5f604ac62dc7aaa27847d63e54c4d326026c26a2
grade: moderate
reviewed: 2026-09-25
status: inducted
tags: [agent-tuning, negative-examples, tool-use, format-overfitting]
---

# Agent-FLAN

## Executive synthesis

Agent-FLAN finds that rigid ReAct/JSON training can teach format faster than the reasoning beneath
it. Decomposing agent competence into reasoning, retrieval, understanding, and instruction
following—and adding negative cases for when not to call tools—improves agent performance and
reduces hallucinated actions.

## Study design

The study remixed 24,703 examples from AgentInstruct and ToolBench, plus a 1:1 general-data mix.
Ninety percent of agent examples were converted to natural conversation and ten percent retained
ReAct format. It balanced reasoning, retrieval, and understanding at 1:0.25:0.75 and added 2,000
instruction-following examples.

Experiments fine-tuned Llama 2 at 7B, 13B, and 70B. The primary 7B comparison covered held-in
and held-out agent tasks, tool use, and a new hallucination evaluation.

## Findings

- Agent-FLAN exceeded earlier agent-tuning methods by a reported 3.5 points on average.
- The largest gains from data scaling occurred in the first 25% of the agent corpus.
- Further scaling yielded smaller gains, suggesting a need for better diversity and quality.
- Reasoning and understanding were more valuable/slower-learning lanes than retrieval and format.
- Negative samples improved the Agent-H score from 84.5 to 89.1 with similar T-Eval performance.
- General benchmarks were roughly preserved or slightly improved across model sizes.

## Negative-example design

The paper added cases where a user requests a tool but no tool is available, and cases where tools
are present but an ordinary conversational answer is appropriate. These examples teach both how
and when to act, reducing unsupported calls and accidental agent-format responses.

## Relevance to a dense 27B target

The current Forge's uniform `Derivation`/`Final answer` wrapper risks the same format shortcut.
A 27B dataset should vary surface realization while preserving capability labels privately. Tool use
should cover selection, argument construction, result interpretation, error recovery, abstention,
and the decision not to call a tool.

AIWG orchestration can become latent through realistic delegation and integration tasks, including
bounded scope, conflict resolution, evidence reconciliation, and accountable final verification.

## Limitations

- Main controlled experiments use Llama2-7B; 27B is inferred between 13B and 70B.
- Agent datasets cover a limited set of interactive environments.
- Only about 20K ToolBench samples were retained.
- General benchmark gains are small and not proof of broad reasoning transfer.
- The paper's hallucination metric contains a formula typo and is format-oriented.

## Inducted controls

1. Separate underlying decision skill from output protocol in data and metrics.
2. Include positive tool calls, negative no-call cases, and recovery from failed tools.
3. Vary valid response formats; do not reward a universal reasoning wrapper.
4. Allocate more examples to slow-learning reasoning and parameter-understanding skills.
5. Hold out tools, APIs, and environments rather than only instances.
6. Evaluate false tool calls and missed tool calls separately.
7. Pair agent-specific data with general replay data.

## Evidence relationships

REF-027 supports paired aligned/misaligned behavior examples. REF-022 supports targeted persona
data and verifiable instruction following. REF-018 explains why format imitation alone should not
be interpreted as capability.
