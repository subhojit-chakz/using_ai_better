# Using AI Better

A personal system for understanding AI usage, project costs, and progress across Windows, Linux, and cloud machines.

## Documents

- [Personal system design](docs/SYSTEM_DESIGN.md): the intended topology, daily workflow, weekly dashboard, and rollout for this setup.
- [Reusable specification](docs/REPLICATION_SPEC.md): requirements, data contracts, accounting rules, setup steps, and acceptance criteria for building a similar system with your own agents.

Status: documentation and proposed implementation specification, dated 2026-10-21. No collectors, dashboard application, scheduled jobs, SSH configuration, or provider integrations are installed by this repository.

Clone this repository into a directory of your choice.

Start with one Windows machine, one Linux machine, and one project. Validate usage and cost attribution before adding cloud jobs and automated weekly summaries.

## Visual walkthrough

- [Looping animation and diagram](media/index.html): local viewer with a looping MP4 and a project-by-model token diagram.
- [Media details and editable source](media/README.md): formats, sample data, and rendering instructions.

The visuals use illustrative data; they do not show collected account activity.

## Accounting principles

Recorded tokens, estimated tokens, provider charges, subscription allocations, and cloud compute charges are separate measures. Missing data remains unknown. A shared account does not automatically provide complete usage logs or project attribution.

Keep credentials, private logs, databases, generated reports, datasets, and checkpoints outside Git. Keep the active database outside cloud-synchronized folders; back it up as a consistent snapshot.
