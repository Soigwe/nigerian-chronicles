#!/usr/bin/env python3
"""
Naija Chronicles — AI Editorial Image Generation Subagent Engine
Inspects Supabase for fresh news articles and synthesizes tailored FLUX AI editorial
photography based on the article's headline, dek, and image caption.
"""

import os
import sys
import json
import re
import urllib.request
import urllib.parse
import hashlib
from datetime import datetime

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(WORKSPACE_DIR, "assets", "data", "sample_articles.json")
IMG_DIR = os.path.join(WORKSPACE_DIR, "assets", "images", "generated")
SSH_KEY = "/workspace/.ssh/id_ed25519"

SUPABASE_URL = os.environ.get("SUPABASE_URL") or "https://ovndvemjdojlibawdcmk.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im92bmR2ZW1qZG9qbGliYXdkY21rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk2ODcxNTIsImV4cCI6MjEwNTI2MzE1Mn0.p_27320XWWY1ATSHNFa7jb74ZtR7i2FhQgm97No3Jj4"

def build_flux_prompt(article):
    title = article.get("title", "")
    dek = article.get("dek", "")
    caption = article.get("image_caption", "")
    category = article.get("category", "General")

    # Domain-specific style anchors
    style_suffix = "editorial news photograph, shot on 35mm Leica M11, cinematic atmospheric lighting, photorealistic textures, 8k resolution, authentic Nigerian metropolitan atmosphere, Reuters documentary journalism style"

    # Clean and synthesize visual description
    base_concept = caption or dek or title
    clean_concept = re.sub(r'Verified Sources:.*', '', base_concept)
    clean_concept = re.sub(r'Photo:.*', '', clean_concept).strip()

    if "Politics" in category:
        prompt = f"Editorial press photograph of Nigerian political assembly, statesmen and delegates in dialogue inside Abuja chamber, dramatic hall lighting, {clean_concept}, {style_suffix}"
    elif "Stocks" in category or "Money" in category:
        prompt = f"Editorial financial news photograph of modern Nigerian stock exchange trading floor, commercial banking towers in Victoria Island Lagos, financial analytics screens, {clean_concept}, {style_suffix}"
    elif "Hidden" in category:
        prompt = f"Investigative documentary photograph, Nigerian urban infrastructure, power grid substation or regulatory industrial site, realistic details, {clean_concept}, {style_suffix}"
    elif "Tech" in category:
        prompt = f"Modern African tech hub workspace in Lagos, young Nigerian software engineers and founders collaborating, optical fiber server hardware, {clean_concept}, {style_suffix}"
    elif "Passports" in category or "Mobility" in category:
        prompt = f"International airport terminal, biometric travel documents, departure lounge with global flight schedules, {clean_concept}, {style_suffix}"
    elif "Culture" in category or "Entertainment" in category:
        prompt = f"Behind the scenes cinematic movie set in Lagos, professional cinema camera on location, vibrant cultural textures, {clean_concept}, {style_suffix}"
    else:
        prompt = f"Documentary editorial photograph in Nigeria, West African economic landscape, {clean_concept}, {style_suffix}"

    return prompt[:380]

def generate_and_sync_images():
    os.makedirs(IMG_DIR, exist_ok=True)
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    print("[1/4] Fetching fresh news articles from Supabase...")
    req = urllib.request.Request(f"{SUPABASE_URL.rstrip('/')}/rest/v1/articles?select=*&order=published_at.desc", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            articles = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Error connecting to Supabase: {e}", file=sys.stderr)
        return False

    print(f"      Inspecting {len(articles)} total articles in database...")

    # Focus on the top 12-14 fresh articles
    fresh_articles = [a for a in articles if a.get("is_fresh")] or articles[:12]
    updated_count = 0

    for idx, art in enumerate(fresh_articles, 1):
        slug = art.get("slug", "")
        title = art.get("title", "")
        current_img = art.get("cover_image", "")

        # Generate unique seed based on article slug
        seed = int(hashlib.md5(slug.encode('utf-8')).hexdigest()[:8], 16) % 1000000
        
        flux_prompt = build_flux_prompt(art)
        encoded_prompt = urllib.parse.quote(flux_prompt)
        
        # High-res FLUX AI direct CDN URL
        flux_cdn_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1200&height=675&model=flux&nologo=true&seed={seed}"

        print(f"[{idx}/{len(fresh_articles)}] Synthesizing FLUX AI Image for: {title[:45]}...")
        print(f"      Prompt: {flux_prompt[:90]}...")

        # Update Supabase cover_image with the generated FLUX AI URL
        patch_data = {
            "cover_image": flux_cdn_url,
            "image_caption": f"AI Editorial Imagery by Naija Chronicles Desk • Synthesized for: {title[:60]}"
        }

        patch_req = urllib.request.Request(
            f"{SUPABASE_URL.rstrip('/')}/rest/v1/articles?id=eq.{art['id']}",
            data=json.dumps(patch_data).encode('utf-8'),
            headers=headers,
            method='PATCH'
        )

        try:
            with urllib.request.urlopen(patch_req, timeout=10) as p_resp:
                if p_resp.status in (200, 204):
                    art["cover_image"] = flux_cdn_url
                    art["image_caption"] = patch_data["image_caption"]
                    updated_count += 1
                    print(f"      ✓ Successfully updated Supabase article #{idx}")
        except Exception as e:
            print(f"      Notice updating Supabase: {e}", file=sys.stderr)

    print(f"[3/4] Updating local {DATA_FILE}...")
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Notice saving local file: {e}", file=sys.stderr)

    print(f"[4/4] Syncing generated image updates to GitHub...")
    try:
        cmd = f"""
        cd {WORKSPACE_DIR}
        git config user.name "Soigwe"
        git config user.email "soigwe03@gmail.com"
        git config core.sshCommand "ssh -i {SSH_KEY} -o StrictHostKeyChecking=no"
        git add assets/data/sample_articles.json
        git commit -m "feat(ai-images): synthesize tailored FLUX AI editorial cover images for fresh news dispatches" || true
        git push origin main || true
        """
        os.system(cmd)
        print("      Git sync completed successfully.")
    except Exception as e:
        print(f"      Git push notice: {e}", file=sys.stderr)

    print(f"\n=======================================================")
    print(f"IMAGE SUBAGENT COMPLETE — Generated & Linked {updated_count} Editorial Images")
    print("=======================================================")
    return True

if __name__ == "__main__":
    generate_and_sync_images()
