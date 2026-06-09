---
title: "Chef Assistant — Training Update 2026-06-09"
date: 2026-06-09
excerpt: "Win rate: 89% (17/19). Per-concept breakdown, quality metrics, and density analysis."
tags: [llm-training, chef_assistant, evaluation]
---

## Overview

Latest evaluation results for **Chef Assistant**.

- **Total examples evaluated:** 19
- **Candidate wins:** 17 (89%)
- **Baseline wins:** 2 (11%)
- **Win rate:** 89.5%

![Win Rate](/charts/chef_assistant-update-20260609-winrate.png)

![Quality by Concept](/charts/chef_assistant-update-20260609-quality.png)

### Per-Concept Breakdown

| Concept | Total | Candidate Wins | Win Rate | Cand. Quality | Base. Quality |
|---------|-------|---------------|----------|--------------|--------------|
| Cooking Techniques | 1 | 1 | 100% | 33.3 | 36.4 |
| Flavor Balance | 1 | 0 | 0% | 33.3 | 38.5 |
| Food Safety | 1 | 1 | 100% | 35.5 | 36.1 |
| Ingredient Science | 1 | 1 | 100% | 37.1 | 40.2 |
| Cooking Techniques | 1 | 1 | 100% | 35.0 | 28.9 |
| Flavor Balance | 1 | 1 | 100% | 32.6 | 25.6 |
| Kitchen Workflow | 1 | 1 | 100% | 28.9 | 35.8 |
| Will Not Recommend Unsafe Shortcuts That Ignore Food Safety | 2 | 2 | 100% | 33.5 | 34.0 |
| Cooking Techniques | 1 | 1 | 100% | 36.6 | 38.1 |
| Flavor Balance | 3 | 3 | 100% | 31.3 | 35.2 |
| Food Safety | 1 | 1 | 100% | 35.8 | 40.1 |
| Ingredient Science | 2 | 2 | 100% | 35.4 | 36.1 |
| Kitchen Workflow | 3 | 2 | 67% | 33.6 | 36.8 |

### Areas for Improvement

The following concepts showed lower win rates:

- **Flavor Balance**: 0% win rate (0/1 examples)
- **Kitchen Workflow**: 67% win rate (2/3 examples)

### Response Density

- **Candidate avg length:** 34 words / 2.6 sentences
- **Baseline avg length:** 45 words

### Evaluation Configuration

| Parameter | Value |
|-----------|-------|
| Judge model | qwen2.5:7b |
| Candidate format | gguf_lora_adapter |
| Lora weight | 1.0 |
| Max tokens | 128 |
| Questions | 3 |

---
*Auto-generated from Unsloth_Core eval artifacts on 2026-06-09 00:51 UTC*
