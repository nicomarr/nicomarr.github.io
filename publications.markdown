---
layout: page
title: Publications
permalink: /publications/
---

{% for item in site.data.articles-metadata %}
  <p>{{ item.publication_year }}: {{ item.article_title }}</p>
{% endfor %}


<br>
<br>
Last update: {{ site.data.update-log.last_modified }} | Back to <a href="{{ '/home/' | relative_url }}">Home</a>.