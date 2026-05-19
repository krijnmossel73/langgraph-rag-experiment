# Agent design patterns

Several recurring patterns appear in production agent systems.

**ReAct.** The agent alternates between reasoning steps (free-text thoughts) and acting steps (tool calls). Simple to implement and debug, but token-heavy and prone to long unproductive loops without good stopping criteria.

**Plan-and-execute.** A planner produces a multi-step plan up front. An executor walks the plan, calling tools as needed. Replanning is triggered on failure. More predictable than ReAct, but the plan can go stale if the world changes mid-run.

**Reflection.** The agent produces an answer, then a critic step inspects it for errors or missing information. The original answer is revised based on the critique. Adds latency, but improves accuracy on tasks where mistakes are systematic.

**Router.** A lightweight classifier dispatches the query to one of several specialised sub-agents or tools. Useful when a single agent's prompt becomes unmanageable.

**Multi-agent (supervisor).** A supervisor agent delegates sub-tasks to specialised worker agents and aggregates their outputs. Powerful, but coordination cost grows quickly with the number of workers.

In practice, production agents usually combine several of these — for example, a router selecting between a plan-and-execute agent and a single-shot RAG path.
