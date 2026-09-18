/**
 * THE CHRONICLE — Editorial News & Magazine Application
 * Supports seamless Supabase live connection + offline curated fallback data.
 */

// State Management
const state = {
  articles: [],
  filteredArticles: [],
  selectedCategory: 'all',
  searchQuery: '',
  currentArticle: null,
  bookmarks: JSON.parse(localStorage.getItem('the_chronicle_bookmarks') || '[]'),
  theme: localStorage.getItem('the_chronicle_theme') || 'light',
  fontSize: localStorage.getItem('the_chronicle_font_size') || 'normal', // normal, large, xlarge
  readerFont: localStorage.getItem('the_chronicle_reader_font') || 'serif',
  supabase: null,
  supabaseConfig: {
    url: (window.CHRONICLE_CONFIG && window.CHRONICLE_CONFIG.supabaseUrl) || localStorage.getItem('chronicle_supabase_url') || '',
    key: (window.CHRONICLE_CONFIG && window.CHRONICLE_CONFIG.supabaseAnonKey) || localStorage.getItem('chronicle_supabase_key') || ''
  },
  isPlayingAudio: false,
  speechSynth: window.speechSynthesis || null,
  currentUtterance: null
};

// Initialize Application
document.addEventListener('DOMContentLoaded', async () => {
  initTheme();
  initSupabaseClient();
  initEventListeners();
  await loadArticles();
  renderAll();
  initReadingProgressBar();
});

// Theme Management
function initTheme() {
  document.documentElement.setAttribute('data-theme', state.theme);
  updateThemeButtons();
}

function setTheme(newTheme) {
  state.theme = newTheme;
  localStorage.setItem('the_chronicle_theme', newTheme);
  document.documentElement.setAttribute('data-theme', newTheme);
  updateThemeButtons();
}

function updateThemeButtons() {
  document.querySelectorAll('[data-set-theme]').forEach(btn => {
    if (btn.dataset.setTheme === state.theme) {
      btn.classList.add('bg-neutral-900', 'text-white', 'dark:bg-white', 'dark:text-neutral-900');
      btn.classList.remove('text-neutral-600', 'dark:text-neutral-400');
    } else {
      btn.classList.remove('bg-neutral-900', 'text-white', 'dark:bg-white', 'dark:text-neutral-900');
      btn.classList.add('text-neutral-600', 'dark:text-neutral-400');
    }
  });
}

// Supabase Connection Layer
function initSupabaseClient() {
  const { url, key } = state.supabaseConfig;
  const statusEl = document.getElementById('supabase-status-badge');
  
  if (url && key && window.supabase) {
    try {
      state.supabase = window.supabase.createClient(url, key);
      if (statusEl) {
        statusEl.innerHTML = `<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span> Supabase Connected
        </span>`;
      }
    } catch (err) {
      console.warn('Supabase initialization failed:', err);
      state.supabase = null;
      if (statusEl) {
        statusEl.innerHTML = `<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-medium bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300">
          <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span> Supabase Offline (Local Fallback)
        </span>`;
      }
    }
  } else {
    state.supabase = null;
    if (statusEl) {
      statusEl.innerHTML = `<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-medium bg-stone-100 text-stone-700 dark:bg-stone-800 dark:text-stone-300">
        <span class="w-1.5 h-1.5 rounded-full bg-stone-400"></span> Local Editorial Store
      </span>`;
    }
  }
}

// Load Articles
async function loadArticles() {
  showLoading(true);
  
  if (state.supabase) {
    try {
      const { data, error } = await state.supabase
        .from('articles')
        .select('*')
        .order('published_at', { ascending: false });

      if (!error && data && data.length > 0) {
        state.articles = data.map(normalizeArticleData);
        showToast(`Loaded ${data.length} articles from Supabase`);
        showLoading(false);
        return;
      }
    } catch (err) {
      console.warn('Supabase fetch error, falling back to local dataset:', err);
    }
  }

  // Fallback to local sample dataset (with cache-busting to ensure instant updates)
  try {
    const res = await fetch('assets/data/sample_articles.json?_v=' + Date.now(), { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      state.articles = data.map(normalizeArticleData);
    }
  } catch (err) {
    console.error('Failed to load local articles:', err);
  }
  
  showLoading(false);
}

function normalizeArticleData(item) {
  return {
    id: item.id || `art-${Date.now()}`,
    title: item.title || 'Untitled Dispatch',
    slug: item.slug || (item.title ? item.title.toLowerCase().replace(/[^a-z0-9]+/g, '-') : 'article'),
    dek: item.dek || item.summary || '',
    category: item.category || 'General',
    tag: item.tag || 'Dispatch',
    author: typeof item.author === 'object' ? item.author : {
      name: item.author_name || item.author || 'The Chronicle Desk',
      role: item.author_role || 'Staff Correspondent',
      avatar: item.author_avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80'
    },
    published_at: item.published_at || item.created_at || new Date().toISOString(),
    read_time: item.read_time || '5 min read',
    cover_image: item.cover_image || 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80',
    image_caption: item.image_caption || '',
    featured: Boolean(item.featured),
    lead_story: Boolean(item.lead_story),
    quote: item.quote || '',
    content: item.content || ''
  };
}

// Render Master Controller
function renderAll() {
  filterArticles();
  renderLeadStory();
  renderFeaturedSecondary();
  renderEditorialColumns();
  renderWeeklyArchiveSection();
  renderBriefings();
  renderVisualEssay();
  renderTrendingList();
  renderCategoryTabs();
  renderBookmarksList();
}

function filterArticles() {
  let list = [...state.articles];

  if (state.selectedCategory !== 'all') {
    list = list.filter(a => a.category.toLowerCase() === state.selectedCategory.toLowerCase());
  }

  if (state.searchQuery.trim()) {
    const q = state.searchQuery.toLowerCase();
    list = list.filter(a => 
      a.title.toLowerCase().includes(q) ||
      a.dek.toLowerCase().includes(q) ||
      a.author.name.toLowerCase().includes(q) ||
      a.category.toLowerCase().includes(q)
    );
  }

  state.filteredArticles = list;
}

// Render Lead Cover Story (Always prioritizes Nigerian Politics & Governance)
function renderLeadStory() {
  const container = document.getElementById('lead-story-container');
  if (!container) return;

  const lead = (state.selectedCategory === 'all')
    ? (state.filteredArticles.find(a => a.category === 'Politics & Governance' && a.lead_story) ||
       state.filteredArticles.find(a => a.category === 'Politics & Governance') ||
       state.filteredArticles.find(a => a.lead_story) ||
       state.filteredArticles[0])
    : (state.filteredArticles.find(a => a.lead_story) || state.filteredArticles[0]);

  if (!lead) {
    container.innerHTML = `<div class="p-12 text-center text-stone-500 font-display">No editorial stories match this filter.</div>`;
    return;
  }

  const isBookmarked = state.bookmarks.some(b => b.id === lead.id);

  container.innerHTML = `
    <div class="group relative cursor-pointer" onclick="openReaderModal('${lead.id}')">
      <div class="flex items-center gap-3 mb-4">
        <span class="inline-block px-2.5 py-0.5 text-xs font-mono font-bold tracking-widest uppercase bg-neutral-950 text-neutral-50 dark:bg-neutral-100 dark:text-neutral-900">${lead.tag || 'Cover Story'}</span>
        <span class="text-xs font-mono text-stone-500 uppercase tracking-wider">${lead.category}</span>
        <span class="text-xs font-mono text-stone-400">•</span>
        <span class="text-xs font-mono text-stone-500">${lead.read_time}</span>
      </div>

      <h1 class="font-display text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-[1.08] mb-5 group-hover:text-red-700 dark:group-hover:text-red-400 transition-colors">
        ${lead.title}
      </h1>

      <p class="font-body-serif text-lg sm:text-xl text-stone-700 dark:text-stone-300 leading-relaxed mb-6 max-w-3xl">
        ${lead.dek}
      </p>

      <div class="image-editorial-frame aspect-[16/9] lg:aspect-[21/9] w-full rounded-sm mb-4 border border-stone-200/80 dark:border-stone-800">
        <img src="${lead.cover_image}" alt="${lead.title}" class="w-full h-full object-cover" loading="lazy" />
      </div>

      ${lead.image_caption ? `<p class="font-mono text-xs text-stone-500 dark:text-stone-400 mb-6 italic border-l-2 border-stone-300 dark:border-stone-700 pl-3">${lead.image_caption}</p>` : ''}

      <div class="flex items-center justify-between border-t border-b border-stone-200 dark:border-stone-800 py-3.5 mt-4">
        <div class="flex items-center gap-3">
          <img src="${lead.author.avatar}" alt="${lead.author.name}" class="w-9 h-9 rounded-full object-cover border border-stone-300 dark:border-stone-700" />
          <div>
            <div class="font-sans text-sm font-semibold text-stone-900 dark:text-stone-100">${lead.author.name}</div>
            <div class="font-sans text-xs text-stone-500 dark:text-stone-400">${lead.author.role}</div>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <button onclick="event.stopPropagation(); playArticleAudio('${lead.id}')" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-sans font-medium border border-stone-300 dark:border-stone-700 hover:border-red-600 dark:hover:border-red-400 hover:text-red-600 transition-colors">
            <svg class="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg> Listen (8 min)
          </button>
          <button onclick="event.stopPropagation(); toggleBookmark('${lead.id}')" class="p-2 rounded-full border border-stone-300 dark:border-stone-700 hover:bg-stone-100 dark:hover:bg-stone-800 transition-colors" title="Bookmark article">
            <svg class="w-4 h-4 ${isBookmarked ? 'fill-red-600 text-red-600' : 'text-stone-600 dark:text-stone-300'}" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
          </button>
        </div>
      </div>
    </div>
  `;
}

// Render Secondary Featured Story
function renderFeaturedSecondary() {
  const container = document.getElementById('featured-secondary-container');
  if (!container) return;

  const second = state.filteredArticles.filter(a => !a.lead_story)[0];
  if (!second) {
    container.innerHTML = '';
    return;
  }

  container.innerHTML = `
    <div class="group cursor-pointer flex flex-col h-full justify-between" onclick="openReaderModal('${second.id}')">
      <div>
        <div class="image-editorial-frame aspect-[4/3] w-full rounded-sm mb-4 border border-stone-200 dark:border-stone-800">
          <img src="${second.cover_image}" alt="${second.title}" class="w-full h-full object-cover" loading="lazy" />
        </div>
        <div class="flex items-center gap-2 mb-2">
          <span class="text-xs font-mono font-semibold uppercase tracking-wider text-red-700 dark:text-red-400">${second.tag || 'Deep Dive'}</span>
          <span class="text-xs font-mono text-stone-400">•</span>
          <span class="text-xs font-mono text-stone-500">${second.read_time}</span>
        </div>
        <h3 class="font-display text-2xl lg:text-3xl font-bold leading-tight mb-3 group-hover:text-red-700 dark:group-hover:text-red-400 transition-colors">
          ${second.title}
        </h3>
        <p class="font-body-serif text-stone-600 dark:text-stone-300 text-sm leading-relaxed mb-4 line-clamp-3">
          ${second.dek}
        </p>
      </div>

      <div class="flex items-center gap-2 pt-3 border-t border-stone-200 dark:border-stone-800 text-xs font-sans text-stone-600 dark:text-stone-400">
        <span>By <strong>${second.author.name}</strong></span>
      </div>
    </div>
  `;
}

// Render 3-Column Editorial Grid
function renderEditorialColumns() {
  const container = document.getElementById('editorial-grid-container');
  if (!container) return;

  const others = state.filteredArticles.filter(a => !a.lead_story).slice(1, 9);
  if (others.length === 0) {
    container.innerHTML = '';
    return;
  }

  container.innerHTML = others.map(art => {
    return `
      <div class="group cursor-pointer flex flex-col justify-between p-4 sm:p-5 border border-stone-200/80 dark:border-stone-800/80 rounded-sm bg-card hover:shadow-lg transition-all" onclick="openReaderModal('${art.id}')">
        <div>
          <div class="image-editorial-frame aspect-[16/10] w-full rounded-sm mb-4 border border-stone-200/50 dark:border-stone-800">
            <img src="${art.cover_image}" alt="${art.title}" class="w-full h-full object-cover" loading="lazy" />
          </div>
          <div class="flex items-center justify-between text-xs font-mono mb-2 text-stone-500">
            <span class="font-bold text-neutral-900 dark:text-neutral-100 uppercase">${art.category}</span>
            <span>${art.read_time}</span>
          </div>
          <h4 class="font-display text-xl font-bold leading-snug mb-2.5 group-hover:text-red-700 dark:group-hover:text-red-400 transition-colors">
            ${art.title}
          </h4>
          <p class="font-body-serif text-sm text-stone-600 dark:text-stone-400 leading-relaxed mb-4 line-clamp-2">
            ${art.dek}
          </p>
        </div>

        <div class="flex items-center justify-between pt-3 border-t border-stone-100 dark:border-stone-800 text-xs">
          <span class="font-sans text-stone-500">By ${art.author.name}</span>
          <span class="text-stone-400 font-mono">${formatDate(art.published_at)}</span>
        </div>
      </div>
    `;
  }).join('');
}

// Render Weekly Archive (Past 7 Days Dispatches)
function renderWeeklyArchiveSection() {
  const container = document.getElementById('weekly-archive-grid');
  if (!container) return;

  // Find articles from the past week (excluding today's top lead story)
  const archiveItems = state.filteredArticles.filter(a => !a.lead_story);
  
  if (archiveItems.length === 0) {
    container.innerHTML = `<div class="col-span-full py-8 text-center text-stone-500 font-sans text-xs">No older dispatches in this 7-day window.</div>`;
    return;
  }

  container.innerHTML = archiveItems.slice(0, 6).map(art => `
    <div class="group cursor-pointer flex flex-col justify-between p-5 border border-stone-200/80 dark:border-stone-800 rounded-sm bg-card hover:shadow-md transition-all" onclick="openReaderModal('${art.id}')">
      <div>
        <div class="flex items-center justify-between text-[11px] font-mono mb-2 text-stone-500">
          <span class="font-bold text-red-700 dark:text-red-400 uppercase">${art.category}</span>
          <span>${formatDate(art.published_at)}</span>
        </div>
        <h4 class="font-display text-lg font-bold leading-snug mb-2 group-hover:text-red-700 dark:group-hover:text-red-400 transition-colors">
          ${art.title}
        </h4>
        <p class="font-body-serif text-xs text-stone-600 dark:text-stone-400 leading-relaxed mb-4 line-clamp-3">
          ${art.dek}
        </p>
      </div>

      <div class="flex items-center justify-between pt-3 border-t border-stone-100 dark:border-stone-800 text-[11px] font-mono text-stone-500">
        <span>${art.author.name}</span>
        <span>${art.read_time}</span>
      </div>
    </div>
  `).join('');
}

// Render Briefings Column
function renderBriefings() {
  const container = document.getElementById('briefings-list');
  if (!container) return;

  const dispatches = [
    { time: '14:20 WAT', tag: 'MARKETS', title: 'West African FinTech Index hits record $4.2B quarterly volume.' },
    { time: '12:05 WAT', tag: 'ENERGY', title: 'Solar grid hybridization project commissions 250MW in Northern corridors.' },
    { time: '09:40 WAT', tag: 'DESIGN', title: 'Milan Triennale announces 2027 Biennale theme: Radical Tactility.' },
    { time: '08:15 WAT', tag: 'AI & ETHICS', title: 'EU standards body approves new benchmark for autonomous reasoning transparency.' }
  ];

  container.innerHTML = dispatches.map(d => `
    <div class="border-b border-stone-200 dark:border-stone-800 pb-3 mb-3 last:border-0">
      <div class="flex items-center gap-2 mb-1">
        <span class="font-mono text-[10px] tracking-wider text-red-700 dark:text-red-400 font-bold uppercase">${d.tag}</span>
        <span class="text-[10px] font-mono text-stone-400">•</span>
        <span class="text-[10px] font-mono text-stone-500">${d.time}</span>
      </div>
      <p class="font-display text-sm font-semibold leading-snug hover:text-red-700 dark:hover:text-red-400 cursor-pointer transition-colors">
        ${d.title}
      </p>
    </div>
  `).join('');
}

// Render Visual Essay Spotlight
function renderVisualEssay() {
  const container = document.getElementById('visual-essay-container');
  if (!container) return;

  const essay = state.articles.find(a => a.tag === 'Visual Essay') || state.articles[2];
  if (!essay) return;

  container.innerHTML = `
    <div class="relative overflow-hidden rounded-sm bg-neutral-950 text-white p-8 sm:p-12 lg:p-16 cursor-pointer group" onclick="openReaderModal('${essay.id}')">
      <div class="absolute inset-0 z-0 opacity-40 group-hover:opacity-50 group-hover:scale-105 transition-all duration-700">
        <img src="${essay.cover_image}" alt="${essay.title}" class="w-full h-full object-cover" />
      </div>
      <div class="absolute inset-0 bg-gradient-to-t from-black via-black/60 to-transparent z-10"></div>

      <div class="relative z-20 max-w-2xl">
        <span class="inline-block px-3 py-1 font-mono text-xs font-bold tracking-widest uppercase bg-amber-500 text-black mb-4">Visual Essay • Photo Portfolio</span>
        <h2 class="font-display text-3xl sm:text-4xl lg:text-5xl font-bold leading-tight mb-4 group-hover:text-amber-300 transition-colors">
          ${essay.title}
        </h2>
        <p class="font-body-serif text-lg text-neutral-300 leading-relaxed mb-6">
          ${essay.dek}
        </p>
        <div class="flex items-center gap-4 text-xs font-mono text-neutral-400">
          <span>Photography & Text by <strong>${essay.author.name}</strong></span>
          <span>•</span>
          <span>${essay.read_time}</span>
        </div>
      </div>
    </div>
  `;
}

// Render Trending Leaderboard
function renderTrendingList() {
  const container = document.getElementById('trending-list');
  if (!container) return;

  const trending = [...state.articles].slice(0, 5);

  container.innerHTML = trending.map((art, idx) => `
    <div class="group cursor-pointer flex items-start gap-4 py-3.5 border-b border-stone-200 dark:border-stone-800 last:border-0" onclick="openReaderModal('${art.id}')">
      <span class="font-display text-3xl font-black text-stone-300 dark:text-stone-700 group-hover:text-red-700 dark:group-hover:text-red-400 transition-colors w-8">
        0${idx + 1}
      </span>
      <div class="flex-1">
        <span class="text-[10px] font-mono font-bold tracking-wider text-stone-500 uppercase">${art.category}</span>
        <h5 class="font-display text-sm sm:text-base font-bold leading-snug group-hover:text-red-700 dark:group-hover:text-red-400 transition-colors">
          ${art.title}
        </h5>
        <div class="text-[11px] font-sans text-stone-400 mt-1">By ${art.author.name} • ${art.read_time}</div>
      </div>
    </div>
  `).join('');
}

// Category Tabs
function renderCategoryTabs() {
  const container = document.getElementById('category-nav');
  if (!container) return;

  const categories = [
    { id: 'all', label: 'Front Page' },
    { id: 'Stocks & Money', label: 'Stocks & Money' },
    { id: 'Hidden Wire', label: 'Hidden Wire' },
    { id: 'Passports & Mobility', label: 'Passports & Mobility' },
    { id: 'Politics & Governance', label: 'Politics & Governance' },
    { id: 'Technology & Startups', label: 'Technology & Startups' },
    { id: 'Culture & Entertainment', label: 'Culture & Entertainment' },
    { id: 'World & Macro', label: 'World & Macro' }
  ];

  container.innerHTML = categories.map(cat => {
    const active = state.selectedCategory.toLowerCase() === cat.id.toLowerCase();
    return `
      <button onclick="selectCategory('${cat.id}')" class="whitespace-nowrap px-3.5 py-1.5 text-xs font-sans font-semibold tracking-wider uppercase transition-all ${
        active 
          ? 'text-neutral-950 dark:text-white border-b-2 border-neutral-950 dark:border-white font-bold' 
          : 'text-stone-500 hover:text-stone-900 dark:hover:text-stone-200'
      }">
        ${cat.label}
      </button>
    `;
  }).join('');
}

function selectCategory(catId) {
  state.selectedCategory = catId;
  renderAll();
}

// Search Handler
function handleSearch(query) {
  state.searchQuery = query;
  renderAll();
}

// Reader View Modal
function openReaderModal(articleId) {
  const article = state.articles.find(a => a.id === articleId);
  if (!article) return;

  state.currentArticle = article;
  const modal = document.getElementById('reader-modal');
  const bodyEl = document.getElementById('reader-article-content');
  if (!modal || !bodyEl) return;

  const isBookmarked = state.bookmarks.some(b => b.id === article.id);

  bodyEl.innerHTML = `
    <div class="max-w-3xl mx-auto py-8">
      <div class="flex items-center gap-3 mb-4">
        <span class="px-2.5 py-0.5 text-xs font-mono font-bold tracking-widest uppercase bg-neutral-950 text-neutral-50 dark:bg-neutral-100 dark:text-neutral-900">${article.tag || 'Dispatch'}</span>
        <span class="text-xs font-mono text-stone-500 uppercase">${article.category}</span>
        <span class="text-xs font-mono text-stone-400">•</span>
        <span class="text-xs font-mono text-stone-500">${article.read_time}</span>
      </div>

      <h1 class="font-display text-3xl sm:text-4xl lg:text-5xl font-bold leading-tight mb-4 text-stone-900 dark:text-stone-100">
        ${article.title}
      </h1>

      <p class="font-body-serif text-lg sm:text-xl text-stone-600 dark:text-stone-300 leading-relaxed mb-6 italic">
        ${article.dek}
      </p>

      <div class="flex items-center justify-between border-t border-b border-stone-200 dark:border-stone-800 py-4 my-6">
        <div class="flex items-center gap-3">
          <img src="${article.author.avatar}" alt="${article.author.name}" class="w-10 h-10 rounded-full object-cover" />
          <div>
            <div class="font-sans font-semibold text-sm text-stone-900 dark:text-stone-100">${article.author.name}</div>
            <div class="font-sans text-xs text-stone-500">${article.author.role} • ${formatDate(article.published_at)}</div>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button onclick="playArticleAudio('${article.id}')" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-sans font-medium bg-stone-100 dark:bg-stone-800 hover:bg-red-50 dark:hover:bg-red-950/40 text-stone-800 dark:text-stone-200 hover:text-red-700 dark:hover:text-red-400 transition-colors">
            <svg class="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg> Narration
          </button>
          <button onclick="toggleBookmark('${article.id}')" class="p-2 rounded-full hover:bg-stone-100 dark:hover:bg-stone-800 transition-colors" title="Bookmark">
            <svg class="w-4 h-4 ${isBookmarked ? 'fill-red-600 text-red-600' : 'text-stone-600 dark:text-stone-300'}" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
          </button>
        </div>
      </div>

      <div class="image-editorial-frame aspect-[16/9] w-full rounded-sm mb-4 border border-stone-200 dark:border-stone-800">
        <img src="${article.cover_image}" alt="${article.title}" class="w-full h-full object-cover" />
      </div>
      ${article.image_caption ? `<p class="font-mono text-xs text-stone-500 dark:text-stone-400 mb-8 italic">${article.image_caption}</p>` : ''}

      ${article.quote ? `
        <div class="editorial-quote my-8">
          ${article.quote}
        </div>
      ` : ''}

      <div id="reader-body-text" class="article-rich-body drop-cap text-stone-800 dark:text-stone-200">
        ${article.content || `<p class="lead-paragraph">${article.dek}</p><p>Full content dispatch transmitted from the Lagos editorial bureau.</p>`}
      </div>

      <!-- Social Outreach & Share Ribbon -->
      <div class="my-8 p-4 sm:p-5 bg-stone-100/80 dark:bg-stone-900/80 rounded border border-stone-200 dark:border-stone-800 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div class="text-xs font-mono">
          <span class="font-bold text-stone-900 dark:text-stone-100 uppercase tracking-wider block sm:inline">Spread the Truth:</span>
          <span class="text-stone-500 hidden sm:inline">Share this intelligence dispatch</span>
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <a href="https://api.whatsapp.com/send?text=${encodeURIComponent(article.title + ' — ' + window.location.href)}" target="_blank" class="px-3 py-1.5 rounded text-xs font-mono font-bold bg-emerald-600 text-white hover:bg-emerald-700 transition-colors flex items-center gap-1.5 shadow-sm">
            WhatsApp
          </a>
          <a href="https://twitter.com/intent/tweet?text=${encodeURIComponent(article.title)}&url=${encodeURIComponent(window.location.href)}" target="_blank" class="px-3 py-1.5 rounded text-xs font-mono font-bold bg-neutral-900 text-white dark:bg-stone-100 dark:text-neutral-900 hover:opacity-90 transition-colors flex items-center gap-1.5 shadow-sm">
            Post on X
          </a>
          <a href="https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(window.location.href)}" target="_blank" class="px-3 py-1.5 rounded text-xs font-mono font-bold bg-blue-700 text-white hover:bg-blue-800 transition-colors flex items-center gap-1.5 shadow-sm">
            LinkedIn
          </a>
          <button onclick="copyArticleLink('${article.slug}')" class="px-3 py-1.5 rounded text-xs font-mono font-medium border border-stone-300 dark:border-stone-700 hover:bg-stone-200 dark:hover:bg-stone-800 text-stone-700 dark:text-stone-300 transition-colors">
            Copy Link
          </button>
        </div>
      </div>

      <div class="border-t border-stone-200 dark:border-stone-800 pt-8 mt-8 flex items-center justify-between">
        <div class="font-mono text-xs text-stone-500">
          BUREAU ARCHIVE REF: ${article.slug.toUpperCase()}
        </div>
        <button onclick="closeReaderModal()" class="px-4 py-2 text-xs font-sans font-semibold uppercase tracking-wider bg-stone-900 text-white dark:bg-stone-100 dark:text-stone-900 rounded-sm">
          Close Reader
        </button>
      </div>
    </div>
  `;

  modal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function copyArticleLink(slug) {
  const url = window.location.origin + window.location.pathname + '#' + slug;
  if (navigator.clipboard) {
    navigator.clipboard.writeText(url).then(() => {
      showToast('Article link copied to clipboard!');
    }).catch(() => {
      prompt('Copy article link:', url);
    });
  } else {
    prompt('Copy article link:', url);
  }
}

function closeReaderModal() {
  const modal = document.getElementById('reader-modal');
  if (modal) modal.classList.add('hidden');
  document.body.style.overflow = '';
  stopArticleAudio();
}

// Narration Player (Web Speech API)
function playArticleAudio(articleId) {
  const article = state.articles.find(a => a.id === articleId);
  if (!article) return;

  if (!state.speechSynth) {
    showToast('Speech synthesis not supported in this browser environment');
    return;
  }

  stopArticleAudio();

  const textToRead = `${article.title}. By ${article.author.name}. ${article.dek}. ${stripHtml(article.content)}`;
  const utterance = new SpeechSynthesisUtterance(textToRead);
  utterance.rate = 0.95; // Editorial calm pace
  utterance.pitch = 1.0;

  utterance.onend = () => {
    state.isPlayingAudio = false;
    updateAudioPlayerUI(false, article.title);
  };

  utterance.onerror = () => {
    state.isPlayingAudio = false;
    updateAudioPlayerUI(false);
  };

  state.currentUtterance = utterance;
  state.speechSynth.speak(utterance);
  state.isPlayingAudio = true;
  updateAudioPlayerUI(true, article.title);
  showToast(`Playing audio narration: "${article.title.substring(0, 30)}..."`);
}

function stopArticleAudio() {
  if (state.speechSynth && state.isPlayingAudio) {
    state.speechSynth.cancel();
    state.isPlayingAudio = false;
    updateAudioPlayerUI(false);
  }
}

function updateAudioPlayerUI(playing, title = '') {
  const bar = document.getElementById('global-audio-player-bar');
  const titleEl = document.getElementById('audio-bar-title');
  if (!bar) return;

  if (playing) {
    bar.classList.remove('hidden');
    if (titleEl) titleEl.textContent = title;
  } else {
    bar.classList.add('hidden');
  }
}

// Bookmarking System
function toggleBookmark(articleId) {
  const article = state.articles.find(a => a.id === articleId);
  if (!article) return;

  const exists = state.bookmarks.findIndex(b => b.id === articleId);
  if (exists >= 0) {
    state.bookmarks.splice(exists, 1);
    showToast('Removed from saved bookmarks');
  } else {
    state.bookmarks.push(article);
    showToast('Article saved to your personal reading list');
  }

  localStorage.setItem('the_chronicle_bookmarks', JSON.stringify(state.bookmarks));
  renderAll();
  
  if (state.currentArticle && state.currentArticle.id === articleId) {
    openReaderModal(articleId);
  }
}

function renderBookmarksList() {
  const container = document.getElementById('bookmarks-drawer-list');
  const countBadge = document.getElementById('bookmarks-count-badge');
  if (countBadge) countBadge.textContent = state.bookmarks.length;
  if (!container) return;

  if (state.bookmarks.length === 0) {
    container.innerHTML = `<div class="p-8 text-center text-stone-500 font-sans text-xs">No saved articles yet. Click the bookmark icon on any dispatch to save it for later.</div>`;
    return;
  }

  container.innerHTML = state.bookmarks.map(art => `
    <div class="flex items-start justify-between gap-3 p-3 rounded bg-stone-50 dark:bg-stone-800/60 mb-2">
      <div class="cursor-pointer flex-1" onclick="openReaderModal('${art.id}'); toggleBookmarksDrawer(false)">
        <span class="text-[10px] font-mono text-red-700 dark:text-red-400 font-bold uppercase">${art.category}</span>
        <h6 class="font-display text-sm font-bold leading-snug line-clamp-2">${art.title}</h6>
        <div class="text-[11px] font-sans text-stone-400 mt-1">By ${art.author.name}</div>
      </div>
      <button onclick="toggleBookmark('${art.id}')" class="text-stone-400 hover:text-red-600 p-1" title="Remove">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
      </button>
    </div>
  `).join('');
}

// Reading Progress Bar
function initReadingProgressBar() {
  window.addEventListener('scroll', () => {
    const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;
    const bar = document.getElementById('reading-progress');
    if (bar) bar.style.width = scrolled + '%';
  });
}

// Supabase Settings & Sync Layer
function openSupabaseModal() {
  const modal = document.getElementById('supabase-modal');
  const urlInput = document.getElementById('supabase-url-input');
  const keyInput = document.getElementById('supabase-key-input');
  
  if (urlInput) urlInput.value = state.supabaseConfig.url;
  if (keyInput) keyInput.value = state.supabaseConfig.key;
  if (modal) modal.classList.remove('hidden');
}

function closeSupabaseModal() {
  const modal = document.getElementById('supabase-modal');
  if (modal) modal.classList.add('hidden');
}

async function saveSupabaseSettings() {
  const url = document.getElementById('supabase-url-input')?.value.trim() || '';
  const key = document.getElementById('supabase-key-input')?.value.trim() || '';

  state.supabaseConfig.url = url;
  state.supabaseConfig.key = key;
  localStorage.setItem('chronicle_supabase_url', url);
  localStorage.setItem('chronicle_supabase_key', key);

  initSupabaseClient();
  closeSupabaseModal();
  showToast('Supabase configuration saved');
  await loadArticles();
  renderAll();
}

async function testAndSyncSupabase() {
  const url = document.getElementById('supabase-url-input')?.value.trim();
  const key = document.getElementById('supabase-key-input')?.value.trim();

  if (!url || !key) {
    showToast('Please enter both Supabase Project URL and Anon Key');
    return;
  }

  try {
    const client = window.supabase.createClient(url, key);
    // Test fetch
    const { data, error } = await client.from('articles').select('count', { count: 'exact', head: true });
    
    if (error) {
      if (error.code === '42P01') {
        alert('Connected to Supabase, but the "articles" table does not exist yet. Please run the SQL schema in your Supabase SQL editor (schema.sql is provided in the root folder).');
      } else {
        alert(`Supabase Error: ${error.message}`);
      }
      return;
    }

    showToast('Supabase connection verified successfully!');
    saveSupabaseSettings();
  } catch (err) {
    alert(`Connection failed: ${err.message}`);
  }
}

// Article Publishing (CMS Modal)
function openPublishModal() {
  const modal = document.getElementById('publish-modal');
  if (modal) modal.classList.remove('hidden');
}

function closePublishModal() {
  const modal = document.getElementById('publish-modal');
  if (modal) modal.classList.add('hidden');
}

async function handlePublishArticle(event) {
  event.preventDefault();
  const form = event.target;
  
  const newArticle = {
    title: form.title.value.trim(),
    slug: form.title.value.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-'),
    dek: form.dek.value.trim(),
    category: form.category.value,
    tag: form.tag.value || 'Dispatch',
    author_name: form.author_name.value.trim() || 'Editorial Desk',
    author_role: form.author_role.value.trim() || 'Staff Writer',
    author_avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80',
    cover_image: form.cover_image.value.trim() || 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80',
    image_caption: form.image_caption.value.trim() || '',
    read_time: form.read_time.value.trim() || '5 min read',
    quote: form.quote.value.trim() || '',
    content: form.content.value.trim(),
    published_at: new Date().toISOString(),
    featured: form.featured.checked,
    lead_story: form.lead_story.checked
  };

  if (state.supabase) {
    try {
      const { data, error } = await state.supabase.from('articles').insert([newArticle]);
      if (error) throw error;
      showToast('Article published directly to Supabase DB!');
    } catch (err) {
      console.warn('Supabase insert failed, storing in memory:', err);
      state.articles.unshift(normalizeArticleData(newArticle));
      showToast('Article published locally (Supabase write failed)');
    }
  } else {
    state.articles.unshift(normalizeArticleData(newArticle));
    showToast('Article published to local edition!');
  }

  closePublishModal();
  form.reset();
  renderAll();
}

// Newsletter Subscription Handler
async function handleNewsletterSignup(event) {
  event.preventDefault();
  const email = event.target.querySelector('input[type="email"]')?.value;
  if (!email) return;

  if (state.supabase) {
    try {
      await state.supabase.from('subscribers').insert([{ email }]);
    } catch (err) {
      console.log('Subscriber save note:', err);
    }
  }

  event.target.innerHTML = `<div class="p-3 bg-stone-900 text-white dark:bg-stone-100 dark:text-stone-900 text-xs font-mono font-medium rounded text-center">✓ Thank you for subscribing to The Morning Dispatch.</div>`;
}

// Drawers & Utility Toggles
function toggleBookmarksDrawer(open) {
  const drawer = document.getElementById('bookmarks-drawer');
  if (!drawer) return;
  if (open) {
    drawer.classList.remove('translate-x-full');
  } else {
    drawer.classList.add('translate-x-full');
  }
}

// Helper Utilities
function formatDate(isoStr) {
  try {
    const d = new Date(isoStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  } catch {
    return 'Recent';
  }
}

function stripHtml(html) {
  const tmp = document.createElement('DIV');
  tmp.innerHTML = html || '';
  return tmp.textContent || tmp.innerText || '';
}

function showToast(msg) {
  const toast = document.getElementById('toast-notification');
  if (!toast) return;
  toast.textContent = msg;
  toast.classList.remove('opacity-0', 'translate-y-4');
  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-4');
  }, 3500);
}

function showLoading(show) {
  const spinner = document.getElementById('loading-spinner');
  if (spinner) {
    if (show) spinner.classList.remove('hidden');
    else spinner.classList.add('hidden');
  }
}

function initEventListeners() {
  document.getElementById('search-input')?.addEventListener('input', (e) => {
    handleSearch(e.target.value);
  });
}
