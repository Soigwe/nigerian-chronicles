# NIGERIAN CHRONICLES (Digital Editorial Magazine)

> **An Independent Journal of Architecture, Geopolitics, Culture, and Contemporary African Thought.**

---

## Overview

**Nigerian Chronicles** is a high-editorial digital news and magazine publication engineered with a refined editorial aesthetic inspired by *The Atlantic*, *Monocle*, and *Kinfolk*.

It features dynamic article layouts, audio narrations, offline/online synchronization, and native integration with **Supabase**.

---

## Architectural & Design Highlights

* **Typography & Aesthetic:**
  * **Bodoni Moda** for masthead and article display titles.
  * **Newsreader** for longform reading typography.
  * **Plus Jakarta Sans** for clean interface navigation.
  * **JetBrains Mono** for dispatches, financial tickers, and editorial metadata.
  * Drop caps, pull quotes, column dividers, and asymmetric 3-column layout.

* **Editorial Sections:**
  * **The Front Page:** Cover story lead feature and secondary deep dive.
  * **Section 02 (The Longform):**
    * *The Briefing:* Real-time short-form updates and market feeds.
    * *Core Grid:* In-depth investigative features and dispatches.
    * *Most Read:* Ranked editorial leaderboard (01–05).
  * **Visual Essay:** Full-bleed photographic portfolio spotlight.
  * **The Editors' Letter & Morning Dispatch:** Weekly newsletter subscription box.

* **Reader & Accessibility Experience:**
  * **Theme Switcher:** Gallery Ivory (Light), Editorial Obsidian (Dark), and Archival Sepia (Print).
  * **Distraction-Free Reader Modal:** Fullscreen magazine reader with live scroll progress indicator.
  * **Audio Narration Player:** In-browser speech synthesis for listening to articles.
  * **Personal Bookmarks:** Save articles for offline reading.
  * **Editorial CMS / Publish Portal:** Submit new articles directly to Supabase or the local wire.

---

## Supabase Integration

The platform operates on a **hybrid database model**:
1. **Out of the Box:** Pre-loaded with high-res curated editorial dispatches from `assets/data/sample_articles.json`.
2. **Live Supabase Sync:** Click the **Supabase** button in the header to enter your Project URL and Public Anon Key.
3. **Database Schema:** Run `schema.sql` in your Supabase SQL Editor to provision tables (`articles`, `subscribers`) with Row Level Security (RLS) policies.

---

## Project Structure

```
nigerian-chronicles/
├── index.html                      # Main magazine application
├── schema.sql                      # Supabase SQL migration & seed script
├── vercel.json                     # Vercel deployment configuration
├── assets/
│   ├── css/
│   │   └── editorial.css          # Magazine styling, typography & themes
│   ├── js/
│   │   └── app.js                 # App state, Supabase client & reader logic
│   └── data/
│       └── sample_articles.json   # Curated seed & fallback articles
└── README.md                       # Documentation
```

---

## Deployment

Deploy instantly to **Vercel**, **Cloudflare Pages**, or any static/edge host.

```bash
# Deploy with Vercel CLI
vercel --prod
```

---

*© 2026 Nigerian Chronicles Publishing House. Built with BizDigits Architecture.*
