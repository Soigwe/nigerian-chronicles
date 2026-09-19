#!/usr/bin/env python3
"""
Naija Chronicles — Quora-Style HTML Morning Newsletter Dispatcher
Dispatches high-retention, question-and-answer style editorial digests to email subscribers.
"""

import os
import sys
import json
import subprocess
import urllib.request
from datetime import datetime

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(WORKSPACE_DIR, "assets", "data", "sample_articles.json")
COMPOSIO_BIN = "/root/.composio/composio"
PRIMARY_RECIPIENT = "soigwe03@gmail.com"

def get_subscribers():
    subscribers = [PRIMARY_RECIPIENT]
    supabase_url = os.environ.get("SUPABASE_URL") or "https://ovndvemjdojlibawdcmk.supabase.co"
    supabase_key = os.environ.get("SUPABASE_ANON_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im92bmR2ZW1qZG9qbGliYXdkY21rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk2ODcxNTIsImV4cCI6MjEwNTI2MzE1Mn0.p_27320XWWY1ATSHNFa7jb74ZtR7i2FhQgm97No3Jj4"

    try:
        req = urllib.request.Request(
            f"{supabase_url.rstrip('/')}/rest/v1/subscribers?select=email&status=eq.active",
            headers={"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            for row in data:
                email = row.get("email", "").strip()
                if email and email not in subscribers:
                    subscribers.append(email)
    except Exception as e:
        print(f"Notice querying Supabase subscribers: {e}", file=sys.stderr)

    return subscribers

def build_quora_digest_html(articles):
    now_str = datetime.now().strftime("%A, %d %B %Y")
    
    # Select key stories
    lead = next((a for a in articles if a.get("lead_story")), articles[0] if articles else {})
    stocks = next((a for a in articles if "Stocks" in a.get("category", "")), None)
    tariffs = next((a for a in articles if "Hidden" in a.get("category", "") or "Tariff" in a.get("title", "")), None)
    mobility = next((a for a in articles if "Passport" in a.get("category", "") or "Mobility" in a.get("category", "")), None)
    macro = next((a for a in articles if "World" in a.get("category", "") or "Macro" in a.get("category", "")), None)
    tech = next((a for a in articles if "Tech" in a.get("category", "")), None)

    items = [x for x in [lead, stocks, tariffs, mobility, macro, tech] if x]

    cards_html = ""
    for idx, art in enumerate(items, 1):
        slug = art.get("slug", "")
        title = art.get("title", "")
        dek = art.get("dek", "")
        cat = art.get("category", "Intelligence").upper()
        read_time = art.get("read_time", "4 min read")
        tag = art.get("tag", "Dispatch")
        sources_text = ", ".join([s.get("name", "") for s in art.get("sources", [])]) if art.get("sources") else "Verified Primary Sources"
        deep_link = f"https://nigerian-chronicles.vercel.app/?article={slug}"

        cards_html += f"""
        <!-- Digest Card {idx} -->
        <div style="background-color: #ffffff; border: 1px solid #e7e5e4; border-radius: 6px; padding: 24px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
          <div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 11px; font-weight: 700; letter-spacing: 0.1em; color: #b91c1c; text-transform: uppercase; margin-bottom: 8px;">
            {cat} • <span style="color: #78716c;">{tag} • {read_time}</span>
          </div>

          <h2 style="font-family: Georgia, 'Times New Roman', serif; font-size: 20px; line-height: 1.35; color: #1c1917; margin: 0 0 12px 0; font-weight: 700;">
            <a href="{deep_link}" style="color: #1c1917; text-decoration: none;">{title}</a>
          </h2>

          <p style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #44403c; margin: 0 0 16px 0;">
            {dek}
          </p>

          <div style="background-color: #fafaf9; border-left: 3px solid #b91c1c; padding: 10px 14px; margin-bottom: 16px; font-size: 12px; font-family: monospace; color: #57534e;">
            <strong>Key Insight:</strong> <em>"{art.get('quote', 'Clear analysis based on verified public records.')}"</em>
          </div>

          <div style="display: flex; align-items: center; justify-content: space-between; border-top: 1px solid #f5f5f4; padding-top: 14px; font-size: 12px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
            <span style="color: #a8a29e; font-size: 11px;">Sources: {sources_text}</span>
            <a href="{deep_link}" style="display: inline-block; background-color: #1c1917; color: #ffffff; padding: 6px 14px; border-radius: 4px; font-weight: 600; font-size: 11px; text-decoration: none; text-transform: uppercase; letter-spacing: 0.05em;">
              Read Story →
            </a>
          </div>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Naija Chronicles Morning Digest</title>
    </head>
    <body style="margin: 0; padding: 0; background-color: #f7f6f2; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
      
      <div style="max-width: 640px; margin: 0 auto; padding: 24px 16px;">
        
        <!-- Header Banner -->
        <div style="text-align: center; padding: 20px 0 24px 0; border-bottom: 2px solid #1c1917; margin-bottom: 24px;">
          <div style="font-family: monospace; font-size: 11px; letter-spacing: 0.2em; color: #78716c; text-transform: uppercase; margin-bottom: 4px;">
            Lagos Bureau • Morning Intelligence Digest
          </div>
          <h1 style="font-family: 'Cinzel', Georgia, serif; font-size: 32px; font-weight: 900; letter-spacing: -0.02em; color: #1c1917; margin: 0;">
            NAIJA CHRONICLES
          </h1>
          <div style="font-family: Georgia, serif; font-style: italic; font-size: 13px; color: #78716c; margin-top: 4px;">
            {now_str} • Your daily edge on Politics, Wealth &amp; Contemporary Thought
          </div>
        </div>

        <!-- Live Markets Strip -->
        <div style="background-color: #1c1917; color: #ffffff; border-radius: 4px; padding: 10px 16px; margin-bottom: 24px; font-family: monospace; font-size: 11px; text-align: center;">
          ⚡ <strong>LIVE MARKETS:</strong> USD/NGN ₦1,640 (Parallel) • NAFEM ₦1,595 • BRENT $78.20 • NGX ▲ 104,280
        </div>

        <!-- Feed Cards -->
        {cards_html}

        <!-- Community Callout -->
        <div style="background-color: #fef2f2; border: 1px dashed #f87171; border-radius: 6px; padding: 18px; margin-bottom: 24px; text-align: center;">
          <h3 style="font-family: Georgia, serif; font-size: 16px; color: #991b1b; margin: 0 0 6px 0;">Have a ground report or state investigation?</h3>
          <p style="font-size: 13px; color: #7f1d1d; margin: 0 0 12px 0;">Publish your perspective to the open Community Wire.</p>
          <a href="https://nigerian-chronicles.vercel.app/community.html" style="display: inline-block; background-color: #b91c1c; color: #ffffff; padding: 8px 18px; border-radius: 4px; font-size: 12px; font-weight: 700; text-decoration: none; text-transform: uppercase;">
            Submit to Community Wire →
          </a>
        </div>

        <!-- Footer -->
        <div style="text-align: center; border-top: 1px solid #e7e5e4; padding-top: 20px; font-size: 11px; color: #a8a29e; font-family: monospace;">
          <p style="margin: 0 0 6px 0;">Published by Naija Chronicles Editorial Bureau (Victoria Island, Lagos, Nigeria).</p>
          <p style="margin: 0 0 12px 0;">© 2026 Naija Chronicles Publishing House. All rights reserved.</p>
          <p style="margin: 0;">
            <a href="https://nigerian-chronicles.vercel.app" style="color: #b91c1c; text-decoration: underline;">Read on Web</a> • 
            <a href="https://nigerian-chronicles.vercel.app/archive.html" style="color: #b91c1c; text-decoration: underline;">Past Editions</a> • 
            <a href="https://nigerian-chronicles.vercel.app/feed.xml" style="color: #b91c1c; text-decoration: underline;">RSS Feed</a>
          </p>
        </div>

      </div>

    </body>
    </html>
    """
    return html

def send_digest_via_composio():
    # 1. Load articles
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            articles = json.load(f)
    except Exception as e:
        print(f"Error loading articles: {e}", file=sys.stderr)
        return False

    if not articles:
        print("No articles to dispatch.", file=sys.stderr)
        return False

    # 2. Build email
    html_body = build_quora_digest_html(articles)
    subject = f"🇳🇬 Naija Chronicles Digest: 2027 Coalition Arithmetic + Dangote IPO Breakdown ({datetime.now().strftime('%b %d')})"
    recipients = get_subscribers()

    print(f"Dispatching Morning Digest to {len(recipients)} subscriber(s): {', '.join(recipients)}")

    for recipient in recipients:
        payload = {
            "recipient_email": recipient,
            "subject": subject,
            "body": html_body,
            "is_html": True
        }

        cmd = [
            COMPOSIO_BIN,
            "execute",
            "GMAIL_SEND_EMAIL",
            "-d",
            json.dumps(payload)
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if res.returncode == 0:
                print(f"✓ Successfully sent morning digest to {recipient}!")
            else:
                print(f"Notice sending to {recipient}: {res.stderr or res.stdout}", file=sys.stderr)
        except Exception as e:
            print(f"Error invoking Composio Gmail tool for {recipient}: {e}", file=sys.stderr)

    return True

if __name__ == "__main__":
    send_digest_via_composio()
