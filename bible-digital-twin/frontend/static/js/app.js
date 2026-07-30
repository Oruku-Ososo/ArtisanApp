// Bible Digital Twin - Main Application Logic

class BibleApp {
    constructor() {
        this.apiBase = '/api/v2';
        this.currentView = 'dashboard';
        this.charts = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboard();
        this.populateBookSelect();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const view = link.dataset.view;
                this.loadView(view);
            });
        });

        // Sidebar toggle
        document.getElementById('toggle-sidebar').addEventListener('click', () => {
            document.getElementById('sidebar').classList.toggle('collapsed');
            document.getElementById('main-content').classList.toggle('expanded');
        });

        // Theme toggle
        document.getElementById('theme-toggle').addEventListener('click', () => {
            document.body.classList.toggle('light-theme');
            const icon = document.querySelector('#theme-toggle i');
            icon.classList.toggle('fa-moon');
            icon.classList.toggle('fa-sun');
        });

        // Reader controls
        document.getElementById('reader-book').addEventListener('change', () => {
            this.updateChapterSelect();
        });

        document.getElementById('reader-chapter').addEventListener('change', () => {
            this.loadScripture();
        });

        document.getElementById('reader-version').addEventListener('change', () => {
            this.loadScripture();
        });

        // Search
        let searchTimeout;
        document.getElementById('search-input').addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.search(e.target.value);
            }, 500);
        });

        // Entity search
        let entitySearchTimeout;
        document.getElementById('entity-search').addEventListener('input', (e) => {
            clearTimeout(entitySearchTimeout);
            entitySearchTimeout = setTimeout(() => {
                this.searchEntities(e.target.value);
            }, 500);
        });
    }

    async loadView(viewName) {
        // Hide all views
        document.querySelectorAll('.view-section').forEach(el => {
            el.style.display = 'none';
        });

        // Update nav active state
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.dataset.view === viewName) {
                link.classList.add('active');
            }
        });

        // Show selected view
        const viewEl = document.getElementById(`view-${viewName}`);
        if (viewEl) {
            viewEl.style.display = 'block';
            viewEl.classList.add('fade-in');
        }

        // Update page title
        const titles = {
            dashboard: 'Dashboard',
            reader: 'Scripture Reader',
            search: 'Semantic Search',
            compare: 'Compare Translations',
            knowledge: 'Knowledge Graph',
            analytics: 'Analytics',
            entities: 'Entities',
            bookmarks: 'Bookmarks'
        };
        document.getElementById('page-title').textContent = titles[viewName] || 'Bible Digital Twin';

        this.currentView = viewName;

        // Load view-specific data
        switch(viewName) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'analytics':
                this.loadAnalytics();
                break;
            case 'knowledge':
                this.loadKnowledgeGraph();
                break;
            case 'entities':
                this.loadEntities();
                break;
        }
    }

    async loadDashboard() {
        try {
            // Load stats
            const stats = await this.fetch('/stats');
            if (stats) {
                document.getElementById('dash-total-verses').textContent = this.formatNumber(stats.total_verses || 0);
                document.getElementById('dash-total-chapters').textContent = this.formatNumber(stats.total_chapters || 0);
                document.getElementById('dash-total-books').textContent = this.formatNumber(stats.total_books || 0);
                document.getElementById('dash-versions').textContent = this.formatNumber(stats.versions_count || 0);
                
                // Update sidebar quick stats
                document.getElementById('stat-verses').textContent = this.formatNumber(stats.total_verses || 0);
                document.getElementById('stat-entities').textContent = this.formatNumber(stats.total_entities || 0);
                document.getElementById('stat-versions').textContent = stats.versions_count || 0;
            }

            // Load charts
            this.loadVerseDistributionChart();
            this.loadTranslationCoverageChart();
            this.loadEntityNetworkChart();
            
        } catch (error) {
            console.error('Error loading dashboard:', error);
        }
    }

    async populateBookSelect() {
        try {
            const books = await this.fetch('/books');
            const bookSelect = document.getElementById('reader-book');
            
            if (books && Array.isArray(books)) {
                books.forEach(book => {
                    const option = document.createElement('option');
                    option.value = book.abbreviation || book.name;
                    option.textContent = `${book.name} (${book.chapters} chapters)`;
                    bookSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading books:', error);
        }
    }

    updateChapterSelect() {
        const bookAbbrev = document.getElementById('reader-book').value;
        const chapterSelect = document.getElementById('reader-chapter');
        
        // Clear existing options
        chapterSelect.innerHTML = '<option value="">Chapter</option>';
        
        if (!bookAbbrev) return;

        // Get book info to determine number of chapters
        fetch(`${this.apiBase}/books`)
            .then(res => res.json())
            .then(books => {
                const book = books.find(b => b.abbreviation === bookAbbrev);
                if (book && book.chapters) {
                    for (let i = 1; i <= book.chapters; i++) {
                        const option = document.createElement('option');
                        option.value = i;
                        option.textContent = i;
                        chapterSelect.appendChild(option);
                    }
                }
            })
            .catch(console.error);
    }

    async loadScripture() {
        const book = document.getElementById('reader-book').value;
        const chapter = document.getElementById('reader-chapter').value;
        const version = document.getElementById('reader-version').value;
        const display = document.getElementById('scripture-display');

        if (!book || !chapter) {
            display.innerHTML = '<div class="loading"><p>Select a book and chapter</p></div>';
            return;
        }

        display.innerHTML = '<div class="loading"><div class="spinner"></div><span style="margin-left: 1rem;">Loading...</span></div>';

        try {
            const response = await fetch(`${this.apiBase}/chapter/${book}/${chapter}?version=${version}`);
            const data = await response.json();

            if (data && data.verses && data.verses.length > 0) {
                let html = `
                    <div class="scripture-header">
                        <div class="scripture-reference">${data.book_name} ${data.chapter}</div>
                        <div class="flex gap-2">
                            <button class="btn btn-outline" onclick="app.previousChapter()">
                                <i class="fas fa-chevron-left"></i> Previous
                            </button>
                            <button class="btn btn-outline" onclick="app.nextChapter()">
                                Next <i class="fas fa-chevron-right"></i>
                            </button>
                        </div>
                    </div>
                `;

                data.verses.forEach(verse => {
                    html += `
                        <div class="scripture-text">
                            <sup style="color: var(--primary-color); font-weight: 600;">${verse.verse}</sup>
                            ${verse.text}
                        </div>
                    `;
                });

                html += `<div class="scripture-version">${version}</div>`;
                display.innerHTML = html;
            } else {
                display.innerHTML = '<div class="loading"><p>No verses found for this selection.</p></div>';
            }
        } catch (error) {
            console.error('Error loading scripture:', error);
            display.innerHTML = '<div class="loading"><p>Error loading scripture. Please try again.</p></div>';
        }
    }

    async search(query) {
        if (!query || query.trim().length < 3) {
            document.getElementById('search-results').innerHTML = `
                <div class="card">
                    <div class="loading">
                        <p>Enter at least 3 characters to search</p>
                    </div>
                </div>
            `;
            return;
        }

        document.getElementById('search-results').innerHTML = `
            <div class="card">
                <div class="loading">
                    <div class="spinner"></div>
                    <span style="margin-left: 1rem;">Searching...</span>
                </div>
            </div>
        `;

        try {
            const response = await fetch(`${this.apiBase}/search?q=${encodeURIComponent(query)}&limit=10`);
            const results = await response.json();

            if (results && results.length > 0) {
                let html = '';
                results.forEach(result => {
                    html += `
                        <div class="card" style="cursor: pointer;" onclick="app.navigateToVerse('${result.reference}')">
                            <div class="flex justify-between items-center mb-2">
                                <strong style="color: var(--primary-color);">${result.reference}</strong>
                                <span style="font-size: 0.75rem; color: var(--text-secondary);">${result.version}</span>
                            </div>
                            <p style="color: var(--text-primary); line-height: 1.6;">${result.text}</p>
                            ${result.similarity ? `
                                <div style="margin-top: 0.5rem;">
                                    <span style="font-size: 0.75rem; color: var(--text-muted);">
                                        Similarity: ${(result.similarity * 100).toFixed(1)}%
                                    </span>
                                </div>
                            ` : ''}
                        </div>
                    `;
                });
                document.getElementById('search-results').innerHTML = html;
            } else {
                document.getElementById('search-results').innerHTML = `
                    <div class="card">
                        <div class="loading">
                            <p>No results found for "${query}"</p>
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Search error:', error);
            document.getElementById('search-results').innerHTML = `
                <div class="card">
                    <div class="loading">
                        <p>Error performing search. Please try again.</p>
                    </div>
                </div>
            `;
        }
    }

    async compareTranslations() {
        const reference = document.getElementById('compare-reference').value.trim();
        const resultsDiv = document.getElementById('compare-results');

        if (!reference) {
            resultsDiv.innerHTML = '<div class="loading"><p>Please enter a verse reference</p></div>';
            return;
        }

        resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div><span style="margin-left: 1rem;">Loading...</span></div>';

        try {
            const response = await fetch(`${this.apiBase}/compare/${encodeURIComponent(reference)}`);
            const data = await response.json();

            if (data && data.versions && data.versions.length > 0) {
                let html = '';
                data.versions.forEach(version => {
                    html += `
                        <div class="card">
                            <div class="card-header">
                                <h4 style="font-size: 1rem; color: var(--primary-color);">${version.version}</h4>
                            </div>
                            <p style="line-height: 1.8;">${version.text}</p>
                        </div>
                    `;
                });
                resultsDiv.innerHTML = html;
            } else {
                resultsDiv.innerHTML = '<div class="loading"><p>No translations found for this reference</p></div>';
            }
        } catch (error) {
            console.error('Compare error:', error);
            resultsDiv.innerHTML = '<div class="loading"><p>Error loading comparisons</p></div>';
        }
    }

    async loadAnalytics() {
        this.loadComplexityChart();
        this.loadEntityTypesChart();
        this.loadWordFrequencyChart();
    }

    async loadKnowledgeGraph() {
        const entityType = document.getElementById('graph-entity-type').value;
        
        try {
            const response = await fetch(`${this.apiBase}/entities?limit=50&type=${entityType !== 'all' ? entityType : ''}`);
            const entities = await response.json();

            if (entities && entities.length > 0) {
                this.renderFullGraph(entities);
            }
        } catch (error) {
            console.error('Error loading knowledge graph:', error);
        }
    }

    async loadEntities() {
        const searchTerm = document.getElementById('entity-search').value;
        
        try {
            const url = searchTerm 
                ? `${this.apiBase}/entities?search=${encodeURIComponent(searchTerm)}&limit=20`
                : `${this.apiBase}/entities?limit=20`;
            
            const response = await fetch(url);
            const entities = await response.json();

            if (entities && entities.length > 0) {
                let html = '';
                entities.forEach(entity => {
                    const icons = {
                        person: 'fa-user',
                        place: 'fa-map-marker-alt',
                        concept: 'fa-lightbulb',
                        event: 'fa-calendar',
                        object: 'fa-box'
                    };
                    
                    html += `
                        <div class="card">
                            <div class="flex items-center gap-3 mb-2">
                                <i class="fas ${icons[entity.type] || 'fa-tag'}" style="color: var(--primary-color); font-size: 1.5rem;"></i>
                                <div>
                                    <h4 style="font-size: 1rem; font-weight: 600;">${entity.name}</h4>
                                    <span style="font-size: 0.75rem; color: var(--text-secondary); text-transform: capitalize;">${entity.type}</span>
                                </div>
                            </div>
                            <p style="font-size: 0.875rem; color: var(--text-secondary); line-height: 1.5;">
                                ${entity.description || 'No description available'}
                            </p>
                            <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid var(--border-color);">
                                <span style="font-size: 0.75rem; color: var(--text-muted);">
                                    Mentioned in ${entity.mention_count || 0} verses
                                </span>
                            </div>
                        </div>
                    `;
                });
                document.getElementById('entities-list').innerHTML = html;
            } else {
                document.getElementById('entities-list').innerHTML = `
                    <div class="card" style="grid-column: 1 / -1;">
                        <div class="loading">
                            <p>No entities found</p>
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading entities:', error);
        }
    }

    // Chart rendering methods
    loadVerseDistributionChart() {
        const chartDom = document.getElementById('chart-verse-distribution');
        if (!chartDom) return;

        const myChart = echarts.init(chartDom);
        const option = {
            backgroundColor: 'transparent',
            tooltip: { trigger: 'axis' },
            xAxis: {
                type: 'category',
                data: ['Gen', 'Exo', 'Lev', 'Num', 'Deu', 'Jos', 'Jdg', 'Rut'],
                axisLabel: { color: '#94a3b8' }
            },
            yAxis: {
                type: 'value',
                axisLabel: { color: '#94a3b8' },
                splitLine: { lineStyle: { color: '#334155' } }
            },
            series: [{
                data: [900, 1200, 850, 1100, 700, 600, 500, 200],
                type: 'bar',
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: '#3b82f6' },
                        { offset: 1, color: '#1d4ed8' }
                    ])
                }
            }]
        };
        myChart.setOption(option);
        this.charts.verseDistribution = myChart;
    }

    loadTranslationCoverageChart() {
        const chartDom = document.getElementById('chart-translation-coverage');
        if (!chartDom) return;

        const myChart = echarts.init(chartDom);
        const option = {
            backgroundColor: 'transparent',
            tooltip: { trigger: 'item' },
            series: [{
                type: 'pie',
                radius: ['40%', '70%'],
                data: [
                    { value: 2672, name: 'KJV' },
                    { value: 2658, name: 'NIV' },
                    { value: 2658, name: 'ESV' },
                    { value: 1800, name: 'AMP' },
                    { value: 1500, name: 'NLT' }
                ],
                label: { color: '#f8fafc' },
                itemStyle: {
                    colors: ['#3b82f6', '#10b981', '#8b5cf6', '#f59e0b', '#ef4444']
                }
            }]
        };
        myChart.setOption(option);
        this.charts.translationCoverage = myChart;
    }

    loadEntityNetworkChart() {
        const chartDom = document.getElementById('chart-entity-network');
        if (!chartDom) return;

        const myChart = echarts.init(chartDom);
        const option = {
            backgroundColor: 'transparent',
            tooltip: {},
            series: [{
                type: 'graph',
                layout: 'force',
                data: [
                    { name: 'God', symbolSize: 50, itemStyle: { color: '#3b82f6' } },
                    { name: 'Adam', symbolSize: 30, itemStyle: { color: '#10b981' } },
                    { name: 'Eve', symbolSize: 30, itemStyle: { color: '#10b981' } },
                    { name: 'Eden', symbolSize: 25, itemStyle: { color: '#f59e0b' } },
                    { name: 'Creation', symbolSize: 25, itemStyle: { color: '#8b5cf6' } }
                ],
                links: [
                    { source: 'God', target: 'Adam' },
                    { source: 'God', target: 'Eve' },
                    { source: 'God', target: 'Eden' },
                    { source: 'God', target: 'Creation' },
                    { source: 'Adam', target: 'Eve' },
                    { source: 'Adam', target: 'Eden' },
                    { source: 'Eve', target: 'Eden' }
                ],
                force: { repulsion: 200, edgeLength: 100 },
                label: { show: true, position: 'right', color: '#f8fafc' },
                lineStyle: { color: '#64748b', width: 1 }
            }]
        };
        myChart.setOption(option);
        this.charts.entityNetwork = myChart;
    }

    loadComplexityChart() {
        const chartDom = document.getElementById('chart-complexity');
        if (!chartDom) return;

        const myChart = echarts.init(chartDom);
        const option = {
            backgroundColor: 'transparent',
            tooltip: { trigger: 'axis' },
            xAxis: {
                type: 'category',
                data: ['Gen', 'Exo', 'Lev', 'Num', 'Deu', 'Jos', 'Jdg', '1Sa', '2Sa', '1Ki'],
                axisLabel: { color: '#94a3b8' }
            },
            yAxis: {
                type: 'value',
                name: 'Avg Word Length',
                axisLabel: { color: '#94a3b8' },
                splitLine: { lineStyle: { color: '#334155' } }
            },
            series: [{
                data: [4.2, 4.5, 4.8, 4.6, 4.9, 4.3, 4.4, 4.7, 4.5, 4.6],
                type: 'line',
                smooth: true,
                itemStyle: { color: '#3b82f6' },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
                        { offset: 1, color: 'rgba(59, 130, 246, 0.05)' }
                    ])
                }
            }]
        };
        myChart.setOption(option);
        this.charts.complexity = myChart;
    }

    loadEntityTypesChart() {
        const chartDom = document.getElementById('chart-entity-types');
        if (!chartDom) return;

        const myChart = echarts.init(chartDom);
        const option = {
            backgroundColor: 'transparent',
            tooltip: { trigger: 'item' },
            series: [{
                type: 'sunburst',
                data: [
                    {
                        name: 'People',
                        children: [
                            { name: 'Patriarchs', value: 25 },
                            { name: 'Prophets', value: 30 },
                            { name: 'Kings', value: 20 }
                        ]
                    },
                    {
                        name: 'Places',
                        children: [
                            { name: 'Cities', value: 40 },
                            { name: 'Regions', value: 25 },
                            { name: 'Mountains', value: 15 }
                        ]
                    },
                    {
                        name: 'Concepts',
                        children: [
                            { name: 'Theology', value: 35 },
                            { name: 'Ethics', value: 20 },
                            { name: 'Prophecy', value: 25 }
                        ]
                    }
                ],
                label: { color: '#f8fafc' }
            }]
        };
        myChart.setOption(option);
        this.charts.entityTypes = myChart;
    }

    loadWordFrequencyChart() {
        const chartDom = document.getElementById('chart-word-frequency');
        if (!chartDom) return;

        const myChart = echarts.init(chartDom);
        const option = {
            backgroundColor: 'transparent',
            tooltip: { trigger: 'axis' },
            xAxis: {
                type: 'category',
                data: ['God', 'Lord', 'said', 'people', 'Israel', 'king', 'house', 'day', 'hand', 'earth'],
                axisLabel: { color: '#94a3b8', rotate: 45 }
            },
            yAxis: {
                type: 'value',
                axisLabel: { color: '#94a3b8' },
                splitLine: { lineStyle: { color: '#334155' } }
            },
            series: [{
                data: [4472, 7711, 3000, 2500, 2300, 2100, 1900, 1800, 1700, 1600],
                type: 'bar',
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: '#10b981' },
                        { offset: 1, color: '#059669' }
                    ])
                }
            }]
        };
        myChart.setOption(option);
        this.charts.wordFrequency = myChart;
    }

    renderFullGraph(entities) {
        const chartDom = document.getElementById('chart-full-graph');
        if (!chartDom) return;

        const myChart = echarts.init(chartDom);
        
        const nodes = entities.map((entity, index) => ({
            id: index,
            name: entity.name,
            symbolSize: Math.min(50, 20 + (entity.mention_count || 1) * 2),
            itemStyle: {
                color: this.getEntityColor(entity.type)
            },
            category: entity.type,
            value: entity.mention_count || 0
        }));

        const links = [];
        // Create some sample connections
        for (let i = 0; i < Math.min(nodes.length, 20); i++) {
            for (let j = i + 1; j < Math.min(nodes.length, 20); j++) {
                if (Math.random() > 0.7) {
                    links.push({
                        source: i,
                        target: j,
                        value: 'related'
                    });
                }
            }
        }

        const option = {
            backgroundColor: 'transparent',
            tooltip: {},
            legend: [{
                data: ['person', 'place', 'concept', 'event', 'object'],
                textStyle: { color: '#f8fafc' },
                top: 'bottom'
            }],
            series: [{
                type: 'graph',
                layout: 'force',
                data: nodes,
                links: links,
                categories: [
                    { name: 'person' },
                    { name: 'place' },
                    { name: 'concept' },
                    { name: 'event' },
                    { name: 'object' }
                ],
                roam: true,
                label: {
                    show: true,
                    position: 'right',
                    formatter: '{b}',
                    color: '#f8fafc'
                },
                force: {
                    repulsion: 300,
                    edgeLength: 120,
                    gravity: 0.1
                },
                lineStyle: {
                    color: 'source',
                    curveness: 0.3,
                    width: 1
                },
                emphasis: {
                    focus: 'adjacency',
                    lineStyle: {
                        width: 3
                    }
                }
            }]
        };
        myChart.setOption(option);
        this.charts.fullGraph = myChart;
    }

    getEntityColor(type) {
        const colors = {
            person: '#3b82f6',
            place: '#10b981',
            concept: '#8b5cf6',
            event: '#f59e0b',
            object: '#ef4444'
        };
        return colors[type] || '#64748b';
    }

    // Utility methods
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    async fetch(endpoint) {
        try {
            const response = await fetch(`${this.apiBase}${endpoint}`);
            if (!response.ok) throw new Error('Network response was not ok');
            return await response.json();
        } catch (error) {
            console.error('Fetch error:', error);
            return null;
        }
    }

    navigateToVerse(reference) {
        // Parse reference and navigate to reader
        const match = reference.match(/^(\w+)\s+(\d+):(\d+)/);
        if (match) {
            const [, book, chapter, verse] = match;
            document.getElementById('reader-book').value = book;
            this.updateChapterSelect();
            document.getElementById('reader-chapter').value = chapter;
            this.loadView('reader');
            setTimeout(() => {
                this.loadScripture();
            }, 500);
        }
    }

    previousChapter() {
        const chapter = parseInt(document.getElementById('reader-chapter').value);
        if (chapter > 1) {
            document.getElementById('reader-chapter').value = chapter - 1;
            this.loadScripture();
        }
    }

    nextChapter() {
        const chapter = parseInt(document.getElementById('reader-chapter').value);
        const book = document.getElementById('reader-book').value;
        
        fetch(`${this.apiBase}/books`)
            .then(res => res.json())
            .then(books => {
                const bookData = books.find(b => b.abbreviation === book);
                if (bookData && chapter < bookData.chapters) {
                    document.getElementById('reader-chapter').value = chapter + 1;
                    this.loadScripture();
                }
            })
            .catch(console.error);
    }
}

// Initialize app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new BibleApp();
});

// Global functions for inline event handlers
function loadView(viewName) {
    if (app) app.loadView(viewName);
}

function compareTranslations() {
    if (app) app.compareTranslations();
}

function refreshGraph() {
    if (app) app.loadKnowledgeGraph();
}

function showAddBookmark() {
    alert('Bookmark feature coming soon! For now, you can save verses manually.');
}
