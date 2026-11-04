# Chromebook (ChromeOS Linux) Career Ops setup

This is a convenience installer for the existing Career Ops integration. It installs prerequisites, Node.js 22, OpenAI Codex CLI, and a separate, local Career Ops workspace. It does **not** run inside GitHub Actions, read your CV, or send messages/applications.

## One Terminal command

In ChromeOS Linux Terminal, run this **as your normal Linux user**:

```bash
curl -fsSLo "$HOME/setup-career-ops.sh" https://raw.githubusercontent.com/Mihir-786/.github.io/main/job_finder/setup_chromebook_career_ops.sh && bash "$HOME/setup-career-ops.sh"
```

This downloads the script to your home folder first, so you can review it with `less ~/setup-career-ops.sh` before running it if you prefer.

The script invokes `sudo apt-get` to install Linux system packages, and may prompt for your Linux password; don't share it. It downloads the official nvm installer (tag v0.40.8) to install a supported Node.js 22 version, installs the official `@openai/codex` CLI with npm, and calls the documented Career Ops initializer `npx @santifer/career-ops init`.

At the end it opens Codex. Choose **Sign in with ChatGPT** on your Chromebook and finish sign-in yourself. Your Career Ops workspace resides in `~/career-ops`; don't publish its private `cv.md`, `data/`, or `reports/` files to the public GitHub repository.

## Integrating job finds

After signing in, download the latest `marketing-jobs` artifact from your existing GitHub Job Finder; it includes `career_ops_candidates.md`. Move that file into **Linux files** in the ChromeOS Files app. In Codex, ask:

> Read `~/career_ops_candidates.md` and import its Pending job URLs into my local Career Ops pipeline, avoiding duplicates. Compare the best five against my real CV, identify recruiters or hiring managers only from verifiable public evidence, and draft LinkedIn notes. Do not send any messages or submit applications. Ask before any external action.

Career Ops is separate from the GitHub workflow; private resume matching and outreach drafts only run after you set up the local workspace and your chosen AI assistant.

## Troubleshooting

- If ChromeOS does not offer Linux development environment, this installer cannot run on that device.
- If you see `command not found: nvm` after a later Terminal restart, run `source ~/.bashrc`.
- The shell syntax is verified by GitHub Actions, but only your actual ChromeOS Linux environment can validate local package installation and ChatGPT sign-in.
- If `~/career-ops` exists, the script leaves its files untouched.
