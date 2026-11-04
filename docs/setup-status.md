# quetzal setup status (2026-11-02)

**Probably feasible, not yet proven on this machine.** vLLM installed, but PyTorch can't initialise the GPU, so no model has been served and the 6 GB fit is untested.

**Design constraint:** Claude and Grok can't run on vLLM because their weights are closed. vLLM serves a local open model; the app calls Claude or Grok over their APIs.

## Toy example
Local Qwen handles cheap tool calls; harder prompts escalate to Claude or Grok.

```
PyTorch router → vLLM (Qwen2.5-1.5B, localhost:8000), via the OpenAI SDK
               → Claude (claude-opus-5-5), via the anthropic SDK
               → Grok (api.x.ai/v1), via the OpenAI SDK
```

Starting point for the server command, not run yet:

```bash
vllm serve Qwen/Qwen2.5-1.5B-instruct --max-model-len 2048 --max-num-seqs 2 \
  --gpu-memory-utilization 0.8 --enable-auto-tool-choice --tool-call-parser hermes
```

## Hardware
| Item | Status |
|---|---|
| GPU | RTX 4050 with 6 GB VRAM; meets vLLM's compute capability requirement |
| Driver and CUDA | Driver 580 reports CUDA 13.0, but `--torch-backend=auto` installed torch 2.13.0+cu132 (CUDA 13.2). Possible mismatch: if CUDA still fails after the `nvidia_uvm` fix, reinstall with `--torch-backend=cu130` |
| Model fit | 4-bit Qwen 1.5B estimated at about 3.1 GB, but for GGUF, not vLLM |
| RAM | Tight: 7.5 GB with no swap; add swap |
| Disk | Slow: live session on USB, `.venv` is 7.9 GB; move to internal NVMe if possible |
| `/tmp` | 3.8 GB in RAM; keep the Hugging Face cache and builds off it |

## Needed to get the repo working
The repo contained only a README at the start.

### User
1. **Fix the GPU.** `nvidia_uvm` isn't loaded (likely cause of the error) and `nvidia-modprobe` isn't installed:
   ```bash
   sudo modprobe nvidia_uvm && [ -e /dev/nvidia-uvm ] || sudo mknod -m 666 /dev/nvidia-uvm c $(awk '$2=="nvidia-uvm"{print $1}' /proc/devices) 0
   ```
2. **Allow pushes.** No `gh`, SSH key or stored token here. Use a fine-grained token with Contents write on this repo, or an SSH key.
3. **Add API keys.** `ANTHROPIC_API_KEY` and/or `XAI_API_KEY` in `.env` (gitignored). Local-only testing needs neither.

### Claude, once the GPU works
1. Add `pyproject.toml` and `uv.lock`; pin the model revision.
2. Run the server test; record VRAM use and tokens per second.
3. Write the router, with a test that runs from a fresh clone.
4. Check current Grok model IDs against docs.x.ai; sources disagree.

## State at time of writing
- `CLAUDE.md` committed locally as `b0fc865`; push failed for lack of credentials.
- `Voltaire` is a checkout of `quetzal`. Local git identity: `toshichavo <sa_jr@yahoo.com>`.
- 30-minute push job is session-only and expires after 7 days; it can't push until credentials exist.
- `vllm download-kernels` was still running when last checked.

## Sources
- [vLLM GPU install](https://docs.vllm.ai/en/latest/getting_started/installation/gpu.html)
- [Conserving memory](https://docs.vllm.ai/en/latest/configuration/conserving_memory.html)
- [Tool calling](https://docs.vllm.ai/en/latest/features/tool_calling.html)
- [Qwen on RTX 4050 estimate](https://willitrunai.com/can-run/qwen-2.5-1.5b-on-rtx-4050-laptop-6gb)
- [Grok API guide (third-party)](https://www.morphllm.com/grok-api-pricing)
