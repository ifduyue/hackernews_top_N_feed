<?xml version="1.0" encoding="UTF-8"?><% from datetime import datetime %>
<rss version="2.0"
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:sy="http://purl.org/rss/1.0/modules/syndication/"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:dc="http://purl.org/dc/elements/1.1/"
     xmlns:wfw="http://wellformedweb.org/CommentAPI/"
     >
  <channel>
    <title>${title}</title>
    <link>${url}</link>
    <description>${description}</description>
    <pubDate>${datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")}</pubDate>
    <generator>${generator}</generator>
    <sy:updatePeriod>hourly</sy:updatePeriod>
    <sy:updateFrequency>1</sy:updateFrequency>
% for entry in entries:
    <item>
      <title>${entry['title']}</title>
      <link>${entry['url']}</link>
      <guid isPermaLink="true">${entry['url']}</guid>
      <description>${entry['title']}</description>
      <content:encoded><![CDATA[<a href="${entry['comments']}" title="${entry['title']} comments">comments</a>]]></content:encoded>
    </item>
% endfor
  </channel>
</rss>
