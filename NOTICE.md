# Marvis adaptation notice

This repository is a fork of [tandpfun/wardrobe](https://github.com/tandpfun/wardrobe).

The upstream project is distributed under the MIT License. Its copyright and permission notice are preserved in [`LICENSE`](LICENSE). A copy of that license is also included inside the added Skill directory so that the notice remains present when the Skill is extracted independently.

Changes in this fork:

- add `.agents/skills/build-ai-wardrobe` for a Marvis-hosted, no-user-key workflow;
- add an offline `wardrobe.json` to `wardrobe.html` gallery builder;
- add a host-capability-based image workflow that does not bundle or redistribute an undocumented background-removal helper;
- document that the original web importer still requires its own API key.

The added Skill is an adaptation of the upstream `.agents/skills/import-clothes` workflow. It does not claim sole authorship of the upstream design or instructions.
