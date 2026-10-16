# Pepito AI eval

## Offline (always, CI-friendly)

```bash
cd /root/pepito/bot
uv run pytest tests/unit/test_logic_layer.py tests/unit/test_ai_structured.py -q
# or full judge:
./judge.sh
```

Contracts under test:

| Layer | What |
|---|---|
| `app/logic/rules.json` | limits, pricing, referral, models |
| `app/logic/schemas.py` | TrainingPlan / WeekPlan / Profile / Intent |
| `app/logic/cascade.py` | cheap → escalate ladder |
| `AiService._generate_structured` | validate → retry → fallback |

## Live promptfoo (optional)

```bash
export PATH="/root/.nvm/versions/node/v22.22.2/bin:$PATH"
# requires GEMINI_API_KEY (from bot .env) and promptfoo
set -a; source /root/pepito/bot/.env; set +a
cd /root/pepito/bot/eval
promptfoo eval
promptfoo view
```

Multi-project offline regression (includes pepito unit + subscription QA):

```bash
bash /root/agents/tools/agent_regression.sh pepito
REGRESSION_LIVE=1 bash /root/agents/tools/agent_regression.sh pepito   # + live promptfoo
```

Shared toolkit: `/root/agents/TOOLKIT.md`

Tune assertions in `promptfooconfig.yaml` before changing coach prompts.

## Langfuse (optional)

Set in bot `.env` (no code change required):

```
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
LANGFUSE_HOST=https://cloud.langfuse.com   # if self-hosted, your URL
```

Install only if you enable it: `uv add langfuse` inside the bot image.
Without keys, `app/logic/trace.py` logs structured `ai_call {...}` lines only.
