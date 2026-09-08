# NEVERMIND.skill

[简体中文](README.md) | **English**

<div align="center">
  <img src="https://img.shields.io/github/stars/barinfo/NEVERMIND.skill?style=social&label=Stars" alt="GitHub Stars" />
  <img src="https://img.shields.io/github/forks/barinfo/NEVERMIND.skill?style=social&label=Forks" alt="GitHub Forks" />
  <img src="https://img.shields.io/github/watchers/barinfo/NEVERMIND.skill?style=social&label=Watchers" alt="GitHub Watchers" />
  <img src="https://img.shields.io/github/license/barinfo/NEVERMIND.skill?color=blue" alt="License: MIT" />
  <img src="https://img.shields.io/github/repo-size/barinfo/NEVERMIND.skill" alt="Repo Size" />
  <img src="https://img.shields.io/github/commit-activity/m/barinfo/NEVERMIND.skill?color=green" alt="Commit Activity" />
</div>

<p align="center">
  <img src="assets/nevermind-logo.png" alt="NEVERMIND — awkward laughing yellow face chasing a dollar bill" width="220" /><br/>
  <em>An awkward laughing yellow face, underwater, chasing a dollar bill with an exclamation mark.<br/>
  At this moment you don't need to count — you only need <strong>NEVERMIND</strong>: a confession room that laughs at the AI bill.</em>
</p>

<div align="center" style="background-color: #1a1a2e; color: #eaeaea; border-radius: 12px; padding: 24px 16px; border: 1px solid #3a3a5e;">

# 😅💵⚠️ NEVERMIND · Cyber Merit Settlement

**Turn today's burned AI tokens into an awkward-but-relieved 'cyber merit', then let it go.**

</div>

`NEVERMIND` is a skill that makes an AI agent broadcast **how many AI tokens you burned today** in the tone of an awkward laughing yellow face. It does not save you money, no leaderboard, no competitor surveillance — it reads your usage, translates it wryly, then tells you: never mind.

It talks to [tokens.ci](https://tokens.ci) when real numbers exist; otherwise it plainly says so — awkward self-report or plain meme, never a fake local ledger. It is an end-credits line, not a popup.

| | |
|---|---|
| 📄 Format | Markdown Skill (frontmatter `SKILL.md`) + `skill.json` metadata |
| 🧩 Compatible | Claude Code / Codex / DSH presets / WorkBuddy / any agent that loads Markdown skills |
| 🌏 Language | 简体中文 (README default, playful voice); English |
| ⚖️ License | MIT |

> ⚠️ **NOT a tokens.ci official project.** NEVERMIND is a third-party fun skill: it only reads the totals your **tokens.ci official CLI** has already aggregated locally, to joke about them. It is not made by, affiliated with, endorsed by, or a partner of tokens.ci — passed off as someone else's official thing, it wouldn't even be honest fun. No organizational relation to the `camelot` Python PDF library or to Nirvana's work, either.

---

## What this is

`nevermind` is a skill that makes your AI agent broadcast **how many AI tokens you burned today** in the tone of an awkward yellow face.

It does not save you money. It does not give you a leaderboard. It does not surveil your competitors. It does one thing:

**Read out today's burned token total, the models you used, an estimated dollar cost — then end with NEVERMIND so you can laugh and let it go.**

Real numbers come **only** from tokens.ci (tightly bound; no separate local ledger), and "unreadable" is never made to look like a failure:

| Tier | Source | Accuracy |
|---|---|---|
| 🥇 Tier 1 | Local `tokens` CLI (tokens.ci official) via `tokens submit --dry-run` | Real numbers |
| 🥈 Tier 2 | tokens.ci absent/unreadable → say so plainly: awkward self-report (manual) or pure-meme sign-off | Honest |
| 🥉 Tier 3 | Awkward self-report — you estimate, we still settle | Enough |

## Install

### 1. Use it directly (in any supporting agent)

Load the `nevermind.skill/` directory as a skill. How you actually install a skill depends on your agent:

- **WorkBuddy / Claude Code**: point the agent at `SKILL.md`, or drop it under `~/.workbuddy/skills/nevermind/`.
- **Other agents**: place it wherever that agent expects skills.

### 2. (Optional, recommended) get real numbers

Cross-platform install commands for the [tokens.ci official CLI](https://tokens.ci/docs) (**not mac-only**):

```bash
# macOS
brew install owo-network/brew/tokens

# Linux (installs a systemd user service that runs in the background)
curl -fsSL https://tokens.ci/install.sh | sh

# Windows / one-off anywhere (Node 18+ or Bun)
npx tokens-cli@latest login
# or: bunx tokens-cli@latest login

# global, cross-platform
npm i -g tokens-cli
```

Run `tokens login` once (links your GitHub). After that, dry-run gives you real numbers. **nevermind only ever calls `tokens submit --dry-run` — it will never submit on your behalf.**

> **⛩️ Host gate**: tokens.ci only recognizes its official supported hosts (built-in list `data/supported-hosts.txt`, 43 clients, incl. Claude Code / Codex / Cursor / Cline / **WorkBuddy**). **If the current host is NOT on the list, nevermind refuses to start any behavior** — even if force-started or driven by a loop/orchestrator. It does not fake a cyber-merit settlement.
>
> Judgment uses the **offline built-in list** (no network). `support_cache.json` (gitignored) is only refreshed on first contact of each new session, on a **~3 day** cadence, by checking tokens.ci for official list changes; offline / before expiry, it uses the built-in list. To know if your current agent is supported, just ask it "is my host supported?" for an instant answer.
>
> The online re-check runs via the bundled script: `python3 scripts/refresh_support.py` (stdlib only, no pip; on drift it rewrites the built-in list from the official source and refreshes the cache; it never fakes success on network failure). Use `--dry-run` to compare without writing. A curl fallback is documented in the script header (only if Python's direct HTTPS path is blocked).
>
> Note the difference: **gate (host unsupported → refuse everything)** ≠ **degrade (host supported but no numbers right now → only then awkward self-report / pure-meme sign-off)**. If the gate fails, there is no degrade either.

> **🔌 Startup env check** (second gate, after host gate passes): checks whether this machine has any runtime env that can run tokens.ci (`cli` / `node` / `bun` / `npm`).
> - **None of the four present** → refuse to start, with the meme: "家里怎么一个家具也没有，难不成我睡地板吗？……"
> - **Has env but no tokens.ci found anywhere** → auto-install (user-authorized exception), then proceed.
> - **Installed but not logged into GitHub** → prompt to log in with GitHub; `ask` for consent before running login.
> - Else: expired login token, auto-install failure (plainly say "can't install", degrade to self-report/pure-meme, no hard error), outdated version.
>
> Passing the check ≠ real numbers guaranteed — it only means "ready to start gracefully"; actual reading still runs Tier-1 real numbers, else self-report / pure-meme.

## Usage

**Mostly automatic.** When a project / task genuinely wraps up, or roughly every 16 turns, nevermind surfaces a cyber-merit settlement at the very end of the finished work — as the closing credits, not a popup. It never interrupts in-progress work.

**You can also call it manually** by saying anything with "nevermind" or "赛博功德" (cyber merit):

- "nevermind it"
- "how many tokens did I burn today"
- "settle my cyber merit"
- "show me my AI bill"
- "money's gone again"

Automatic or manual, it **ends in NEVERMIND every single time**.

## Sample broadcast

> 😅💵⚠️ Today's cyber merit settlement · 2026-09-09
> 
> Today you burned 1,145,141,919,810 tokens inside Codex CLI, on models like GPT-6-Astra + GPT-5.6-Luna — that's 1.145 TB.
> 
> Enough to:  
>   • write 87 novels,  
>   • train a small domain model from scratch,  
>   • read *War and Peace* aloud 2,847 times.
> 
> In dollars… about 214 iced lattes.  
> 
> Your cyber merit is recorded on tokens.ci ✨  
> But…… **NEVERMIND**! 😅  
> It's all on the record, and you did your best today. Go to sleep.

More samples in [`examples/demo-broadcast.md`](./examples/demo-broadcast.md).

## What it is NOT

- ❌ Not a cost-saver — no optimization advice
- ❌ Not a leaderboard — no comparison with others
- ❌ Not a competitor surveillance radar — that's not Nevermind's job
- ❌ Not your bank statement — estimates only, no tax reports

**It is: a confessional where you laugh awkwardly at your AI bill.**

## Docs

- [`SKILL.md`](./SKILL.md) — main behavior file (this is what the agent actually reads, incl. the host gate)
- [`skill.json`](./skill.json) — metadata / triggers / data sources / gate config / privacy promise
- [`data/supported-hosts.txt`](./data/supported-hosts.txt) — R3 built-in authoritative host list (official 43 clients, offline instant judgment)
- [`scripts/refresh_support.py`](./scripts/refresh_support.py) — host-list online refresh script (C3 backend; stdlib-only, curl fallback in header)
- [`docs/BANTEDEX.md`](./docs/BANTEDEX.md) — full banter lexicon, magnitude tiers, golden lines (PR to add more)
- [`examples/demo-broadcast.md`](./examples/demo-broadcast.md) — real broadcast samples

## Privacy

- **Never uploads on your behalf.** `tokens submit --dry-run` is preview only.
- **Never reads prompts, code, or file contents.** Only aggregate token counts and model names.
- **Never invents a fake local ledger** — the only real counts live in tokens.ci; if it is absent there is no "local record" to read.
- **There is no channel to upload a potentially fabricated ledger** — tokens.ci accepts only the real totals its own official CLI scans; third-party made-up/self-reported data is neither accepted by it, nor provided, nor uploaded by this skill.
- The data is only about your own "cyber merit" — never transmitted, never compared.

## License

MIT — fork it, mod it, PR more banter.

*The yellow-face-chasing-a-dollar logo is original artwork by Barinfo, free to reuse with this skill.*
