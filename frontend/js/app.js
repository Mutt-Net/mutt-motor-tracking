let currentVehicleId = null;
const API_BASE = '/api';

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
        case 'maintenance': loadMaintenance(); break;
        case 'mods': loadMods(); break;
        case 'costs': loadCosts(); break;
        case 'notes': loadNotes(); break;
        case 'vcds': loadVCDS(); break;
    }
}

async function loadDashboard() {
    if (!currentVehicleId) return;
    const data = await apiCall(`/dashboard?vehicle_id=${currentVehicleId}`);
    document.getElementById('total-spent').textContent = `£${(data.total_spent || 0).toFixed(2)}`;
    document.getElementById('maintenance-cost').textContent = `£${(data.maintenance_cost || 0).toFixed(2)}`;
    document.getElementById('mods-cost').textContent = `£${(data.mods_cost || 0).toFixed(2)}`;
    document.getElementById('active-faults').textContent = data.active_faults || 0;
    
    const list = document.getElementById('recent-list');
    list.innerHTML = data.recent_maintenance.map(m => `
        <li>${m.date || 'N/A'} - ${m.category || ''}: ${m.description || ''}</li>
    `).join('') || '<li>No recent service records</li>';
}

async function loadVehicle() {
    const vehicles = await apiCall('/vehicles');
    if (vehicles.length > 0) {
        currentVehicleId = vehicles[0].id;
        document.getElementById('v-name').value = vehicles[0].name || '';
        document.getElementById('v-vin').value = vehicles[0].vin || '';
        document.getElementById('v-year').value = vehicles[0].year || '';
        document.getElementById('v-mileage').value = vehicles[0].mileage || '';
        document.getElementById('v-engine').value = vehicles[0].engine || '';
        document.getElementById('v-transmission').value = vehicles[0].transmission || '';
    }
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
                    <span>${r.mileage || ''} km</span>
                </div>
                <div class="record-description">${r.description || ''}</div>
                ${r.notes ? `<div class="record-notes">${r.notes}</div>` : ''}
            </div>
            <div class="record-actions">
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
                    <label>Mileage (km)</label>
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

async function loadMods() {
    if (!currentVehicleId) return;
    const statusFilter = document.getElementById('mod-status-filter').value;
    let url = `/mods?vehicle_id=${currentVehicleId}`;
    const mods = await apiCall(url);
    const filtered = statusFilter ? mods.filter(m => m.status === statusFilter) : mods;
    
    const list = document.getElementById('mods-list');
    list.innerHTML = filtered.map(m => `
        <div class="record-item">
            <div class="record-info">
                <div class="record-header">
                    <span class="record-date">${m.date || ''}</span>
                    <span class="record-category">${m.category || ''}</span>
                    <span class="badge badge-${m.status}">${m.status}</span>
                    <span class="record-cost">£${(m.cost || 0).toFixed(2)}</span>
                </div>
                <div class="record-description">${m.description || ''}</div>
            </div>
            <div class="record-actions">
                <button class="btn-secondary" onclick="editMod(${m.id}, '${m.status}')">Edit</button>
                <button class="btn-danger" onclick="deleteMod(${m.id})">Delete</button>
            </div>
        </div>
    `).join('') || '<p>No mods yet</p>';
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
                    <label>Mileage (km)</label>
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
    
    document.getElementById('mod-form').addEventListener('submit', async (e) => {
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
    });
});

async function editMod(id, currentStatus) {
    const mods = await apiCall(`/mods?vehicle_id=${currentVehicleId}`);
    const mod = mods.find(m => m.id === id);
    if (!mod) return;
    
    showModal('Edit Modification', `
        <form id="mod-edit-form">
            <input type="hidden" id="mod-edit-id" value="${id}">
            <div class="form-group">
                <label>Status</label>
                <select id="mod-edit-status">
                    <option value="planned" ${mod.status === 'planned' ? 'selected' : ''}>Planned</option>
                    <option value="in_progress" ${mod.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                    <option value="completed" ${mod.status === 'completed' ? 'selected' : ''}>Completed</option>
                </select>
            </div>
            <div class="form-group">
                <label>Notes</label>
                <textarea id="mod-edit-notes" rows="3">${mod.notes || ''}</textarea>
            </div>
            <button type="submit" class="btn-primary">Update</button>
        </form>
    `);
    
    document.getElementById('mod-edit-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await apiCall(`/mods/${id}`, {
            method: 'PUT',
            body: JSON.stringify({
                status: document.getElementById('mod-edit-status').value,
                notes: document.getElementById('mod-edit-notes').value
            })
        });
        closeModal();
        loadMods();
    });
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

document.addEventListener('DOMContentLoaded', async () => {
    const vehicles = await apiCall('/vehicles');
    if (vehicles.length > 0) {
        currentVehicleId = vehicles[0].id;
    } else {
        const result = await apiCall('/vehicles', {
            method: 'POST',
            body: JSON.stringify({
                name: 'VW EOS',
                vin: 'WVWZZZ1FZ7V033393',
                year: 2007,
                engine: '2.0 R4/4V TFSI (AXX)',
                transmission: '6-speed Manual',
                mileage: 116000
            })
        });
        currentVehicleId = result.id;
    }
    loadDashboard();
});
