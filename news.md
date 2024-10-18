---
layout: page
title: News
---

<div class="card border-0">
  {% assign news = site.news | sort: 'date' | reverse %}
  {% for new in news %}

  <div class="row">
    <div class="col-12 col-sm-3">
      <strong>{{ new.date | date: "%d %b %Y"}}</strong>
    </div>
    <div class="col-12 col-sm-9">
      {{ new.content }}
    </div>
  </div>




  {% endfor %}
</div>

<!-- <a class="twitter-timeline" href="https://twitter.com/####?ref_src=twsrc%5Etfw">Tweets by ####</a> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script> -->