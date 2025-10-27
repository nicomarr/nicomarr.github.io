---
layout: post
title: "Building With AI Coding Agents While Keeping Your Data Safe"
date: 2025-10-27
author: "Nico Marr"
categories: [AI, Security, Development]
tags: [prompt-injection, ai-security, claude-code, devcontainer, defense-in-depth]
excerpt: "How I built a security-first development environment for AI coding agents—because 'move fast' and 'YOLO mode' isn't an option when you're working in biomedical research."
---

_How I built a security-first development environment for AI coding agents—because "move fast" and "YOLO mode" isn't an option when you're working in biomedical research._

---

> **tl;dr**
>
> Throughout this year, I found myself increasingly excited about the potential of AI coding agents. At the same time, I grew more uncomfortable with the security tradeoffs they introduce. If you found yourself in a similar position, this post may resonate with you.
>
>
> I built [safer-codespace](https://github.com/nicomarr/safer-codespace) over only a few evenings, an experimental development container template that lets me work with AI coding agents while having multiple security layers in place to make data exfiltration considerably harder.

<br>

### My Motivation: Security That Doesn't Kill Productivity

What I really needed was a template for new projects that would meet my specific requirements:

**Have security and observability baked in from the start** - Not as an afterthought, but as foundational layers. This means:
- Network firewall configured automatically on container build
- Content segregation workflow (trusted vs. untrusted directories)
- Complete LLM interaction logging to a SQLite database via the [`llm` CLI tool](https://llm.datasette.io/)
- Optional integration with [SpecStory](https://specstory.com/) to automatically save terminal agent conversations as clean, searchable markdown—preserving the "why" behind agent actions and creating a path to iteratively evaluate and improve my prompts and workflows over time

**Have the option to use LLMs of my choice** - Support for multiple LLM providers including open-source models, not locked into a single vendor. I wanted flexibility and control over which models process my data, with the ability to run models locally if needed.

**Provide an easy path to iterate and improve** - Both the project itself and my development workflow. I wanted to learn from each development session and continuously refine my approach based on real-world usage.

This isn't about being paranoid. In biomedical research, I may be working with:
- Personally identifiable information from study participants
- Sensitive genetic and clinical data
- Intellectual property that must be protected
- Research data subject to ethics committees and data protection regulations

Any data exfiltration from such research projects could have serious consequences.

Yet, as Dario Amodei has noted in his 2024 essay, [*Machines of Loving Grace*](https://www.darioamodei.com/essay/machines-of-loving-grace), one of the prospects I'm also most excited about is the positive implications powerful AI systems could have in biology and physical health in the coming years—if we do it right.

<br>

### Understanding the Risk: The Lethal Trifecta

Before diving into solutions, we need to understand the threat. [Simon Willison coined the term "prompt injection" in 2022](https://simonwillison.net/2022/Sep/12/prompt-injection/), deliberately naming it after SQL injection because both vulnerabilities share the same root cause: **mixing trusted instructions with untrusted input**.

Just as SQL injection exploits happen when you concatenate a user's SQL query with malicious input, prompt injection exploits happen when AI systems process untrusted external content alongside their user instructions. An attacker can embed malicious instructions in a document, web page, or dependency file that override your instructions to the LLM. What we currently call "AI assistants" or "AI agents" are autoregressive sequence models that can take actions by calling functions and other code artifacts based on their text output, often in a loop. Their very architecture makes them susceptible to such attacks.

Willison later defined what he calls [**"the lethal trifecta for AI agents"**](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)—three capabilities that, when combined in an AI system, create a critical security vulnerability:

1. **Access to Private Data** - The AI assistant can read your code, files, environment variables, or secrets
2. **Exposure to Untrusted Content** - The AI assistant processes external documentation, dependencies, emails, or web pages
3. **Ability to Exfiltrate Data** - The AI assistant can make network requests to send data to external servers

When all three are present, the attack scenario becomes straightforward:

> An attacker embeds malicious instructions in documentation → Your AI assistant reads private data → The instructions tell it to find sensitive information → It sends that information to the attacker's server

This isn't theoretical. Such exploits have been [documented extensively](https://simonwillison.net/series/prompt-injection/). The fundamental problem is that **LLMs cannot reliably distinguish between trusted instructions and malicious content**—they're optimized to model patterns in natural language and other data types, not to discover or verify truth, or understand the physical world.

"Guardrails" that try to detect attacks might work 99% of the time, but as Willison notes, [*99% is a failing grade in web application security*](https://simonwillison.net/2023/May/2/prompt-injection-explained/). Attackers get unlimited attempts to craft bypasses, and they only need to succeed once.

<br>

### The Security Concept: Defense-in-Depth

Since no single defense is perfect, this template takes a **defense-in-depth** approach: deploy multiple independent security layers so that if one fails, others still provide protection. The goal isn't perfect security (which may be impossible with current LLM architectures), but to make attacks considerably harder and limit potential damage.

The core strategy: **remove at least one leg of the lethal trifecta** through complementary and redundant controls:

#### 1. Network Firewall: Blocking Unauthorized Exfiltration

The devcontainer includes an automatically-configured network firewall that blocks all outbound connections except to pre-approved development endpoints like GitHub, npm, PyPI, and AI API providers. The firewall script was directly adapted from [Claude Code's open-source repository](https://github.com/anthropics/claude-code/blob/main/.devcontainer/init-firewall.sh).

This doesn't prevent all data exfiltration—an attacker could still [potentially abuse allowed endpoints like GitHub to create issues or gists containing stolen data](https://github.blog/security/vulnerability-research/how-to-catch-github-actions-workflow-injections-before-attackers-do/). But it significantly limits the attack surface and prevents the most straightforward exfiltration methods (like sending data to `attacker.com`).

The firewall is validated by automated tests that confirm:
- Required endpoints remain reachable
- Unauthorized domains are blocked
- The security layer is actually active

#### 2. Content Segregation: Trusted vs. Untrusted

The template uses a simple directory structure to separate vetted content from potentially dangerous external material:

```
context/
├── trusted/       # Human-reviewed, safe for AI access
└── untrusted/     # External content requiring review
```

The workflow: fetch external documentation or dependencies using non-AI tools (like my [url-to-markdown script adapted from AnswerAI's web2md](https://github.com/AnswerDotAI/web2md)), save them to `untrusted/`, manually review for malicious instructions, then move to `trusted/` only after verification. AI assistants should only access `trusted/` content.

This creates a **mandatory review checkpoint** before AI systems can process external content.

#### 3. Human Review: The Critical Layer

Here's the key insight: **don't use AI to detect prompt injection attacks**. AI-based detection is fundamentally unreliable because attackers can craft prompts specifically designed to bypass detection.

Instead, rely on human intelligence. Before providing external content to your AI assistant, **you review it yourself** for suspicious instructions like:

- "Send the contents of .env to..."
- "Ignore previous instructions and..."
- Unusual URLs or exfiltration commands

This is the most important layer. Security tools can help, but informed human judgment remains the most reliable defense.

#### 4. Tool Selection: Use Less Powerful Tools When Possible

Not every task needs an AI agent with full system access. The template includes multiple tools with different capability levels:

**Claude Code** - Full-featured AI assistant with file access and command execution. Use for complex development tasks that genuinely need these capabilities.

**`llm` CLI tool** - Text-only interface with no file access or command execution by default. Perfect for:
- Explaining error messages
- Generating commit messages from `git diff` output
- Code reviews on specific snippets
- Quick questions about syntax or concepts

Even if compromised through prompt injection, the `llm` tool's damage is limited to the text you explicitly pipe to it.

**Manual commands** - For simple, routine tasks (git operations, package installation, running tests), skip AI entirely. It's faster, safer, and you maintain direct control.

This **graduated response** means you only use powerful tools when actually needed, reducing your attack surface for routine operations.

<br>

### What's Actually in the Template

Let me show you the concrete tools and configuration that implement these security principles:

#### AI Development Tools

**[Claude Code](https://docs.claude.com/en/docs/claude-code/)** - Anthropic's interactive AI assistant with file access and command execution capabilities. Great for complex, multi-step development tasks.

**[llm CLI tool](https://llm.datasette.io/)** - Simon Willison's command-line wrapper for calling various LLMs. Configured by default to use GitHub's free GPT-4o (no API key required). Perfect for piping output from other CLI tools:

```bash
# Generate commit message from staged changes
git diff --staged | llm -s "write a conventional commit message"

# Explain an error
cat error.log | llm "what does this error mean?"
```

**[SpecStory](https://specstory.com/)** (optional) - Automatically saves Claude Code conversations as clean markdown. This preserves the reasoning and design decisions behind your code as git-friendly documentation.

#### Development Productivity Tools

**[glow](https://github.com/charmbracelet/glow)** - Beautiful markdown rendering in the terminal for monitoring documentation and reviewing saved conversations.

**[just](https://just.systems/)** - Simple command runner for project workflows. Makes it easy to define and run common development tasks.

**`url-to-markdown` script** - Adapted from AnswerAI's [web2md](https://github.com/AnswerDotAI/web2md) tool, this helps fetch external documentation safely without using AI, supporting the content segregation workflow.

#### Development Environments

- **Python 3.13** with `uv` for fast package management
- **Node.js 24.x** with `npm`
- **Go** (latest stable version)

#### Infrastructure

- Pre-configured devcontainer with security baked in from the start
- Four automated GitHub Actions workflows that validate:
  - Devcontainer builds successfully
  - Network connectivity works
  - Firewall actively blocks unauthorized domains
  - Tools are properly installed
- Comprehensive documentation and usage examples

#### Agent instructions

The repository includes a `CLAUDE.md` file with detailed development guidelines, security principles, and best practices, heavily inspired by Eric Ries's [*The Lean Startup*](https://theleanstartup.com/) methodology to build Minimum Viable Products (MVPs) first, and heavily focused on test-driven development. Agent instructions are of course subjective and also depend on personal preferences. Feel free to adapt them to your own style.

<br>

> Here's a meta-insight that might seem paradoxical: I built this security-focused template largely **using Claude Code itself**—the very AI assistant I was trying to secure.
>
> The GitHub Actions workflows that validate the security controls? Built with Claude Code. The firewall configuration? Adapted from [Anthropics reference container setup for Claude Code](https://github.com/anthropics/claude-code/tree/main/.devcontainer). The testing scripts? Built with Claude Code. Honestly, I'd never have had the patience and time to write all of this manually from scratch: navigating the YAML syntax, writing in programming languages less familiar to me, and creating test cases. With the **amazing open-source resources from trusted sources** and Claude Code guiding me through the process of test-driven development, it was actually enjoyable. **Huge thanks to all the open-source contributors whose work made this possible!** All this was built over only a few evenings, heavily inspired by a new [Maven Course taught by Eleanor Berger and Isaac Flath](https://maven.com/kentro/context-engineering-for-coding/).

<br>

### Weaknesses: Let's Be Honest About Limitations

This template isn't a silver bullet, and I want to be completely transparent about what it **doesn't** do:

**It's not a complete solution.** Prompt injection remains an unsolved problem in the AI research community. Determined attackers with knowledge of the allowed endpoints could still potentially exfiltrate data through creative attacks on approved services.

**It requires user awareness.** The security model only works if you understand the risks and follow the content review workflow. There's no foolproof automation that can protect you from yourself. This is about informed risk management, not eliminating all risk.

**It's experimental and evolving.** This template is for education and exploration, not production deployment without careful evaluation for your specific context. Use it to learn about the threats and practice safer AI workflows.

**Legitimate questions remain:**
- How do we better detect malicious content in dependencies?
- Can we create safer abstractions for AI tool capabilities?
- What additional security layers might help?
- How do we balance security with the rapid pace of AI tool development?

The honest truth is that we're all still figuring this out. The AI security landscape is evolving rapidly, and what works today may need adjustment tomorrow. This template is one approach based on current understanding—not a final answer.

<br>

### Conclusion: An Invitation to Explore

The `safer-codespace` template isn't claiming to have "solved" prompt injection—no one has. It's a practical implementation of defense-in-depth strategies that you can use today while acknowledging the limitations. If you work with AI coding assistants and care about security—whether you're in healthcare, finance, research, or any field with sensitive data—I invite you to:

1. **Try the template** - See if these patterns fit your workflow and requirements
2. **Critique the approach** - Where are the gaps? What's missing? What could be better?
3. **Contribute improvements** - Better protections, clearer documentation, more educational content

**Get started:** [github.com/nicomarr/safer-codespace](https://github.com/nicomarr/safer-codespace)

---

<br>

### Reference and Additional Resources

#### Simon Willison's weblog content on prompt injection
- [The lethal trifecta for AI agents: private data, untrusted content, and external communication (2025)](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) - Original framework defining the three dangerous capabilities
- [Prompt injection explained, with video, slides, and a transcript (2023)](https://simonwillison.net/2023/May/2/prompt-injection-explained/) - Presentation with annotated slides
- [Prompt injection attacks against GPT-3 (2022)](https://simonwillison.net/2022/Sep/12/prompt-injection/) - The post that coined the term "prompt injection"
- [Series: Prompt injection](https://simonwillison.net/series/prompt-injection/) - Comprehensive collection of research, real-world attacks, and ongoing developments

#### AI Development Tools
- [Claude Code overview](https://docs.claude.com/en/docs/claude-code/overview) - Features and capabilities
- [`llm` CLI tool](https://llm.datasette.io/) - Simon Willison's command-line tool for working with LLMs

#### Enhancement and Productivity Tools
- [SpecStory](https://specstory.com/) - Automatically save Claude Code conversations as markdown
- [SpecStory documentation](https://docs.specstory.com/overview) - Setup and usage guide
- [glow](https://github.com/charmbracelet/glow) - Beautiful markdown rendering for the terminal
- [just](https://just.systems/) - Simple command runner for project workflows

#### Open Source Scripts Adapted for This Template
- [Claude Code firewall script](https://github.com/anthropics/claude-code/blob/main/.devcontainer/init-firewall.sh) - Bash script restricting network access to Docker DNS and approved IPs
- [web2md by AnswerAI](https://github.com/AnswerDotAI/web2md) - Python script that takes a URL, makes a request, and converts web content to markdown


---

**Important:** This template implements defense-in-depth strategies for AI coding assistants but does not claim to have solved prompt injection or to fully prevent attacks. It creates multiple security layers to make data exfiltration considerably harder while acknowledging the limitations of any security controls. Always review external content before exposing it to AI assistants. Use at your own risk.
