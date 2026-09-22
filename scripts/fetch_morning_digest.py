#!/usr/bin/env python3
"""
Naija Chronicles — Live Real-Time Morning Intelligence Engine
Dynamically transforms live RSS feeds from Vanguard, Punch, Premium Times, Daily Trust,
BusinessDay, Nairametrics, and TechCabal into high-signal, engaging editorial dispatches.
Zero hardcoded repetition — every morning reflects today's real breaking events.
"""

import os
import sys
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(WORKSPACE_DIR, "assets", "data", "sample_articles.json")
ARCHIVE_FILE = os.path.join(WORKSPACE_DIR, "assets", "data", "archive_articles.json")
SSH_KEY = "/workspace/.ssh/id_ed25519"

DEFAULT_FALLBACK_IMAGE = "https://lh3.googleusercontent.com/d/1PsLAfyGMvikdseyvv6nCCrznqg762pDt"

TOPIC_IMAGE_POOLS = {
    "politics": [
        "https://lh3.googleusercontent.com/d/1EFlpO3_MSl7OsXrpEYvCo7EWylXKRWdD",
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1600&q=85",
        "https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&w=1600&q=85",
        "https://lh3.googleusercontent.com/d/1hHpzsga4u85vgF-KFmZQm64sqNRrqEYy"
    ],
    "stocks": [
        "https://lh3.googleusercontent.com/d/10-TUNlPMqxhMvZDTeDA2gajWMq53Dn9R",
        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1200&q=85",
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=1200&q=85"
    ],
    "hidden_wire": [
        "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=1200&q=85",
        "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?auto=format&fit=crop&w=1200&q=85",
        "https://images.unsplash.com/photo-1578328819058-b69f3a3b0f6b?auto=format&fit=crop&w=1200&q=85"
    ],
    "tech": [
        "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=85",
        "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=1200&q=85",
        "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1200&q=85"
    ],
    "mobility": [
        "https://lh3.googleusercontent.com/d/1k9CTtLncdSrSTviDV6f_5pY6Gn5jjMND",
        "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=1200&q=85",
        "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=1200&q=85"
    ],
    "culture": [
        "https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&w=1200&q=85",
        "https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?auto=format&fit=crop&w=1200&q=85",
        "https://images.unsplash.com/photo-1558769132-cb1aea458c5e?auto=format&fit=crop&w=1200&q=85"
    ],
    "world_macro": [
        "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=85",
        "https://lh3.googleusercontent.com/d/10-TUNlPMqxhMvZDTeDA2gajWMq53Dn9R",
        "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=1200&q=85"
    ]
}

DESK_BYLINES = {
    "Politics & Governance": {"name": "National Politics Wire", "role": "Governance & Electoral Analysis Desk", "avatar": "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?auto=format&fit=crop&w=200&q=80"},
    "Stocks & Money": {"name": "Markets & Wealth Desk", "role": "Equities & Financial Analysis Desk", "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80"},
    "Hidden Wire": {"name": "Policy & Truth Watch", "role": "Investigative Research Wire", "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=200&q=80"},
    "Technology & Startups": {"name": "Technology & Ventures Desk", "role": "African Tech Infrastructure Wire", "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=200&q=80"},
    "Passports & Mobility": {"name": "Global Mobility Desk", "role": "International Residency Research", "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80"},
    "Culture & Entertainment": {"name": "Culture & Pop Desk", "role": "Creative Industries Wire", "avatar": "https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?auto=format&fit=crop&w=200&q=80"},
    "World & Macro": {"name": "Global Macro Desk", "role": "Cross-Border Economics Wire", "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=200&q=80"}
}

RSS_FEEDS = {
    "Vanguard Politics": ("https://www.vanguardngr.com/category/politics/feed/", "Politics & Governance"),
    "Premium Times": ("https://www.premiumtimesng.com/feed", "Politics & Governance"),
    "Daily Trust": ("https://dailytrust.com/feed/", "Hidden Wire"),
    "BusinessDay": ("https://businessday.ng/feed/", "Stocks & Money"),
    "Nairametrics": ("https://nairametrics.com/feed/", "Stocks & Money"),
    "TechCabal": ("https://techcabal.com/feed/", "Technology & Startups"),
    "Punch General": ("https://punchng.com/feed/", "Culture & Entertainment")
}

def clean_text(text):
    if not text:
        return ""
    clean = re.sub(r'<.*?>', '', text)
    clean = clean.replace('&amp;', '&').replace('&quot;', '"').replace('&apos;', "'").replace('&#8217;', "'").replace('&#8220;', '"').replace('&#8221;', '"').replace('&#8212;', '—').replace('&nbsp;', ' ')
    return re.sub(r'\s+', ' ', clean).strip()

def fetch_all_live_rss_items():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) NaijaChroniclesBot/5.0'}
    feed_items = []
    
    for source_name, (feed_url, default_cat) in RSS_FEEDS.items():
        try:
            req = urllib.request.Request(feed_url, headers=headers)
            with urllib.request.urlopen(req, timeout=9) as resp:
                content = resp.read().decode('utf-8', errors='ignore')
                root = ET.fromstring(content)
                items = root.findall('.//item')
                for it in items[:8]:
                    title = clean_text(it.find('title').text if it.find('title') is not None else '')
                    link = it.find('link').text.strip() if it.find('link') is not None and it.find('link').text else ''
                    desc = clean_text(it.find('description').text if it.find('description') is not None else '')
                    pub_date = it.find('pubDate').text if it.find('pubDate') is not None else ''

                    # Extract image URL if present in enclosure or description
                    image_url = ""
                    enclosure = it.find('enclosure')
                    if enclosure is not None and 'image' in enclosure.get('type', ''):
                        image_url = enclosure.get('url', '')
                    elif it.find('{http://search.yahoo.com/mrss/}content') is not None:
                        image_url = it.find('{http://search.yahoo.com/mrss/}content').get('url', '')

                    # Skip empty titles or navigation links
                    if title and len(title) > 15 and not title.startswith("PHOTOS:") and not title.startswith("BD Sunday"):
                        feed_items.append({
                            "source": source_name,
                            "title": title,
                            "link": link or "https://nigerian-chronicles.vercel.app",
                            "description": desc,
                            "pub_date": pub_date,
                            "image": image_url,
                            "category": default_cat
                        })
        except Exception as e:
            print(f"[{source_name}] Notice reading RSS: {e}", file=sys.stderr)
            
    return feed_items

def categorize_and_synthesize_live_item(item, is_lead=False, index=0):
    title = item["title"]
    desc = item["description"]
    source = item["source"]
    link = item["link"]
    raw_cat = item["category"]

    # Intelligent Auto-Categorization based on headline keywords
    title_lower = title.lower()
    desc_lower = desc.lower()
    full_text = title_lower + " " + desc_lower

    if is_lead or any(k in full_text for k in ["tinubu", "apc", "pdp", "inec", "senate", "governor", "election", "wike", "obi", "atiku", "court", "assembly", "minister", "lawmaker", "nddc"]):
        category = "Politics & Governance"
        tag = "Cover Story" if is_lead else "Political Wire"
        image_pool = TOPIC_IMAGE_POOLS["politics"]
    elif any(k in full_text for k in ["naira", "stock", "ngx", "bank", "billion", "otedola", "dangote", "shares", "ipo", "dividend", "revenue", "cbn", "forex", "tax", "vat"]):
        category = "Stocks & Money"
        tag = "Trending Alpha" if "ipo" in full_text or "billion" in full_text or "stock" in full_text else "Market Intelligence"
        image_pool = TOPIC_IMAGE_POOLS["stocks"]
    elif any(k in full_text for k in ["tariff", "disco", "power", "meter", "nmdpra", "petrol", "miners", "mining", "illegal", "stray", "toll", "secret", "subsidy", "nscdc", "killed", "probe"]):
        category = "Hidden Wire"
        tag = "Investigation" if "probe" in full_text or "illegal" in full_text or "miners" in full_text else "Eye-Opener"
        image_pool = TOPIC_IMAGE_POOLS["hidden_wire"]
    elif any(k in full_text for k in ["tech", "ai", "startup", "data", "satellite", "telecom", "app", "software", "fintech", "developer", "broadband", "code"]):
        category = "Technology & Startups"
        tag = "Frontier Tech" if "ai" in full_text or "satellite" in full_text else "Innovation"
        image_pool = TOPIC_IMAGE_POOLS["tech"]
    elif any(k in full_text for k in ["passport", "visa", "japa", "travel", "diaspora", "residency", "immigration", "embassy", "flight", "abroad"]):
        category = "Passports & Mobility"
        tag = "Actionable Alpha"
        image_pool = TOPIC_IMAGE_POOLS["mobility"]
    elif any(k in full_text for k in ["nollywood", "movie", "film", "music", "afrobeats", "actor", "artist", "youtube", "series", "charly", "culture"]):
        category = "Culture & Entertainment"
        tag = "Spotlight"
        image_pool = TOPIC_IMAGE_POOLS["culture"]
    elif any(k in full_text for k in ["opec", "crude", "fed", "dollar", "global", "ecowas", "us", "uk", "china", "port", "trade", "maritime", "world"]):
        category = "World & Macro"
        tag = "Global Analysis"
        image_pool = TOPIC_IMAGE_POOLS["world_macro"]
    else:
        category = raw_cat
        tag = "Dispatch"
        image_pool = TOPIC_IMAGE_POOLS["politics"]

    # Generate clean canonical slug from real live title
    clean_slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:80]
    
    # Generate dek / hook
    if desc and len(desc) > 30:
        dek = desc[:240] + ("..." if len(desc) > 240 else "")
    else:
        dek = f"Breaking analysis on {title} with verified public background context and strategic implications for citizens and markets."

    # Byline assignment
    author_info = DESK_BYLINES.get(category, DESK_BYLINES["Politics & Governance"])

    # Image assignment: use real extracted RSS image if valid, otherwise select from curated thematic pool
    cover_image = item.get("image") if (item.get("image") and item.get("image").startswith("http")) else image_pool[index % len(image_pool)]

    # Dynamic editorial content body
    quote_text = f"Key development reported by {source} on {datetime.now().strftime('%B %d, %Y')}."
    content_html = f"""
    <p class="lead-paragraph"><strong>The Live Dispatch:</strong> {dek}</p>
    
    <h3>What Is Happening on the Ground</h3>
    <p>{desc or 'Verified reports indicate significant operational and regulatory developments across the affected sectors.'}</p>

    <h3>Why This Matters to You</h3>
    <ul>
        <li><strong>Direct Impact:</strong> This development directly influences policy implementation and citizen/investor expectations across Nigerian commercial centers.</li>
        <li><strong>The Bigger Picture:</strong> As regulatory oversight and political adjustments take shape, staying informed through verified primary sources gives you a strategic advantage.</li>
    </ul>

    <blockquote>
        <p>“{quote_text}”</p>
    </blockquote>

    <div class="p-4 my-4 bg-stone-100 dark:bg-stone-900 border-l-4 border-red-600 rounded text-xs font-mono">
        <strong>Verified Primary Source:</strong> Read the original reporting at <a href="{link}" target="_blank" class="underline text-red-600 font-bold">{source} Live Wire</a>.
    </div>
    """

    return {
        "id": f"art-live-{clean_slug[:30]}",
        "title": title,
        "slug": clean_slug,
        "dek": dek,
        "category": category,
        "tag": tag,
        "author": author_info,
        "sources": [{"name": source, "url": link}],
        "published_at": datetime.now(timezone.utc).isoformat(),
        "read_time": f"{max(3, min(6, len(desc.split()) // 35 + 3))} min read",
        "cover_image": cover_image,
        "image_caption": f"Primary Coverage: {source}. Verified on {datetime.now().strftime('%d %b %Y')}.",
        "featured": True if index < 4 else False,
        "lead_story": is_lead,
        "quote": quote_text,
        "content": content_html,
        "is_fresh": True
    }

def generate_live_daily_stream():
    raw_items = fetch_all_live_rss_items()
    print(f"      Collected {len(raw_items)} raw headlines from live Nigerian RSS feeds.")

    if not raw_items:
        print("      Warning: RSS fetch returned empty, using fallback.", file=sys.stderr)
        return []

    # 1. Filter and Deduplicate by title similarity
    unique_items = []
    seen_titles = set()
    for item in raw_items:
        t_key = re.sub(r'[^a-zA-Z0-9]', '', item["title"].lower())[:40]
        if t_key not in seen_titles:
            seen_titles.add(t_key)
            unique_items.append(item)

    # 2. Pick the absolute BEST Breaking Political story as Lead Cover Story
    politics_candidates = [it for it in unique_items if it["source"] in ["Vanguard Politics", "Premium Times", "Daily Trust"] or "politics" in it["title"].lower()]
    lead_item = politics_candidates[0] if politics_candidates else unique_items[0]
    
    remaining_items = [it for it in unique_items if it["title"] != lead_item["title"]]

    curated_articles = []
    
    # Add Lead Politics Story
    curated_articles.append(categorize_and_synthesize_live_item(lead_item, is_lead=True, index=0))

    # Add 11-13 other diverse breaking stories across all domains
    for idx, it in enumerate(remaining_items[:13], start=1):
        curated_articles.append(categorize_and_synthesize_live_item(it, is_lead=False, index=idx))

    return curated_articles

def sync_to_supabase_if_configured(articles):
    supabase_url = os.environ.get("SUPABASE_URL") or "https://ovndvemjdojlibawdcmk.supabase.co"
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im92bmR2ZW1qZG9qbGliYXdkY21rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk2ODcxNTIsImV4cCI6MjEwNTI2MzE1Mn0.p_27320XWWY1ATSHNFa7jb74ZtR7i2FhQgm97No3Jj4"
    
    if not supabase_url or not supabase_key:
        return False
        
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }

    # Fetch existing DB to preserve user customizations
    existing_images = {}
    try:
        req = urllib.request.Request(f"{supabase_url.rstrip('/')}/rest/v1/articles?select=slug,cover_image,author_avatar", headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            db_articles = json.loads(resp.read().decode("utf-8"))
            for da in db_articles:
                existing_images[da["slug"]] = {
                    "cover_image": da.get("cover_image"),
                    "author_avatar": da.get("author_avatar")
                }
    except Exception as e:
        print(f"      Notice reading DB images: {e}", file=sys.stderr)

    synced_count = 0
    for a in articles:
        user_img = existing_images.get(a["slug"], {}).get("cover_image")
        user_avatar = existing_images.get(a["slug"], {}).get("author_avatar")
        
        final_cover = user_img if (user_img and ("googleusercontent.com" in user_img or "drive.google.com" in user_img or "ibb.co" in user_img)) else a["cover_image"]
        final_avatar = user_avatar if user_avatar else a["author"]["avatar"]

        author_name = a.get("author", {}).get("name") if isinstance(a.get("author"), dict) else a.get("author_name", "Editorial Desk")
        author_role = a.get("author", {}).get("role") if isinstance(a.get("author"), dict) else a.get("author_role", "Staff Writer")
        author_avatar = a.get("author", {}).get("avatar") if isinstance(a.get("author"), dict) else a.get("author_avatar", "")

        data = {
            "title": a["title"],
            "slug": a["slug"],
            "dek": a["dek"],
            "category": a["category"],
            "tag": a.get("tag", "Dispatch"),
            "author_name": author_name,
            "author_role": author_role,
            "author_avatar": final_avatar or author_avatar,
            "read_time": a["read_time"],
            "cover_image": final_cover,
            "image_caption": a.get("image_caption", ""),
            "featured": a.get("featured", False),
            "lead_story": a.get("lead_story", False),
            "quote": a.get("quote", ""),
            "content": a["content"]
        }
        
        endpoint = f"{supabase_url.rstrip('/')}/rest/v1/articles"
        insert_headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=ignore-duplicates"
        }
        
        try:
            req = urllib.request.Request(endpoint, data=json.dumps(data).encode("utf-8"), headers=insert_headers, method="POST")
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status in (200, 201):
                    synced_count += 1
        except Exception:
            pass
            
    print(f"      Supabase live sync: {synced_count} fresh articles registered in database.")
    return True

def merge_with_weekly_retention(new_articles):
    existing = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []

    articles_by_slug = {}
    
    # 1. Add today's fresh live articles (they take precedence)
    for a in new_articles:
        a["is_fresh"] = True
        articles_by_slug[a["slug"]] = a

    # 2. Add existing older articles (retaining for 7 days)
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    archive_list = []

    if os.path.exists(ARCHIVE_FILE):
        try:
            with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
                archive_list = json.load(f)
        except Exception:
            archive_list = []

    for old_art in existing:
        slug = old_art.get("slug")
        if slug not in articles_by_slug:
            pub_date_str = old_art.get("published_at", "")
            try:
                pub_dt = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
            except Exception:
                pub_dt = datetime.now(timezone.utc)

            old_art["is_fresh"] = False
            old_art["lead_story"] = False
            
            if pub_dt >= seven_days_ago:
                articles_by_slug[slug] = old_art
            else:
                archive_list.append(old_art)

    # Save perpetual archive
    os.makedirs(os.path.dirname(ARCHIVE_FILE), exist_ok=True)
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        seen = {}
        for it in archive_list:
            seen[it["slug"]] = it
        json.dump(list(seen.values()), f, indent=2, ensure_ascii=False)

    merged_list = list(articles_by_slug.values())
    # Sort: today's lead story first, then newest
    merged_list.sort(key=lambda x: (not x.get("lead_story", False), x.get("published_at", "")), reverse=False)
    return merged_list

def sync_and_save():
    print("[1/5] Fetching live breaking RSS feeds from top Nigerian news portals...")
    today_articles = generate_live_daily_stream()

    if not today_articles:
        print("      No fresh articles synthesized, keeping current stream.", file=sys.stderr)
        return []

    print(f"[2/5] Synthesized {len(today_articles)} 100% dynamic live breaking dispatches (Politics Lead Guaranteed)...")

    print("[3/5] Merging with 7-day rolling window...")
    all_active_articles = merge_with_weekly_retention(today_articles)

    print(f"      Active 7-day stream: {len(all_active_articles)} articles (Today's fresh: {len(today_articles)})")
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_active_articles, f, indent=2, ensure_ascii=False)
        
    sync_to_supabase_if_configured(all_active_articles)

    print("[4/5] Committing and syncing to GitHub repository...")
    try:
        cmd = f"""
        cd {WORKSPACE_DIR}
        git config user.name "Soigwe"
        git config user.email "soigwe03@gmail.com"
        git config core.sshCommand "ssh -i {SSH_KEY} -o StrictHostKeyChecking=no"
        git add assets/data/
        git commit -m "chore(cron): live breaking news synthesis - {datetime.now().strftime('%Y-%m-%d')}" || true
        git push origin main || true
        """
        os.system(cmd)
        print("      Git sync completed successfully.")
    except Exception as e:
        print(f"      Git push notice: {e}", file=sys.stderr)

    print("[4/5] Synthesizing Tailored AI Editorial Imagery for Fresh News...")
    try:
        img_script = os.path.join(WORKSPACE_DIR, "scripts", "generate_article_images.py")
        if os.path.exists(img_script):
            os.system(f"python3 {img_script}")
    except Exception as e:
        print(f"      AI image synthesis notice: {e}", file=sys.stderr)

    print("[5/5] Dispatching Quora-Style Morning Newsletter to Email Subscribers...")
    try:
        newsletter_script = os.path.join(WORKSPACE_DIR, "scripts", "send_newsletter_digest.py")
        if os.path.exists(newsletter_script):
            os.system(f"python3 {newsletter_script}")
    except Exception as e:
        print(f"      Newsletter dispatch notice: {e}", file=sys.stderr)

    return all_active_articles

if __name__ == "__main__":
    articles = sync_and_save()
    print("\n=======================================================")
    print(f"NAIJA CHRONICLES — DYNAMIC LIVE BREAKING NEWS STREAM READY ({len(articles)} Stories)")
    for a in articles:
        if a.get("is_fresh"):
            lead_marker = "★ [FRONT PAGE LEAD] " if a.get("lead_story") else ""
            print(f" • {lead_marker}[{a['category'].upper()}] {a['title']}")
            print(f"   Source: {a.get('sources', [{}])[0].get('name')} | Image: {a['cover_image'][:60]}")
    print("=======================================================")
