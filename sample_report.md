# 🤖 Multi-Model LLM Comparison Report

**Run ID:** `2026-05-20_10-00-00`  

**Started:** 2026-05-20T10:00:00+00:00  

**Finished:** 2026-05-20T10:45:00+00:00  

**Models compared:** 5  

**Prompts:** 5 across 4 categories  

**Judge model:** `nvidia/llama-3.1-nemotron-70b-instruct`  

---

## 🏆 Overall Leaderboard



| Rank | Model | Overall Score | Win Rate |

|------|-------|---------------|----------|

| 🥇 | **Kimi k2.6** | 94.8% ██████████████░ | 3/4 categories |

| 🥈 | **Qwen3-235B** | 92.6% ██████████████░ | 1/4 categories |

| 🥉 | **Llama Nemotron 70B** | 90.0% ██████████████░ | 0/4 categories |

| #4 | **DeepSeek-V3** | 89.8% █████████████░░ | 0/4 categories |

| #5 | **Mistral Large** | 44.4% ███████░░░░░░░░ | 0/4 categories |



## 📊 Per-Category Breakdown

### Code Generation

| Rank | Model | Avg Score |

|------|-------|-----------|

| 🥇 | Qwen3-235B | 100.0% ████████████ |

| 🥈 | Kimi k2.6 | 95.0% ███████████░ |

| 🥉 | DeepSeek-V3 | 90.0% ███████████░ |

| #4 | Llama Nemotron 70B | 90.0% ███████████░ |

| #5 | Mistral Large | 70.0% ████████░░░░ |



> **Winner:** Qwen3-235B (+5.0% over runner-up Kimi k2.6)



### Creative Writing

| Rank | Model | Avg Score |

|------|-------|-----------|

| 🥇 | Kimi k2.6 | 96.0% ████████████ |

| 🥈 | Llama Nemotron 70B | 93.0% ███████████░ |

| 🥉 | DeepSeek-V3 | 92.0% ███████████░ |

| #4 | Qwen3-235B | 88.0% ███████████░ |

| #5 | Mistral Large | 48.0% ██████░░░░░░ |



> **Winner:** Kimi k2.6 (+3.0% over runner-up Llama Nemotron 70B)



### Factual Recall

| Rank | Model | Avg Score |

|------|-------|-----------|

| 🥇 | Kimi k2.6 | 92.0% ███████████░ |

| 🥈 | Qwen3-235B | 88.0% ███████████░ |

| 🥉 | Llama Nemotron 70B | 88.0% ███████████░ |

| #4 | DeepSeek-V3 | 85.0% ██████████░░ |

| #5 | Mistral Large | 77.0% █████████░░░ |



> **Winner:** Kimi k2.6 (+4.0% over runner-up Qwen3-235B)



### Reasoning

| Rank | Model | Avg Score |

|------|-------|-----------|

| 🥇 | Kimi k2.6 | 95.5% ███████████░ |

| 🥈 | Qwen3-235B | 93.5% ███████████░ |

| 🥉 | DeepSeek-V3 | 91.0% ███████████░ |

| #4 | Llama Nemotron 70B | 89.5% ███████████░ |

| #5 | Mistral Large | 13.5% ██░░░░░░░░░░ |



> **Winner:** Kimi k2.6 (+2.0% over runner-up Qwen3-235B)



## ⏱️ Latency Comparison



| Model | Median Latency | Mean Latency | P95 Latency |

|-------|---------------|--------------|-------------|

| Qwen3-235B | 0.78s | 0.98s | 1.90s |

| Mistral Large | 0.88s | 0.88s | 1.10s |

| Llama Nemotron 70B | 1.05s | 1.32s | 2.40s |

| Kimi k2.6 | 1.10s | 1.29s | 2.30s |

| DeepSeek-V3 | 1.30s | 1.34s | 2.10s |



## 🪙 Completion Tokens



| Model | Total Tokens | Avg per Prompt |

|-------|-------------|----------------|

| DeepSeek-V3 | 364 | 73 |

| Kimi k2.6 | 361 | 72 |

| Qwen3-235B | 318 | 64 |

| Mistral Large | 258 | 52 |

| Llama Nemotron 70B | 359 | 72 |



## ⚠️ Conflict of Interest Disclosure

The judge model (`nvidia/llama-3.1-nemotron-70b-instruct`) was used to evaluate its own responses on 2 prompt(s). These scores may be inflated and should be interpreted with caution.



| Prompt ID | Category |

|-----------|----------|

| `c01` | code_generation |

| `w01` | creative_writing |



---

## 📎 Appendix: Full Per-Prompt Outputs

### Category: Code Generation

#### Prompt `c01`

**Prompt:**

```
Write a Python fizzbuzz(n) function with type hints and docstring.
```



**DeepSeek-V3** — Score: `90.0%` (llm-as-judge)

*Correct implementation with type hints and docstring.*

> def fizzbuzz(n: int) -> list[str]:
    """Return fizzbuzz list up to n."""
    result = []
    for i in range(1, n+1):
        if i % 15 == 0: result.append('FizzBuzz')
        elif i % 3 == 0: result.append('Fizz')
        elif i % 5 == 0: result.append('Buzz')
        else: result.append(str(i))
    return result

*Latency: 1.10s | Tokens: 75*



**Kimi k2.6** — Score: `95.0%` (llm-as-judge)

*Elegant one-liner with full type hints and docstring.*

> def fizzbuzz(n: int) -> list[str]:
    """Generate FizzBuzz list from 1 to n."""
    return ['FizzBuzz' if i%15==0 else 'Fizz' if i%3==0 else 'Buzz' if i%5==0 else str(i) for i in range(1,n+1)]

*Latency: 0.95s | Tokens: 55*



**Qwen3-235B** — Score: `100.0%` (llm-as-judge)

*Best approach: concatenation-based, handles all cases correctly.*

> def fizzbuzz(n: int) -> list[str]:
    """Return FizzBuzz from 1..n."""
    out = []
    for i in range(1, n+1):
        s = ''
        if i%3==0: s += 'Fizz'
        if i%5==0: s += 'Buzz'
        out.append(s or str(i))
    return out

*Latency: 0.78s | Tokens: 68*



**Mistral Large** — Score: `70.0%` (llm-as-judge)

*Missing type hints and docstring as requested.*

> def fizzbuzz(n):
    res = []
    for i in range(1, n+1):
        if i % 3 == 0 and i % 5 == 0: res.append('FizzBuzz')
        elif i % 3 == 0: res.append('Fizz')
        elif i % 5 == 0: res.append('Buzz')
        else: res.append(str(i))
    return res

*Latency: 0.88s | Tokens: 65*



**Llama Nemotron 70B** — Score: `90.0%` (llm-as-judge) ⚠️ COI

*Correct with type hints and docstring.*

> def fizzbuzz(n: int) -> list[str]:
    """Compute FizzBuzz up to n."""
    result = []
    for i in range(1, n+1):
        if i % 15 == 0: result.append('FizzBuzz')
        elif i % 3 == 0: result.append('Fizz')
        elif i % 5 == 0: result.append('Buzz')
        else: result.append(str(i))
    return result

*Latency: 1.20s | Tokens: 78*



### Category: Creative Writing

#### Prompt `w01`

**Prompt:**

```
Write a 150-200 word flash fiction about an astronaut who discovers something unexpected on a spacewalk. End with a twist.
```



**DeepSeek-V3** — Score: `92.0%` (llm-as-judge)

*Compelling twist, vivid sensory detail, strong emotional payoff.*

> Commander Reyes floated 200 feet above the ISS, tether anchored, torque wrench in hand. The solar panel replacement was routine — she'd done it seventeen times. Then she saw it: a child's sneaker, bright red, wedged between the truss segments. Impossible. Her heart hammered. She photographed it, transmitted the image. Houston went silent. Three minutes passed. 'Commander, do not touch the object.' She stared at it. One size four. Velcro strap. And a name written in marker on the tongue: her own daughter's name. Back inside, hands shaking, she called home. 'Mom, I left my shoe on the rocket before you launched,' her daughter said. 'I thought it would bring you luck.' The sneaker had clung there for seven months, invisible in the endless junk that orbits Earth. Reyes laughed until she cried,…

*Latency: 2.10s | Tokens: 162*



**Kimi k2.6** — Score: `96.0%` (llm-as-judge)

*Atmospheric, genuinely unsettling twist, excellent prose economy.*

> The EVA was supposed to take forty minutes. Dr. Park had the patch kit in one hand and the universe in her visor. Stars everywhere, merciless and gorgeous. She found the micro-impact site — routine damage, three centimetres. She reached out to apply the patch and her glove touched something warm. In the vacuum of space. Nothing should be warm. She peered closer. A handprint glowed faintly on the hull, small, human-sized. Her radio crackled. Houston, reading her biometrics, asked if she was okay. 'There's a handprint,' she said. 'On the outer hull. Warm.' Long pause. 'Doctor, you're the only human being within 400 kilometres.' She floated back, staring. The handprint faded. Later, reviewing the exterior cameras, the footage showed nothing unusual. Just Park, working alone. No handprint. No …

*Latency: 2.30s | Tokens: 178*



**Qwen3-235B** — Score: `88.0%` (llm-as-judge)

*Good atmosphere and twist, slightly predictable but well-executed.*

> Mission day 203. Yuko tethered herself outside the station and began her inspection. Halfway along the port side, she stopped. Someone had scratched words into the hull. Not erosion, not micrometeorite pitting — deliberate letters: I WAS HERE FIRST. She photographed them, her breath loud in the helmet. Back inside, she showed Commander Ellis. He studied the image for a long time. 'That wasn't there on the last EVA,' he said. 'Three weeks ago.' They checked the crew manifest, the EVA logs. Only four humans had ever worked that section of hull. All four were currently inside the station. All four gathered around the photograph. All four read the words. None of them had written it. And none of them mentioned what they all knew: that their station had been built on the bones of an older one, d…

*Latency: 1.90s | Tokens: 168*



**Mistral Large** — Score: `48.0%` (llm-as-judge)

*Flat prose, underdeveloped characters, weak twist with no real impact.*

> Astronaut John floated outside the space station on a routine maintenance check. The stars were beautiful. Suddenly he noticed something strange attached to the hull. It was a message written in old paint: 'Turn back.' John was confused. Who had written this? When? He reported it to mission control and they said they had no record of anyone writing such a message. John completed his tasks and went back inside. That night, he had strange dreams. The next day, mission control revealed the twist: the message had been written by the previous crew — as a joke before they left. John felt relieved and also a little silly.

*Latency: 1.10s | Tokens: 112*



**Llama Nemotron 70B** — Score: `93.0%` (llm-as-judge) ⚠️ COI

*Pi sequence reveal is clever, tense atmosphere, strong final silence.*

> The panel was supposed to be dead — the whole array shut down after the micrometeorite strike. That's why Sergeant Adisa was out here, in the dark on the night side, alone with her tools and the silence. She replaced the connector, expected nothing. The array lit up. All of it. Every panel, in sequence, like a wave rolling outward. Then the pattern started. Lights blinking. Not randomly. A sequence — 3, 1, 4, 1, 5, 9, 2, 6. She stared. Her helmet display translated it automatically: pi, to eight decimal places. She reported it. Houston ran diagnostics. Fault in the sequencer, they said. Random firing, they said. She watched the array repeat the sequence three more times, perfectly, before it finally went dark. Back inside, she Googled the sequence one more time, just to be sure. Then she c…

*Latency: 2.40s | Tokens: 174*



### Category: Factual Recall

#### Prompt `f01`

**Prompt:**

```
What is the time complexity of quicksort in the average case, and why?
```

**Expected / Reference Answer:**

```
O(n log n) average case. Each partition step is O(n); with a good pivot...
```



**DeepSeek-V3** — Score: `85.0%` (rubric)

*Covered 11/13 expected key terms (85%).*

> Quicksort has O(n log n) average case complexity. The partition step scans the array in O(n). With a random pivot, the array is split into roughly equal halves, creating log n levels of recursion. Each level does O(n) work total. Worst case is O(n²) with sorted input and always picking the first/last element as pivot.

*Latency: 1.30s | Tokens: 68*



**Kimi k2.6** — Score: `92.0%` (rubric)

*Covered 12/13 expected key terms (92%).*

> Average case: O(n log n). The partition is O(n); on average the pivot splits the array in half, yielding log n recursive levels. Total: O(n) × O(log n) = O(n log n). Worst case is O(n²) when pivot is always the min or max.

*Latency: 1.10s | Tokens: 60*



**Qwen3-235B** — Score: `88.0%` (rubric)

*Covered 11/13 expected key terms (88%).*

> O(n log n) on average. Partition is O(n). Good pivot selection leads to balanced splits (log n depth). Worst case O(n²).

*Latency: 0.70s | Tokens: 36*



**Mistral Large** — Score: `77.0%` (rubric)

*Covered 10/13 expected key terms (77%).*

> Quicksort is generally O(n log n) in the average case because partitioning is linear and on average the partitions are reasonably balanced, giving a logarithmic depth. Bad pivot choices lead to O(n²).

*Latency: 0.90s | Tokens: 50*



**Llama Nemotron 70B** — Score: `88.0%` (rubric)

*Covered 11/13 key terms (88%).*

> Quicksort average case is O(n log n). Partition step: O(n). With a pivot near the median, we get log n levels. Total: O(n log n). Worst case O(n²) with already-sorted input.

*Latency: 1.00s | Tokens: 50*



### Category: Reasoning

#### Prompt `r01`

**Prompt:**

```
A farmer has 17 sheep. All but 9 die. How many sheep are left?
```

**Expected / Reference Answer:**

```
9
```



**DeepSeek-V3** — Score: `100.0%` (rubric)

*Exact match bonus.*

> 9 sheep are left.

*Latency: 0.82s | Tokens: 7*



**Kimi k2.6** — Score: `100.0%` (rubric)

*Exact match bonus.*

> There are 9 sheep left.

*Latency: 0.91s | Tokens: 8*



**Qwen3-235B** — Score: `100.0%` (rubric)

*Exact match bonus.*

> 9

*Latency: 0.65s | Tokens: 2*



**Mistral Large** — Score: `0.0%` (rubric)

*No key terms matched.*

> 8 sheep remain.

*Latency: 0.78s | Tokens: 6*



**Llama Nemotron 70B** — Score: `100.0%` (rubric)

*Exact match bonus.*

> 9 sheep are left alive.

*Latency: 0.95s | Tokens: 9*



#### Prompt `r02`

**Prompt:**

```
3-gallon and 5-gallon jug puzzle to get 4 gallons.
```

**Expected / Reference Answer:**

```
Fill 5-gal, pour into 3-gal...
```



**DeepSeek-V3** — Score: `82.0%` (rubric)

*Covered 9/11 expected key terms (82%).*

> Fill the 5-gallon jug. Pour into 3-gallon until full (2 remain). Empty 3-gal. Pour 2 gallons in. Fill 5-gal again, pour 1 gallon to fill 3-gal. 4 gallons remain in 5-gal jug.

*Latency: 1.40s | Tokens: 52*



**Kimi k2.6** — Score: `91.0%` (rubric)

*Covered 10/11 expected key terms (91%).*

> Step 1: Fill the 5-gal jug. Step 2: Pour into 3-gal, leaving 2 gallons. Step 3: Empty 3-gal. Step 4: Pour 2 gallons into 3-gal. Step 5: Fill 5-gal. Step 6: Top off 3-gal (needs 1 more). 5-gal now has 4.

*Latency: 1.20s | Tokens: 60*



**Qwen3-235B** — Score: `87.0%` (rubric)

*Covered 9/11 key terms (87%).*

> Fill 5-gal, transfer to 3-gal (2 remain), empty 3-gal, move 2 to 3-gal, refill 5-gal, top off 3-gal. Result: 4 gallons in 5-gal.

*Latency: 0.88s | Tokens: 44*



**Mistral Large** — Score: `27.0%` (rubric)

*Covered 3/11 expected key terms (27%).*

> Pour water between the two jugs several times until you measure 4 gallons in the 5-gallon container.

*Latency: 0.75s | Tokens: 25*



**Llama Nemotron 70B** — Score: `79.0%` (rubric)

*Covered 9/11 key terms (79%).*

> Fill 5-gallon. Pour into 3-gallon (2 left). Dump 3-gal. Pour 2 into 3-gal. Refill 5-gal. Fill remainder of 3-gal (1 gallon). 4 remain in 5-gal.

*Latency: 1.05s | Tokens: 48*



---

## 🔬 Methodology

**Rubric-based scoring** is used for prompts with a ground-truth `expected` field. Key terms from the expected answer are extracted and matched against the response; coverage ratio forms the base score, with a bonus for exact short-answer matches.



**LLM-as-judge scoring** is used for open-ended prompts (reasoning, creative writing). The judge model `nvidia/llama-3.1-nemotron-70b-instruct` is prompted with a 0–10 scale rubric and its score is normalised to [0, 1]. Prompts where the judge model evaluates its own output are flagged with a conflict-of-interest warning.



**Reproducibility:** Random seeds are pinned per model. Model IDs are recorded verbatim.


