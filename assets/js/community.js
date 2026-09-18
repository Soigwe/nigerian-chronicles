/**
 * NAIJA CHRONICLES — Community Dispatches & Individual Submissions Controller
 * Seamlessly fetches and posts community articles directly to Supabase.
 */

const communityState = {
  articles: [],
  filteredArticles: [],
  selectedCategory: 'all',
  searchQuery: '',
  supabase: null,
  theme: localStorage.getItem('the_chronicle_theme') || 'light'
};

document.addEventListener('DOMContentLoaded', async () => {
  initCommunityTheme();
  initCommunitySupabase();
  await loadCommunityArticles();
  renderCommunityAll();
  initCommunitySearch();
});

function initCommunityTheme() {
  document.documentElement.setAttribute('data-theme', communityState.theme);
}

function setTheme(newTheme) {
  communityState.theme = newTheme;
  localStorage.setItem('the_chronicle_theme', newTheme);
  document.documentElement.setAttribute('data-theme', newTheme);
}

function initCommunitySupabase() {
  const url = (window.CHRONICLE_CONFIG && window.CHRONICLE_CONFIG.supabaseUrl) || localStorage.getItem('chronicle_supabase_url');
  const key = (window.CHRONICLE_CONFIG && window.CHRONICLE_CONFIG.supabaseAnonKey) || localStorage.getItem('chronicle_supabase_key');
  const badge = document.getElementById('supabase-status-badge');

  if (url && key && window.supabase) {
    try {
      communityState.supabase = window.supabase.createClient(url, key);
      if (badge) {
        badge.innerHTML = `<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span> Supabase Connected
        </span>`;
      }
    } catch (e) {
      communityState.supabase = null;
    }
  } else {
    if (badge) {
      badge.innerHTML = `<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-medium bg-stone-100 text-stone-700 dark:bg-stone-800 dark:text-stone-300">
        <span class="w-1.5 h-1.5 rounded-full bg-stone-400"></span> Local Community Store
      </span>`;
    }
  }
}

async function loadCommunityArticles() {
  showCommunityLoading(true);

  // 1. Try fetching from Supabase (tag = 'Community Dispatch' or custom submissions)
  if (communityState.supabase) {
    try {
      const { data, error } = await communityState.supabase
        .from('articles')
        .select('*')
        .eq('tag', 'Community Dispatch')
        .order('created_at', { ascending: false });

      if (!error && data && data.length > 0) {
        communityState.articles = data.map(normalizeCommunityArticle);
        showCommunityLoading(false);
        return;
      }
    } catch (err) {
      console.warn('Supabase community fetch fallback:', err);
    }
  }

  // 2. Fallback to local community articles dataset (with cache-busting)
  try {
    const res = await fetch('assets/data/community_articles.json?_v=' + Date.now(), { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      communityState.articles = data.map(normalizeCommunityArticle);
    }
  } catch (err) {
    console.error('Failed to load local community articles:', err);
  }

  showCommunityLoading(false);
}

function normalizeCommunityArticle(item) {
  return {
    id: item.id || `comm-${Date.now()}`,
    title: item.title || 'Community Dispatch',
    slug: item.slug || 'community-dispatch',
    dek: item.dek || '',
    category: item.category || 'General',
    tag: item.tag || 'Community Dispatch',
    author: typeof item.author === 'object' ? item.author : {
      name: item.author_name || 'Anonymous Contributor',
      role: item.author_role || 'Citizen Journalist',
      avatar: item.author_avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80'
    },
    published_at: item.published_at || item.created_at || new Date().toISOString(),
    read_time: item.read_time || '4 min read',
    cover_image: item.cover_image || 'https://images.unsplash.com/photo-1509391365360-2e959784a276?auto=format&fit=crop&w=1200&q=85',
    image_caption: item.image_caption || '',
    quote: item.quote || '',
    content: item.content || ''
  };
}

function renderCommunityAll() {
  filterCommunityArticles();
  renderCommunityGrid();
  renderCommunityCategoryNav();
}

function filterCommunityArticles() {
  let list = [...communityState.articles];

  if (communityState.selectedCategory !== 'all') {
    list = list.filter(a => a.category.toLowerCase() === communityState.selectedCategory.toLowerCase());
  }

  if (communityState.searchQuery.trim()) {
    const q = communityState.searchQuery.toLowerCase();
    list = list.filter(a => 
      a.title.toLowerCase().includes(q) ||
      a.dek.toLowerCase().includes(q) ||
      a.author.name.toLowerCase().includes(q) ||
      a.author.role.toLowerCase().includes(q) ||
      a.category.toLowerCase().includes(q)
    );
  }

  communityState.filteredArticles = list;
  const countLabel = document.getElementById('community-count-label');
  if (countLabel) countLabel.textContent = `Showing ${list.length} community dispatches`;
}

function renderCommunityGrid() {
  const container = document.getElementById('community-articles-grid');
  if (!container) return;

  if (communityState.filteredArticles.length === 0) {
    container.innerHTML = `
      <div class="col-span-full text-center py-16 p-8 border border-dashed border-stone-300 dark:border-stone-700 rounded">
        <h4 class="font-display text-xl font-bold mb-2">No community dispatches found</h4>
        <p class="font-body-serif text-sm text-stone-500 mb-6">Be the first to publish a ground report or analysis on this topic.</p>
        <button onclick="openCommunityPublishModal()" class="px-5 py-2.5 bg-red-700 text-white text-xs font-mono font-bold uppercase tracking-wider rounded hover:bg-red-800">
          Submit an Article
        </button>
      </div>
    `;
    return;
  }

  container.innerHTML = communityState.filteredArticles.map(art => `
    <div class="group cursor-pointer flex flex-col justify-between p-5 border border-stone-200/80 dark:border-stone-800 rounded-sm bg-card hover:shadow-xl transition-all" onclick="openCommunityReader('${art.id}')">
      <div>
        <div class="image-editorial-frame aspect-[16/10] w-full rounded-sm mb-4 border border-stone-200/60 dark:border-stone-800">
          <img src="${art.cover_image}" alt="${art.title}" class="w-full h-full object-cover" loading="lazy" />
        </div>
        
        <div class="flex items-center justify-between text-xs font-mono mb-2">
          <span class="font-bold text-red-700 dark:text-red-400 uppercase tracking-wider">${art.category}</span>
          <span class="text-stone-500">${art.read_time}</span>
        </div>

        <h3 class="font-display text-xl font-bold leading-snug mb-2 group-hover:text-red-700 dark:group-hover:text-red-400 transition-colors">
          ${art.title}
        </h3>

        <p class="font-body-serif text-sm text-stone-600 dark:text-stone-400 leading-relaxed mb-4 line-clamp-3">
          ${art.dek}
        </p>
      </div>

      <div class="flex items-center gap-3 pt-3 border-t border-stone-100 dark:border-stone-800 mt-2">
        <img src="${art.author.avatar}" alt="${art.author.name}" class="w-8 h-8 rounded-full object-cover border border-stone-300 dark:border-stone-700" />
        <div class="flex-1 min-w-0">
          <div class="text-xs font-sans font-bold text-stone-900 dark:text-stone-100 truncate">${art.author.name}</div>
          <div class="text-[11px] font-sans text-stone-500 truncate">${art.author.role}</div>
        </div>
      </div>
    </div>
  `).join('');
}

function renderCommunityCategoryNav() {
  const container = document.getElementById('community-category-nav');
  if (!container) return;

  const categories = [
    { id: 'all', label: 'All Dispatches' },
    { id: 'Economy & Business', label: 'Economy & Business' },
    { id: 'Technology & Startups', label: 'Technology & Startups' },
    { id: 'Local Governance & States', label: 'Local Governance & States' },
    { id: 'Opinion & Essays', label: 'Opinion & Essays' },
    { id: 'Culture & Life', label: 'Culture & Life' }
  ];

  container.innerHTML = categories.map(cat => {
    const active = communityState.selectedCategory.toLowerCase() === cat.id.toLowerCase();
    return `
      <button onclick="selectCommunityCategory('${cat.id}')" class="whitespace-nowrap px-3.5 py-1.5 text-xs font-sans font-semibold tracking-wider uppercase transition-all ${
        active 
          ? 'text-neutral-950 dark:text-white border-b-2 border-neutral-950 dark:border-white font-bold' 
          : 'text-stone-500 hover:text-stone-900 dark:hover:text-stone-200'
      }">
        ${cat.label}
      </button>
    `;
  }).join('');
}

function selectCommunityCategory(catId) {
  communityState.selectedCategory = catId;
  renderCommunityAll();
}

function initCommunitySearch() {
  document.getElementById('community-search-input')?.addEventListener('input', (e) => {
    communityState.searchQuery = e.target.value;
    renderCommunityAll();
  });
}

function openCommunityPublishModal() {
  const modal = document.getElementById('community-publish-modal');
  if (modal) modal.classList.remove('hidden');
}

function closeCommunityPublishModal() {
  const modal = document.getElementById('community-publish-modal');
  if (modal) modal.classList.add('hidden');
}

async function handleCommunitySubmit(event) {
  event.preventDefault();
  const form = event.target;

  const newArticle = {
    title: form.title.value.trim(),
    slug: form.title.value.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-') + '-' + Date.now(),
    dek: form.dek.value.trim(),
    category: form.category.value,
    tag: 'Community Dispatch',
    author_name: form.author_name.value.trim(),
    author_role: form.author_role.value.trim(),
    author_avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80',
    cover_image: form.cover_image.value.trim() || 'https://images.unsplash.com/photo-1509391365360-2e959784a276?auto=format&fit=crop&w=1200&q=85',
    image_caption: `Submitted by ${form.author_name.value.trim()}`,
    read_time: form.read_time.value.trim() || '4 min read',
    quote: form.quote.value.trim() || '',
    content: form.content.value.trim(),
    published_at: new Date().toISOString(),
    featured: false,
    lead_story: false
  };

  // Push directly to Supabase if connected
  if (communityState.supabase) {
    try {
      const { data, error } = await communityState.supabase.from('articles').insert([newArticle]);
      if (error) throw error;
      showCommunityToast('Article published live to Supabase Community Wire!');
    } catch (err) {
      console.warn('Supabase community insert notice:', err);
      communityState.articles.unshift(normalizeCommunityArticle(newArticle));
      showCommunityToast('Article published to local community wire!');
    }
  } else {
    communityState.articles.unshift(normalizeCommunityArticle(newArticle));
    showCommunityToast('Article published to local community stream!');
  }

  closeCommunityPublishModal();
  form.reset();
  renderCommunityAll();
}

function openCommunityReader(articleId) {
  const article = communityState.articles.find(a => a.id === articleId);
  if (!article) return;

  const modal = document.getElementById('reader-modal');
  const bodyEl = document.getElementById('reader-article-content');
  if (!modal || !bodyEl) return;

  bodyEl.innerHTML = `
    <div class="max-w-3xl mx-auto py-6">
      <div class="flex items-center gap-3 mb-4">
        <span class="px-2.5 py-0.5 text-xs font-mono font-bold tracking-widest uppercase bg-red-700 text-white">Community Dispatch</span>
        <span class="text-xs font-mono text-stone-500 uppercase">${article.category}</span>
        <span class="text-xs font-mono text-stone-400">•</span>
        <span class="text-xs font-mono text-stone-500">${article.read_time}</span>
      </div>

      <h1 class="font-display text-3xl sm:text-4xl lg:text-5xl font-bold leading-tight mb-4 text-stone-900 dark:text-stone-100">
        ${article.title}
      </h1>

      <p class="font-body-serif text-lg text-stone-600 dark:text-stone-300 leading-relaxed mb-6 italic">
        ${article.dek}
      </p>

      <div class="flex items-center justify-between border-t border-b border-stone-200 dark:border-stone-800 py-4 my-6">
        <div class="flex items-center gap-3">
          <img src="${article.author.avatar}" alt="${article.author.name}" class="w-10 h-10 rounded-full object-cover" />
          <div>
            <div class="font-sans font-semibold text-sm text-stone-900 dark:text-stone-100">${article.author.name}</div>
            <div class="font-sans text-xs text-stone-500">${article.author.role} • ${new Date(article.published_at).toLocaleDateString()}</div>
          </div>
        </div>
      </div>

      <div class="image-editorial-frame aspect-[16/9] w-full rounded-sm mb-6 border border-stone-200 dark:border-stone-800">
        <img src="${article.cover_image}" alt="${article.title}" class="w-full h-full object-cover" />
      </div>

      ${article.quote ? `<div class="editorial-quote my-6">${article.quote}</div>` : ''}

      <div class="article-rich-body drop-cap text-stone-800 dark:text-stone-200">
        ${article.content}
      </div>

      <div class="border-t border-stone-200 dark:border-stone-800 pt-8 mt-12 flex items-center justify-between">
        <div class="font-mono text-xs text-stone-500">COMMUNITY WIRE SUBMISSION</div>
        <button onclick="closeReaderModal()" class="px-4 py-2 text-xs font-sans font-semibold uppercase tracking-wider bg-stone-900 text-white dark:bg-stone-100 dark:text-stone-900 rounded-sm">
          Close Reader
        </button>
      </div>
    </div>
  `;

  modal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closeReaderModal() {
  const modal = document.getElementById('reader-modal');
  if (modal) modal.classList.add('hidden');
  document.body.style.overflow = '';
}

function showCommunityToast(msg) {
  const toast = document.getElementById('toast-notification');
  if (!toast) return;
  toast.textContent = msg;
  toast.classList.remove('opacity-0', 'translate-y-4');
  setTimeout(() => toast.classList.add('opacity-0', 'translate-y-4'), 3500);
}

function showCommunityLoading(show) {
  const el = document.getElementById('community-loading');
  if (el) {
    if (show) el.classList.remove('hidden');
    else el.classList.add('hidden');
  }
}
