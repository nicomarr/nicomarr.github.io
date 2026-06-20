---
layout: page
title: Code
permalink: /code/
---

Below is a list of my open-source software contributions:

<section>
    <h3>Safer Codespace</h3>
    <p>A template development environment for working with AI coding agents (<a href="https://docs.claude.com/en/docs/claude-code" target="_blank" rel="noopener noreferrer">Claude Code</a> and <a href="https://pi.dev" target="_blank" rel="noopener noreferrer">Pi</a>) and the <a href="https://llm.datasette.io/" target="_blank" rel="noopener noreferrer">llm CLI</a>, with a defense-in-depth setup that reduces prompt injection and data exfiltration risks. Released under the MIT license.</p>
    <p>
        <a href="{% post_url 2025-10-27-safer-codespace %}">Blog Post</a> |
        <a href="https://github.com/nicomarr/safer-codespace" target="_blank" rel="noopener noreferrer">Source Code on GitHub</a>
    </p>
</section>

<section>
    <h3>Agent Skills</h3>
    <p>Open-source collections of <a href="https://agentskills.io/" target="_blank" rel="noopener noreferrer">Agent Skills</a>, reusable tools that install into Claude Code, Claude Cowork, and other Agent Skills-compatible clients. Each repository is also a GitHub template with a preconfigured devcontainer, so you can open it in GitHub Codespaces with the tools preinstalled and try the skills right away. Released under the MIT license. Source code, plus install and usage instructions, are in each repository's README.</p>
    <ul>
        <li><a href="https://github.com/nicomarr/ai4biomed-skills" target="_blank" rel="noopener noreferrer">ai4biomed-skills</a>: skills for biomedical literature research (PubMed and OpenAlex search with citation enrichment) and research document authoring. Codespaces image preinstalls <a href="https://docs.claude.com/en/docs/claude-code" target="_blank" rel="noopener noreferrer">Claude Code</a>, <a href="https://pi.dev" target="_blank" rel="noopener noreferrer">Pi</a>, and the <a href="https://llm.datasette.io/" target="_blank" rel="noopener noreferrer">llm CLI</a>.</li>
        <li><a href="https://github.com/nicomarr/ai4nonprofit-skills" target="_blank" rel="noopener noreferrer">ai4nonprofit-skills</a>: skills for nonprofit and community-led organizations, such as co-authoring funder-facing documents. Codespaces image preinstalls <a href="https://docs.claude.com/en/docs/claude-code" target="_blank" rel="noopener noreferrer">Claude Code</a> and the <a href="https://llm.datasette.io/" target="_blank" rel="noopener noreferrer">llm CLI</a>.</li>
    </ul>
</section>

<section>
    <h3>Scholaris</h3>
    <p>A Python package that sets up a local research assistant for health and life sciences, leveraging function calling capabilities to analyze scholarly articles and interact with academic databases.</p>
    <p>
        <a href="https://nicomarr.github.io/scholaris/" target="_blank" rel="noopener noreferrer">Documentation</a> |
        <a href="https://pypi.org/project/scholaris/" target="_blank" rel="noopener noreferrer">Project Page on PyPI</a> |
        <a href="https://github.com/nicomarr/scholaris/" target="_blank" rel="noopener noreferrer">Source Code on GitHub</a>
    </p>
    <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; margin: 20px 0;">
        <video autoplay="autoplay" loop="loop" controls muted playsinline preload="auto" class="demo" defaultPlaybackRate="1.2" style="position: absolute; top: 0; left: 0; width: 90%; height: 90%; object-fit: contain;">
            <source src="/assets/media/scholaris-demo.mp4" type="video/mp4">
        </video>
	</div>
    
</section>

<section>
    <h3>OpenAlex API Utils</h3>
    <p>A Python module with helper functions to interact with the <a href="https://docs.openalex.org/how-to-use-the-api/api-overview" target="_blank" rel="noopener noreferrer">OpenAlex API</a>.</p>
    <p>
        <a href="https://nicomarr.github.io/tutorials/2024/08/14/streamlining-full-text-article-retrieval-for-research.html" target="_blank" rel="noopener noreferrer">Tutorial</a> |
        <a href="https://github.com/nicomarr/public-tutorials/blob/main/tutorial01_streamlining_full_text_article_retrieval_for_research.ipynb" target="_blank" rel="noopener noreferrer">Notebook</a> |
        <a href="https://github.com/nicomarr/public-tutorials/blob/main/openalex_api_utils.py" target="_blank" rel="noopener noreferrer">Source Code on GitHub</a>
    </p>
</section>

<p style="margin-top: 40px;">Back to <a href="{{ '/' | relative_url }}">Home</a>.</p>