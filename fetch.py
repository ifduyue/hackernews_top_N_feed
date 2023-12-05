import json
import logging
import os
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

import feedparser
import urlfetch
from mako.template import Template


def get_path(dirname=None, filename=None):
    f = os.path.dirname(os.path.abspath(__file__))
    if dirname is not None:
        f = os.path.join(f, dirname)
        if not os.path.isdir(f):
            os.makedirs(f)
    if filename is not None:
        f = os.path.join(f, filename)
    return f


def load_last_entries(num, prefix=None):
    filename = (
        "last_entries.%d" % num if not prefix else "last_entries.%s_%d" % (prefix, num)
    )
    path = Path(get_path("data", filename))
    if path.exists():
        return json.loads(path.read_text())
    else:
        return None


def save_last_entries(obj, num, prefix=None):
    filename = (
        "last_entries.%d" % num if not prefix else "last_entries.%s_%d" % (prefix, num)
    )
    Path(get_path("data", filename)).write_text(json.dumps(obj))


def mb_code(s, coding=None):
    if isinstance(s, str):
        return s if coding is None else s.encode(coding)
    for c in ("utf-8", "gb2312", "gbk", "gb18030", "big5"):
        try:
            s = s.decode(c)
            return s if coding is None else s.encode(coding)
        except:
            pass
    return s


def log(msg, *args):
    def init():
        logger = logging.getLogger("wet")
        handler = logging.FileHandler(get_path("data", "log"))
        formatter = logging.Formatter("[%(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        log.logger = logger
        return logger

    logger = getattr(log, "logger", None)
    if logger is None:
        logger = init()

    logger.debug(msg, *args)


def get_rss_entries(url):
    try:
        log("fetching %s", url)
        r = urlfetch.get(url, timeout=5, randua=True, max_redirects=3)
        log("%d bytes fetched", len(r.body))

        log("parsing feed content")
        d = feedparser.parse(r.body)
        log("parsing OK")
    except Exception as e:
        log("[error] get_rss_entries: %s", str(e))
        return []

    entries = []
    for e in d.entries:
        title = mb_code(e.title)
        href = mb_code(e.links[0]["href"])
        comments = mb_code(e["comments"])

        entry = {
            "title": title,
            "url": href,
            "comments": comments,
            "pubdate": datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"),
        }

        entries.append(entry)

    return entries


def write_rss_file(entries, num, prefix=None):
    tofilename = "top_%d.rss" % num if not prefix else "%s_%d.rss" % (prefix, num)
    log("writing %s", tofilename)
    template = get_path(filename="rss.mako")
    template = Template(
        filename=template, output_encoding="utf-8", encoding_errors="replace"
    )
    content = template.render(
        n=num,
        entries=entries,
        title="%s Top %s Feed" % (prefix or "Hackernews", num),
        url="http://hnfeeds.top/",
        description="%s Top %s Feed, for your convenience"
        % (prefix or "Hackernews", num),
        generator="https://github.com/ifduyue/hackernews_top_N_feed",
    )

    f = get_path("rss", tofilename)
    Path(f).write_bytes(content)


def run():
    log("start.")

    url = "http://news.ycombinator.com/rss"
    all_entries = get_rss_entries(url)

    for num in (1, 3, 5, 10, 15, 20, 25, 30, 512, 1024):
        log("processing top_%d", num)
        last_entries = load_last_entries(num) or []
        last_entries_dict = OrderedDict(
            (entry["comments"], entry) for entry in last_entries
        )
        entries = []
        changed = False

        for entry in all_entries[:num]:
            entry_id = entry["comments"]
            if entry_id in last_entries_dict:
                if entry["title"] != last_entries_dict[entry_id]["title"]:
                    # title changed
                    old_title = last_entries_dict[entry_id]["title"]
                    changed = True
                    log(
                        "[%s.rss][changed] %s title changed from `%s` to `%s`",
                        num,
                        entry["url"],
                        old_title,
                        entry["title"],
                    )
                    last_entries_dict[entry_id]["title"] = entry["title"]
            else:
                log("[%s.rss][new] %s (%s) added", num, entry["title"], entry["url"])
                entries.append(entry)

        if entries or changed:
            maxn = 512 if num <= 512 else 1024
            entries.extend(last_entries[: maxn - len(entries)])
            write_rss_file(entries, num)
            save_last_entries(entries, num)

    log("end.")


def run_lobsters():
    log("start.")

    url = "http://lobste.rs/rss"
    all_entries = get_rss_entries(url)

    for num in (1, 3, 5, 10, 15, 20, 25, 30, 512, 1024):
        log("processing top_%d", num)
        last_entries = load_last_entries(num, prefix="lobsters") or []
        last_entries_dict = OrderedDict(
            (entry["comments"], entry) for entry in last_entries
        )
        entries = []
        changed = False

        for entry in all_entries[:num]:
            entry_id = entry["comments"]
            if entry_id in last_entries_dict:
                if entry["title"] != last_entries_dict[entry_id]["title"]:
                    # title changed
                    old_title = last_entries_dict[entry_id]["title"]
                    changed = True
                    log(
                        "[%s.rss][changed] %s title changed from `%s` to `%s`",
                        num,
                        entry["url"],
                        old_title,
                        entry["title"],
                    )
                    last_entries_dict[entry_id]["title"] = entry["title"]
            else:
                log("[%s.rss][new] %s (%s) added", num, entry["title"], entry["url"])
                entries.append(entry)

        if entries or changed:
            maxn = 512 if num <= 512 else 1024
            entries.extend(last_entries[: maxn - len(entries)])
            write_rss_file(entries, num, prefix="lobsters")
            save_last_entries(entries, num, prefix="lobsters")

    log("end.")


if __name__ == "__main__":
    run()
    run_lobsters()
