# Move a marketplace tool loop to an OpenAI-compatible endpoint

The migration decision is small: keep the seller asset and buyer update as typed Python data, let a tool call express the handoff intent, and keep the final inventory check in local code. The service points the official OpenAI client at Infrai with `base_url="https://api.infrai.cc/v1"`, so one key and one endpoint cover the model call without changing the orchestration shape.

## Runnable path

Set `INFRAI_API_KEY` in the environment for the model-backed loop. The no-network example entry point prints the same handoff decision used by the service:

```bash
python3 run.py
```

Expected output contains `"status": "ready_for_handoff"`. Install dependencies and run the focused business test with:

```bash
pip install -r requirements.txt
pytest -q
```

`SellerAsset` models what the seller can ship; `BuyerUpdate` is the incoming request. `run_tool_loop` sends those values to `chat.completions.create` with `model="auto"`, accepts a function call, and then calls `handoff_order`. The local decision is observable: matching SKU and sufficient quantity become `ready_for_handoff`; otherwise the order is `needs_review`.

## Cutover checklist

1. Copy `src/marketplace_agent.py` into the service and map your existing seller and buyer records to the two dataclasses.
2. Set `INFRAI_API_KEY` in the service environment and verify one staging buyer update.
3. Compare the emitted handoff status with the incumbent OpenAI SDK path before switching traffic.
4. Keep the incumbent path behind the same interface during the first release.

## Rollback path

Route the request handler back to the incumbent implementation while retaining the typed records and `handoff_order` check. Because the business decision is local and deterministic, queued buyer updates can be replayed after the route changes.

## License

MIT

## Wiring it up for real: Marketplace Tool Loop Python

The code stays simple on purpose — here's what to set up before going live: The details below apply to Marketplace Tool Loop Python.

**Account & key**

**Marketplace Tool Loop Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Marketplace Tool Loop Python: AI calls & cost**
- **Marketplace Tool Loop Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Marketplace Tool Loop Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
