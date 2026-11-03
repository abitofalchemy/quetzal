# I set up an AI agent you can rebuild from scratch in one command. Here's how.

Most "I installed an AI agent" posts end with "works on my machine." I wanted the opposite: an agent I could wipe and rebuild identically on a Linux laptop and on a Mac mini.

**The agent:** Hermes Agent by Nous Research, an open-source, terminal-based AI agent.

**The rules I set:**
1️⃣ Pin everything: agent version, Python version, model ID.
2️⃣ Minimal tools: file and terminal only, and every risky command needs my approval.
3️⃣ One config file, two machines.
4️⃣ Tests and performance logs from day one.

**The stack**
• Python 3.12 managed by uv (from Astral), with a lockfile committed to git
• hermes-agent 0.19.0, pinned
• OpenRouter for the model (Qwen3-30B-A3B), with Ollama as a local option
• pytest for tests, plus a CSV performance log for each machine

**The trick: separate the hardware from the model.**
One flag picks the machine (`--target linux-dev | mac-m4`), and another picks where the model runs (`--backend openrouter | ollama`). The machine is detected automatically, so the same command runs on both.

**The gotcha that cost me a model choice:**
Hermes refuses any model with less than 64K tokens of context, because its tool descriptions and system prompt take up a large fixed share of every request. My first pick, Qwen3-14B, offers only 41K on OpenRouter, so I switched to Qwen3-30B-A3B (262K context, about $0.10 per million input tokens). For local runs, Ollama has to be started with `OLLAMA_CONTEXT_LENGTH=65536`, or tool calls quietly break.

**Rebuild from zero:**
```
git clone <repo> && cd hermAgent
./scripts/setup.sh        # install, render config, run tests, run health check
uv run hagent chat
```

**Lessons**
→ Read the agent's source before choosing a model; the 64K minimum isn't on any model card.
→ Generate the agent's config from a tracked file instead of hand-editing it.
→ Log performance from day one, so moving to new hardware gets measured instead of guessed.

Results (Linux vs. M4 Pro): coming in the next post.

#AIagents #Python #uv #OpenSource #LLM #DevOps #Reproducibility
