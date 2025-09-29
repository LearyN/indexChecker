# sitemap_utils.py
from __future__ import annotations
import io, gzip
from typing import Iterable, Set, List
from urllib.parse import urlparse
import requests
import xml.etree.ElementTree as ET

HEADERS = {"User-Agent": "IndexingChecker/1.0 (+https://example.local)"}

def _fetch_bytes(url: str) -> bytes:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.content
    # 简单判断 gzip：扩展名 .gz 或 响应头
    if url.lower().endswith(".gz") or r.headers.get("Content-Type","").lower().startswith("application/x-gzip"):
        try:
            data = gzip.decompress(data)
        except OSError:
            pass
    return data

def _ns(tag: str) -> str:
    # Sitemap 协议常见命名空间
    return tag

def _parse_xml_urls(xml_bytes: bytes) -> tuple[List[str], List[str]]:
    """
    返回 (sitemap_locs, url_locs)
    兼容：<sitemapindex><sitemap><loc>...</loc></sitemap></sitemapindex>
         <urlset><url><loc>...</loc></url></urlset>
    """
    # 去掉 BOM 与空白
    xml_bytes = xml_bytes.strip()
    root = ET.fromstring(xml_bytes)

    # 去命名空间
    def strip_ns(s: str) -> str:
        return s.split("}",1)[1] if "}" in s else s

    name = strip_ns(root.tag).lower()
    sitemaps, urls = [], []
    if name == "sitemapindex":
        for sm in root.findall(".//"):
            if strip_ns(sm.tag).lower() == "loc" and sm.text:
                sitemaps.append(sm.text.strip())
    elif name == "urlset":
        for u in root.findall(".//"):
            if strip_ns(u.tag).lower() == "loc" and u.text:
                urls.append(u.text.strip())
    else:
        # 某些站点直接给 <urlset> without ns / 或 sitemapindex 不标准
        for loc in root.findall(".//loc"):
            if loc.text:
                urls.append(loc.text.strip())
    return (sitemaps, urls)

def _same_origin(a: str, b: str) -> bool:
    pa, pb = urlparse(a), urlparse(b)
    return (pa.scheme, pa.netloc) == (pb.scheme, pb.netloc)

def collect_urls_from_sitemap(entry_url: str, max_depth: int = 3, same_host_only: bool = True) -> List[str]:
    """
    递归抓取 sitemap 索引，返回 URL 列表（去重）。
    - max_depth：限制索引深度，防止无限递归
    - same_host_only：只保留与 sitemap 同域的 URL
    """
    visited_indexes: Set[str] = set()
    urls: Set[str] = set()
    start = entry_url

    def walk(u: str, depth: int):
        if depth > max_depth: return
        if u in visited_indexes: return
        visited_indexes.add(u)

        data = _fetch_bytes(u)
        sitemaps, url_locs = _parse_xml_urls(data)

        for x in url_locs:
            if not same_host_only or _same_origin(start, x):
                urls.add(x.strip())

        for sm in sitemaps:
            walk(sm.strip(), depth + 1)

    walk(start, 0)
    return sorted(urls)
