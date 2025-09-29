from typing import Dict, Any, List
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from urllib.parse import urlparse

def build_service(creds: Credentials):
    return build("searchconsole", "v1", credentials=creds)

def list_sites(creds: Credentials) -> List[str]:
    svc = build_service(creds)
    sites = svc.sites().list().execute().get("siteEntry", [])
    # 仅返回你已验证且权限为 siteRestricted/owner 的属性
    return [s["siteUrl"] for s in sites if s.get("permissionLevel") in ("siteOwner", "siteFullUser")]

def site_matches_url(site_url: str, page_url: str) -> bool:
    # 仅做基本匹配；Domain属性如 "sc-domain:example.com" 由 API 负责识别
    if site_url.startswith("sc-domain:"):
        host = urlparse(page_url).hostname or ""
        return host.endswith(site_url.replace("sc-domain:", ""))
    # URL-prefix：必须以其为前缀
    return page_url.startswith(site_url)

def inspect_url(creds: Credentials, site_url: str, page_url: str) -> Dict[str, Any]:
    svc = build_service(creds)
    body = {"inspectionUrl": page_url, "siteUrl": site_url, "languageCode": "en-US"}
    resp = svc.urlInspection().index().inspect(body=body).execute()
    idx = resp.get("inspectionResult", {}).get("indexStatusResult", {})
    return {
        "coverageState": idx.get("coverageState"),
        "verdict": idx.get("verdict"),
        "pageFetchState": idx.get("pageFetchState"),
        "robotsTxtState": idx.get("robotsTxtState"),
        "indexingState": idx.get("indexingState"),
        "lastCrawlTime": idx.get("lastCrawlTime"),
        "referringUrls": ";".join(idx.get("referringUrls", [])),
    }

def map_status(row: Dict[str, Any]) -> str:
    cov = (row.get("coverageState") or "").lower()
    if "indexed" in cov:
        return "indexed"
    if "not indexed" in cov or "duplicate" in cov or "crawled" in cov or "discovered" in cov:
        return "not_indexed"
    return "unknown"

def advice(row: Dict[str, Any]) -> str:
    hints = []
    pfetch = (row.get("pageFetchState") or "").lower()
    robots = (row.get("robotsTxtState") or "").lower()
    cov = (row.get("coverageState") or "").lower()

    if "soft 404" in pfetch or "not found" in pfetch:
        hints.append("检查内容质量/状态码；避免软404或404。")
    if "blocked" in robots:
        hints.append("robots.txt 阻塞抓取，建议放开。")
    if "duplicate" in cov:
        hints.append("重复内容/Canonical 异常，检查 rel=canonical。")
    if "discovered – currently not indexed" in cov:
        hints.append("加强站内链接与sitemap；可手动请求收录。")
    if not hints:
        hints.append("检查标题/正文、内部链接与sitemap提交。")
    return " | ".join(hints)
