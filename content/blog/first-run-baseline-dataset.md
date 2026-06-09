---
title: "First Run — Baseline Dataset Generation"
date: 2026-06-08
excerpt: "Setting up the initial data pipeline for synthetic instruction-following dataset generation, and a first look at the quality metrics."
tags: [dataset-generation, pipeline, baseline]
---

## Goal

Generate a synthetic instruction-following dataset to use as a baseline for fine-tuning experiments. This first run uses a simple self-instruct pipeline with a Llama 3.1 8B base model.

## Pipeline

```
seed_prompts/ → LLM expansion → dedup → quality filter → shuffle → train/val split
```

- **Seed prompts**: 50 hand-written instruction seeds across 5 categories
- **Model**: Llama 3.1 8B (unsloth quantized)
- **Temperature**: 0.7 (first pass) / 0.9 (second pass for diversity)
- **Filtering**: Length > 10 tokens, no API-error artifacts, dedup by MinHash

## Results

| Metric | Value |
|--------|-------|
| Total generated | 2,450 |
| After dedup | 2,112 |
| After quality filter | 1,847 |
| Train/val split | 1,660 / 187 |

## Quality Spot-Check

A few random samples look coherent but tend to be _verbose_ — the model over-explains simple concepts. This is expected at 0.7 temp with no system prompt tuning.

Next step: experiment with system prompt constraints and lower temperature (0.5) for the second generation pass.
