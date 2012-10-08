<?xml version="1.0" encoding="UTF-8"?><% from datetime import datetime %>
<rss version="2.0"
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:sy="http://purl.org/rss/1.0/modules/syndication/"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:dc="http://purl.org/dc/elements/1.1/"
     xmlns:wfw="http://wellformedweb.org/CommentAPI/"
     >
  <channel>
    <title>${title | x}</title>
    <link>${url | x}</link>
    <description>${description | x}</description>
    <lastBuildDate>${datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT") }</lastBuildDate>
    <generator>${generator | x}</generator>
    <atom:link href="http://hackernews.lyxint.com/top_${n}.rss" rel="self" type="application/rss+xml" />
    <sy:updatePeriod>hourly</sy:updatePeriod>
    <sy:updateFrequency>1</sy:updateFrequency>
% for entry in entries:
    <item>
      <title>${entry['title'] | x}</title>
      <link>${entry['url'] | x}</link>
      <pubDate>${entry['pubdate']}</pubDate>
      <guid isPermaLink="false">${entry['title'] | x} - ${entry['url'] | x}</guid>
      <description>${entry['title'] | x}</description>
      <content:encoded><![CDATA[<a href="${entry['comments'] | x,h}" title="${entry['title'] | x,h} comments">comments</a>]]></content:encoded>
    </item>
% endfor
  </channel>
</rss>
