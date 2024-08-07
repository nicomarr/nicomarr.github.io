---
layout: page
title: Publications
permalink: /publications/
---

{% if site.data.articles-metadata %}
  {% assign publications_by_year = site.data.articles-metadata | group_by: "publication_year" | sort: "name" | reverse %}
  {% for year in publications_by_year %}
    <h3>{{ year.name }}</h3>
    <ul>
      {% for publication in year.items %}
        <ul>
          <ul>{{ publication.first_author_last_name }} <i>et al.</i>, {{ publication.article_title }}. {{ publication.journal }}. {{ publication.publication_year }}</ul>
          <ul>
            {% if publication.doi_url != "not available" %}
              <a href="{{ publication.doi_url }}" target="_blank">Read article</a>
            {% else %}
              DOI not available
            {% endif %}
            |
            {% if publication.pdf_url != "not available" %}
              <a href="{{ publication.pdf_url }}" target="_blank">Download PDF</a>
            {% else %}
              PDF not available
            {% endif %}
            | 
            <a href="{{ publication.cited_by_ui_url }}" target="_blank">Cited by</a>: {{ publication.cited_by_count }}
          </ul>
        </ul>
        <br>
      {% endfor %}
    </ul>
  {% endfor %}
{% else %}
  <p>No publication data available. Make sure data are included in config.yml. </p>
{% endif %}


{{ site.data.update-log.basename }}
<br>
<br>
Last update: {{ site.data.update-log.last_modified }} | Back to <a href="{{ '/home/' | relative_url }}">Home</a>.