let currentVehicleId = null;
const API_BASE = '/api';

const STORAGE_KEY = 'muttlogbook_vehicle_id';

const validators = {
    required: (value) => value && value.trim() ? null : 'This field is required',
    
    positiveInt: (value) => {
        const num = parseInt(value);
        return (!isNaN(num) && num > 0) ? null : 'Must be a positive number';
    },
    
    nonNegativeInt: (value) => {
        const num = parseInt(value);
        return (!isNaN(num) && num >= 0) ? null : 'Must be 0 or greater';
    },
    
    positiveFloat: (value) => {
        const num = parseFloat(value);
        return (!isNaN(num) && num >= 0) ? null : 'Must be 0 or greater';
    },
    
    vin: (value) => {
        if (!value) return null;
        const clean = value.replace(/[\s-]/g, '').toUpperCase();
        return (clean.length === 17 && /^[A-HJ-NPR-Z0-9]{17}$/.test(clean)) ? null : 'VIN must be 17 characters (letters A-Z except I, O, Q)';
    },
    
    year: (value) => {
        const year = parseInt(value);
        const currentYear = new Date().getFullYear();
        return (!isNaN(year) && year >= 1900 && year <= currentYear + 1) ? null : `Year must be between 1900 and ${currentYear + 1}`;
    },
    
    date: (value) => {
        if (!value) return 'Date is required';
        const d = new Date(value);
        return (!isNaN(d.getTime())) ? null : 'Invalid date';
    },
    
    dateNotFuture: (value) => {
        if (!value) return 'Date is required';
        const d = new Date(value);
        const today = new Date();
        today.setHours(23, 59, 59, 999);
        return (d <= today) ? null : 'Date cannot be in the future';
    }
};

function showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    requestAnimationFrame(() => {
        toast.classList.add('toast-show');
    });
    
    setTimeout(() => {
        toast.classList.remove('toast-show');
        toast.classList.add('toast-hide');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function validateField(value, rules) {
    if (!rules || rules.length === 0) return null;
    for (const rule of rules) {
        const error = validators[rule](value);
        if (error) return error;
    }
    return null;
}

function showFieldError(input, message) {
    input.classList.add('input-error');
    let errorEl = input.parentElement.querySelector('.field-error');
    if (!errorEl) {
        errorEl = document.createElement('div');
        errorEl.className = 'field-error';
        input.parentElement.appendChild(errorEl);
    }
    errorEl.textContent = message;
    errorEl.style.display = message ? 'block' : 'none';
}

function clearFieldError(input) {
    input.classList.remove('input-error');
    const errorEl = input.parentElement.querySelector('.field-error');
    if (errorEl) errorEl.style.display = 'none';
}

function validateForm(formId, rules) {
    let isValid = true;
    const form = document.getElementById(formId);
    
    for (const [fieldId, fieldRules] of Object.entries(rules)) {
        const input = document.getElementById(fieldId);
        if (!input) continue;
        
        clearFieldError(input);
        const error = validateField(input.value, fieldRules);
        if (error) {
            showFieldError(input, error);
            isValid = false;
        }
    }
    
    return isValid;
}

async function loadVehicleSelector() {
    const vehicles = await apiCall('/vehicles');
    const select = document.getElementById('vehicle-select');
    select.innerHTML = vehicles.map(v => 
        `<option value="${v.id}" ${v.id === currentVehicleId ? 'selected' : ''}>${v.name}</option>`
    ).join('');
    
    const savedVehicle = localStorage.getItem(STORAGE_KEY);
    if (savedVehicle && vehicles.find(v => v.id === parseInt(savedVehicle))) {
        currentVehicleId = parseInt(savedVehicle);
        select.value = currentVehicleId;
    } else if (vehicles.length > 0 && !currentVehicleId) {
        currentVehicleId = vehicles[0].id;
        select.value = currentVehicleId;
        localStorage.setItem(STORAGE_KEY, currentVehicleId);
    }
}

document.getElementById('vehicle-select').addEventListener('change', (e) => {
    currentVehicleId = parseInt(e.target.value);
    localStorage.setItem(STORAGE_KEY, currentVehicleId);
    loadDashboard();
});

document.querySelector('header h1').addEventListener('click', () => {
    showView('dashboard');
});

document.getElementById('add-vehicle-btn').addEventListener('click', () => {
    showModal('Add Vehicle', `
        <form id="new-vehicle-form">
            <div class="form-group">
                <label>Name</label>
                <input type="text" id="nv-name" required>
            </div>
            <div class="form-group">
                <label>VIN</label>
                <input type="text" id="nv-vin">
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Year</label>
                    <input type="number" id="nv-year">
                </div>
                <div class="form-group">
                    <label>Mileage (miles)</label>
                    <input type="number" id="nv-mileage" value="0">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Engine</label>
                    <input type="text" id="nv-engine">
                </div>
                <div class="form-group">
                    <label>Transmission</label>
                    <input type="text" id="nv-transmission">
                </div>
            </div>
            <button type="submit" class="btn-primary">Add Vehicle</button>
        </form>
    `);
    
    document.getElementById('new-vehicle-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const result = await apiCall('/vehicles', {
            method: 'POST',
            body: JSON.stringify({
                name: document.getElementById('nv-name').value,
                vin: document.getElementById('nv-vin').value || null,
                year: parseInt(document.getElementById('nv-year').value) || null,
                mileage: parseInt(document.getElementById('nv-mileage').value) || 0,
                engine: document.getElementById('nv-engine').value || null,
                transmission: document.getElementById('nv-transmission').value || null
            })
        });
        closeModal();
        await loadVehicleSelector();
        currentVehicleId = result.id;
        document.getElementById('vehicle-select').value = currentVehicleId;
        localStorage.setItem(STORAGE_KEY, currentVehicleId);
    });
});

async function apiCall(endpoint, options = {}) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        }
    });
    const text = await response.text();
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    try {
        return JSON.parse(text);
    } catch (e) {
        throw new Error(`Invalid JSON response: ${text.substring(0, 100)}`);
    }
}

function showView(viewId) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(viewId).classList.add('active');
    document.querySelector(`[data-view="${viewId}"]`).classList.add('active');
    
    if (viewId === 'documentation') {
        const activeTab = document.querySelector('.doc-tab-btn.active');
        if (activeTab) {
            switchDocTab(activeTab.dataset.docTab);
        }
    }
    
    switch(viewId) {
        case 'dashboard': loadDashboard(); break;
        case 'vehicle': loadVehicle(); break;
        case 'analytics': loadAnalytics(); break;
        case 'maintenance': loadMaintenance(); break;
        case 'mods': loadMods(); break;
        case 'costs': loadCosts(); break;
        case 'documentation': 
            const activeTab = document.querySelector('.doc-tab-btn.active');
            if (activeTab) {
                switchDocTab(activeTab.dataset.docTab);
            }
            break;
        case 'notes': loadNotes(); break;
        case 'vcds': loadVCDS(); break;
        case 'settings': loadSettings(); break;
    }
}

function switchDocTab(tabName) {
    document.querySelectorAll('.doc-tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.docTab === tabName);
    });
    document.querySelectorAll('.doc-subview').forEach(subview => {
        subview.classList.remove('active');
    });
    const subview = document.getElementById(`${tabName}-subview`);
    if (subview) subview.classList.add('active');
    
    if (tabName === 'receipts') {
        loadReceipts();
    } else if (tabName === 'guides') {
        loadGuides();
    } else if (tabName === 'documents') {
        loadDocuments();
    }
}

document.querySelectorAll('.doc-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => switchDocTab(btn.dataset.docTab));
});

async function loadDashboard() {
    if (!currentVehicleId) return;
    const data = await apiCall(`/dashboard?vehicle_id=${currentVehicleId}`);
    const analytics = await apiCall(`/analytics?vehicle_id=${currentVehicleId}`);
    const vehicles = await apiCall('/vehicles');
    const vehicle = vehicles.find(v => v.id === currentVehicleId);
    const maintenance = await apiCall(`/maintenance?vehicle_id=${currentVehicleId}`);
    const mods = await apiCall(`/mods?vehicle_id=${currentVehicleId}`);
    
    document.getElementById('total-spent').textContent = `£${(data.total_spent || 0).toFixed(2)}`;
    document.getElementById('maintenance-cost').textContent = `£${(data.maintenance_cost || 0).toFixed(2)}`;
    document.getElementById('mods-cost').textContent = `£${(data.mods_cost || 0).toFixed(2)}`;
    document.getElementById('active-faults').textContent = data.active_faults || 0;
    
    const mileage = vehicle?.mileage || 0;
    document.getElementById('current-mileage').textContent = `${mileage.toLocaleString()} mi`;
    document.getElementById('cost-per-mile').textContent = mileage > 0 ? `£${(data.total_spent / mileage).toFixed(2)}` : '£0.00';
    document.getElementById('total-services').textContent = maintenance.length;
    const activeMods = mods.filter(m => m.status === 'in_progress').length;
    document.getElementById('active-mods').textContent = activeMods;
    
    const list = document.getElementById('recent-list');
    list.innerHTML = data.recent_maintenance.map(m => `
        <li>${m.date || 'N/A'} - ${m.category || ''}: ${m.description || ''}</li>
    `).join('') || '<li>No recent service records</li>';
    
    // Maintenance alerts
    const alertsDiv = document.getElementById('maintenance-alerts');
    if (alertsDiv && analytics.service_intervals) {
        const current = analytics.current_mileage || 0;
        const intervals = analytics.service_intervals;
        const lastService = analytics.last_service;
        let alerts = [];
        
        for (const [key, interval] of Object.entries(intervals)) {
            const last = lastService[key];
            if (last && last.mileage) {
                const milesSince = current - last.mileage;
                const percentDue = (milesSince / interval.miles) * 100;
                
                if (percentDue >= 100) {
                    alerts.push({ type: 'danger', text: `${key.replace('_', ' ').toUpperCase()} is OVERDUE by ${(milesSince - interval.miles).toLocaleString()} miles` });
                } else if (percentDue >= 80) {
                    alerts.push({ type: 'warning', text: `${key.replace('_', ' ').toUpperCase()} due soon (${(interval.miles - milesSince).toLocaleString()} miles remaining)` });
                }
            } else if (!last) {
                alerts.push({ type: 'info', text: `${key.replace('_', ' ').toUpperCase()} has never been recorded` });
            }
        }
        
        if (alerts.length > 0) {
            alertsDiv.innerHTML = alerts.map(a => `<div class="alert alert-${a.type}">${a.text}</div>`).join('');
        } else {
            alertsDiv.innerHTML = '';
        }
    }
    
    loadDashboardCharts();
}

let dashboardCharts = {};
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom',
            labels: { color: '#999', padding: 10, font: { size: 11 } }
        }
    },
    scales: {
        x: {
            ticks: { color: '#888', font: { size: 10 } },
            grid: { color: '#333' }
        },
        y: {
            ticks: { color: '#888', font: { size: 10 } },
            grid: { color: '#333' }
        }
    }
};

const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'right',
            labels: { color: '#999', padding: 8, font: { size: 11 } }
        }
    }
};

async function loadDashboardCharts() {
    const analytics = await apiCall(`/analytics?vehicle_id=${currentVehicleId}`);
    
    if (dashboardCharts.category) dashboardCharts.category.destroy();
    if (dashboardCharts.trends) dashboardCharts.trends.destroy();
    if (dashboardCharts.timeline) dashboardCharts.timeline.destroy();
    
    const catCtx = document.getElementById('category-chart');
    if (catCtx && analytics.category_spending) {
        dashboardCharts.category = new Chart(catCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(analytics.category_spending),
                datasets: [{
                    data: Object.values(analytics.category_spending),
                    backgroundColor: ['#4a90d9', '#50c878', '#f5a623', '#d0021b', '#9013fe', '#b8e986']
                }]
            },
            options: doughnutOptions
        });
    }
    
    const trendCtx = document.getElementById('trends-chart');
    if (trendCtx && analytics.monthly_spending) {
        const months = Object.keys(analytics.monthly_spending).sort().slice(-12);
        dashboardCharts.trends = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Monthly Spending (£)',
                    data: months.map(m => analytics.monthly_spending[m]),
                    borderColor: '#4a90d9',
                    backgroundColor: 'rgba(74, 144, 217, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: chartOptions
        });
    }
    
    const timelineCtx = document.getElementById('timeline-chart');
    if (timelineCtx) {
        const maintenance = await apiCall(`/maintenance?vehicle_id=${currentVehicleId}`);
        const sorted = maintenance.slice(0, 20).reverse();
        dashboardCharts.timeline = new Chart(timelineCtx, {
            type: 'bar',
            data: {
                labels: sorted.map(m => m.date || ''),
                datasets: [{
                    label: 'Service Cost (£)',
                    data: sorted.map(m => m.cost || 0),
                    backgroundColor: '#cc0000'
                }]
            },
            options: chartOptions
        });
    }
}

async function loadVehicle() {
    if (!currentVehicleId) return;
    const vehicles = await apiCall('/vehicles');
    const vehicle = vehicles.find(v => v.id === currentVehicleId);
    if (vehicle) {
        document.getElementById('v-name').value = vehicle.name || '';
        document.getElementById('v-vin').value = vehicle.vin || '';
        document.getElementById('v-year').value = vehicle.year || '';
        document.getElementById('v-mileage').value = vehicle.mileage || '';
        document.getElementById('v-engine').value = vehicle.engine || '';
        document.getElementById('v-transmission').value = vehicle.transmission || '';
    }
}

async function loadAnalytics() {
    if (!currentVehicleId) return;
    
    const dateFilter = document.getElementById('analytics-date-filter')?.value || 'all';
    const categoryFilter = document.getElementById('analytics-category-filter')?.value || '';
    let startDate = null;
    let endDate = null;
    
    if (dateFilter === 'custom') {
        startDate = document.getElementById('analytics-start-date')?.value;
        endDate = document.getElementById('analytics-end-date')?.value;
    } else if (dateFilter === '6months') {
        const d = new Date();
        d.setMonth(d.getMonth() - 6);
        startDate = d.toISOString().split('T')[0];
    } else if (dateFilter === '12months') {
        const d = new Date();
        d.setFullYear(d.getFullYear() - 1);
        startDate = d.toISOString().split('T')[0];
    } else if (dateFilter === 'ytd') {
        const d = new Date();
        startDate = `${d.getFullYear()}-01-01`;
    }
    
    let url = `/analytics?vehicle_id=${currentVehicleId}`;
    if (startDate) url += `&start_date=${startDate}`;
    if (endDate) url += `&end_date=${endDate}`;
    if (categoryFilter) url += `&category=${categoryFilter}`;
    
    const data = await apiCall(url);
    
    const trendCtx = document.getElementById('analytics-trend-chart');
    if (trendCtx) {
        const months = Object.keys(data.monthly_spending).sort();
        const values = months.map(m => data.monthly_spending[m]);
        if (window.analyticsTrendChart) window.analyticsTrendChart.destroy();
        window.analyticsTrendChart = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Monthly Spending (£)',
                    data: values,
                    borderColor: '#4a90d9',
                    backgroundColor: 'rgba(74, 144, 217, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: chartOptions
        });
    }
    
    const catCtx = document.getElementById('analytics-category-chart');
    if (catCtx && data.category_spending) {
        if (window.analyticsCatChart) window.analyticsCatChart.destroy();
        window.analyticsCatChart = new Chart(catCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(data.category_spending),
                datasets: [{
                    data: Object.values(data.category_spending),
                    backgroundColor: ['#4a90d9', '#50c878', '#f5a623', '#d0021b', '#9013fe', '#b8e986']
                }]
            },
            options: doughnutOptions
        });
    }
    
    const yearlyCtx = document.getElementById('analytics-yearly-chart');
    if (yearlyCtx && data.yearly_spending) {
        const years = Object.keys(data.yearly_spending).sort();
        if (window.analyticsYearlyChart) window.analyticsYearlyChart.destroy();
        window.analyticsYearlyChart = new Chart(yearlyCtx, {
            type: 'bar',
            data: {
                labels: years,
                datasets: [{
                    label: 'Yearly Spending (£)',
                    data: years.map(y => data.yearly_spending[y]),
                    backgroundColor: '#4a90d9'
                }]
            },
            options: chartOptions
        });
    }
    
    const intervalsDiv = document.getElementById('service-intervals');
    if (intervalsDiv && data.service_intervals) {
        const current = data.current_mileage || 0;
        let html = '<div class="intervals-list">';
        for (const [key, interval] of Object.entries(data.service_intervals)) {
            const last = data.last_service[key];
            const miles_since = last ? current - (last.mileage || 0) : null;
            const due_percent = miles_since ? Math.min(100, (miles_since / interval.miles) * 100) : 0;
            const is_due = miles_since !== null && miles_since >= interval.miles;
            html += `
                <div class="interval-item ${is_due ? 'interval-due' : ''}">
                    <div class="interval-name">${key.replace('_', ' ').toUpperCase()}</div>
                    <div class="interval-bar">
                        <div class="interval-fill" style="width: ${due_percent}%"></div>
                    </div>
                    <div class="interval-info">
                        ${last ? `${miles_since?.toLocaleString()} / ${interval.miles.toLocaleString()} mi` : 'Not recorded'}
                        ${is_due ? '<span class="interval-warning">DUE</span>' : ''}
                    </div>
                </div>
            `;
        }
        html += '</div>';
        intervalsDiv.innerHTML = html;
    }
}

let guidesChartInstances = {};
async function loadGuides() {
    const categoryFilter = document.getElementById('guide-category-filter')?.value || '';
    let url = '/guides';
    if (categoryFilter) {
        url += `?category=${categoryFilter}`;
    }
    const guides = await apiCall(url);
    const container = document.getElementById('guides-list');
    
    if (guides.length === 0) {
        container.innerHTML = '<p>No guides yet. Click "Load Templates" to get started.</p>';
        return;
    }
    
    container.innerHTML = guides.map(g => `
        <div class="guide-card">
            <div class="guide-header">
                <h3>${g.title}</h3>
                <span class="guide-category">${g.category || ''}</span>
            </div>
            <div class="guide-content">${g.content || ''}</div>
            <div class="guide-meta">
                ${g.interval_miles ? `<span>Every ${g.interval_miles.toLocaleString()} miles</span>` : ''}
                ${g.interval_months ? `<span>Every ${g.interval_months} months</span>` : ''}
            </div>
            <div class="guide-actions">
                ${!g.is_template ? `<button class="btn-secondary" onclick="editGuide(${g.id})">Edit</button>` : ''}
                ${!g.is_template ? `<button class="btn-danger" onclick="deleteGuide(${g.id})">Delete</button>` : ''}
            </div>
        </div>
    `).join('');
}

async function loadDocuments() {
    if (!currentVehicleId) return;
    
    const typeFilter = document.getElementById('document-type-filter')?.value || '';
    let url = `/documents?vehicle_id=${currentVehicleId}`;
    if (typeFilter) {
        url += `&document_type=${typeFilter}`;
    }
    
    const documents = await apiCall(url);
    const container = document.getElementById('documents-list');
    
    if (documents.length === 0) {
        container.innerHTML = '<p>No documents yet. Click "Add Document" to upload one.</p>';
        return;
    }
    
    container.innerHTML = documents.map(d => `
        <div class="document-card">
            <div class="document-header">
                <h4>${d.title || 'Untitled'}</h4>
                <span class="document-type">${d.document_type || ''}</span>
            </div>
            ${d.description ? `<div class="document-description">${d.description}</div>` : ''}
            <div class="document-date">${d.upload_date ? new Date(d.upload_date).toLocaleDateString() : ''}</div>
            ${d.file_path && d.file_path.match(/\.(jpg|jpeg|png|gif|webp)$/i) ? 
                `<img src="${d.file_path}" alt="${d.title}" class="document-thumbnail" onclick="window.open('${d.file_path}', '_blank')">` : ''}
            ${d.file_path ? `<button class="btn-secondary document-link" onclick="window.open('${d.file_path}', '_blank')">View File</button>` : ''}
        </div>
    `).join('');
}

async function loadReceipts() {
    if (!currentVehicleId) return;
    const categoryFilter = document.getElementById('receipt-category-filter')?.value || '';
    let url = `/receipts?vehicle_id=${currentVehicleId}`;
    if (categoryFilter) {
        url += `&category=${categoryFilter}`;
    }
    const receipts = await apiCall(url);
    const container = document.getElementById('receipts-list');
    
    if (receipts.length === 0) {
        container.innerHTML = '<p>No receipts yet. Click "Add Receipt" to create one.</p>';
        return;
    }
    
    container.innerHTML = receipts.map(r => `
        <div class="receipt-card">
            <div class="receipt-header">
                <span class="receipt-date">${r.date || ''}</span>
                <span class="receipt-category">${r.category || ''}</span>
                <span class="receipt-amount">£${(r.amount || 0).toFixed(2)}</span>
            </div>
            <div class="receipt-vendor">${r.vendor || ''}</div>
            ${r.notes ? `<div class="receipt-notes">${r.notes}</div>` : ''}
            ${r.thumbnail ? `<div class="receipt-thumbnail"><img src="${r.thumbnail}" alt="Receipt thumbnail" onclick="viewReceiptImage('${r.image_url}')"></div>` : ''}
            <div class="receipt-link">
                ${r.maintenance_id ? `<span>Linked to maintenance #${r.maintenance_id}</span>` : ''}
            </div>
            <div class="receipt-actions">
                <button class="btn-secondary" onclick="editReceipt(${r.id})">Edit</button>
                <button class="btn-danger" onclick="deleteReceipt(${r.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

document.getElementById('receipt-category-filter')?.addEventListener('change', loadReceipts);

function viewReceiptImage(imageUrl) {
    if (imageUrl) {
        window.open(imageUrl, '_blank');
    }
}

async function showAddReceiptModal(existingReceipt = null) {
    const isEdit = !!existingReceipt;
    const title = isEdit ? 'Edit Receipt' : 'Add Receipt';
    
    const maintenance = await apiCall(`/maintenance?vehicle_id=${currentVehicleId}`);
    const maintenanceOptions = maintenance.map(m => 
        `<option value="${m.id}" ${existingReceipt?.maintenance_id === m.id ? 'selected' : ''}>${m.date || ''} - ${m.description || 'Maintenance #' + m.id}</option>`
    ).join('');
    
    showModal(title, `
        <form id="receipt-form">
            ${isEdit ? `<input type="hidden" id="receipt-id" value="${existingReceipt.id}">` : ''}
            <div class="form-row">
                <div class="form-group">
                    <label>Date</label>
                    <input type="date" id="r-date" value="${existingReceipt?.date || ''}" required>
                </div>
                <div class="form-group">
                    <label>Amount (£)</label>
                    <input type="number" step="0.01" id="r-amount" value="${existingReceipt?.amount || ''}" required>
                </div>
            </div>
            <div class="form-group">
                <label>Vendor</label>
                <input type="text" id="r-vendor" value="${existingReceipt?.vendor || ''}" required>
            </div>
            <div class="form-group">
                <label>Category</label>
                <select id="r-category" required>
                    <option value="parts" ${existingReceipt?.category === 'parts' ? 'selected' : ''}>Parts</option>
                    <option value="labor" ${existingReceipt?.category === 'labor' ? 'selected' : ''}>Labor</option>
                    <option value="fluids" ${existingReceipt?.category === 'fluids' ? 'selected' : ''}>Fluids</option>
                    <option value="other" ${existingReceipt?.category === 'other' ? 'selected' : ''}>Other</option>
                </select>
            </div>
            <div class="form-group">
                <label>Notes</label>
                <textarea id="r-notes" rows="3">${existingReceipt?.notes || ''}</textarea>
            </div>
            <div class="form-group">
                <label>Receipt Image (optional)</label>
                <input type="file" id="r-image" accept="image/*">
                ${existingReceipt?.thumbnail ? `<p class="form-hint">Current image uploaded</p>` : ''}
            </div>
            <div class="form-group">
                <label>Link to Maintenance *</label>
                <select id="r-maintenance-id" required>
                    <option value="">Select maintenance record...</option>
                    ${maintenanceOptions}
                </select>
                <button type="button" class="btn-secondary btn-small" id="create-new-maintenance-btn" style="margin-top: 8px;">+ Create New Maintenance Record</button>
                <p class="form-hint">You must link this receipt to an existing maintenance record or create a new one.</p>
            </div>
            <button type="submit" class="btn-primary">${isEdit ? 'Update' : 'Add'} Receipt</button>
        </form>
    `);
    
    document.getElementById('create-new-maintenance-btn')?.addEventListener('click', async () => {
        closeModal();
        document.getElementById('add-maintenance-btn').click();
    });
    
    document.getElementById('receipt-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const maintenanceId = document.getElementById('r-maintenance-id').value;
        if (!maintenanceId) {
            showFieldError(document.getElementById('r-maintenance-id'), 'Please select or create a maintenance record');
            return;
        }
        
        const formData = new FormData();
        formData.append('vehicle_id', currentVehicleId);
        formData.append('date', document.getElementById('r-date').value);
        formData.append('vendor', document.getElementById('r-vendor').value);
        formData.append('amount', document.getElementById('r-amount').value);
        formData.append('category', document.getElementById('r-category').value);
        formData.append('notes', document.getElementById('r-notes').value || '');
        formData.append('maintenance_id', maintenanceId);
        
        const imageFile = document.getElementById('r-image').files[0];
        if (imageFile) {
            formData.append('image', imageFile);
        }
        
        const method = isEdit ? 'PUT' : 'POST';
        const endpoint = isEdit ? `/receipts/${existingReceipt.id}` : '/receipts';
        
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: method,
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        closeModal();
        loadReceipts();
    });
}

async function editReceipt(id) {
    const receipts = await apiCall(`/receipts?vehicle_id=${currentVehicleId}`);
    const receipt = receipts.find(r => r.id === id);
    if (!receipt) return;
    showAddReceiptModal(receipt);
}

async function deleteReceipt(id) {
    if (confirm('Delete this receipt?')) {
        await apiCall(`/receipts/${id}`, { method: 'DELETE' });
        loadReceipts();
    }
}

document.getElementById('add-receipt-btn')?.addEventListener('click', () => {
    showAddReceiptModal();
});

document.getElementById('document-type-filter')?.addEventListener('change', loadDocuments);

document.getElementById('guide-category-filter')?.addEventListener('change', loadGuides);

document.getElementById('analytics-date-filter')?.addEventListener('change', (e) => {
    const customDates = document.getElementById('analytics-custom-dates');
    customDates.style.display = e.target.value === 'custom' ? 'flex' : 'none';
    loadAnalytics();
});

document.getElementById('analytics-category-filter')?.addEventListener('change', loadAnalytics);

document.getElementById('apply-analytics-filter')?.addEventListener('click', loadAnalytics);

document.getElementById('add-guide-btn')?.addEventListener('click', () => {
    showModal('Add Guide', `
        <form id="guide-form">
            <div class="form-group">
                <label>Title</label>
                <input type="text" id="g-title" required>
            </div>
            <div class="form-group">
                <label>Category</label>
                <select id="g-category">
                    <option value="maintenance">Maintenance</option>
                    <option value="howto">How-To</option>
                    <option value="mods">Mods</option>
                </select>
            </div>
            <div class="form-group">
                <label>Content</label>
                <textarea id="g-content" rows="6" placeholder="Step-by-step instructions..."></textarea>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Interval (miles)</label>
                    <input type="number" id="g-interval-miles">
                </div>
                <div class="form-group">
                    <label>Interval (months)</label>
                    <input type="number" id="g-interval-months">
                </div>
            </div>
            <button type="submit" class="btn-primary">Save</button>
        </form>
    `);
    
    document.getElementById('guide-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await apiCall('/guides', {
            method: 'POST',
            body: JSON.stringify({
                vehicle_id: currentVehicleId,
                title: document.getElementById('g-title').value,
                category: document.getElementById('g-category').value,
                content: document.getElementById('g-content').value,
                interval_miles: parseInt(document.getElementById('g-interval-miles').value) || null,
                interval_months: parseInt(document.getElementById('g-interval-months').value) || null
            })
        });
        closeModal();
        loadGuides();
    });
});

document.getElementById('load-templates-btn')?.addEventListener('click', async () => {
    await apiCall('/guides/templates', { method: 'POST' });
    loadGuides();
});

document.getElementById('add-document-btn')?.addEventListener('click', showAddDocumentModal);

async function showAddDocumentModal() {
    if (!currentVehicleId) {
        showNotification('Please select a vehicle first', 'error');
        return;
    }
    
    const maintenanceRecords = await apiCall(`/maintenance?vehicle_id=${currentVehicleId}`);
    
    const maintenanceOptions = maintenanceRecords.map(r => 
        `<option value="${r.id}">${r.date || ''} - ${r.category || ''}: ${r.description || ''}</option>`
    ).join('');
    
    showModal('Add Document', `
        <form id="document-form">
            <div class="form-group">
                <label>Title</label>
                <input type="text" id="doc-title" required>
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea id="doc-description" rows="3" placeholder="Optional description..."></textarea>
            </div>
            <div class="form-group">
                <label>Document Type</label>
                <select id="doc-type" required>
                    <option value="">Select type...</option>
                    <option value="invoice">Invoice</option>
                    <option value="manual">Manual</option>
                    <option value="warranty">Warranty</option>
                    <option value="other">Other</option>
                </select>
            </div>
            <div class="form-group">
                <label>File</label>
                <input type="file" id="doc-file" accept=".pdf,.jpg,.jpeg,.png,.gif,.webp,.doc,.docx">
            </div>
            <div class="form-group">
                <label>Link to Maintenance Record (Optional)</label>
                <div class="form-row" style="gap: 0.5rem; align-items: flex-start;">
                    <select id="doc-maintenance-link" style="flex: 1;">
                        <option value="">None - No linked record</option>
                        ${maintenanceOptions}
                    </select>
                    <button type="button" class="btn-secondary" id="doc-create-maintenance-btn" style="white-space: nowrap;">Create New</button>
                </div>
                <div id="doc-new-maintenance-fields" style="display: none; margin-top: 1rem; padding: 1rem; background: var(--bg-tertiary); border-radius: 4px;">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Date</label>
                            <input type="date" id="doc-m-date">
                        </div>
                        <div class="form-group">
                            <label>Mileage</label>
                            <input type="number" id="doc-m-mileage">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Category</label>
                        <select id="doc-m-category">
                            <option value="other">Other</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <input type="text" id="doc-m-description">
                    </div>
                </div>
            </div>
            <button type="submit" class="btn-primary">Upload Document</button>
        </form>
    `);
    
    let newMaintenanceId = null;
    
    document.getElementById('doc-create-maintenance-btn')?.addEventListener('click', async () => {
        const fieldsDiv = document.getElementById('doc-new-maintenance-fields');
        const btn = document.getElementById('doc-create-maintenance-btn');
        
        if (fieldsDiv.style.display === 'none') {
            fieldsDiv.style.display = 'block';
            btn.textContent = 'Cancel';
        } else {
            fieldsDiv.style.display = 'none';
            btn.textContent = 'Create New';
        }
    });
    
    document.getElementById('document-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const fileInput = document.getElementById('doc-file');
        const maintenanceSelect = document.getElementById('doc-maintenance-link');
        const newMaintenanceFields = document.getElementById('doc-new-maintenance-fields');
        
        const isCreatingNewMaintenance = newMaintenanceFields.style.display !== 'none';
        
        if (isCreatingNewMaintenance) {
            const result = await apiCall('/maintenance', {
                method: 'POST',
                body: JSON.stringify({
                    vehicle_id: currentVehicleId,
                    date: document.getElementById('doc-m-date').value || null,
                    mileage: parseInt(document.getElementById('doc-m-mileage').value) || null,
                    category: document.getElementById('doc-m-category').value || 'other',
                    description: document.getElementById('doc-m-description').value || null
                })
            });
            newMaintenanceId = result.id;
        }
        
        if (!fileInput.files[0] && !newMaintenanceId && !maintenanceSelect.value) {
            showNotification('Please upload a file or link to a maintenance record', 'error');
            return;
        }
        
        if (!fileInput.files[0] && (maintenanceSelect.value || newMaintenanceId)) {
            closeModal();
            showNotification('Document created successfully', 'success');
            loadDocuments();
            return;
        }
        
        const formData = new FormData();
        formData.append('title', document.getElementById('doc-title').value);
        formData.append('description', document.getElementById('doc-description').value);
        formData.append('document_type', document.getElementById('doc-type').value);
        formData.append('vehicle_id', currentVehicleId);
        
        if (maintenanceSelect.value) {
            formData.append('maintenance_id', maintenanceSelect.value);
        } else if (newMaintenanceId) {
            formData.append('maintenance_id', newMaintenanceId);
        }
        
        if (fileInput.files[0]) {
            formData.append('file', fileInput.files[0]);
        }
        
        const response = await fetch(`${API_BASE}/documents`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }
        
        closeModal();
        loadDocuments();
        showNotification('Document uploaded successfully', 'success');
    });
}

async function editGuide(id) {
    const guides = await apiCall('/guides');
    const guide = guides.find(g => g.id === id);
    if (!guide) return;
    
    showModal('Edit Guide', `
        <form id="guide-edit-form">
            <input type="hidden" id="g-edit-id" value="${id}">
            <div class="form-group">
                <label>Title</label>
                <input type="text" id="g-edit-title" value="${guide.title || ''}" required>
            </div>
            <div class="form-group">
                <label>Content</label>
                <textarea id="g-edit-content" rows="6">${guide.content || ''}</textarea>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Interval (miles)</label>
                    <input type="number" id="g-edit-interval-miles" value="${guide.interval_miles || ''}">
                </div>
                <div class="form-group">
                    <label>Interval (months)</label>
                    <input type="number" id="g-edit-interval-months" value="${guide.interval_months || ''}">
                </div>
            </div>
            <button type="submit" class="btn-primary">Save</button>
        </form>
    `);
    
    document.getElementById('guide-edit-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await apiCall(`/guides/${id}`, {
            method: 'PUT',
            body: JSON.stringify({
                title: document.getElementById('g-edit-title').value,
                content: document.getElementById('g-edit-content').value,
                interval_miles: parseInt(document.getElementById('g-edit-interval-miles').value) || null,
                interval_months: parseInt(document.getElementById('g-edit-interval-months').value) || null
            })
        });
        closeModal();
        loadGuides();
    });
}

async function deleteGuide(id) {
    if (confirm('Delete this guide?')) {
        await apiCall(`/guides/${id}`, { method: 'DELETE' });
        loadGuides();
    }
}

function selectVehicle(id) {
    currentVehicleId = id;
    localStorage.setItem(STORAGE_KEY, id);
    document.getElementById('vehicle-select').value = id;
    loadDashboard();
}

async function editVehicle(id) {
    const vehicles = await apiCall('/vehicles');
    const v = vehicles.find(veh => veh.id === id);
    if (!v) return;
    
    showModal('Edit Vehicle', `
        <form id="edit-vehicle-form">
            <input type="hidden" id="ev-id" value="${id}">
            <div class="form-group">
                <label>Name</label>
                <input type="text" id="ev-name" value="${v.name || ''}" required>
            </div>
            <div class="form-group">
                <label>VIN</label>
                <input type="text" id="ev-vin" value="${v.vin || ''}">
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Year</label>
                    <input type="number" id="ev-year" value="${v.year || ''}">
                </div>
                <div class="form-group">
                    <label>Mileage (miles)</label>
                    <input type="number" id="ev-mileage" value="${v.mileage || 0}">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Engine</label>
                    <input type="text" id="ev-engine" value="${v.engine || ''}">
                </div>
                <div class="form-group">
                    <label>Transmission</label>
                    <input type="text" id="ev-transmission" value="${v.transmission || ''}">
                </div>
            </div>
            <button type="submit" class="btn-primary">Save</button>
        </form>
    `);
    
    document.getElementById('edit-vehicle-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await apiCall(`/api/vehicles/${id}`, {
            method: 'PUT',
            body: JSON.stringify({
                name: document.getElementById('ev-name').value,
                vin: document.getElementById('ev-vin').value || null,
                year: parseInt(document.getElementById('ev-year').value) || null,
                mileage: parseInt(document.getElementById('ev-mileage').value) || 0,
                engine: document.getElementById('ev-engine').value || null,
                transmission: document.getElementById('ev-transmission').value || null
            })
        });
        closeModal();
        loadVehicleSelector();
        loadProfiles();
    });
}

async function deleteVehicle(id) {
    if (!confirm('Delete this vehicle and all its data?')) return;
    await apiCall(`/api/vehicles/${id}`, { method: 'DELETE' });
    if (currentVehicleId === id) {
        const vehicles = await apiCall('/vehicles');
        currentVehicleId = vehicles.length > 0 ? vehicles[0].id : null;
        localStorage.setItem(STORAGE_KEY, currentVehicleId || '');
    }
    loadVehicleSelector();
    loadProfiles();
}

async function exportVehicle(id) {
    const data = await apiCall(`/api/vehicles/${id}/export`);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `vehicle_${id}_export.json`;
    a.click();
    URL.revokeObjectURL(url);
}

function importVehicle() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
        const file = e.target.files[0];
        const reader = new FileReader();
        reader.onload = async (event) => {
            try {
                const data = JSON.parse(event.target.result);
                const result = await apiCall('/api/vehicles/import', {
                    method: 'POST',
                    body: JSON.stringify(data)
                });
                alert('Vehicle imported successfully!');
                loadVehicleSelector();
                loadProfiles();
            } catch (err) {
                alert('Failed to import: ' + err.message);
            }
        };
        reader.readAsText(file);
    };
    input.click();
}

document.getElementById('vehicle-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        name: document.getElementById('v-name').value,
        vin: document.getElementById('v-vin').value,
        year: parseInt(document.getElementById('v-year').value),
        mileage: parseInt(document.getElementById('v-mileage').value),
        engine: document.getElementById('v-engine').value,
        transmission: document.getElementById('v-transmission').value
    };
    
    if (currentVehicleId) {
        await apiCall(`/api/vehicles/${currentVehicleId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    } else {
        const result = await apiCall('/vehicles', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        currentVehicleId = result.id;
    }
    alert('Vehicle saved!');
});

async function loadMaintenance() {
    if (!currentVehicleId) return;
    const records = await apiCall(`/maintenance?vehicle_id=${currentVehicleId}`);
    const list = document.getElementById('maintenance-list');
    list.innerHTML = records.map(r => `
        <div class="record-item">
            <div class="record-info">
                <div class="record-header">
                    <span class="record-date">${r.date || ''}</span>
                    <span class="record-category">${r.category || ''}</span>
                    <span class="record-cost">£${(r.cost || 0).toFixed(2)}</span>
                    <span>${r.mileage || ''} mi</span>
                </div>
                <div class="record-description">${r.description || ''}</div>
                ${r.notes ? `<div class="record-notes">${r.notes}</div>` : ''}
            </div>
            <div class="record-actions">
                <button class="btn-secondary" onclick="editMaintenance(${r.id})">Edit</button>
                <button class="btn-danger" onclick="deleteMaintenance(${r.id})">Delete</button>
            </div>
        </div>
    `).join('') || '<p>No service records yet</p>';
    
    await renderMaintenanceTimeline();
    loadReminders();
}

async function renderMaintenanceTimeline() {
    const container = document.getElementById('maintenance-timeline');
    if (!container || !currentVehicleId) {
        if (container) container.innerHTML = '';
        return;
    }
    
    try {
        const [maintenance, settings, vehicles] = await Promise.all([
            apiCall(`/maintenance?vehicle_id=${currentVehicleId}`),
            apiCall('/settings'),
            apiCall('/vehicles')
        ]);
        
        const vehicle = vehicles.find(v => v.id === currentVehicleId);
        const currentMileage = vehicle?.mileage || 0;
        const now = new Date();
        
        const defaultIntervals = {
            'oil_change': { miles: 5000, months: 6 },
            'brakes': { miles: 20000, months: 24 },
            'tire_rotation': { miles: 7500, months: 6 },
            'inspection': { miles: 15000, months: 12 },
            'transmission': { miles: 30000, months: 24 },
            'coolant': { miles: 30000, months: 24 },
            'spark_plugs': { miles: 30000, months: 36 },
            'air_filter': { miles: 15000, months: 12 },
            'fuel_filter': { miles: 30000, months: 24 }
        };
        
        const intervals = settings?.service_intervals || defaultIntervals;
        
        const serviceTypes = [
            { key: 'oil_change', label: 'Oil Change' },
            { key: 'brakes', label: 'Brakes' },
            { key: 'tire_rotation', label: 'Tire Rotation' },
            { key: 'inspection', label: 'Inspection' },
            { key: 'transmission', label: 'Transmission' },
            { key: 'coolant', label: 'Coolant' },
            { key: 'spark_plugs', label: 'Spark Plugs' },
            { key: 'air_filter', label: 'Air Filter' },
            { key: 'fuel_filter', label: 'Fuel Filter' }
        ];
        
        const serviceData = {};
        
        maintenance.forEach(record => {
            if (!record.date || !record.category) return;
            const cat = record.category;
            if (!serviceData[cat]) {
                serviceData[cat] = [];
            }
            serviceData[cat].push({
                date: new Date(record.date),
                mileage: record.mileage || 0,
                description: record.description
            });
        });
        
        for (const cat of Object.keys(serviceData)) {
            serviceData[cat].sort((a, b) => a.date - b.date);
        }
        
        const monthsBack = 6;
        const monthsForward = 6;
        const startDate = new Date(now);
        startDate.setMonth(startDate.getMonth() - monthsBack);
        startDate.setDate(1);
        
        const endDate = new Date(now);
        endDate.setMonth(endDate.getMonth() + monthsForward);
        endDate.setDate(0);
        
        const totalMonths = (endDate.getFullYear() - startDate.getFullYear()) * 12 + (endDate.getMonth() - startDate.getMonth()) + 1;
        
        const monthLabels = [];
        const currentMonth = new Date(startDate);
        while (currentMonth <= endDate) {
            monthLabels.push(currentMonth.toLocaleDateString('en-US', { month: 'short', year: '2-digit' }));
            currentMonth.setMonth(currentMonth.getMonth() + 1);
        }
        
        function getMonthPosition(date) {
            const monthsDiff = (date.getFullYear() - startDate.getFullYear()) * 12 + (date.getMonth() - startDate.getMonth());
            return (monthsDiff / totalMonths) * 100;
        }
        
        function getWidthMonths(startDateBar, endDateBar) {
            const monthsDiff = (endDateBar.getFullYear() - startDateBar.getFullYear()) * 12 + (endDateBar.getMonth() - startDateBar.getMonth());
            return Math.max((monthsDiff / totalMonths) * 100, 2);
        }
        
        let html = `
            <div class="gantt-container">
                <h3>Service Timeline</h3>
                <div class="gantt-header">
                    <div class="gantt-label-header">Service Type</div>
                    <div class="gantt-time-axis">
                        ${monthLabels.map(m => `<div class="gantt-month">${m}</div>`).join('')}
                    </div>
                </div>
        `;
        
        let hasData = false;
        
        for (const serviceType of serviceTypes) {
            const typeKey = serviceType.key;
            const interval = intervals[typeKey] || { miles: 0, months: 0 };
            const recordsForType = serviceData[typeKey] || [];
            
            if (recordsForType.length === 0 && interval.miles === 0) continue;
            
            html += `
                <div class="gantt-row">
                    <div class="gantt-service-label">${serviceType.label}</div>
                    <div class="gantt-bar-container">
            `;
            
            if (recordsForType.length > 0) {
                hasData = true;
                const lastRecord = recordsForType[recordsForType.length - 1];
                const lastDate = lastRecord.date;
                const lastMileage = lastRecord.mileage;
                
                const nextDueDate = new Date(lastDate);
                nextDueDate.setMonth(nextDueDate.getMonth() + interval.months);
                
                const nextDueMileage = lastMileage + interval.miles;
                
                const todayPos = getMonthPosition(now);
                const lastPos = getMonthPosition(lastDate);
                const duePos = Math.min(getMonthPosition(nextDueDate), 100);
                
                let status = 'completed';
                let isOverdue = false;
                
                if (now > nextDueDate || currentMileage > nextDueMileage) {
                    status = 'overdue';
                    isOverdue = true;
                } else if (nextDueDate - now < 30 * 24 * 60 * 60 * 1000 || nextDueMileage - currentMileage < 1000) {
                    status = 'upcoming';
                }
                
                const barStart = Math.max(lastPos, 0);
                const barEnd = isOverdue ? 100 : duePos;
                const barWidth = Math.max(barEnd - barStart, 3);
                
                const barLeft = barStart;
                const completedWidth = status === 'completed' ? (todayPos - lastPos) : (barWidth * 0.7);
                
                if (status === 'completed') {
                    html += `
                        <div class="gantt-bar completed" style="left: ${barLeft}%; width: ${completedWidth}%;" title="Last: ${lastDate.toLocaleDateString()}">
                            ${lastDate.toLocaleDateString('en-US', { month: 'short', year: '2-digit' })}
                        </div>
                    `;
                } else if (status === 'upcoming') {
                    html += `
                        <div class="gantt-bar completed" style="left: ${barLeft}%; width: ${completedWidth}%;" title="Last: ${lastDate.toLocaleDateString()}"></div>
                        <div class="gantt-bar upcoming" style="left: ${barLeft + completedWidth}%; width: ${barWidth - completedWidth}%;" title="Due: ${nextDueDate.toLocaleDateString()}">
                            Due ${nextDueDate.toLocaleDateString('en-US', { month: 'short' })}
                        </div>
                    `;
                } else {
                    const overdueWidth = 100 - (barLeft + completedWidth);
                    html += `
                        <div class="gantt-bar completed" style="left: ${barLeft}%; width: ${completedWidth}%;" title="Last: ${lastDate.toLocaleDateString()}"></div>
                        <div class="gantt-bar overdue" style="left: ${barLeft + completedWidth}%; width: ${overdueWidth}%;" title="Overdue since: ${nextDueDate.toLocaleDateString()}">
                            OVERDUE
                        </div>
                    `;
                }
            } else if (interval.miles > 0) {
                html += `<span class="gantt-bar-empty">No record</span>`;
            }
            
            html += `
                    </div>
                </div>
            `;
        }
        
        if (!hasData) {
            html += `
                <div class="gantt-no-data">
                    No service records to display. Add maintenance records to see the timeline.
                </div>
            `;
        }
        
        html += `
                <div class="gantt-legend">
                    <div class="gantt-legend-item">
                        <div class="gantt-legend-color completed"></div>
                        <span>Completed</span>
                    </div>
                    <div class="gantt-legend-item">
                        <div class="gantt-legend-color upcoming"></div>
                        <span>Upcoming</span>
                    </div>
                    <div class="gantt-legend-item">
                        <div class="gantt-legend-color overdue"></div>
                        <span>Overdue</span>
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Error rendering timeline:', error);
        container.innerHTML = '<p class="gantt-no-data">Unable to load timeline</p>';
    }
}

async function loadReminders() {
    if (!currentVehicleId) return;
    
    const filter = document.getElementById('reminder-filter')?.value || '';
    let url = `/reminders?vehicle_id=${currentVehicleId}`;
    const reminders = await apiCall(url);
    const vehicles = await apiCall('/vehicles');
    const vehicle = vehicles.find(v => v.id === currentVehicleId);
    const currentMileage = vehicle?.mileage || 0;
    
    const filtered = filter ? reminders.filter(r => r.type === filter) : reminders;
    const container = document.getElementById('reminders-list');
    
    if (filtered.length === 0) {
        container.innerHTML = '<p class="no-data">No reminders set. Click "Add Reminder" to create one.</p>';
        return;
    }
    
    container.innerHTML = filtered.map(r => {
        const nextDueDate = r.next_due_date ? new Date(r.next_due_date) : null;
        const today = new Date();
        let status = 'upcoming';
        let statusText = '';
        
        if (nextDueDate && nextDueDate < today) {
            status = 'overdue';
            statusText = 'OVERDUE';
        } else if (nextDueDate && (nextDueDate - today) < 30 * 24 * 60 * 60 * 1000) {
            status = 'due-soon';
            statusText = 'Due Soon';
        } else if (r.next_due_mileage && r.next_due_mileage < currentMileage) {
            status = 'overdue';
            statusText = 'OVERDUE';
        } else if (r.next_due_mileage && (r.next_due_mileage - currentMileage) < 1000) {
            status = 'due-soon';
            statusText = 'Due Soon';
        }
        
        const typeLabel = SERVICE_INTERVAL_TYPES.find(t => t.key === r.type)?.label || r.type;
        
        return `
            <div class="reminder-item reminder-${status}">
                <div class="reminder-info">
                    <div class="reminder-header">
                        <span class="reminder-type">${typeLabel}</span>
                        ${statusText ? `<span class="reminder-status">${statusText}</span>` : ''}
                    </div>
                    <div class="reminder-details">
                        ${r.next_due_date ? `<span>Due: ${new Date(r.next_due_date).toLocaleDateString()}</span>` : ''}
                        ${r.next_due_mileage ? `<span>Due at: ${r.next_due_mileage.toLocaleString()} mi</span>` : ''}
                    </div>
                    ${r.notes ? `<div class="reminder-notes">${r.notes}</div>` : ''}
                    <div class="reminder-interval">
                        Every ${r.interval_miles?.toLocaleString() || '?'} mi / ${r.interval_months || '?'} mo
                    </div>
                </div>
                <div class="reminder-actions">
                    <button class="btn-secondary" onclick="editReminder(${r.id})">Edit</button>
                    <button class="btn-danger" onclick="deleteReminder(${r.id})">Delete</button>
                </div>
            </div>
        `;
    }).join('');
}

function showAddReminderModal(existingReminder = null) {
    const isEdit = !!existingReminder;
    const title = isEdit ? 'Edit Reminder' : 'Add Reminder';
    
    const serviceTypeOptions = SERVICE_INTERVAL_TYPES.map(t => 
        `<option value="${t.key}" ${existingReminder?.type === t.key ? 'selected' : ''}>${t.label}</option>`
    ).join('') + `<option value="custom" ${existingReminder?.type === 'custom' ? 'selected' : ''}>Custom</option>`;
    
    const isCustom = existingReminder?.type === 'custom';
    
    showModal(title, `
        <form id="reminder-form">
            ${isEdit ? `<input type="hidden" id="reminder-id" value="${existingReminder.id}">` : ''}
            <div class="form-group">
                <label>Service Type</label>
                <select id="reminder-type" required>
                    <option value="">Select type...</option>
                    ${serviceTypeOptions}
                </select>
            </div>
            <div class="form-group" id="custom-type-group" style="display: ${isCustom ? 'block' : 'none'};">
                <label>Custom Type Name</label>
                <input type="text" id="reminder-custom-type" value="${existingReminder?.notes || ''}" placeholder="e.g. Timing Belt">
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Interval (miles)</label>
                    <input type="number" id="reminder-interval-miles" value="${existingReminder?.interval_miles || ''}" min="0" placeholder="e.g. 5000">
                </div>
                <div class="form-group">
                    <label>Interval (months)</label>
                    <input type="number" id="reminder-interval-months" value="${existingReminder?.interval_months || ''}" min="0" placeholder="e.g. 6">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Last Service Date</label>
                    <input type="date" id="reminder-last-date" value="${existingReminder?.last_service_date || ''}">
                </div>
                <div class="form-group">
                    <label>Last Service Mileage</label>
                    <input type="number" id="reminder-last-mileage" value="${existingReminder?.last_service_mileage || ''}" min="0">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Next Due Date</label>
                    <input type="date" id="reminder-next-date" value="${existingReminder?.next_due_date || ''}">
                </div>
                <div class="form-group">
                    <label>Next Due Mileage</label>
                    <input type="number" id="reminder-next-mileage" value="${existingReminder?.next_due_mileage || ''}" min="0">
                </div>
            </div>
            <div class="form-group">
                <label>Notes</label>
                <textarea id="reminder-notes" rows="2">${existingReminder?.notes || ''}</textarea>
            </div>
            <button type="submit" class="btn-primary">${isEdit ? 'Update' : 'Add'} Reminder</button>
        </form>
    `);
    
    const typeSelect = document.getElementById('reminder-type');
    const intervalMilesInput = document.getElementById('reminder-interval-miles');
    const intervalMonthsInput = document.getElementById('reminder-interval-months');
    const customTypeGroup = document.getElementById('custom-type-group');
    
    if (existingReminder) {
        typeSelect.value = existingReminder.type;
    }
    
    typeSelect.addEventListener('change', async () => {
        const selectedType = typeSelect.value;
        
        if (selectedType === 'custom') {
            customTypeGroup.style.display = 'block';
            intervalMilesInput.value = '';
            intervalMonthsInput.value = '';
            return;
        }
        
        customTypeGroup.style.display = 'none';
        
        if (!selectedType) return;
        
        try {
            const settings = await apiCall('/settings');
            const intervals = settings?.service_intervals;
            if (intervals && intervals[selectedType]) {
                intervalMilesInput.value = intervals[selectedType].miles || '';
                intervalMonthsInput.value = intervals[selectedType].months || '';
            }
        } catch (e) {
            console.error('Error loading service intervals:', e);
        }
    });
    
    document.getElementById('reminder-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const data = {
            vehicle_id: currentVehicleId,
            type: document.getElementById('reminder-type').value,
            interval_miles: parseInt(document.getElementById('reminder-interval-miles').value) || null,
            interval_months: parseInt(document.getElementById('reminder-interval-months').value) || null,
            last_service_date: document.getElementById('reminder-last-date').value || null,
            last_service_mileage: parseInt(document.getElementById('reminder-last-mileage').value) || null,
            next_due_date: document.getElementById('reminder-next-date').value || null,
            next_due_mileage: parseInt(document.getElementById('reminder-next-mileage').value) || null,
            notes: document.getElementById('reminder-notes').value || null
        };
        
        if (isEdit) {
            await apiCall(`/reminders/${existingReminder.id}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
        } else {
            await apiCall('/reminders', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        }
        
        closeModal();
        loadReminders();
    });
}

async function editReminder(id) {
    const reminders = await apiCall(`/reminders?vehicle_id=${currentVehicleId}`);
    const reminder = reminders.find(r => r.id === id);
    if (!reminder) return;
    showAddReminderModal(reminder);
}

async function deleteReminder(id) {
    if (!confirm('Delete this reminder?')) return;
    await apiCall(`/reminders/${id}`, { method: 'DELETE' });
    loadReminders();
}

document.getElementById('add-reminder-btn')?.addEventListener('click', () => {
    showAddReminderModal();
});

document.getElementById('reminder-filter')?.addEventListener('change', loadReminders);

document.getElementById('add-maintenance-btn').addEventListener('click', () => {
    showModal('Add Service Record', `
        <form id="maintenance-form">
            <div class="form-row">
                <div class="form-group">
                    <label>Date</label>
                    <input type="date" id="m-date" required>
                </div>
                <div class="form-group">
                    <label>Mileage (miles)</label>
                    <input type="number" id="m-mileage">
                </div>
            </div>
            <div class="form-group">
                <label>Category</label>
                <select id="m-category">
                    <option value="oil_change">Oil Change</option>
                    <option value="brakes">Brakes</option>
                    <option value="suspension">Suspension</option>
                    <option value="electrical">Electrical</option>
                    <option value="engine">Engine</option>
                    <option value="transmission">Transmission</option>
                    <option value="interior">Interior</option>
                    <option value="exterior">Exterior</option>
                    <option value="tires_wheels">Tires & Wheels</option>
                    <option value="other">Other</option>
                </select>
            </div>
            <div class="form-group">
                <label>Description</label>
                <input type="text" id="m-description" required>
            </div>
            <div class="form-group">
                <label>Parts Used (comma separated)</label>
                <input type="text" id="m-parts">
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Cost (£)</label>
                    <input type="number" step="0.01" id="m-cost">
                </div>
                <div class="form-group">
                    <label>Labor Hours</label>
                    <input type="number" step="0.5" id="m-labor">
                </div>
            </div>
            <div class="form-group">
                <label>Shop Name</label>
                <input type="text" id="m-shop">
            </div>
            <div class="form-group">
                <label>Notes</label>
                <textarea id="m-notes" rows="3"></textarea>
            </div>
            <button type="submit" class="btn-primary">Save</button>
        </form>
    `);
    
    document.getElementById('maintenance-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await apiCall('/maintenance', {
            method: 'POST',
            body: JSON.stringify({
                vehicle_id: currentVehicleId,
                date: document.getElementById('m-date').value,
                mileage: parseInt(document.getElementById('m-mileage').value) || null,
                category: document.getElementById('m-category').value,
                description: document.getElementById('m-description').value,
                parts_used: document.getElementById('m-parts').value.split(',').map(p => p.trim()).filter(p => p),
                cost: parseFloat(document.getElementById('m-cost').value) || null,
                labor_hours: parseFloat(document.getElementById('m-labor').value) || null,
                shop_name: document.getElementById('m-shop').value || null,
                notes: document.getElementById('m-notes').value || null
            })
        });
        closeModal();
        loadMaintenance();
    });
});

async function deleteMaintenance(id) {
    if (confirm('Delete this record?')) {
        await apiCall(`/maintenance/${id}`, { method: 'DELETE' });
        loadMaintenance();
    }
}

async function editMaintenance(id) {
    const records = await apiCall(`/maintenance?vehicle_id=${currentVehicleId}`);
    const r = records.find(m => m.id === id);
    if (!r) return;
    
    let partsUsed = '';
    try {
        partsUsed = JSON.parse(r.parts_used || '[]').join(', ');
    } catch (e) { partsUsed = r.parts_used || ''; }
    
    showModal('Edit Service Record', `
        <form id="maintenance-edit-form">
            <input type="hidden" id="me-id" value="${id}">
            <div class="form-group">
                <label>Mileage (miles)</label>
                <input type="number" id="me-mileage" value="${r.mileage || ''}">
            </div>
            <div class="form-group">
                <label>Description</label>
                <input type="text" id="me-description" value="${r.description || ''}" required>
            </div>
            <div class="form-group">
                <label>Parts Used (comma separated)</label>
                <input type="text" id="me-parts" value="${partsUsed}">
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Cost (£)</label>
                    <input type="number" step="0.01" id="me-cost" value="${r.cost || ''}">
                </div>
                <div class="form-group">
                    <label>Labor Hours</label>
                    <input type="number" step="0.5" id="me-labor" value="${r.labor_hours || ''}">
                </div>
            </div>
            <div class="form-group">
                <label>Shop Name</label>
                <input type="text" id="me-shop" value="${r.shop_name || ''}">
            </div>
            <div class="form-group">
                <label>Notes</label>
                <textarea id="me-notes" rows="3">${r.notes || ''}</textarea>
            </div>
            <button type="submit" class="btn-primary">Save</button>
        </form>
    `);
    
    document.getElementById('maintenance-edit-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await apiCall(`/maintenance/${id}`, {
            method: 'PUT',
            body: JSON.stringify({
                mileage: parseInt(document.getElementById('me-mileage').value) || null,
                description: document.getElementById('me-description').value,
                parts_used: document.getElementById('me-parts').value.split(',').map(p => p.trim()).filter(p => p),
                cost: parseFloat(document.getElementById('me-cost').value) || null,
                labor_hours: parseFloat(document.getElementById('me-labor').value) || null,
                shop_name: document.getElementById('me-shop').value || null,
                notes: document.getElementById('me-notes').value || null
            })
        });
        closeModal();
        loadMaintenance();
    });
}

async function loadMods() {
    if (!currentVehicleId) return;
    const statusFilter = document.getElementById('mod-status-filter').value;
    let url = `/mods?vehicle_id=${currentVehicleId}`;
    const mods = await apiCall(url);
    const filtered = statusFilter ? mods.filter(m => m.status === statusFilter) : mods;
    
    // Calculate totals by status
    const totals = { planned: 0, in_progress: 0, completed: 0 };
    mods.forEach(m => {
        if (totals.hasOwnProperty(m.status)) {
            totals[m.status] += m.cost || 0;
        }
    });
    
    // Update summary cards
    const plannedEl = document.getElementById('mod-planned-total');
    const progressEl = document.getElementById('mod-progress-total');
    const completedEl = document.getElementById('mod-completed-total');
    if (plannedEl) plannedEl.textContent = `£${totals.planned.toFixed(2)}`;
    if (progressEl) progressEl.textContent = `£${totals.in_progress.toFixed(2)}`;
    if (completedEl) completedEl.textContent = `£${totals.completed.toFixed(2)}`;
    
    // Load mod list
    const list = document.getElementById('mods-list');
    list.innerHTML = filtered.map(m => {
        let partsDisplay = '';
        try {
            const partsArr = typeof m.parts === 'string' ? JSON.parse(m.parts || '[]') : (m.parts || []);
            partsDisplay = partsArr.join(', ');
        } catch (e) { partsDisplay = m.parts || ''; }
        
        return `
        <div class="record-item">
            <div class="record-info">
                <div class="record-header">
                    <span class="record-date">${m.date || ''}</span>
                    <span class="record-category">${m.category || ''}</span>
                    <span class="badge badge-${m.status}">${m.status}</span>
                    <span class="record-cost">£${(m.cost || 0).toFixed(2)}</span>
                </div>
                <div class="record-description">${m.description || ''}</div>
                ${m.mileage ? `<div class="record-detail"><small>Mileage: ${m.mileage} mi</small></div>` : ''}
                ${partsDisplay ? `<div class="record-detail"><small>Parts: ${partsDisplay}</small></div>` : ''}
                ${m.notes ? `<div class="record-detail"><small>Notes: ${m.notes}</small></div>` : ''}
            </div>
            <div class="record-actions">
                <button class="btn-secondary" onclick="editMod(${m.id}, '${m.status}')">Edit</button>
                <button class="btn-danger" onclick="deleteMod(${m.id})">Delete</button>
            </div>
        </div>
    `}).join('') || '<p>No mods yet</p>';
}

document.getElementById('mod-status-filter').addEventListener('change', loadMods);

document.getElementById('add-mod-btn').addEventListener('click', () => {
    showModal('Add Modification', `
        <form id="mod-form">
            <div class="form-row">
                <div class="form-group">
                    <label>Date</label>
                    <input type="date" id="mod-date">
                </div>
                <div class="form-group">
                    <label>Mileage (miles)</label>
                    <input type="number" id="mod-mileage">
                </div>
            </div>
            <div class="form-group">
                <label>Category</label>
                <select id="mod-category">
                    <option value="engine">Engine</option>
                    <option value="suspension">Suspension</option>
                    <option value="exhaust">Exhaust</option>
                    <option value="interior">Interior</option>
                    <option value="exterior">Exterior</option>
                    <option value="brakes">Brakes</option>
                    <option value="wheels">Wheels</option>
                    <option value="other">Other</option>
                </select>
            </div>
            <div class="form-group">
                <label>Description</label>
                <input type="text" id="mod-description" required>
            </div>
            <div class="form-group">
                <label>Parts (comma separated)</label>
                <input type="text" id="mod-parts">
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Cost (£)</label>
                    <input type="number" step="0.01" id="mod-cost">
                </div>
                <div class="form-group">
                    <label>Status</label>
                    <select id="mod-status">
                        <option value="planned">Planned</option>
                        <option value="in_progress">In Progress</option>
                        <option value="completed">Completed</option>
                    </select>
                </div>
            </div>
            <div class="form-group">
                <label>Notes</label>
                <textarea id="mod-notes" rows="3"></textarea>
            </div>
            <button type="submit" class="btn-primary">Save</button>
        </form>
    `);
    
    // Handle status change - disable date for planned mods
    const modDateInput = document.getElementById('mod-date');
    const modStatusSelect = document.getElementById('mod-status');
    
    const handleStatusChange = (e) => {
        if (e.target.value === 'planned') {
            modDateInput.value = '';
            modDateInput.disabled = true;
            modDateInput.placeholder = 'N/A for planned mods';
        } else {
            modDateInput.disabled = false;
            modDateInput.placeholder = '';
        }
    };
    
    modStatusSelect.addEventListener('change', handleStatusChange);
    // Check initial value
    if (modStatusSelect.value === 'planned') {
        modDateInput.disabled = true;
        modDateInput.placeholder = 'N/A for planned mods';
    }
    
    const form = document.getElementById('mod-form');
    const oldSubmitHandler = form._submitHandler;
    if (oldSubmitHandler) {
        form.removeEventListener('submit', oldSubmitHandler);
    }
    
    const newSubmitHandler = async (e) => {
        e.preventDefault();
        await apiCall('/mods', {
            method: 'POST',
            body: JSON.stringify({
                vehicle_id: currentVehicleId,
                date: document.getElementById('mod-date').value || null,
                mileage: parseInt(document.getElementById('mod-mileage').value) || null,
                category: document.getElementById('mod-category').value,
                description: document.getElementById('mod-description').value,
                parts: document.getElementById('mod-parts').value.split(',').map(p => p.trim()).filter(p => p),
                cost: parseFloat(document.getElementById('mod-cost').value) || null,
                status: document.getElementById('mod-status').value,
                notes: document.getElementById('mod-notes').value || null
            })
        });
        closeModal();
        loadMods();
    };
    
    form.addEventListener('submit', newSubmitHandler);
    form._submitHandler = newSubmitHandler;
});

async function editMod(id, currentStatus) {
    const mods = await apiCall(`/mods?vehicle_id=${currentVehicleId}`);
    const mod = mods.find(m => m.id === id);
    if (!mod) return;
    
    let partsUsed = '';
    try {
        partsUsed = JSON.parse(mod.parts || '[]').join(', ');
    } catch (e) { partsUsed = mod.parts || ''; }
    
    showModal('Edit Modification', `
        <form id="mod-edit-form">
            <input type="hidden" id="mod-edit-id" value="${id}">
            <div class="form-row">
                <div class="form-group">
                    <label>Date</label>
                    <input type="date" id="mod-edit-date" value="${mod.date || ''}">
                </div>
                <div class="form-group">
                    <label>Mileage (miles)</label>
                    <input type="number" id="mod-edit-mileage" value="${mod.mileage || ''}">
                </div>
            </div>
            <div class="form-group">
                <label>Category</label>
                <select id="mod-edit-category">
                    <option value="engine" ${mod.category === 'engine' ? 'selected' : ''}>Engine</option>
                    <option value="suspension" ${mod.category === 'suspension' ? 'selected' : ''}>Suspension</option>
                    <option value="exhaust" ${mod.category === 'exhaust' ? 'selected' : ''}>Exhaust</option>
                    <option value="interior" ${mod.category === 'interior' ? 'selected' : ''}>Interior</option>
                    <option value="exterior" ${mod.category === 'exterior' ? 'selected' : ''}>Exterior</option>
                    <option value="brakes" ${mod.category === 'brakes' ? 'selected' : ''}>Brakes</option>
                    <option value="wheels" ${mod.category === 'wheels' ? 'selected' : ''}>Wheels</option>
                    <option value="other" ${mod.category === 'other' ? 'selected' : ''}>Other</option>
                </select>
            </div>
            <div class="form-group">
                <label>Description</label>
                <input type="text" id="mod-edit-description" value="${mod.description || ''}" required>
            </div>
            <div class="form-group">
                <label>Parts (comma separated)</label>
                <input type="text" id="mod-edit-parts" value="${partsUsed}">
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Cost (£)</label>
                    <input type="number" step="0.01" id="mod-edit-cost" value="${mod.cost || ''}">
                </div>
                <div class="form-group">
                    <label>Status</label>
                    <select id="mod-edit-status">
                        <option value="planned" ${mod.status === 'planned' ? 'selected' : ''}>Planned</option>
                        <option value="in_progress" ${mod.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                        <option value="completed" ${mod.status === 'completed' ? 'selected' : ''}>Completed</option>
                    </select>
                </div>
            </div>
            <div class="form-group">
                <label>Notes</label>
                <textarea id="mod-edit-notes" rows="3">${mod.notes || ''}</textarea>
            </div>
            <button type="submit" class="btn-primary">Save</button>
        </form>
    `);
    
    // Handle status change - disable date for planned mods
    const modEditDateInput = document.getElementById('mod-edit-date');
    const modEditStatusSelect = document.getElementById('mod-edit-status');
    
    const handleEditStatusChange = (e) => {
        if (e.target.value === 'planned') {
            modEditDateInput.value = '';
            modEditDateInput.disabled = true;
            modEditDateInput.placeholder = 'N/A for planned mods';
        } else {
            modEditDateInput.disabled = false;
            modEditDateInput.placeholder = '';
        }
    };
    
    modEditStatusSelect.addEventListener('change', handleEditStatusChange);
    // Check initial value
    if (modEditStatusSelect.value === 'planned') {
        modEditDateInput.disabled = true;
        modEditDateInput.placeholder = 'N/A for planned mods';
    }
    
    const form = document.getElementById('mod-edit-form');
    const oldSubmitHandler = form._submitHandler;
    if (oldSubmitHandler) {
        form.removeEventListener('submit', oldSubmitHandler);
    }
    
    const newSubmitHandler = async (e) => {
        e.preventDefault();
        await apiCall(`/mods/${id}`, {
            method: 'PUT',
            body: JSON.stringify({
                date: document.getElementById('mod-edit-date').value || null,
                mileage: parseInt(document.getElementById('mod-edit-mileage').value) || null,
                category: document.getElementById('mod-edit-category').value,
                description: document.getElementById('mod-edit-description').value,
                parts: document.getElementById('mod-edit-parts').value.split(',').map(p => p.trim()).filter(p => p),
                cost: parseFloat(document.getElementById('mod-edit-cost').value) || null,
                status: document.getElementById('mod-edit-status').value,
                notes: document.getElementById('mod-edit-notes').value || null
            })
        });
        closeModal();
        loadMods();
    };
    
    form.addEventListener('submit', newSubmitHandler);
    form._submitHandler = newSubmitHandler;
}

async function deleteMod(id) {
    if (confirm('Delete this mod?')) {
        await apiCall(`/mods/${id}`, { method: 'DELETE' });
        loadMods();
    }
}

async function loadCosts() {
    if (!currentVehicleId) return;
    const records = await apiCall(`/costs?vehicle_id=${currentVehicleId}`);
    const summary = await apiCall(`/costs/summary?vehicle_id=${currentVehicleId}`);
    
    const breakdown = document.getElementById('cost-breakdown');
    breakdown.innerHTML = Object.entries(summary).map(([cat, amount]) => `
        <div class="cost-breakdown-item">
            <span>${cat}</span>
            <span>£${amount.toFixed(2)}</span>
        </div>
    `).join('') || '<p>No costs recorded</p>';
    
    const list = document.getElementById('costs-list');
    list.innerHTML = records.map(c => `
        <div class="record-item">
            <div class="record-info">
                <div class="record-header">
                    <span class="record-date">${c.date || ''}</span>
                    <span class="record-category">${c.category || ''}</span>
                    <span class="record-cost">£${(c.amount || 0).toFixed(2)}</span>
                </div>
                <div class="record-description">${c.description || ''}</div>
            </div>
        </div>
    `).join('') || '<p>No costs recorded</p>';
}

document.getElementById('cost-quick-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    await apiCall('/costs', {
        method: 'POST',
        body: JSON.stringify({
            vehicle_id: currentVehicleId,
            date: document.getElementById('qc-date').value,
            amount: parseFloat(document.getElementById('qc-amount').value),
            category: document.getElementById('qc-category').value,
            description: document.getElementById('qc-description').value
        })
    });
    document.getElementById('cost-quick-form').reset();
    loadCosts();
});

document.getElementById('add-cost-btn')?.addEventListener('click', () => {
    showModal('Add Expense', `
        <form id="cost-form">
            <div class="form-row">
                <div class="form-group">
                    <label>Date</label>
                    <input type="date" id="c-date" required>
                </div>
                <div class="form-group">
                    <label>Amount (£)</label>
                    <input type="number" step="0.01" id="c-amount" required>
                </div>
            </div>
            <div class="form-group">
                <label>Category</label>
                <select id="c-category">
                    <option value="maintenance">Maintenance</option>
                    <option value="mods">Mods</option>
                    <option value="insurance">Insurance</option>
                    <option value="fuel">Fuel</option>
                    <option value="tax">Tax</option>
                    <option value="other">Other</option>
                </select>
            </div>
            <div class="form-group">
                <label>Description</label>
                <input type="text" id="c-description">
            </div>
            <button type="submit" class="btn-primary">Save</button>
        </form>
    `);
    
    document.getElementById('cost-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await apiCall('/costs', {
            method: 'POST',
            body: JSON.stringify({
                vehicle_id: currentVehicleId,
                date: document.getElementById('c-date').value,
                amount: parseFloat(document.getElementById('c-amount').value),
                category: document.getElementById('c-category').value,
                description: document.getElementById('c-description').value
            })
        });
        closeModal();
        loadCosts();
    });
});

async function loadNotes() {
    if (!currentVehicleId) return;
    const records = await apiCall(`/notes?vehicle_id=${currentVehicleId}`);
    const list = document.getElementById('notes-list');
    list.innerHTML = records.map(n => `
        <div class="record-item">
            <div class="record-info">
                <div class="record-header">
                    <span class="record-date">${n.date || ''}</span>
                    <span class="record-title">${n.title || ''}</span>
                </div>
                <div class="record-description">${n.content || ''}</div>
            </div>
            <div class="record-actions">
                <button class="btn-danger" onclick="deleteNote(${n.id})">Delete</button>
            </div>
        </div>
    `).join('') || '<p>No notes yet</p>';
}

document.getElementById('add-note-btn').addEventListener('click', () => {
    showModal('Add Note', `
        <form id="note-form">
            <div class="form-row">
                <div class="form-group">
                    <label>Date</label>
                    <input type="date" id="n-date" required>
                </div>
                <div class="form-group">
                    <label>Title</label>
                    <input type="text" id="n-title" required>
                </div>
            </div>
            <div class="form-group">
                <label>Content</label>
                <textarea id="n-content" rows="5" required></textarea>
            </div>
            <div class="form-group">
                <label>Tags (comma separated)</label>
                <input type="text" id="n-tags">
            </div>
            <button type="submit" class="btn-primary">Save</button>
        </form>
    `);
    
    document.getElementById('note-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await apiCall('/notes', {
            method: 'POST',
            body: JSON.stringify({
                vehicle_id: currentVehicleId,
                date: document.getElementById('n-date').value,
                title: document.getElementById('n-title').value,
                content: document.getElementById('n-content').value,
                tags: document.getElementById('n-tags').value.split(',').map(t => t.trim()).filter(t => t)
            })
        });
        closeModal();
        loadNotes();
    });
});

async function deleteNote(id) {
    if (confirm('Delete this note?')) {
        await apiCall(`/notes/${id}`, { method: 'DELETE' });
        loadNotes();
    }
}

async function loadVCDS() {
    if (!currentVehicleId) return;
    const faults = await apiCall(`/vcds?vehicle_id=${currentVehicleId}`);
    const active = faults.filter(f => f.status === 'active').length;
    const cleared = faults.filter(f => f.status === 'cleared').length;
    
    document.getElementById('active-fault-count').textContent = `${active} Active`;
    document.getElementById('cleared-fault-count').textContent = `${cleared} Cleared`;
    
    const list = document.getElementById('vcds-list');
    list.innerHTML = faults.map(f => `
        <div class="record-item">
            <div class="record-info">
                <div class="record-header">
                    <span class="record-date">${f.address || ''}</span>
                    <span class="badge badge-${f.status === 'active' ? 'active' : 'cleared'}">${f.status}</span>
                    <span class="fault-code">${f.fault_code || ''}</span>
                </div>
                <div class="record-description">${f.component || ''}</div>
                ${f.description ? `<div>${f.description}</div>` : ''}
            </div>
            <div class="record-actions">
                ${f.status === 'active' ? `<button class="btn-secondary" onclick="clearFault(${f.id})">Mark Cleared</button>` : ''}
            </div>
        </div>
    `).join('') || '<p>No VCDS faults recorded</p>';
}

document.getElementById('import-vcds-btn').addEventListener('click', () => {
    showModal('Import VCDS Faults', `
        <p>Paste VCDS scan results below (one fault per line):</p>
        <textarea id="vcds-paste" class="vcds-input" placeholder="08 Auto HVAC 00819 High Pressure Sensor&#10;19 CAN Gateway 03582 Radio no signal"></textarea>
        <button class="btn-primary" onclick="parseVCDS()">Parse</button>
        <div id="vcds-preview"></div>
    `);
});

async function parseVCDS() {
    const content = document.getElementById('vcds-paste').value;
    const faults = await apiCall('/api/vcds/parse', {
        method: 'POST',
        body: JSON.stringify({ content })
    });
    
    const preview = document.getElementById('vcds-preview');
    preview.innerHTML = `
        <h4>Parsed Faults (${faults.length})</h4>
        ${faults.map((f, i) => `
            <div style="margin: 0.5rem 0; padding: 0.5rem; background: var(--bg-tertiary);">
                <strong>${f.address}</strong> ${f.fault_code} - ${f.component}
            </div>
        `).join('')}
        ${faults.length > 0 ? `<button class="btn-primary" onclick="importVCDS(${JSON.stringify(faults).replace(/"/g, '&quot;')})">Import All</button>` : ''}
    `;
}

async function importVCDS(faults) {
    await apiCall('/api/vcds/import', {
        method: 'POST',
        body: JSON.stringify({
            vehicle_id: currentVehicleId,
            faults: faults
        })
    });
    closeModal();
    loadVCDS();
}

async function clearFault(id) {
    const today = new Date().toISOString().split('T')[0];
    await apiCall(`/api/vcds/${id}`, {
        method: 'PUT',
        body: JSON.stringify({
            status: 'cleared',
            cleared_date: today
        })
    });
    loadVCDS();
}

function showModal(title, content) {
    document.getElementById('modal-body').innerHTML = `<h3>${title}</h3>${content}`;
    document.getElementById('modal').style.display = 'block';
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
}

document.querySelector('.close').addEventListener('click', closeModal);
window.addEventListener('click', (e) => {
    if (e.target === document.getElementById('modal')) closeModal();
});

document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => showView(btn.dataset.view));
});

document.getElementById('quick-add-service')?.addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('add-maintenance-btn').click();
});

document.getElementById('quick-add-mod')?.addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('add-mod-btn').click();
});

document.getElementById('quick-add-cost')?.addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('add-cost-btn').click();
});

document.addEventListener('DOMContentLoaded', async () => {
    await loadVehicleSelector();
    if (currentVehicleId) {
        loadDashboard();
    }
});

// Settings Functions
async function loadSettings() {
    try {
        const settings = await apiCall('/settings');
        
        if (!settings || typeof settings !== 'object') {
            throw new Error('Invalid settings data');
        }
        
        if (settings.currency_symbol) {
            document.getElementById('setting-currency').value = settings.currency_symbol;
        }
        if (settings.mileage_unit) {
            document.getElementById('setting-mileage-unit').value = settings.mileage_unit;
        }
        if (settings.date_format) {
            document.getElementById('setting-date-format').value = settings.date_format;
        }
        
        if (settings.service_intervals) {
            renderServiceIntervalsForm(settings.service_intervals);
        } else {
            renderServiceIntervalsForm(null);
        }
        
        if (settings.total_spend_include_maintenance !== undefined) {
            document.getElementById('setting-total-spend-maintenance').checked = settings.total_spend_include_maintenance;
        }
        if (settings.total_spend_include_mods !== undefined) {
            document.getElementById('setting-total-spend-mods').checked = settings.total_spend_include_mods;
        }
        if (settings.total_spend_include_costs !== undefined) {
            document.getElementById('setting-total-spend-costs').checked = settings.total_spend_include_costs;
        }
        if (settings.total_spend_include_fuel !== undefined) {
            document.getElementById('setting-total-spend-fuel').checked = settings.total_spend_include_fuel;
        }
        
        const customSettingsList = document.getElementById('custom-settings-list');
        const defaultKeys = ['currency_symbol', 'mileage_unit', 'date_format', 'service_intervals', 'total_spend_include_maintenance', 'total_spend_include_mods', 'total_spend_include_costs', 'total_spend_include_fuel'];
        const customSettings = Object.entries(settings).filter(([key]) => !defaultKeys.includes(key));
        
        if (customSettings.length > 0) {
            customSettingsList.innerHTML = customSettings.map(([key, value]) => `
                <div class="custom-setting-item">
                    <span class="setting-key">${key}</span>
                    <span class="setting-value">${value}</span>
                    <button class="btn-danger btn-small" onclick="deleteSetting('${key}')">Delete</button>
                </div>
            `).join('');
        } else {
            customSettingsList.innerHTML = '<p class="no-settings">No custom settings</p>';
        }
    } catch (e) {
        console.error('Failed to load settings:', e);
        showNotification('Failed to load settings: ' + e.message, 'error');
        const customSettingsList = document.getElementById('custom-settings-list');
        if (customSettingsList) {
            customSettingsList.innerHTML = '<p class="no-settings">Unable to load settings</p>';
        }
    }
}

async function saveSetting(key, value) {
    try {
        const payload = { key, value };
        if (typeof value === 'boolean') {
            payload.value_type = 'boolean';
        }
        const result = await apiCall('/settings', {
            method: 'PUT',
            body: JSON.stringify(payload)
        });
        if (result.success) {
            showNotification('Setting saved successfully', 'success');
        } else {
            showNotification('Failed to save setting', 'error');
        }
    } catch (e) {
        showNotification('Error saving setting', 'error');
    }
}

const SERVICE_INTERVAL_TYPES = [
    { key: 'oil_change', label: 'Oil Change' },
    { key: 'brakes', label: 'Brakes' },
    { key: 'tire_rotation', label: 'Tire Rotation' },
    { key: 'inspection', label: 'Inspection' },
    { key: 'transmission', label: 'Transmission' },
    { key: 'coolant', label: 'Coolant' },
    { key: 'spark_plugs', label: 'Spark Plugs' },
    { key: 'air_filter', label: 'Air Filter' },
    { key: 'fuel_filter', label: 'Fuel Filter' }
];

function renderServiceIntervalsForm(intervals) {
    const container = document.getElementById('service-intervals-form');
    const defaultIntervals = {
        'oil_change': {'miles': 5000, 'months': 6},
        'brakes': {'miles': 20000, 'months': 24},
        'tire_rotation': {'miles': 7500, 'months': 6},
        'inspection': {'miles': 15000, 'months': 12},
        'transmission': {'miles': 30000, 'months': 24},
        'coolant': {'miles': 30000, 'months': 24},
        'spark_plugs': {'miles': 30000, 'months': 36},
        'air_filter': {'miles': 15000, 'months': 12},
        'fuel_filter': {'miles': 30000, 'months': 24}
    };
    
    const data = intervals || defaultIntervals;
    
    container.innerHTML = SERVICE_INTERVAL_TYPES.map(type => `
        <div class="service-interval-item">
            <label>${type.label}</label>
            <div class="service-interval-inputs">
                <input type="number" id="si-${type.key}-miles" value="${data[type.key]?.miles || 0}" min="0" placeholder="Miles">
                <span>mi</span>
                <input type="number" id="si-${type.key}-months" value="${data[type.key]?.months || 0}" min="0" placeholder="Months">
                <span>mo</span>
            </div>
        </div>
    `).join('');
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('save-service-intervals-btn')?.addEventListener('click', async () => {
        const serviceIntervals = {};
        
        for (const type of SERVICE_INTERVAL_TYPES) {
            const miles = parseInt(document.getElementById(`si-${type.key}-miles`).value) || 0;
            const months = parseInt(document.getElementById(`si-${type.key}-months`).value) || 0;
            serviceIntervals[type.key] = { miles, months };
        }
        
        try {
            const result = await apiCall('/settings', {
                method: 'PUT',
                body: JSON.stringify({ 
                    key: 'service_intervals', 
                    value: serviceIntervals,
                    value_type: 'json'
                })
            });
            if (result.success) {
                showNotification('Service intervals saved successfully', 'success');
            } else {
                showNotification('Failed to save service intervals', 'error');
            }
        } catch (e) {
            showNotification('Error saving service intervals', 'error');
        }
    });
});

async function addCustomSetting() {
    const key = document.getElementById('new-setting-key').value.trim();
    const value = document.getElementById('new-setting-value').value.trim();
    
    if (!key) {
        showNotification('Setting key is required', 'error');
        return;
    }
    
    try {
        const result = await apiCall('/settings', {
            method: 'PUT',
            body: JSON.stringify({ key, value })
        });
        
        if (result.success) {
            document.getElementById('new-setting-key').value = '';
            document.getElementById('new-setting-value').value = '';
            loadSettings();
            showNotification('Setting added successfully', 'success');
        }
    } catch (e) {
        showNotification('Error adding setting', 'error');
    }
}

async function deleteSetting(key) {
    if (!confirm(`Are you sure you want to delete "${key}"?`)) return;
    
    try {
        const result = await apiCall(`/settings/${key}`, { method: 'DELETE' });
        if (result.success) {
            loadSettings();
            showNotification('Setting deleted', 'success');
        }
    } catch (e) {
        showNotification('Error deleting setting', 'error');
    }
}

// Export CSV
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('export-csv-btn')?.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/settings/export');
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `muttlogbook_export_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            URL.revokeObjectURL(url);
            showNotification('Export downloaded successfully', 'success');
        } catch (e) {
            showNotification('Export failed', 'error');
        }
    });
    
    document.getElementById('backup-settings-btn')?.addEventListener('click', async () => {
        try {
            const backup = await apiCall('/settings/backup');
            const blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `muttlogbook_settings_${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
            showNotification('Backup downloaded successfully', 'success');
        } catch (e) {
            showNotification('Backup failed', 'error');
        }
    });
    
    document.getElementById('load-data-view-btn')?.addEventListener('click', async () => {
        try {
            const vehicles = await apiCall('/vehicles');
            const maintenance = await apiCall('/maintenance');
            const mods = await apiCall('/mods');
            const costs = await apiCall('/costs');
            
            const container = document.getElementById('data-view-tables');
            let html = '';
            
            if (vehicles.length > 0) {
                html += '<div class="data-section"><h4>Vehicles</h4><table><thead><tr><th>ID</th><th>Name</th><th>Make</th><th>Model</th><th>Year</th><th>Mileage</th></tr></thead><tbody>';
                vehicles.forEach(v => {
                    html += `<tr><td>${v.id}</td><td>${v.name}</td><td>${v.make}</td><td>${v.model}</td><td>${v.year}</td><td>${v.mileage}</td></tr>`;
                });
                html += '</tbody></table></div>';
            }
            
            if (maintenance.length > 0) {
                html += '<div class="data-section"><h4>Maintenance</h4><table><thead><tr><th>ID</th><th>Vehicle</th><th>Date</th><th>Category</th><th>Cost</th><th>Description</th></tr></thead><tbody>';
                maintenance.forEach(m => {
                    html += `<tr><td>${m.id}</td><td>${m.vehicle_id}</td><td>${m.date || ''}</td><td>${m.category || ''}</td><td>${m.cost || 0}</td><td>${(m.description || '').substring(0, 50)}</td></tr>`;
                });
                html += '</tbody></table></div>';
            }
            
            if (mods.length > 0) {
                html += '<div class="data-section"><h4>Mods</h4><table><thead><tr><th>ID</th><th>Vehicle</th><th>Date</th><th>Category</th><th>Status</th><th>Cost</th></tr></thead><tbody>';
                mods.forEach(m => {
                    html += `<tr><td>${m.id}</td><td>${m.vehicle_id}</td><td>${m.date || ''}</td><td>${m.category || ''}</td><td>${m.status || ''}</td><td>${m.cost || 0}</td></tr>`;
                });
                html += '</tbody></table></div>';
            }
            
            if (costs.length > 0) {
                html += '<div class="data-section"><h4>Costs</h4><table><thead><tr><th>ID</th><th>Vehicle</th><th>Date</th><th>Category</th><th>Amount</th></tr></thead><tbody>';
                costs.forEach(c => {
                    html += `<tr><td>${c.id}</td><td>${c.vehicle_id}</td><td>${c.date || ''}</td><td>${c.category || ''}</td><td>${c.amount || 0}</td></tr>`;
                });
                html += '</tbody></table></div>';
            }
            
            container.innerHTML = html || '<p class="no-data">No data available</p>';
        } catch (e) {
            showNotification('Failed to load data', 'error');
        }
    });
});
