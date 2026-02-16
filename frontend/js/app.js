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
    return response.json();
}

function showView(viewId) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(viewId).classList.add('active');
    document.querySelector(`[data-view="${viewId}"]`).classList.add('active');
    
    switch(viewId) {
        case 'dashboard': loadDashboard(); break;
        case 'vehicle': loadVehicle(); break;
        case 'analytics': loadAnalytics(); break;
        case 'maintenance': loadMaintenance(); break;
        case 'mods': loadMods(); break;
        case 'costs': loadCosts(); break;
        case 'guides': loadGuides(); break;
        case 'notes': loadNotes(); break;
        case 'vcds': loadVCDS(); break;
        case 'settings': loadSettings(); break;
    }
}

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

document.getElementById('guide-category-filter')?.addEventListener('change', loadGuides);

document.getElementById('analytics-date-filter')?.addEventListener('change', (e) => {
    const customDates = document.getElementById('analytics-custom-dates');
    customDates.style.display = e.target.value === 'custom' ? 'flex' : 'none';
    loadAnalytics();
});

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
}

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
    
    // Load trend chart
    loadModsTrendChart(mods);
    
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

async function loadModsTrendChart(mods) {
    const ctx = document.getElementById('mods-trend-chart');
    if (!ctx) return;
    
    if (window.modsTrendChart) {
        window.modsTrendChart.destroy();
    }
    
    const monthlyData = {};
    mods.forEach(m => {
        if (m.date && m.cost) {
            const month = m.date.substring(0, 7);
            if (!monthlyData[month]) {
                monthlyData[month] = { planned: 0, in_progress: 0, completed: 0 };
            }
            monthlyData[month][m.status] = (monthlyData[month][m.status] || 0) + m.cost;
        }
    });
    
    const sortedMonths = Object.keys(monthlyData).sort();
    
    if (sortedMonths.length === 0) {
        ctx.style.display = 'none';
        return;
    }
    
    ctx.style.display = 'block';
    
    window.modsTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: sortedMonths,
            datasets: [
                {
                    label: 'Planned',
                    data: sortedMonths.map(m => monthlyData[m].planned),
                    borderColor: '#888888',
                    backgroundColor: 'rgba(136, 136, 136, 0.1)',
                    fill: true,
                    tension: 0.3
                },
                {
                    label: 'In Progress',
                    data: sortedMonths.map(m => monthlyData[m].in_progress),
                    borderColor: '#f39c12',
                    backgroundColor: 'rgba(243, 156, 18, 0.1)',
                    fill: true,
                    tension: 0.3
                },
                {
                    label: 'Completed',
                    data: sortedMonths.map(m => monthlyData[m].completed),
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    fill: true,
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true, position: 'bottom', labels: { color: '#999', padding: 8, font: { size: 10 } } }
            },
            scales: {
                x: { display: true, ticks: { color: '#999', font: { size: 9 } } },
                y: { display: true, ticks: { color: '#999', font: { size: 9 } }, beginAtZero: true }
            }
        }
    });
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

document.getElementById('add-cost-btn').addEventListener('click', () => {
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
        
        if (settings.currency_symbol) {
            document.getElementById('setting-currency').value = settings.currency_symbol;
        }
        if (settings.mileage_unit) {
            document.getElementById('setting-mileage-unit').value = settings.mileage_unit;
        }
        if (settings.date_format) {
            document.getElementById('setting-date-format').value = settings.date_format;
        }
        
        const customSettingsList = document.getElementById('custom-settings-list');
        const defaultKeys = ['currency_symbol', 'mileage_unit', 'date_format'];
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
    }
}

async function saveSetting(key, value) {
    try {
        const result = await apiCall('/settings', {
            method: 'PUT',
            body: JSON.stringify({ key, value })
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
