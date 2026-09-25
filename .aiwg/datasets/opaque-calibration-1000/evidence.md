# Execution Evidence — Opaque Calibration 1000

**Result:** PASS for technical calibration; HOLD for production release pending independent review.

## Counts

| Measure | Result |
|---|---:|
| Submitted worker tasks | 3,000 |
| Raw candidates | 3,000 |
| Candidates with validation failures | 0 |
| Candidates with verifier failures | 0 |
| Contamination rejections | 0 |
| Selected records | 1,000 |
| Unique selected lineages | 1,000 |
| Selected per category | 100 each across 10 categories |
| Train / validation / test | 910 / 48 / 42 |
| Forge stage | `awaiting_review` |
| Production release created | No |

## Artifact hashes

```text
3f68841f8b88aa81b0af8dbe8bed96c4cb61369d688c4894d86548c8700ebe59  seeds/seeds.jsonl
4c9d71b14c355e56564e1b5d56754c4fcdfbf9190394fa034d2756369e477df5  runs/opaque-calibration-1000/run-manifest.json
ab70d85376e26b91ab4af0db983428545640eb0cf644f57d798c720ebfe3f132  runs/opaque-calibration-1000/raw.jsonl
23a60898bc23fa54b2005413c8e0249d365aa130b40e673e183c929c5198049a  runs/opaque-calibration-1000/evaluated.jsonl
954758dd7077fc79d35ff3f111113499bc56660143c4dd5510ee02e310a06a49  runs/opaque-calibration-1000/selected.jsonl
083fb2451b1fc458231cf92b219eb2f60b1fc418d0cca5c249c28dd916ad8bc6  calibration-report.json
```

The runtime workspace is `/srv/question_stack/pilot-workspace` and is intentionally excluded from Git. The service state is `finalized`, meaning collection has entered the immutable Forge run; it does not mean the dataset has passed review or been released. The pilot drove the separate FastAPI application contracts through in-process test clients. It did not start TCP listeners or exercise the documented split Unix identities/systemd units.
