---
layout: page
title: Tutorials
permalink: /tutorials/
---

{% for post in site.posts %}
  {% if post.categories contains 'tutorials' %}
  <ul>
  <h3><a href="{{ post.url }}">{{ post.title }}</a></h3> 
  Posted on {{ post.date | date: "%b %d, %Y" }}
  </ul>
  {% endif %}
{% endfor %}

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
Back to <a href="{{ '/' | relative_url }}">Home</a>.