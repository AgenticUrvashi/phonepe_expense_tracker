/**
 * PhonePe Expense Tracker - High-Performance Standalone Frontend Controller
 * Featuring Built-in Offline SVG Charting Engine + PyWebView Desktop Bridge
 */

// Global Application State
const state = {
    payload: null,
    activeCategoryFilter: 'ALL',
    searchQuery: '',
    currentPage: 1,
    rowsPerPage: 8,
    sortField: 'date',
    sortOrder: 'asc',
    budgetLimit: 10000.0,
    sourceFileName: 'transactions.txt (Sample)'
};

// FinTech Category Metadata
const CATEGORY_META = {
    Food: { color: '#f59e0b', icon: '🍔' },
    Travel: { color: '#3b82f6', icon: '✈️' },
    Shopping: { color: '#ec4899', icon: '🛍️' },
    Bills: { color: '#a855f7', icon: '💡' },
    Health: { color: '#10b981', icon: '💊' },
    Entertainment: { color: '#ef4444', icon: '🎬' },
    Education: { color: '#06b6d4', icon: '📚' },
    Investment: { color: '#eab308', icon: '📈' },
    Other: { color: '#94a3b8', icon: '🏷️' }
};

// Currency Formatter
function formatINR(amount) {
    if (isNaN(amount) || amount === null || amount === undefined) return '₹0.00';
    return '₹' + Number(amount).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Escape HTML for safety
function escapeHtml(text) {
    if (!text) return '';
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// -------------------------------------------------------------
// Initialization & Lifecycle
// -------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    initDropzone();
    initEventListeners();

    // Initial render with built-in default data immediately
    loadSampleData();

    // Re-sync if PyWebView bridge connects
    window.addEventListener('pywebviewready', () => {
        console.log("Desktop PyWebView bridge connected successfully");
        if (window.pywebview && window.pywebview.api && window.pywebview.api.get_sample_data) {
            window.pywebview.api.get_sample_data().then(response => {
                if (response && response.success) {
                    applyPayload(response.data, 'transactions.txt (Sample)');
                }
            }).catch(e => console.warn("Bridge sync error:", e));
        }
    });
});

// Setup File Drag-and-Drop & File Picker
function initDropzone() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');

    if (!dropzone) return;

    ['dragenter', 'dragover'].forEach(name => {
        dropzone.addEventListener(name, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(name => {
        dropzone.addEventListener(name, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
        });
    });

    dropzone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            handleUploadedFile(files[0]);
        }
    });

    dropzone.addEventListener('click', triggerFileSelect);
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files.length > 0) {
                handleUploadedFile(e.target.files[0]);
            }
        });
    }
}

function triggerFileSelect() {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.open_file_dialog) {
        window.pywebview.api.open_file_dialog().then(filePath => {
            if (filePath) {
                processFilePath(filePath);
            }
        }).catch(() => {
            const fi = document.getElementById('fileInput');
            if (fi) fi.click();
        });
    } else {
        const fi = document.getElementById('fileInput');
        if (fi) fi.click();
    }
}

// Event Listeners for UI Controls
function initEventListeners() {
    const searchInput = document.getElementById('tableSearch');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            state.searchQuery = e.target.value.toLowerCase().trim();
            state.currentPage = 1;
            renderTransactionTable();
        });
    }

    const budgetSlider = document.getElementById('budgetSlider');
    const budgetInput = document.getElementById('budgetInput');

    if (budgetSlider && budgetInput) {
        budgetSlider.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value);
            budgetInput.value = val;
            updateBudgetLimit(val);
        });

        budgetInput.addEventListener('change', (e) => {
            let val = parseFloat(e.target.value);
            if (isNaN(val) || val < 500) val = 500;
            budgetSlider.value = val;
            updateBudgetLimit(val);
        });
    }

    const btnSample = document.getElementById('btnLoadSample');
    if (btnSample) {
        btnSample.addEventListener('click', loadSampleData);
    }

    const btnBrowse = document.getElementById('btnBrowseFile');
    if (btnBrowse) {
        btnBrowse.addEventListener('click', triggerFileSelect);
    }
}

// -------------------------------------------------------------
// File Processing
// -------------------------------------------------------------
function handleUploadedFile(file) {
    showToast(`Loading: ${file.name}...`, 'info');
    const reader = new FileReader();
    reader.onload = (e) => {
        const content = e.target.result;
        processRawText(content, file.name);
    };
    reader.onerror = () => showToast('Failed to read selected file', 'error');
    reader.readAsText(file);
}

function processFilePath(filePath) {
    showToast('Analyzing statement...', 'info');
    const fileName = filePath.split(/[\/\\]/).pop();
    if (window.pywebview && window.pywebview.api && window.pywebview.api.process_file) {
        window.pywebview.api.process_file(filePath, state.budgetLimit).then(response => {
            if (response && response.success) {
                applyPayload(response.data, fileName);
                showToast('Analysis completed successfully!', 'success');
            } else {
                showToast(response.error || 'Failed to analyze file', 'error');
            }
        }).catch(err => showToast(`Bridge error: ${err}`, 'error'));
    }
}

function processRawText(content, fileName = 'transactions.txt') {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.process_raw_text) {
        window.pywebview.api.process_raw_text(content, state.budgetLimit).then(response => {
            if (response && response.success) {
                applyPayload(response.data, fileName);
                showToast('Analysis completed successfully!', 'success');
            } else {
                showToast(response.error || 'Failed to parse text', 'error');
            }
        });
    } else {
        const local = parseLocally(content, state.budgetLimit);
        applyPayload(local, fileName);
        showToast('Processed locally!', 'success');
    }
}

function updateBudgetLimit(newLimit) {
    state.budgetLimit = newLimit;
    if (window.pywebview && window.pywebview.api && window.pywebview.api.recalculate_budget && state.payload) {
        window.pywebview.api.recalculate_budget(newLimit).then(response => {
            if (response && response.success) {
                state.payload.summary = response.data.summary;
                renderKpiCards();
                renderAllCharts();
            }
        });
    } else if (state.payload) {
        const total = state.payload.summary.total_spent;
        state.payload.summary.budget_limit = newLimit;
        state.payload.summary.is_over_budget = total > newLimit;
        state.payload.summary.over_budget_amount = Math.max(0, total - newLimit);
        state.payload.summary.remaining_budget = Math.max(0, newLimit - total);
        renderKpiCards();
        renderAllCharts();
    }
}

function applyPayload(payload, sourceName = 'transactions.txt') {
    state.payload = payload;
    state.sourceFileName = sourceName;
    state.currentPage = 1;
    state.budgetLimit = payload.summary.budget_limit || 10000.0;

    const activeFileBadge = document.getElementById('activeFileBadge');
    if (activeFileBadge) activeFileBadge.textContent = sourceName;

    const budgetSlider = document.getElementById('budgetSlider');
    const budgetInput = document.getElementById('budgetInput');
    if (budgetSlider && budgetInput) {
        budgetSlider.value = state.budgetLimit;
        budgetInput.value = state.budgetLimit;
    }

    renderKpiCards();
    renderCategoryChips();
    renderAllCharts();
    renderTransactionTable();
    renderErrorDrawer();
}

// -------------------------------------------------------------
// KPI Cards Rendering — 4-Card Premium Dashboard
// -------------------------------------------------------------
function renderKpiCards() {
    if (!state.payload) return;
    const { summary, transactions } = state.payload;

    // ── Card 1: Total Spent ──
    document.getElementById('kpiTotalSpent').textContent = formatINR(summary.total_spent);
    document.getElementById('kpiTxnCount').textContent = `${summary.transaction_count} transactions`;
    document.getElementById('kpiAvgSpend').textContent = formatINR(summary.average_transaction);

    // Budget-used progress bar (% of budget consumed)
    const usedPct = Math.min((summary.total_spent / summary.budget_limit) * 100, 100);
    const usedBar = document.getElementById('kpiBudgetUsedBar');
    if (usedBar) {
        usedBar.style.width = usedPct.toFixed(1) + '%';
        usedBar.style.background = usedPct >= 100
            ? 'linear-gradient(90deg, #ef4444, #f87171)'
            : 'linear-gradient(90deg, #7c3aed, #a855f7)';
    }

    // ── Card 2: Monthly Budget ──
    document.getElementById('kpiBudgetLimit').textContent = formatINR(summary.budget_limit);
    const remainingEl = document.getElementById('kpiBudgetRemaining');
    if (remainingEl) {
        const remaining = summary.remaining_budget;
        if (summary.is_over_budget) {
            remainingEl.textContent = `${formatINR(summary.over_budget_amount)} over`;
            remainingEl.className = 'kpi-trend down';
        } else {
            remainingEl.textContent = `${formatINR(remaining)} left`;
            remainingEl.className = remaining < summary.budget_limit * 0.2 ? 'kpi-trend down' : 'kpi-trend up';
        }
    }

    // ── Card 3: Highest Single Spend ──
    const topTxn = (transactions || []).reduce(
        (best, t) => (parseFloat(t.amount) > parseFloat(best?.amount || 0) ? t : best),
        null
    );
    if (topTxn) {
        document.getElementById('kpiHighestSpend').textContent = formatINR(topTxn.amount);
        document.getElementById('kpiHighestMerchant').textContent = topTxn.merchant || '—';
        document.getElementById('kpiHighestDate').textContent = topTxn.date || '—';
    } else {
        document.getElementById('kpiHighestSpend').textContent = '₹0.00';
        document.getElementById('kpiHighestMerchant').textContent = '—';
        document.getElementById('kpiHighestDate').textContent = '—';
    }

    // ── Card 4: Budget Health ──
    const catTotals = summary.category_total || {};
    const topCat = summary.top_category || 'N/A';
    const topCatAmt = catTotals[topCat] || 0;
    document.getElementById('kpiTopCategory').textContent = topCat;
    document.getElementById('kpiTopCategoryAmt').textContent = formatINR(topCatAmt);

    const healthEl    = document.getElementById('kpiBudgetHealth');
    const statusCard  = document.getElementById('kpiStatusCard');
    const statusIcon  = document.getElementById('kpiStatusIcon');
    const healthBar   = document.getElementById('kpiBudgetHealthBar');
    const pct = ((summary.total_spent / summary.budget_limit) * 100).toFixed(1);

    if (summary.is_over_budget) {
        healthEl.innerHTML = `<span style="color:#ef4444;">⚠️ Over by ${formatINR(summary.over_budget_amount)}</span>`;
        healthEl.style.color = '#ef4444';
        if (statusCard) statusCard.style.setProperty('--card-accent', 'linear-gradient(90deg, #ef4444, #f87171)');
        if (statusIcon) { statusIcon.textContent = '🚨'; statusIcon.style.background = 'rgba(239,68,68,0.15)'; }
        if (healthBar)  { healthBar.style.width = '100%'; healthBar.style.background = 'linear-gradient(90deg, #ef4444, #f87171)'; }
    } else {
        healthEl.innerHTML = `<span style="color:#10b981;">✅ ${pct}% used · Safe</span>`;
        healthEl.style.color = '#10b981';
        if (statusCard) statusCard.style.setProperty('--card-accent', 'linear-gradient(90deg, #10b981, #34d399)');
        if (statusIcon) { statusIcon.textContent = '✅'; statusIcon.style.background = 'rgba(16,185,129,0.12)'; }
        if (healthBar)  { healthBar.style.width = pct + '%'; healthBar.style.background = 'linear-gradient(90deg, #10b981, #34d399)'; }
    }
}

// -------------------------------------------------------------
// Category Filter Chips
// -------------------------------------------------------------
function renderCategoryChips() {
    const container = document.getElementById('categoryChipsContainer');
    if (!container || !state.payload) return;

    const categories = Object.keys(state.payload.summary.category_total || {});
    let chipsHtml = `
        <button class="chip ${state.activeCategoryFilter === 'ALL' ? 'active' : ''}" onclick="setCategoryFilter('ALL')">
            All (${state.payload.transactions.length})
        </button>
    `;

    categories.forEach(cat => {
        const count = state.payload.transactions.filter(t => t.category === cat).length;
        const meta = CATEGORY_META[cat] || CATEGORY_META.Other;
        const isActive = state.activeCategoryFilter === cat ? 'active' : '';
        chipsHtml += `
            <button class="chip ${isActive}" onclick="setCategoryFilter('${cat}')">
                ${meta.icon} ${cat} (${count})
            </button>
        `;
    });

    container.innerHTML = chipsHtml;
}

window.setCategoryFilter = function(category) {
    state.activeCategoryFilter = category;
    state.currentPage = 1;
    renderCategoryChips();
    renderTransactionTable();
};

// -------------------------------------------------------------
// High-Performance Native SVG Charting Engine (100% Offline)
// -------------------------------------------------------------
function renderAllCharts() {
    if (!state.payload) return;
    renderDonutChart();
    renderTrendChart();
    renderBudgetGauge();
}

// 1. Standalone SVG Donut Chart
function renderDonutChart() {
    const container = document.getElementById('chartCategoryDonut');
    if (!container || !state.payload) return;

    const summary = state.payload.summary;
    const catTotals = summary.category_total || {};
    const total = summary.total_spent || 1;
    const entries = Object.entries(catTotals);

    if (entries.length === 0) {
        container.innerHTML = `<div style="color:#64748b; text-align:center; padding:40px;">No category data</div>`;
        return;
    }

    const radius = 80;
    const strokeWidth = 28;
    const circumference = 2 * Math.PI * radius;
    let accumulatedAngle = 0;

    let circlesSvg = '';
    let legendHtml = '<div style="display:flex; flex-wrap:wrap; justify-content:center; gap:10px; margin-top:14px;">';

    entries.forEach(([cat, amt]) => {
        const fraction = amt / total;
        const dashArray = fraction * circumference;
        const dashOffset = -accumulatedAngle * circumference;
        const color = CATEGORY_META[cat] ? CATEGORY_META[cat].color : '#94a3b8';
        const pct = (fraction * 100).toFixed(1);

        circlesSvg += `
            <circle cx="120" cy="120" r="${radius}" fill="none"
                stroke="${color}" stroke-width="${strokeWidth}"
                stroke-dasharray="${dashArray} ${circumference}"
                stroke-dashoffset="${dashOffset}"
                style="transition: stroke-width 0.2s; cursor: pointer;"
                onmouseover="this.setAttribute('stroke-width', '34')"
                onmouseout="this.setAttribute('stroke-width', '${strokeWidth}')"
            >
                <title>${cat}: ${formatINR(amt)} (${pct}%)</title>
            </circle>
        `;

        legendHtml += `
            <div style="display:flex; align-items:center; gap:6px; font-size:12px; color:#cbd5e1; cursor:pointer;" onclick="setCategoryFilter('${cat}')">
                <span style="width:10px; height:10px; border-radius:50%; background:${color}; display:inline-block;"></span>
                <span>${cat}</span>
                <span style="color:#94a3b8; font-weight:600;">${pct}%</span>
            </div>
        `;

        accumulatedAngle += fraction;
    });

    legendHtml += '</div>';

    container.innerHTML = `
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; width:100%;">
            <svg width="240" height="240" viewBox="0 0 240 240" style="transform: rotate(-90deg); overflow: visible;">
                <circle cx="120" cy="120" r="${radius}" fill="none" stroke="#1c1e2e" stroke-width="${strokeWidth}" />
                ${circlesSvg}
                <text x="120" y="115" text-anchor="middle" fill="#ffffff" font-size="18" font-weight="700" font-family="Outfit, sans-serif" style="transform: rotate(90deg); transform-origin: 120px 120px;">
                    ${formatINR(total)}
                </text>
                <text x="120" y="135" text-anchor="middle" fill="#94a3b8" font-size="11" font-family="Outfit, sans-serif" style="transform: rotate(90deg); transform-origin: 120px 120px;">
                    Total Spent
                </text>
            </svg>
            ${legendHtml}
        </div>
    `;
}

// 2. Standalone SVG Spending Trend Timeline Area Chart
function renderTrendChart() {
    const container = document.getElementById('chartSpendTrend');
    if (!container || !state.payload) return;

    const trend = state.payload.summary.daily_trend || [];
    if (trend.length === 0) {
        container.innerHTML = `<div style="color:#64748b; text-align:center; padding:40px;">No timeline data</div>`;
        return;
    }

    const width = 460;
    const height = 200;
    const padX = 40;
    const padY = 25;
    const chartW = width - padX * 2;
    const chartH = height - padY * 2;

    const maxAmt = Math.max(...trend.map(d => d.amount), 100);
    const points = trend.map((d, i) => {
        const x = padX + (i / Math.max(trend.length - 1, 1)) * chartW;
        const y = height - padY - (d.amount / maxAmt) * chartH;
        return { x, y, ...d };
    });

    let pathD = `M ${points[0].x} ${points[0].y}`;
    for (let i = 1; i < points.length; i++) {
        pathD += ` L ${points[i].x} ${points[i].y}`;
    }

    const areaD = `${pathD} L ${points[points.length - 1].x} ${height - padY} L ${points[0].x} ${height - padY} Z`;

    let dotsSvg = '';
    points.forEach(p => {
        dotsSvg += `
            <circle cx="${p.x}" cy="${p.y}" r="4" fill="#8b5cf6" stroke="#ffffff" stroke-width="1.5" style="cursor:pointer;">
                <title>${p.date}: ${formatINR(p.amount)} (${p.count} txns)</title>
            </circle>
        `;
    });

    const firstDate = trend[0].date.slice(5);
    const lastDate = trend[trend.length - 1].date.slice(5);

    container.innerHTML = `
        <div style="width:100%; display:flex; flex-direction:column; align-items:center;">
            <svg viewBox="0 0 ${width} ${height}" style="width:100%; height:auto; max-height:220px;">
                <defs>
                    <linearGradient id="purpleAreaGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.5"/>
                        <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0.0"/>
                    </linearGradient>
                </defs>
                <!-- Grid Lines -->
                <line x1="${padX}" y1="${padY}" x2="${width - padX}" y2="${padY}" stroke="#1c1e2e" stroke-dasharray="3 3" />
                <line x1="${padX}" y1="${padY + chartH / 2}" x2="${width - padX}" y2="${padY + chartH / 2}" stroke="#1c1e2e" stroke-dasharray="3 3" />
                <line x1="${padX}" y1="${height - padY}" x2="${width - padX}" y2="${height - padY}" stroke="#2e3148" />

                <!-- Area Fill -->
                <path d="${areaD}" fill="url(#purpleAreaGrad)" />
                <!-- Stroke Line -->
                <path d="${pathD}" fill="none" stroke="#8b5cf6" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
                ${dotsSvg}

                <!-- X Axis Labels -->
                <text x="${padX}" y="${height - 6}" fill="#64748b" font-size="11" font-family="Outfit">${firstDate}</text>
                <text x="${width - padX}" y="${height - 6}" text-anchor="end" fill="#64748b" font-size="11" font-family="Outfit">${lastDate}</text>
                <!-- Y Axis Max Label -->
                <text x="${padX - 8}" y="${padY + 4}" text-anchor="end" fill="#64748b" font-size="10" font-family="JetBrains Mono">₹${Math.round(maxAmt)}</text>
            </svg>
            <div style="font-size:12px; color:#94a3b8; margin-top:4px;">
                Spend progression across ${trend.length} active transaction days
            </div>
        </div>
    `;
}

// 3. Standalone SVG Budget Utilization Radial Gauge
function renderBudgetGauge() {
    const container = document.getElementById('chartBudgetGauge');
    if (!container || !state.payload) return;

    const summary = state.payload.summary;
    const limit = summary.budget_limit || 10000;
    const spent = summary.total_spent || 0;
    const ratio = spent / limit;
    const pct = (ratio * 100).toFixed(1);

    const isOver = summary.is_over_budget;
    const strokeColor = isOver ? '#ef4444' : '#10b981';

    const radius = 70;
    const strokeWidth = 16;
    const circumference = 2 * Math.PI * radius;
    // 270 degree gauge arc
    const gaugeArc = 0.75 * circumference;
    const filledArc = Math.min(1.0, ratio) * gaugeArc;

    container.innerHTML = `
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:10px;">
            <svg width="200" height="190" viewBox="0 0 200 190">
                <!-- Background Track -->
                <circle cx="100" cy="100" r="${radius}" fill="none" stroke="#1c1e2e" stroke-width="${strokeWidth}"
                    stroke-dasharray="${gaugeArc} ${circumference}"
                    stroke-dashoffset="0"
                    stroke-linecap="round"
                    style="transform: rotate(135deg); transform-origin: 100px 100px;"
                />
                <!-- Progress Arc -->
                <circle cx="100" cy="100" r="${radius}" fill="none" stroke="${strokeColor}" stroke-width="${strokeWidth}"
                    stroke-dasharray="${filledArc} ${circumference}"
                    stroke-dashoffset="0"
                    stroke-linecap="round"
                    style="transform: rotate(135deg); transform-origin: 100px 100px; transition: stroke-dasharray 0.5s ease;"
                />
                <text x="100" y="95" text-anchor="middle" fill="#ffffff" font-size="28" font-weight="800" font-family="Outfit, sans-serif">
                    ${pct}%
                </text>
                <text x="100" y="120" text-anchor="middle" fill="${strokeColor}" font-size="12" font-weight="600" font-family="Outfit, sans-serif">
                    ${isOver ? '⚠️ Over Budget' : '✅ Within Budget'}
                </text>
            </svg>
            <div style="font-size:12px; color:#cbd5e1; text-align:center;">
                ${isOver 
                    ? `<span style="color:#ef4444; font-weight:600;">Exceeded by ${formatINR(summary.over_budget_amount)}</span>` 
                    : `<span style="color:#10b981; font-weight:600;">${formatINR(summary.remaining_budget)} remaining</span>`}
            </div>
        </div>
    `;
}

// -------------------------------------------------------------
// Transactions Table & Pagination
// -------------------------------------------------------------
function renderTransactionTable() {
    const tableBody = document.getElementById('transactionTableBody');
    const countLabel = document.getElementById('tableCountLabel');
    if (!tableBody || !state.payload) return;

    let list = [...state.payload.transactions];

    if (state.activeCategoryFilter !== 'ALL') {
        list = list.filter(t => t.category === state.activeCategoryFilter);
    }

    if (state.searchQuery) {
        list = list.filter(t =>
            t.merchant.toLowerCase().includes(state.searchQuery) ||
            t.date.toLowerCase().includes(state.searchQuery) ||
            t.category.toLowerCase().includes(state.searchQuery)
        );
    }

    list.sort((a, b) => {
        let valA = a[state.sortField];
        let valB = b[state.sortField];
        if (state.sortField === 'amount') {
            return state.sortOrder === 'asc' ? valA - valB : valB - valA;
        }
        return state.sortOrder === 'asc'
            ? String(valA).localeCompare(String(valB))
            : String(valB).localeCompare(String(valA));
    });

    const totalRecords = list.length;
    const totalPages = Math.max(1, Math.ceil(totalRecords / state.rowsPerPage));
    state.currentPage = Math.min(state.currentPage, totalPages);

    const startIndex = (state.currentPage - 1) * state.rowsPerPage;
    const paginated = list.slice(startIndex, startIndex + state.rowsPerPage);

    if (countLabel) {
        countLabel.textContent = `Showing ${paginated.length} of ${totalRecords} records`;
    }

    if (paginated.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 36px; color: #64748b;">
                    🔍 No transactions found matching your criteria.
                </td>
            </tr>
        `;
        renderPagination(1, 1);
        return;
    }

    tableBody.innerHTML = paginated.map(txn => {
        const meta = CATEGORY_META[txn.category] || CATEGORY_META.Other;
        return `
            <tr>
                <td style="color: #64748b; font-size: 12px;">#${txn.raw_line_number}</td>
                <td class="font-mono" style="color: #94a3b8;">${txn.date}</td>
                <td style="font-weight: 500;">${escapeHtml(txn.merchant)}</td>
                <td>
                    <span class="badge-category cat-${txn.category}">
                        <span>${meta.icon}</span> ${txn.category}
                    </span>
                </td>
                <td class="font-mono" style="text-align: right; font-weight: 700; color: #f8fafc;">
                    ${formatINR(txn.amount)}
                </td>
            </tr>
        `;
    }).join('');

    renderPagination(state.currentPage, totalPages);
}

function renderPagination(currentPage, totalPages) {
    const container = document.getElementById('paginationControls');
    if (!container) return;

    container.innerHTML = `
        <button class="btn-secondary" style="padding: 6px 12px; font-size: 12px;" ${currentPage <= 1 ? 'disabled' : ''} onclick="changePage(${currentPage - 1})">
            ◀ Prev
        </button>
        <span style="font-size: 13px; color: #94a3b8;">Page ${currentPage} of ${totalPages}</span>
        <button class="btn-secondary" style="padding: 6px 12px; font-size: 12px;" ${currentPage >= totalPages ? 'disabled' : ''} onclick="changePage(${currentPage + 1})">
            Next ▶
        </button>
    `;
}

window.changePage = function(p) {
    state.currentPage = p;
    renderTransactionTable();
};

window.sortTable = function(field) {
    if (state.sortField === field) {
        state.sortOrder = state.sortOrder === 'asc' ? 'desc' : 'asc';
    } else {
        state.sortField = field;
        state.sortOrder = 'asc';
    }
    renderTransactionTable();
};

// -------------------------------------------------------------
// Skipped / Malformed Lines Drawer
// -------------------------------------------------------------
function renderErrorDrawer() {
    const errorSection = document.getElementById('errorDrawerSection');
    const errorCountBadge = document.getElementById('errorCountBadge');
    const errorList = document.getElementById('errorList');

    if (!errorSection || !state.payload) return;

    const errors = state.payload.errors || [];
    if (errors.length === 0) {
        errorSection.style.display = 'none';
        return;
    }

    errorSection.style.display = 'block';
    if (errorCountBadge) {
        errorCountBadge.textContent = `${errors.length} skipped line(s)`;
    }

    if (errorList) {
        errorList.innerHTML = errors.map(err => `
            <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; font-size: 13px;">
                <span style="color: #ef4444; font-weight: 600;">Line ${err.line_number}:</span>
                <code style="background: #1c1e2e; padding: 2px 6px; border-radius: 4px; color: #f87171; margin: 0 6px;">${escapeHtml(err.raw_line)}</code>
                <span style="color: #94a3b8;">— ${escapeHtml(err.reason)}</span>
            </div>
        `).join('');
    }
}

// -------------------------------------------------------------
// Export System
// -------------------------------------------------------------
window.triggerExport = function(formatType) {
    if (!state.payload) {
        showToast('No data available to export', 'error');
        return;
    }

    showToast(`Exporting ${formatType.toUpperCase()} report...`, 'info');

    if (window.pywebview && window.pywebview.api && window.pywebview.api.export_data) {
        window.pywebview.api.export_data(formatType).then(response => {
            if (response && response.success) {
                showToast(`Saved to: ${response.path}`, 'success');
            } else {
                showToast(response.error || 'Export cancelled', 'error');
            }
        });
    } else {
        downloadLocalExport(formatType);
    }
};

function downloadLocalExport(formatType) {
    let content = '', mime = 'text/plain', filename = `phonepe_expense_report.${formatType}`;

    if (formatType === 'csv') {
        content = "Line,Date,Merchant,Category,Amount\n" +
            state.payload.transactions.map(t => `${t.raw_line_number},${t.date},"${t.merchant}",${t.category},${t.amount}`).join("\n");
        mime = 'text/csv';
    } else if (formatType === 'json') {
        content = JSON.stringify(state.payload, null, 2);
        mime = 'application/json';
    }

    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    showToast(`Downloaded ${filename}`, 'success');
}

// -------------------------------------------------------------
// Sample Data & Local Parser
// -------------------------------------------------------------
function loadSampleData() {
    const sampleText = `2026-08-01, Swiggy, 350
2026-08-02, Uber Ride, 180
2026-08-03, DMart Supermarket, 1450
2026-08-04, Zomato Food, 220
2026-08-05, Petrol Pump HPCL, 600
2026-08-06, Amazon Purchase, 999
2026-08-07, Canteen Snacks, 60
2026-08-08, Mobile Recharge Jio, 299
2026-08-09, Invalid Line Without Comma
2026-08-10, Tea Stall, 40
2026-08-11, Flipkart Order, 1299
2026-08-12, Ola Mini Ride, 215
2026-08-13, Electricity Bill Bescom, 1850
2026-08-14, Restaurant Dinner, 850
2026-08-15, Broadband Wifi Bill Airtel, 799
2026-08-16, Metro Card Recharge, 500
2026-08-17, Myntra Fashion Shopping, 1750
2026-08-18, Rapido Bike Taxi, 75
2026-08-19, Swiggy Instamart, 420
2026-08-20, Cinema Movie Ticket, 350
2026-08-21, Petrol Pump BPCL, 750
2026-08-22, Pharmacy Medical Store, 240
2026-08-23, Zomato Delivery, 540
2026-08-24, Water Bill Payment, 310
2026-08-25, Gym Membership, 1200`;

    processRawText(sampleText, 'transactions.txt (Sample)');
}

function parseLocally(text, budget = 10000.0) {
    const lines = text.split(/\r?\n/);
    const txns = [];
    const errs = [];
    const catTotals = {};
    let total = 0;

    lines.forEach((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('#')) return;

        const parts = trimmed.split(',').map(p => p.trim());
        if (parts.length < 3) {
            errs.push({ line_number: idx + 1, raw_line: trimmed, reason: "Malformed format: Missing comma separator" });
            return;
        }

        const amt = parseFloat(parts[2].replace(/[₹$,]/g, ''));
        if (isNaN(amt)) {
            errs.push({ line_number: idx + 1, raw_line: trimmed, reason: "Invalid numeric amount" });
            return;
        }

        const m = parts[1].toLowerCase();
        let cat = 'Other';
        if (/swiggy|zomato|canteen|tea|restaurant|instamart|food/.test(m)) cat = 'Food';
        else if (/ola|uber|rapido|metro|petrol|fuel|hpcl|bpcl/.test(m)) cat = 'Travel';
        else if (/dmart|amazon|flipkart|flipcart|myntra/.test(m)) cat = 'Shopping';
        else if (/recharge|electricity|bescom|wifi|airtel|jio|water|bill/.test(m)) cat = 'Bills';
        else if (/pharmacy|gym|medical/.test(m)) cat = 'Health';
        else if (/cinema|movie|netflix/.test(m)) cat = 'Entertainment';

        txns.push({
            id: `txn_${idx + 1}`,
            date: parts[0],
            merchant: parts[1],
            amount: amt,
            category: cat,
            raw_line_number: idx + 1
        });

        catTotals[cat] = (catTotals[cat] || 0) + amt;
        total += amt;
    });

    const isOver = total > budget;
    const datesMap = {};
    txns.forEach(t => {
        datesMap[t.date] = (datesMap[t.date] || 0) + t.amount;
    });

    const dailyTrend = Object.keys(datesMap).sort().map(d => ({ date: d, amount: datesMap[d], count: 1 }));

    return {
        summary: {
            total_spent: total,
            budget_limit: budget,
            is_over_budget: isOver,
            over_budget_amount: Math.max(0, total - budget),
            remaining_budget: Math.max(0, budget - total),
            category_total: catTotals,
            category_percentages: {},
            daily_trend: dailyTrend,
            transaction_count: txns.length,
            average_transaction: txns.length ? total / txns.length : 0,
            top_category: Object.keys(catTotals)[0] || 'None'
        },
        transactions: txns,
        errors: errs
    };
}

// Toast Notifications
function showToast(message, type = 'info') {
    const toast = document.getElementById('notificationToast');
    if (!toast) return;

    toast.textContent = message;
    toast.className = `notification-toast show ${type}`;

    setTimeout(() => {
        toast.className = 'notification-toast';
    }, 3200);
}

// -------------------------------------------------------------
// About Modal Controls
// -------------------------------------------------------------
function openAboutModal() {
    const modal = document.getElementById('aboutModal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

function closeAboutModal(event) {
    if (event && event.target && event.target.id !== 'aboutModal' && event.target.tagName !== 'BUTTON') {
        return;
    }
    const modal = document.getElementById('aboutModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Ensure global accessibility for inline onclick handlers
window.openAboutModal = openAboutModal;
window.closeAboutModal = closeAboutModal;

