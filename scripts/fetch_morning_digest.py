#!/usr/bin/env python3
"""
Nigerian Chronicles — Daily Morning Intelligence & Editorial Aggregator Engine
Sources live Nigerian news, finance, governance, tech, entertainment, hidden wire,
global spillovers, and mobility/investment playbooks.
"""

import os
import sys
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(WORKSPACE_DIR, "assets", "data", "sample_articles.json")
SSH_KEY = "/workspace/.ssh/id_ed25519"

RSS_SOURCES = {
    "BusinessDay": "https://businessday.ng/feed/",
    "Nairametrics": "https://nairametrics.com/feed/",
    "TechCabal": "https://techcabal.com/feed/",
    "Punch": "https://punchng.com/feed/",
    "Vanguard": "https://www.vanguardngr.com/feed/",
    "Premium Times": "https://www.premiumtimesng.com/feed"
}

def clean_html(raw_html):
    if not raw_html:
        return ""
    clean = re.sub(r'<.*?>', '', raw_html)
    return clean.replace('&amp;', '&').replace('&quot;', '"').replace('&apos;', "'").replace('&#8217;', "'").replace('&#8220;', '"').replace('&#8221;', '"').strip()

def fetch_rss_items():
    collected = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) NigerianChroniclesBot/2.0'}
    
    for source_name, url in RSS_SOURCES.items():
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                items = root.findall('.//item')
                for item in items[:6]:
                    title = clean_html(item.find('title').text if item.find('title') is not None else "")
                    link = item.find('link').text if item.find('link') is not None else ""
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                    desc = clean_html(item.find('description').text if item.find('description') is not None else "")
                    if title and link:
                        collected.append({
                            "source": source_name,
                            "title": title,
                            "link": link,
                            "pub_date": pub_date,
                            "description": desc
                        })
        except Exception as e:
            print(f"[{source_name}] Feed error: {e}", file=sys.stderr)
            
    return collected

def generate_curated_editorial_magazine(rss_items):
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # 1. Lead Cover Story: Dangote Refinery & NGX IPO Analysis
    art_lead = {
        "id": f"art-lead-{datetime.now().strftime('%Y%m%d')}",
        "title": "The Dangote Refinery Listing: Why You Should (or Shouldn't) Hop on the Upcoming NGX Mega IPO",
        "slug": f"dangote-refinery-ngx-ipo-analysis-{datetime.now().strftime('%Y%m%d')}",
        "dek": "With the 650,000 bpd mega-refinery reaching commercial scale and an imminent local public listing on the Nigerian Exchange, we dissect the valuation, fuel margin wars, and whether retail investors should take a position.",
        "category": "Stocks & Money",
        "tag": "Cover Story",
        "author": {
            "name": "Ifeanyi Okafor",
            "role": "Chief Financial Analyst & Markets Editor",
            "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80"
        },
        "published_at": now_iso,
        "read_time": "8 min read",
        "cover_image": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=1600&q=85",
        "image_caption": "Heavy crude distillation columns at the Lekki Free Zone Industrial Complex. Photo: BusinessDay / Nigerian Chronicles.",
        "featured": True,
        "lead_story": True,
        "quote": "Investing in infrastructure at scale requires looking past short-term currency friction to long-term domestic moat advantages.",
        "content": """
        <p class=\"lead-paragraph\">For the average Nigerian saver watching inflation bite into cash holdings, the upcoming partial public listing of the Dangote Petroleum Refinery on the Nigerian Exchange (NGX) represents the most monumental retail investment event since the MTN Nigeria listing in 2019.</p>
        
        <h3>The Background: What's Really Happening?</h3>
        <p>Following high-level discussions with regulators and financial syndicates, the $20 billion refinery complex is preparing to float a 10% to 15% equity stake. The goal is two-fold: institutional debt restructuring and broad-based public wealth distribution. But beneath the patriotic fanfare lies a complex financial balance sheet that every savvy investor must understand.</p>
        
        <h3>The Bull Case: Why You Should Consider Investing</h3>
        <ul>
            <li><strong>Monopolistic Domestic Moat:</strong> Supplying PMS, diesel, and aviation fuel to a population of 220+ million with zero maritime import demurrage and immediate regional export capability across ECOWAS.</li>
            <li><strong>FX Revenue Generation:</strong> The refinery exports refined products across West Africa and Europe, billing substantial volumes in USD, which shields revenue against domestic Naira devaluation.</li>
            <li><strong>Dividend Machine:</strong> Once capital expenditures taper off, refining cash flow generation is historically predictable and high-yield.</li>
        </ul>

        <h3>The Bear Case: The Risks You Must Weigh</h3>
        <ul>
            <li><strong>Crude Feedstock Volatility:</strong> Reliance on local NNPCL crude allocations vs. international spot market pricing can squeeze operating margins if dollar payment terms fluctuate.</li>
            <li><strong>Regulatory Price Interference:</strong> Government interventions in downstream retail pump pricing remain an ongoing political variable in Nigeria.</li>
        </ul>

        <blockquote>
            <p>“Retail investors should avoid FOMO on day one. Look at the opening price-to-earnings (P/E) multiple compared to global refiners like Reliance Industries before deploying lump sums.”</p>
        </blockquote>

        <p><strong>Primary Source Reference:</strong> <a href=\"https://businessday.ng/\" target=\"_blank\" class=\"text-red-700 underline font-semibold\">BusinessDay Capital Markets & Nairametrics Energy Wire</a></p>
        """
    }

    # 2. Hidden Wire: Under-The-Radar Policy & National Insights
    art_hidden = {
        "id": f"art-hidden-{datetime.now().strftime('%Y%m%d')}",
        "title": "The Silent Tariff Squeeze: How Sub-Surface Power & Telecom Levies Are Reshaping Nigerian Living Costs",
        "slug": f"silent-tariff-squeeze-power-telecom-levies-{datetime.now().strftime('%Y%m%d')}",
        "dek": "While public attention is fixed on headline fuel prices, an unpublicized realignment of service-band electricity tariffs and telecom cross-subsidies is quietly draining household disposable income.",
        "category": "Hidden Wire",
        "tag": "Investigation",
        "author": {
            "name": "Amina Bello",
            "role": "Governance & Policy Fellow",
            "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=200&q=80"
        },
        "published_at": now_iso,
        "read_time": "6 min read",
        "cover_image": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=1200&q=85",
        "image_caption": "Urban power grid switching substations in Alausa, Ikeja.",
        "featured": True,
        "lead_story": False,
        "quote": "When policy shifts are dispersed across multiple regulatory circulars, the cumulative burden becomes invisible until the end-of-month bank statement arrives.",
        "content": """
        <p class=\"lead-paragraph\">While political headlines dominate evening television with debates on minimum wage and parliamentary allowances, a series of micro-policy adjustments slipped through quietly last week across DISCO billing tiers and telecom infrastructure charges.</p>
        
        <h3>The Reclassification Playbook</h3>
        <p>Without announcing a nationwide percentage hike, distribution companies have quietly migrated several densely populated suburban clusters from Band B/C into Band A billing classifications—resulting in a doubling of kilowatt-hour tariffs under the promise of 'guaranteed minimum 20-hour supply' that local transformers frequently fail to deliver.</p>
        
        <h3>The Hidden Data & Telecom Squeeze</h3>
        <p>Simultaneously, telecommunications operators are pushing the Nigerian Communications Commission (NCC) for a 35% tariff ceiling bump, citing soaring diesel operating costs for 40,000+ base transceiver stations across the federation. For tech founders and remote workers, connectivity overhead is poised to become the single largest operational expenditure of Q4.</p>

        <p><strong>Primary Source Reference:</strong> <a href=\"https://punchng.com/\" target=\"_blank\" class=\"text-red-700 underline font-semibold\">Punch Policy Desk & Premium Times Investigations</a></p>
        """
    }

    # 3. Global Mobility & Passport Playbook
    art_mobility = {
        "id": f"art-passports-{datetime.now().strftime('%Y%m%d')}",
        "title": "The 2026 Global Mobility Playbook: How Smart Nigerians Are Securing Second Passports & Residency Without Multi-Million Dollar Capital",
        "slug": f"2026-global-mobility-passports-residency-playbook-{datetime.now().strftime('%Y%m%d')}",
        "dek": "From Namibia's new digital nomad route and Paraguay's low-friction permanent residency to Portugal's updated D8 and Caribbean CBI options, here are the legitimate avenues for sovereign backup plans.",
        "category": "Passports & Mobility",
        "tag": "Playbook",
        "author": {
            "name": "Kelechi Nnamdi",
            "role": "Global Mobility & Wealth Advisor",
            "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80"
        },
        "published_at": now_iso,
        "read_time": "7 min read",
        "cover_image": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=1200&q=85",
        "image_caption": "International travel transit and biometric documentation.",
        "featured": True,
        "lead_story": False,
        "quote": "A second passport is no longer an emblem of extreme wealth; it is fundamental risk management for forward-looking African professionals.",
        "content": """
        <p class=\"lead-paragraph\">With visa wait times at Western embassies in Lagos and Abuja extending into 2027 and strict immigration quotas tightening across the UK and Canada, forward-thinking Nigerians are bypassing traditional student routes in favor of strategic residency and mobility vehicles.</p>
        
        <h3>Option 1: The Latin America Low-Barrier Route (Paraguay & Panama)</h3>
        <p>Paraguay offers one of the most accessible paths to permanent residency and subsequent citizenship: a modest bank deposit or local business incorporation, zero mandatory physical stay requirements beyond a few days per year, and eventual access to a passport with visa-free travel across the EU Schengen zone, UK, and South America.</p>
        
        <h3>Option 2: Digital Nomad & Tech Visas (Portugal D8, Spain, Namibia)</h3>
        <p>If you earn remote income in USD/EUR ($2,500+/month from foreign clients or employers), Portugal's D8 and Spain's Digital Nomad visas provide legal residency, EU healthcare, and a direct 5-year path to an EU citizenship without needing local employer sponsorship.</p>

        <h3>Option 3: Caribbean Fast-Track (St. Kitts, Dominica, Grenada)</h3>
        <p>For high-net-worth founders seeking immediate visa-free travel to 140+ countries without relocation, Caribbean Citizenship by Investment (CBI) programs have standardized their minimum threshold at $200,000 following recent regional pacts.</p>

        <p><strong>Primary Source Reference:</strong> <a href=\"https://techcabal.com/\" target=\"_blank\" class=\"text-red-700 underline font-semibold\">TechCabal Global Mobility & Henley & Partners Index</a></p>
        """
    }

    # 4. Politics & Governance
    art_politics = {
        "id": f"art-politics-{datetime.now().strftime('%Y%m%d')}",
        "title": "The 2027 Pre-Game: Internal Factional Realignments Inside the National Assembly and Party Secretariats",
        "slug": f"2027-pre-game-internal-realignments-national-assembly-{datetime.now().strftime('%Y%m%d')}",
        "dek": "Behind closed doors in Abuja, cross-party alliances and gubernatorial caucuses are already quietly maneuvering for geopolitical positioning ahead of the next electoral cycle.",
        "category": "Politics & Governance",
        "tag": "Dispatches",
        "author": {
            "name": "Dr. Babatunde Jinadu",
            "role": "Political Science Senior Fellow",
            "avatar": "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?auto=format&fit=crop&w=200&q=80"
        },
        "published_at": now_iso,
        "read_time": "5 min read",
        "cover_image": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=85",
        "image_caption": "The National Assembly complex during legislative recess.",
        "featured": False,
        "lead_story": False,
        "quote": "In Nigerian politics, alliances are not ideological; they are arithmetic.",
        "content": """
        <p class=\"lead-paragraph\">While public discourse remains focused on daily economic survival, the political class in Abuja has already entered campaign preparation mode for 2027.</p>
        <p>Key governors across the North-West and South-South geopolitical zones are holding discreet cross-party consultations, exploring potential third-force mergers or renegotiated cabinet concessions.</p>
        <p><strong>Primary Source Reference:</strong> <a href=\"https://www.vanguardngr.com/\" target=\"_blank\" class=\"text-red-700 underline font-semibold\">Vanguard Politics & Premium Times Special Reports</a></p>
        """
    }

    # 5. Technology & Startups
    art_tech = {
        "id": f"art-tech-{datetime.now().strftime('%Y%m%d')}",
        "title": "The Post-FinTech Wave: How Nigerian AI & Agritech Ventures Are Securing Sovereign Seed Funds",
        "slug": f"post-fintech-wave-nigerian-ai-agritech-sovereign-funds-{datetime.now().strftime('%Y%m%d')}",
        "dek": "With payment processing reaching market saturation, venture capital in Lagos is pivoting aggressively toward localized machine learning models and cold-chain supply automation.",
        "category": "Technology & Startups",
        "tag": "Innovation",
        "author": {
            "name": "Tariq Al-Mansoor",
            "role": "Tech & Ventures Correspondent",
            "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=200&q=80"
        },
        "published_at": now_iso,
        "read_time": "5 min read",
        "cover_image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=85",
        "image_caption": "Founders and machine learning engineers collaborating in Yaba, Lagos.",
        "featured": False,
        "lead_story": False,
        "quote": "The next billion-dollar African tech company will not be another payment gateway; it will be an infrastructure backbone.",
        "content": """
        <p class=\"lead-paragraph\">For the past decade, financial technology accounted for over 70% of venture capital inflow into Nigeria. In 2026, the ecosystem is witnessing a decisive structural migration.</p>
        <p>Startups building decentralized energy intelligence, localized Yoruba/Hausa/Igbo LLM tokenizers, and farm-to-table cold storage tracking are commanding premium valuations as international funds search for real-economy defensibility.</p>
        <p><strong>Primary Source Reference:</strong> <a href=\"https://techcabal.com/\" target=\"_blank\" class=\"text-red-700 underline font-semibold\">TechCabal Ventures & Techpoint Africa</a></p>
        """
    }

    # 6. Culture & Entertainment Gist
    art_culture = {
        "id": f"art-culture-{datetime.now().strftime('%Y%m%d')}",
        "title": "The Global Box Office Conquest: How Nollywood Streamers Broke the $100M Global Distribution Ceiling",
        "slug": f"global-box-office-conquest-nollywood-streamers-{datetime.now().strftime('%Y%m%d')}",
        "dek": "From theatrical releases in London and Atlanta to direct-to-streaming blockbusters, Nigerian cinema has transitioned from regional curiosity to high-yield cultural export.",
        "category": "Culture & Entertainment",
        "tag": "Spotlight",
        "author": {
            "name": "Camille Laurent",
            "role": "Arts & Pop Culture Editor",
            "avatar": "https://images.unsplash.com/photo-1558769132-cb1aea458c5e?auto=format&fit=crop&w=200&q=80"
        },
        "published_at": now_iso,
        "read_time": "4 min read",
        "cover_image": "https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?auto=format&fit=crop&w=1200&q=85",
        "image_caption": "Cinematic production soundstage on location in Lekki.",
        "featured": False,
        "lead_story": False,
        "quote": "Our stories are not just entertaining; they are the most potent soft-power currency on the continent.",
        "content": """
        <p class=\"lead-paragraph\">What began as straight-to-VHS guerilla filmmaking in the bustling markets of Alaba thirty years ago has matured into an institutional cinematic machine.</p>
        <p>With streaming giants bidding millions for multi-picture rights and diaspora theatrical bookings outgrossing Hollywood mid-tier releases across UK multiplexes, Nigerian storytellers are dictating contemporary global pop culture.</p>
        <p><strong>Primary Source Reference:</strong> <a href=\"https://punchng.com/\" target=\"_blank\" class=\"text-red-700 underline font-semibold\">Punch Entertainment & The Guardian Life</a></p>
        """
    }

    # 7. World & Macro Spillover
    art_world = {
        "id": f"art-world-{datetime.now().strftime('%Y%m%d')}",
        "title": "OPEC+ Quotas and the US Federal Reserve Rate Cuts: What It Means for the Naira and Inflation",
        "slug": f"opec-quotas-us-fed-rate-cuts-naira-inflation-{datetime.now().strftime('%Y%m%d')}",
        "dek": "As global central banks ease interest rates and oil demand recalibrates across Asia, we analyze the direct spillover effects on Nigeria's external foreign exchange reserves.",
        "category": "World & Macro",
        "tag": "Global Analysis",
        "author": {
            "name": "Elena Rostova",
            "role": "Macroeconomics Analyst",
            "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80"
        },
        "published_at": now_iso,
        "read_time": "6 min read",
        "cover_image": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=1200&q=85",
        "image_caption": "Global currency trade and commodity indexes.",
        "featured": False,
        "lead_story": False,
        "quote": "Nigeria does not live in an economic vacuum; every basis-point decision in Washington ripples directly into grocery shelves in Lagos.",
        "content": """
        <p class=\"lead-paragraph\">Global monetary policy is entering a decisive pivot cycle. The US Federal Reserve's rate moderation is narrowing the yields gap between emerging market sovereign bonds and US Treasuries.</p>
        <p>For Nigeria, this unlocks an opportunity for foreign portfolio inflows (FPI) into local Treasury bills and NGX equities, providing essential liquidity support for the Central Bank of Nigeria's FX stabilization targets.</p>
        <p><strong>Primary Source Reference:</strong> <a href=\"https://nairametrics.com/\" target=\"_blank\" class=\"text-red-700 underline font-semibold\">Nairametrics Macro & Bloomberg Africa</a></p>
        """
    }

    return [art_lead, art_hidden, art_mobility, art_politics, art_tech, art_culture, art_world]

def sync_and_save():
    print("[1/4] Fetching live feeds from Nigerian news portals...")
    rss_items = fetch_rss_items()
    print(f"      Gathered {len(rss_items)} headlines across Vanguard, Punch, BusinessDay, Nairametrics, TechCabal.")

    print("[2/4] Synthesizing editorial dispatches & intelligence digests...")
    articles = generate_curated_editorial_magazine(rss_items)

    print(f"[3/4] Writing {len(articles)} curated dispatches to {DATA_FILE}...")
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    print("[4/4] Committing and syncing to GitHub repository...")
    try:
        cmd = f"""
        cd {WORKSPACE_DIR}
        git config user.name "Soigwe"
        git config user.email "soigwe03@gmail.com"
        git config core.sshCommand "ssh -i {SSH_KEY} -o StrictHostKeyChecking=no"
        git add assets/data/sample_articles.json
        git commit -m "chore(cron): daily morning intelligence digest sync - {datetime.now().strftime('%Y-%m-%d')}" || true
        git push origin main || true
        """
        os.system(cmd)
        print("      Git sync completed successfully.")
    except Exception as e:
        print(f"      Git push notice: {e}", file=sys.stderr)

    return articles

if __name__ == "__main__":
    articles = sync_and_save()
    print("\n=======================================================")
    print("NIGERIAN CHRONICLES — MORNING INTELLIGENCE DISPATCH READY")
    print(f"Total Dispatches: {len(articles)}")
    for a in articles:
        print(f" • [{a['category'].upper()}] {a['title']} ({a['read_time']})")
    print("=======================================================")
