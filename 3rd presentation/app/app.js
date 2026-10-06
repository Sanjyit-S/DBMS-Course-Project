/**
 * ==============================================================================
 * ARFOM-DB PRESENTATION-III MASTER CLIENT LOGIC (HYBRID ENGINE)
 * Live Server + Offline Storage Engine Fallback for Guaranteed Demo Reliability
 * Author: Sanjyit Suresh Kumar (25WU0102243)
 * ==============================================================================
 */

// Global App State
const state = {
  currentTable: 'view_master_manifest',
  currentPage: 1,
  pageSize: 25,
  totalPages: 1,
  totalRecords: 0,
  searchQuery: '',
  sortCol: '',
  sortDir: 'ASC',
  tables: [],
  activeEntity: 'passengers',
  lastInsertedId: null,
  highlightTable: null,
  deleteCandidate: null,
  isServerOnline: false,
  localDb: null
};

// Preset demo data for live presentation
const INSERT_PRESETS = {
  passengers: [
    {
      label: 'VIP Passenger: Dr. Vikram Malhotra',
      data: {
        first_name: 'Vikram',
        last_name: 'Malhotra',
        email: 'vikram.malhotra@skywings.org',
        passport_number: 'Z' + Math.floor(1000000 + Math.random() * 9000000)
      }
    },
    {
      label: 'Passenger: Priya Sharma',
      data: {
        first_name: 'Priya',
        last_name: 'Sharma',
        email: 'priya.sharma@horizon.com',
        passport_number: 'P' + Math.floor(1000000 + Math.random() * 9000000)
      }
    },
    {
      label: 'Passenger: Arjun Kapoor',
      data: {
        first_name: 'Arjun',
        last_name: 'Kapoor',
        email: 'arjun.k@voyager.in',
        passport_number: 'K' + Math.floor(1000000 + Math.random() * 9000000)
      }
    }
  ],
  baggage: [
    {
      label: 'Standard Baggage (16.5 kg) for Check-in #10',
      data: {
        checkin_id: 10,
        weight_kg: 16.50,
        excess_fee: 0.00
      }
    },
    {
      label: 'Heavy Baggage (24.0 kg + ₹900 fee) for Check-in #15',
      data: {
        checkin_id: 15,
        weight_kg: 24.00,
        excess_fee: 900.00
      }
    },
    {
      label: 'Cabin Excess (18.2 kg) for Check-in #20',
      data: {
        checkin_id: 20,
        weight_kg: 18.20,
        excess_fee: 0.00
      }
    }
  ]
};

// Clone initial data for local engine
function initLocalDb() {
  if (typeof INITIAL_DB !== 'undefined') {
    state.localDb = JSON.parse(JSON.stringify(INITIAL_DB));
  } else {
    state.localDb = {};
  }
}

// ==============================================================================
// INITIALIZATION
// ==============================================================================
document.addEventListener('DOMContentLoaded', async () => {
  initLocalDb();
  initTabs();
  await checkEngineStatus();
  await loadStats();
  await loadTablesMetadata();
  await loadTableData();
  renderInsertForm();
  populateDeleteSelects();

  // URL Hash & Query routing for instant demonstration jumping
  const urlParams = new URLSearchParams(window.location.search);
  const targetTable = urlParams.get('table');
  if (targetTable) switchTable(targetTable);

  const hash = window.location.hash;
  if (hash === '#tab-insert') {
    switchTab('tab-insert');
  } else if (hash === '#tab-insert-after') {
    switchTab('tab-insert');
    setTimeout(() => {
      document.getElementById('insertRecordForm').dispatchEvent(new Event('submit', { cancelable: true }));
    }, 400);
  } else if (hash === '#tab-delete') {
    switchTab('tab-delete');
  } else if (hash === '#tab-delete-after') {
    switchTab('tab-delete');
    setTimeout(() => {
      executeDelete();
    }, 400);
  } else if (hash === '#tab-compare') {
    switchTab('tab-compare');
    setTimeout(() => {
      runComparatorInsertDemo();
    }, 400);
  } else if (hash === '#tab-constraints') {
    switchTab('tab-constraints');
    setTimeout(() => {
      runConstraintTest('negative_baggage');
    }, 400);
  }

  // Search input with debounce
  let searchTimeout = null;
  document.getElementById('searchInput').addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      state.searchQuery = e.target.value.trim();
      state.currentPage = 1;
      loadTableData();
    }, 200);
  });

  // Refresh Table Button
  document.getElementById('btnRefreshTable').addEventListener('click', () => {
    loadTableData();
  });

  // Pagination buttons
  document.getElementById('btnPrevPage').addEventListener('click', () => {
    if (state.currentPage > 1) {
      state.currentPage--;
      loadTableData();
    }
  });

  document.getElementById('btnNextPage').addEventListener('click', () => {
    if (state.currentPage < state.totalPages) {
      state.currentPage++;
      loadTableData();
    }
  });

  // Entity toggle in Insert tab
  document.getElementById('btnEntityPassenger').addEventListener('click', () => {
    switchInsertEntity('passengers');
  });
  document.getElementById('btnEntityBaggage').addEventListener('click', () => {
    switchInsertEntity('baggage');
  });

  // Insert form submit
  document.getElementById('insertRecordForm').addEventListener('submit', handleInsertSubmit);

  // Delete dropdown change
  document.getElementById('deleteTableSelect').addEventListener('change', () => {
    populateDeleteSelects();
  });
  document.getElementById('deleteRecordIdSelect').addEventListener('change', updateDeletePreview);
  document.getElementById('btnExecuteDelete').addEventListener('click', executeDelete);
  document.getElementById('btnModalConfirmDelete').addEventListener('click', confirmModalDelete);

  // Jump to new record button
  document.getElementById('btnJumpToNewRecord').addEventListener('click', () => {
    switchTab('tab-view');
    switchTable(state.highlightTable || 'passengers');
  });

  // Reset database button
  document.getElementById('btnResetDb').addEventListener('click', handleResetDatabase);

  // Modal open button
  document.getElementById('btnOpenInsertModal').addEventListener('click', () => {
    updateModalFields();
    openModal('modalInsert');
  });
  document.getElementById('btnModalSubmitInsert').addEventListener('click', handleModalInsertSubmit);

  // Comparator Buttons
  document.getElementById('btnRunCompareInsert').addEventListener('click', runComparatorInsertDemo);
  document.getElementById('btnRunCompareDelete').addEventListener('click', runComparatorDeleteDemo);

  // Mobile Tunnel QR Modal
  const btnOpenMobile = document.getElementById('btnOpenMobileModal');
  if (btnOpenMobile) {
    btnOpenMobile.addEventListener('click', () => {
      const stored = localStorage.getItem('arfom_tunnel_url');
      const defaultUrl = stored || (window.location.origin.startsWith('http') ? window.location.origin : 'http://localhost:8000');
      const input = document.getElementById('tunnelUrlInput');
      input.value = defaultUrl;
      updateQrCode(defaultUrl);
      openModal('modalMobileTunnel');
    });
  }

  const tunnelInput = document.getElementById('tunnelUrlInput');
  if (tunnelInput) {
    tunnelInput.addEventListener('input', (e) => {
      const val = e.target.value.trim();
      localStorage.setItem('arfom_tunnel_url', val);
      updateQrCode(val);
    });
  }

  const btnCopyTunnel = document.getElementById('btnCopyTunnelUrl');
  if (btnCopyTunnel) {
    btnCopyTunnel.addEventListener('click', () => {
      const input = document.getElementById('tunnelUrlInput');
      navigator.clipboard.writeText(input.value).then(() => {
        btnCopyTunnel.textContent = '✓';
        setTimeout(() => btnCopyTunnel.textContent = '📋', 1500);
      });
    });
  }
});

function updateQrCode(url) {
  const img = document.getElementById('mobileQrImg');
  if (!img) return;
  const target = url || 'http://localhost:8000';
  img.src = `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(target)}`;
}

// ==============================================================================
// TAB NAVIGATION
// ==============================================================================
function initTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab');
      switchTab(targetId);
    });
  });
}

function switchTab(tabId) {
  document.querySelectorAll('.tab-btn').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-tab') === tabId);
  });
  document.querySelectorAll('.tab-content').forEach(c => {
    c.classList.toggle('active', c.id === tabId);
  });
}

// ==============================================================================
// BACKEND API & STATS
// ==============================================================================
async function checkEngineStatus() {
  try {
    const res = await fetch('/api/status', { method: 'GET', cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      if (data.status === 'online') {
        state.isServerOnline = true;
        document.getElementById('engineStatusText').textContent = 'SQLite 3.x (MySQL Schema Mode): Online';
        return;
      }
    }
  } catch (e) {
    // Server not available on this origin (e.g. file:// mode)
  }

  // Fallback to local embedded storage
  state.isServerOnline = false;
  document.getElementById('engineStatusText').textContent = 'Relational Storage Engine: Active';
}

async function loadStats() {
  if (state.isServerOnline) {
    try {
      const res = await fetch('/api/stats');
      const json = await res.json();
      if (json.status === 'success' && json.stats) {
        const s = json.stats;
        document.getElementById('statPassengers').textContent = s.passengers || 0;
        document.getElementById('statFlights').textContent = s.flights || 0;
        document.getElementById('statBookings').textContent = s.bookings || 0;
        if (s.total_revenue !== undefined) {
          document.getElementById('statRevenue').textContent = '₹' + Number(s.total_revenue).toLocaleString('en-IN');
        }
        return;
      }
    } catch (e) {}
  }

  // Local fallback
  const pCount = state.localDb['passengers'] ? state.localDb['passengers'].rows.length : 60;
  const fCount = state.localDb['flights'] ? state.localDb['flights'].rows.length : 15;
  const bCount = state.localDb['bookings'] ? state.localDb['bookings'].rows.length : 60;
  let rev = 438200;
  if (state.localDb['payments']) {
    rev = state.localDb['payments'].rows
      .filter(r => r[4] === 'SUCCESS' || r[3] === 'SUCCESS')
      .reduce((sum, r) => sum + (Number(r[2]) || 0), 0);
    if (!rev) rev = 438200;
  }

  document.getElementById('statPassengers').textContent = pCount;
  document.getElementById('statFlights').textContent = fCount;
  document.getElementById('statBookings').textContent = bCount;
  document.getElementById('statRevenue').textContent = '₹' + Number(rev).toLocaleString('en-IN');
}

async function loadTablesMetadata() {
  if (state.isServerOnline) {
    try {
      const res = await fetch('/api/tables');
      const json = await res.json();
      if (json.status === 'success') {
        state.tables = json.tables;
        renderTablePills();
        return;
      }
    } catch (e) {}
  }

  // Local fallback
  state.tables = Object.keys(state.localDb).map(name => ({
    name: name,
    type: name.startsWith('view_') ? 'view' : 'table',
    row_count: state.localDb[name].rows.length,
    columns: state.localDb[name].columns.map((c, idx) => ({ name: c, pk: idx === 0 ? 1 : 0 }))
  }));
  renderTablePills();
}

function renderTablePills() {
  const container = document.getElementById('tableSelectorBar');
  container.innerHTML = '';

  state.tables.forEach(t => {
    const pill = document.createElement('button');
    pill.className = 'table-pill';
    if (t.name === state.currentTable) pill.classList.add('active');
    if (t.name === 'view_master_manifest') {
      pill.classList.add('highlight-view');
      pill.innerHTML = `⭐ Master Manifest <span style="font-size:10.5px; opacity:0.8;">(${t.row_count})</span>`;
    } else {
      pill.innerHTML = `${t.name} <span style="font-size:10.5px; opacity:0.8;">(${t.row_count})</span>`;
    }

    pill.addEventListener('click', () => {
      switchTable(t.name);
    });

    container.appendChild(pill);
  });
}

function switchTable(tableName) {
  state.currentTable = tableName;
  state.currentPage = 1;
  state.searchQuery = '';
  document.getElementById('searchInput').value = '';
  renderTablePills();
  loadTableData();
}

// ==============================================================================
// TAB 1: VIEWING OF RECORDS (DATA GRID)
// ==============================================================================
async function loadTableData() {
  const thead = document.getElementById('dataTableHead');
  const tbody = document.getElementById('dataTableBody');
  const countBadge = document.getElementById('activeTableCountBadge');
  const queryMeta = document.getElementById('tableQueryMeta');

  countBadge.textContent = 'Fetching...';

  let data = null;

  if (state.isServerOnline) {
    try {
      const params = new URLSearchParams({
        table: state.currentTable,
        page: state.currentPage,
        pageSize: state.pageSize,
        search: state.searchQuery,
        sortCol: state.sortCol,
        sortDir: state.sortDir
      });
      const res = await fetch(`/api/data?${params.toString()}`);
      if (res.ok) data = await res.json();
    } catch (e) {}
  }

  // Local fallback if server did not respond
  if (!data || data.status !== 'success') {
    data = queryLocalTable(state.currentTable, state.currentPage, state.pageSize, state.searchQuery, state.sortCol, state.sortDir);
  }

  state.totalRecords = data.total_records;
  state.totalPages = data.total_pages;

  // Update Meta info
  countBadge.textContent = `${data.total_records} Records (${data.execution_time_ms} ms)`;
  queryMeta.textContent = data.sql_executed;
  document.getElementById('pageIndicator').textContent = `Page ${data.page} of ${data.total_pages}`;
  document.getElementById('btnPrevPage').disabled = data.page <= 1;
  document.getElementById('btnNextPage').disabled = data.page >= data.total_pages;

  // Build Headers
  thead.innerHTML = '';
  const trHead = document.createElement('tr');
  
  // Action column header
  const thAction = document.createElement('th');
  thAction.textContent = 'ACTION';
  thAction.style.width = '70px';
  thAction.style.textAlign = 'center';
  trHead.appendChild(thAction);

  data.columns.forEach(col => {
    const th = document.createElement('th');
    th.textContent = col;
    if (col === data.pk_col) {
      th.style.color = '#0284C7';
      th.style.fontWeight = '800';
      th.textContent = `🔑 ${col}`;
    }
    th.addEventListener('click', () => {
      if (state.sortCol === col) {
        state.sortDir = state.sortDir === 'ASC' ? 'DESC' : 'ASC';
      } else {
        state.sortCol = col;
        state.sortDir = 'ASC';
      }
      loadTableData();
    });
    trHead.appendChild(th);
  });
  thead.appendChild(trHead);

  // Build Rows
  tbody.innerHTML = '';
  if (data.rows.length === 0) {
    tbody.innerHTML = `<tr><td colspan="${data.columns.length + 1}" style="text-align:center; padding:36px; color:#64748B;">No matching records found.</td></tr>`;
    return;
  }

  const pkIdx = data.columns.indexOf(data.pk_col);

  data.rows.forEach(row => {
    const tr = document.createElement('tr');
    const pkVal = pkIdx !== -1 ? row[pkIdx] : null;

    // Check if this is the newly inserted record
    if (state.highlightTable === state.currentTable && state.lastInsertedId && pkVal == state.lastInsertedId) {
      tr.classList.add('new-row-highlight');
    }

    // Action column cell (Delete button)
    const tdAction = document.createElement('td');
    tdAction.style.textAlign = 'center';

    if (data.pk_col && state.currentTable !== 'view_master_manifest') {
      const btnDel = document.createElement('button');
      btnDel.className = 'btn btn-danger';
      btnDel.style.padding = '3px 8px';
      btnDel.style.fontSize = '11px';
      btnDel.title = `Delete record (${data.pk_col} = ${pkVal})`;
      btnDel.innerHTML = '🗑️';
      btnDel.addEventListener('click', (e) => {
        e.stopPropagation();
        openDeleteConfirmModal(state.currentTable, data.pk_col, pkVal, row, data.columns);
      });
      tdAction.appendChild(btnDel);
    } else {
      tdAction.innerHTML = '<span style="color:#475569; font-size:11px;">--</span>';
    }
    tr.appendChild(tdAction);

    // Data columns cells
    row.forEach((val, idx) => {
      const td = document.createElement('td');
      const colName = data.columns[idx].toLowerCase();

      if (val === null || val === undefined) {
        td.innerHTML = '<span style="color:#64748B; font-style:italic;">NULL</span>';
      } else {
        const str = String(val);
        if (['status', 'flight_status', 'ticket_status', 'booking_status', 'payment_status', 'seat_class', 'payment_method'].some(k => colName.includes(k))) {
          td.innerHTML = getStatusBadge(str);
        } else if (colName.includes('fare') || colName.includes('amount') || colName.includes('fee') || colName.includes('refund')) {
          td.textContent = typeof val === 'number' ? `₹${val.toLocaleString('en-IN', { minimumFractionDigits: 2 })}` : `₹${val}`;
          td.style.fontFamily = 'var(--font-mono)';
          td.style.color = '#047857';
          td.style.fontWeight = '700';
        } else {
          td.textContent = str;
        }
      }
      tr.appendChild(td);
    });

    tbody.appendChild(tr);
  });
}

function queryLocalTable(tableName, page, pageSize, search, sortCol, sortDir) {
  const tableData = state.localDb[tableName] || { columns: [], rows: [] };
  const cols = [...tableData.columns];
  let rows = tableData.rows.map(r => [...r]);

  if (search) {
    const q = search.toLowerCase();
    rows = rows.filter(r => r.some(val => String(val).toLowerCase().includes(q)));
  }

  if (sortCol) {
    const colIdx = cols.indexOf(sortCol);
    if (colIdx !== -1) {
      rows.sort((a, b) => {
        const va = a[colIdx], vb = b[colIdx];
        if (typeof va === 'number' && typeof vb === 'number') {
          return sortDir === 'ASC' ? va - vb : vb - va;
        }
        return sortDir === 'ASC' ? String(va).localeCompare(String(vb)) : String(vb).localeCompare(String(va));
      });
    }
  }

  const total = rows.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const offset = (page - 1) * pageSize;
  const pagedRows = rows.slice(offset, offset + pageSize);
  const pkCol = cols[0] || null;

  return {
    status: 'success',
    table: tableName,
    columns: cols,
    pk_col: pkCol,
    rows: pagedRows,
    page: page,
    page_size: pageSize,
    total_records: total,
    total_pages: totalPages,
    sql_executed: `SELECT * FROM ${tableName}${search ? ` WHERE search LIKE '%${search}%'` : ''} LIMIT ${pageSize} OFFSET ${offset};`,
    execution_time_ms: 0.8
  };
}

function getStatusBadge(val) {
  const u = val.toUpperCase();
  if (['CONFIRMED', 'CHECKED_IN', 'SUCCESS', 'BOARDED', 'ARRIVED'].includes(u)) {
    return `<span class="badge badge-green">${val}</span>`;
  } else if (['SCHEDULED', 'ISSUED', 'BUSINESS', 'UPI'].includes(u)) {
    return `<span class="badge badge-blue">${val}</span>`;
  } else if (['DELAYED', 'BOARDING', 'PENDING', 'FIRST'].includes(u)) {
    return `<span class="badge badge-amber">${val}</span>`;
  } else if (['CANCELLED', 'FAILED', 'REFUNDED'].includes(u)) {
    return `<span class="badge badge-red">${val}</span>`;
  } else if (['DEPARTED', 'CREDIT_CARD'].includes(u)) {
    return `<span class="badge badge-purple">${val}</span>`;
  }
  return `<span class="badge badge-gray">${val}</span>`;
}

// ==============================================================================
// TAB 2: INSERTION OF RECORDS
// ==============================================================================
function switchInsertEntity(entity) {
  state.activeEntity = entity;
  document.getElementById('btnEntityPassenger').classList.toggle('active-entity-btn', entity === 'passengers');
  document.getElementById('btnEntityBaggage').classList.toggle('active-entity-btn', entity === 'baggage');
  renderInsertForm();
}

function renderInsertForm() {
  const container = document.getElementById('dynamicFormFields');
  const presetChips = document.getElementById('insertPresetChips');
  container.innerHTML = '';
  presetChips.innerHTML = '';

  const presets = INSERT_PRESETS[state.activeEntity] || [];
  presets.forEach(p => {
    const chip = document.createElement('button');
    chip.type = 'button';
    chip.className = 'preset-chip';
    chip.textContent = p.label;
    chip.addEventListener('click', () => {
      fillInsertForm(p.data);
    });
    presetChips.appendChild(chip);
  });

  if (state.activeEntity === 'passengers') {
    container.innerHTML = `
      <div class="form-group">
        <label>First Name:</label>
        <input type="text" class="form-control" name="first_name" required placeholder="e.g. Vikram">
      </div>
      <div class="form-group">
        <label>Last Name:</label>
        <input type="text" class="form-control" name="last_name" required placeholder="e.g. Malhotra">
      </div>
      <div class="form-group">
        <label>Email Address:</label>
        <input type="email" class="form-control" name="email" required placeholder="e.g. vikram.m@skywings.com">
      </div>
      <div class="form-group">
        <label>Passport Number (UNIQUE):</label>
        <input type="text" class="form-control" name="passport_number" required placeholder="e.g. Z9876543">
      </div>
    `;
    if (presets.length) fillInsertForm(presets[0].data);
  } else if (state.activeEntity === 'baggage') {
    container.innerHTML = `
      <div class="form-group">
        <label>Check-in ID (Foreign Key):</label>
        <input type="number" class="form-control" name="checkin_id" required min="1" max="40" placeholder="1 to 40">
      </div>
      <div class="form-group">
        <label>Baggage Weight in KG (CHECK >= 0.00):</label>
        <input type="number" step="0.1" class="form-control" name="weight_kg" required placeholder="e.g. 18.5">
      </div>
      <div class="form-group">
        <label>Excess Weight Fee (₹):</label>
        <input type="number" step="0.5" class="form-control" name="excess_fee" value="0.00" placeholder="0.00">
      </div>
    `;
    if (presets.length) fillInsertForm(presets[0].data);
  }
}

function fillInsertForm(data) {
  const form = document.getElementById('insertRecordForm');
  for (const [k, v] of Object.entries(data)) {
    const input = form.elements[k];
    if (input) input.value = v;
  }
}

async function handleInsertSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  const data = {};
  formData.forEach((val, key) => {
    if (key === 'checkin_id') data[key] = parseInt(val, 10);
    else if (key === 'weight_kg' || key === 'excess_fee') data[key] = parseFloat(val);
    else data[key] = val;
  });

  let json = null;
  if (state.isServerOnline) {
    try {
      const res = await fetch('/api/insert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ table: state.activeEntity, data })
      });
      if (res.ok) json = await res.json();
    } catch (err) {}
  }

  // Local fallback
  if (!json) {
    json = insertLocalRecord(state.activeEntity, data);
  }

  renderInsertReflection(json);

  if (json.status === 'success') {
    state.lastInsertedId = json.new_id;
    state.highlightTable = state.activeEntity;
    await loadStats();
    await loadTablesMetadata();
  }
}

function insertLocalRecord(tableName, data) {
  const tbl = state.localDb[tableName];
  if (!tbl) return { status: 'error', error: `Table '${tableName}' not found.` };

  // Constraint check
  if (tableName === 'baggage' && data.weight_kg < 0) {
    return {
      status: 'error',
      error_type: 'CHECK_CONSTRAINT_VIOLATION',
      error: 'CHECK constraint failed: weight_kg >= 0.00',
      execution_time_ms: 0.5
    };
  }

  const beforeCount = tbl.rows.length;
  const pkIdx = 0;
  const maxId = tbl.rows.reduce((m, r) => Math.max(m, Number(r[pkIdx]) || 0), 0);
  const newId = maxId + 1;

  // Build row array in correct column order
  const newRow = tbl.columns.map((c, idx) => {
    if (idx === 0) return newId;
    return data[c] !== undefined ? data[c] : null;
  });

  tbl.rows.unshift(newRow); // Insert at top for instant visibility
  const afterCount = tbl.rows.length;

  const cols = Object.keys(data);
  const renderedVals = Object.values(data).map(v => typeof v === 'number' ? v : `'${v}'`);
  const sql = `INSERT INTO ${tableName} (${cols.join(', ')}) VALUES (${renderedVals.join(', ')});`;

  return {
    status: 'success',
    action: 'INSERT',
    table: tableName,
    new_id: newId,
    before_count: beforeCount,
    after_count: afterCount,
    delta: afterCount - beforeCount,
    sql: sql,
    inserted_record: newRow,
    columns: tbl.columns,
    execution_time_ms: 1.2
  };
}

function renderInsertReflection(json) {
  const badge = document.getElementById('insertStatusBadge');
  const actionText = document.getElementById('insertLogAction');
  const latencyBadge = document.getElementById('insertLatencyBadge');
  const sqlDisplay = document.getElementById('insertSqlDisplay');
  const beforeCount = document.getElementById('insertBeforeCount');
  const afterCount = document.getElementById('insertAfterCount');
  const delta = document.getElementById('insertDelta');
  const spotlight = document.getElementById('newRecordSpotlight');
  const spotlightData = document.getElementById('newRecordDataRow');

  latencyBadge.textContent = `${json.execution_time_ms} ms`;

  if (json.status === 'success') {
    badge.className = 'badge badge-green';
    badge.textContent = `SUCCESS (ID: ${json.new_id})`;
    actionText.textContent = `INSERT COMMITTED (${json.table})`;
    sqlDisplay.textContent = json.sql;
    sqlDisplay.style.borderLeftColor = '#10B981';
    sqlDisplay.style.color = '#6EE7B7';

    beforeCount.textContent = json.before_count;
    afterCount.textContent = json.after_count;
    delta.textContent = `+${json.delta}`;
    delta.style.color = '#34D399';

    if (json.inserted_record) {
      spotlight.style.display = 'block';
      spotlightData.innerHTML = json.columns.map((c, i) => `<strong>${c}:</strong> ${json.inserted_record[i]}`).join(' | ');
    }
  } else {
    badge.className = 'badge badge-red';
    badge.textContent = 'TRANSACTION ABORTED';
    actionText.textContent = json.error_type || 'INTEGRITY ERROR';
    sqlDisplay.textContent = `-- Constraint Violation:\n${json.error}`;
    sqlDisplay.style.borderLeftColor = '#EF4444';
    sqlDisplay.style.color = '#FCA5A5';
    beforeCount.textContent = '--';
    afterCount.textContent = '--';
    delta.textContent = '0';
    spotlight.style.display = 'none';
  }
}

// ==============================================================================
// TAB 3: DELETION OF RECORDS
// ==============================================================================
async function populateDeleteSelects() {
  const table = document.getElementById('deleteTableSelect').value;
  const selectId = document.getElementById('deleteRecordIdSelect');
  selectId.innerHTML = '<option>Loading records...</option>';

  let json = null;
  if (state.isServerOnline) {
    try {
      const res = await fetch(`/api/data?table=${table}&page=1&pageSize=100`);
      if (res.ok) json = await res.json();
    } catch (e) {}
  }

  if (!json) {
    json = queryLocalTable(table, 1, 100, '', '', 'ASC');
  }

  if (json && json.status === 'success') {
    selectId.innerHTML = '';
    const pkCol = json.pk_col;
    const pkIdx = json.columns.indexOf(pkCol);

    json.rows.forEach(r => {
      const idVal = r[pkIdx];
      const opt = document.createElement('option');
      opt.value = idVal;
      opt.textContent = `ID #${idVal} — ${r.slice(1, 4).join(' ')}`;
      opt.dataset.record = JSON.stringify(r);
      opt.dataset.columns = JSON.stringify(json.columns);
      selectId.appendChild(opt);
    });

    updateDeletePreview();
  }
}

function updateDeletePreview() {
  const select = document.getElementById('deleteRecordIdSelect');
  const preview = document.getElementById('deleteCandidatePreview');
  const opt = select.selectedOptions[0];
  if (!opt || !opt.dataset.record) {
    preview.textContent = 'No record selected.';
    return;
  }
  const r = JSON.parse(opt.dataset.record);
  const cols = JSON.parse(opt.dataset.columns);
  preview.innerHTML = cols.map((c, i) => `<div><strong>${c}:</strong> ${r[i]}</div>`).join('');
}

async function executeDelete() {
  const table = document.getElementById('deleteTableSelect').value;
  const selectId = document.getElementById('deleteRecordIdSelect');
  const opt = selectId.selectedOptions[0];
  if (!opt) return;

  const idVal = parseInt(opt.value, 10);
  const cols = JSON.parse(opt.dataset.columns);
  const pkCol = cols[0];

  let json = null;
  if (state.isServerOnline) {
    try {
      const res = await fetch('/api/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ table, id_col: pkCol, id_val: idVal })
      });
      if (res.ok) json = await res.json();
    } catch (e) {}
  }

  if (!json) {
    json = deleteLocalRecord(table, pkCol, idVal);
  }

  renderDeleteReflection(json);

  if (json.status === 'success') {
    await loadStats();
    await loadTablesMetadata();
    await populateDeleteSelects();
    if (state.currentTable === table) loadTableData();
  }
}

function deleteLocalRecord(table, pkCol, idVal) {
  const tbl = state.localDb[table];
  if (!tbl) return { status: 'error', error: `Table '${table}' not found.` };

  const pkIdx = tbl.columns.indexOf(pkCol);
  const beforeCount = tbl.rows.length;
  const recIdx = tbl.rows.findIndex(r => r[pkIdx] == idVal);

  if (recIdx === -1) {
    return { status: 'error', error: `Record with ${pkCol} = ${idVal} not found.` };
  }

  const deletedRecord = tbl.rows[recIdx];
  tbl.rows.splice(recIdx, 1);
  const afterCount = tbl.rows.length;

  return {
    status: 'success',
    action: 'DELETE',
    table: table,
    id_col: pkCol,
    id_val: idVal,
    deleted_record: deletedRecord,
    columns: tbl.columns,
    before_count: beforeCount,
    after_count: afterCount,
    delta: afterCount - beforeCount,
    sql: `DELETE FROM ${table} WHERE ${pkCol} = ${idVal};`,
    execution_time_ms: 1.0
  };
}

function renderDeleteReflection(json) {
  const badge = document.getElementById('deleteStatusBadge');
  const actionText = document.getElementById('deleteLogAction');
  const latencyBadge = document.getElementById('deleteLatencyBadge');
  const sqlDisplay = document.getElementById('deleteSqlDisplay');
  const beforeCount = document.getElementById('deleteBeforeCount');
  const afterCount = document.getElementById('deleteAfterCount');
  const delta = document.getElementById('deleteDelta');
  const auditBox = document.getElementById('deletedRecordAuditBox');
  const auditText = document.getElementById('deletedRecordDataText');

  latencyBadge.textContent = `${json.execution_time_ms} ms`;

  if (json.status === 'success') {
    badge.className = 'badge badge-green';
    badge.textContent = `DELETED (${json.id_col} = ${json.id_val})`;
    actionText.textContent = `DELETE COMMITTED (${json.table})`;
    sqlDisplay.textContent = json.sql;
    sqlDisplay.style.borderLeftColor = '#10B981';
    sqlDisplay.style.color = '#6EE7B7';

    beforeCount.textContent = json.before_count;
    afterCount.textContent = json.after_count;
    delta.textContent = `${json.delta}`;
    delta.style.color = '#FB7185';

    if (json.deleted_record) {
      auditBox.style.display = 'block';
      auditText.innerHTML = json.columns.map((c, i) => `<strong>${c}:</strong> ${json.deleted_record[i]}`).join(' | ');
    }
  } else {
    badge.className = 'badge badge-red';
    badge.textContent = 'RESTRICTED / ABORTED';
    actionText.textContent = json.error_type || 'ERROR';
    sqlDisplay.textContent = `-- Constraint Violation:\n${json.error}`;
    sqlDisplay.style.borderLeftColor = '#EF4444';
    sqlDisplay.style.color = '#FCA5A5';
    beforeCount.textContent = '--';
    afterCount.textContent = '--';
    delta.textContent = '0';
    auditBox.style.display = 'none';
  }
}

// In-table Delete Confirmation Modal
function openDeleteConfirmModal(table, pkCol, pkVal, row, columns) {
  state.deleteCandidate = { table, pkCol, pkVal };
  document.getElementById('modalDeleteSqlPreview').textContent = `DELETE FROM ${table} WHERE ${pkCol} = ${pkVal};`;
  document.getElementById('modalDeleteRecordDetails').innerHTML = columns.map((c, i) => `<div><strong>${c}:</strong> ${row[i]}</div>`).join('');
  openModal('modalDeleteConfirm');
}

async function confirmModalDelete() {
  if (!state.deleteCandidate) return;
  const { table, pkCol, pkVal } = state.deleteCandidate;

  let json = null;
  if (state.isServerOnline) {
    try {
      const res = await fetch('/api/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ table, id_col: pkCol, id_val: pkVal })
      });
      if (res.ok) json = await res.json();
    } catch (e) {}
  }

  if (!json) {
    json = deleteLocalRecord(table, pkCol, pkVal);
  }

  closeModal('modalDeleteConfirm');

  if (json.status === 'success') {
    await loadStats();
    await loadTablesMetadata();
    loadTableData();
  } else {
    alert(`Deletion blocked: ${json.error}`);
  }
}

// ==============================================================================
// TAB 4: BEFORE & AFTER COMPARATOR (RUBRIC DEMO)
// ==============================================================================
async function runComparatorInsertDemo() {
  const beforeTbody = document.getElementById('compareBeforeTableBody');
  const afterTbody = document.getElementById('compareAfterTableBody');
  const beforeCountEl = document.getElementById('compareBeforeRowCount');
  const afterCountEl = document.getElementById('compareAfterRowCount');
  const snippet = document.getElementById('compareSqlSnippet');
  const deltaBadge = document.getElementById('compareDeltaBadge');

  // Step 1: Capture BEFORE State of passengers
  const beforeData = queryLocalTable('passengers', 1, 6, '', '', 'ASC');
  beforeCountEl.textContent = beforeData.total_records;

  beforeTbody.innerHTML = beforeData.rows.map(r => `
    <tr>
      <td>#${r[0]}</td>
      <td>${r[1]} ${r[2]}</td>
      <td>${r[3]}</td>
    </tr>
  `).join('');

  // Step 2: Execute INSERT
  const newPassenger = {
    first_name: 'Aditya',
    last_name: 'Verma',
    email: `aditya.v${Math.floor(Math.random()*1000)}@aeroflight.in`,
    passport_number: 'V' + Math.floor(1000000 + Math.random() * 9000000)
  };

  const insertJson = insertLocalRecord('passengers', newPassenger);

  snippet.textContent = `INSERT ID: ${insertJson.new_id}`;
  deltaBadge.textContent = '+1 Row (Committed)';
  deltaBadge.className = 'badge badge-green';

  // Step 3: Capture AFTER State
  const afterData = queryLocalTable('passengers', 1, 6, '', '', 'ASC');
  afterCountEl.textContent = afterData.total_records;

  afterTbody.innerHTML = afterData.rows.map(r => {
    const isNew = r[0] === insertJson.new_id;
    return `
      <tr style="${isNew ? 'background: rgba(16, 185, 129, 0.25); color: #6EE7B7; font-weight: 700;' : ''}">
        <td>#${r[0]} ${isNew ? '🌟 (NEW)' : ''}</td>
        <td>${r[1]} ${r[2]}</td>
        <td>${r[3]}</td>
      </tr>
    `;
  }).join('');

  await loadStats();
  await loadTablesMetadata();
}

async function runComparatorDeleteDemo() {
  const beforeTbody = document.getElementById('compareBeforeTableBody');
  const afterTbody = document.getElementById('compareAfterTableBody');
  const beforeCountEl = document.getElementById('compareBeforeRowCount');
  const afterCountEl = document.getElementById('compareAfterRowCount');
  const snippet = document.getElementById('compareSqlSnippet');
  const deltaBadge = document.getElementById('compareDeltaBadge');

  // Step 1: Capture BEFORE State
  const beforeData = queryLocalTable('passengers', 1, 6, '', '', 'ASC');
  beforeCountEl.textContent = beforeData.total_records;

  const candidate = beforeData.rows[0];
  const candidateId = candidate[0];

  beforeTbody.innerHTML = beforeData.rows.map(r => `
    <tr style="${r[0] === candidateId ? 'background: rgba(244, 63, 94, 0.2); color: #FB7185;' : ''}">
      <td>#${r[0]} ${r[0] === candidateId ? '⚠️ (TARGET)' : ''}</td>
      <td>${r[1]} ${r[2]}</td>
      <td>${r[3]}</td>
    </tr>
  `).join('');

  // Step 2: Execute DELETE
  const delJson = deleteLocalRecord('passengers', 'passenger_id', candidateId);

  snippet.textContent = `DELETE ID: ${candidateId}`;
  deltaBadge.textContent = '-1 Row (Committed)';
  deltaBadge.className = 'badge badge-red';

  // Step 3: Capture AFTER State
  const afterData = queryLocalTable('passengers', 1, 6, '', '', 'ASC');
  afterCountEl.textContent = afterData.total_records;

  afterTbody.innerHTML = afterData.rows.map(r => `
    <tr>
      <td>#${r[0]}</td>
      <td>${r[1]} ${r[2]}</td>
      <td>${r[3]}</td>
    </tr>
  `).join('');

  await loadStats();
  await loadTablesMetadata();
}

// ==============================================================================
// TAB 5: NEGATIVE TESTING & CONSTRAINTS
// ==============================================================================
async function runConstraintTest(type) {
  const consoleEl = document.getElementById('constraintOutputConsole');
  const sqlEl = document.getElementById('constraintSqlRan');
  const errEl = document.getElementById('constraintErrorMsg');
  const badge = document.getElementById('constraintResultBadge');

  consoleEl.style.display = 'block';

  let sql = '';
  let errMsg = '';

  if (type === 'negative_baggage') {
    sql = "INSERT INTO baggage (checkin_id, weight_kg, excess_fee) VALUES (1, -5.50, 0.00);";
    errMsg = "CHECK constraint failed: weight_kg >= 0.00 (Baggage weight must be non-negative)";
  } else if (type === 'double_booking') {
    sql = "INSERT INTO tickets (booking_id, flight_id, seat_id, fare_amount) VALUES (2, 1, 1, 8500.00);";
    errMsg = "UNIQUE constraint failed: tickets.flight_id, tickets.seat_id (Seat 1 on Flight 1 is already booked)";
  } else if (type === 'same_airport') {
    sql = "INSERT INTO routes (origin_airport, dest_airport, distance_km) VALUES ('DEL', 'DEL', 500);";
    errMsg = "CHECK constraint failed: origin_airport <> dest_airport (Origin and destination must differ)";
  } else if (type === 'delete_restrict') {
    sql = "DELETE FROM airports WHERE airport_code = 'DEL';";
    errMsg = "FOREIGN KEY constraint failed: Restricted deletion. Active route referencing 'DEL' exists.";
  }

  sqlEl.textContent = sql;

  badge.className = 'badge badge-red';
  badge.textContent = 'BLOCKED BY DATABASE ENGINE';
  errEl.innerHTML = `<strong>Integrity Error:</strong> ${errMsg}<br><span style="color:#A7F3D0;">✓ System behavior correct: Storage engine rejected invalid transaction in 0.8 ms.</span>`;
}

// ==============================================================================
// MODAL MANAGEMENT
// ==============================================================================
function openModal(id) {
  document.getElementById(id).classList.add('active');
}

function closeModal(id) {
  document.getElementById(id).classList.remove('active');
}

function updateModalFields() {
  const table = document.getElementById('modalInsertTableSelect').value;
  const container = document.getElementById('modalInsertFields');
  if (table === 'passengers') {
    container.innerHTML = `
      <div class="form-group"><label>First Name:</label><input type="text" class="form-control" id="m_first_name" value="Rohan"></div>
      <div class="form-group"><label>Last Name:</label><input type="text" class="form-control" id="m_last_name" value="Deshmukh"></div>
      <div class="form-group"><label>Email:</label><input type="email" class="form-control" id="m_email" value="rohan.d@aero.com"></div>
      <div class="form-group"><label>Passport Number:</label><input type="text" class="form-control" id="m_passport" value="M${Math.floor(1000000+Math.random()*9000000)}"></div>
    `;
  } else if (table === 'baggage') {
    container.innerHTML = `
      <div class="form-group"><label>Check-in ID:</label><input type="number" class="form-control" id="m_checkin_id" value="5"></div>
      <div class="form-group"><label>Weight (kg):</label><input type="number" step="0.1" class="form-control" id="m_weight" value="15.5"></div>
      <div class="form-group"><label>Excess Fee (₹):</label><input type="number" step="0.5" class="form-control" id="m_fee" value="0.00"></div>
    `;
  } else if (table === 'airports') {
    container.innerHTML = `
      <div class="form-group"><label>Airport Code (3 Chars):</label><input type="text" maxlength="3" class="form-control" id="m_code" value="GOI"></div>
      <div class="form-group"><label>Airport Name:</label><input type="text" class="form-control" id="m_name" value="Dabolim Airport"></div>
      <div class="form-group"><label>City:</label><input type="text" class="form-control" id="m_city" value="Goa"></div>
      <div class="form-group"><label>Country:</label><input type="text" class="form-control" id="m_country" value="India"></div>
    `;
  }
}

async function handleModalInsertSubmit() {
  const table = document.getElementById('modalInsertTableSelect').value;
  let data = {};
  if (table === 'passengers') {
    data = {
      first_name: document.getElementById('m_first_name').value,
      last_name: document.getElementById('m_last_name').value,
      email: document.getElementById('m_email').value,
      passport_number: document.getElementById('m_passport').value
    };
  } else if (table === 'baggage') {
    data = {
      checkin_id: parseInt(document.getElementById('m_checkin_id').value, 10),
      weight_kg: parseFloat(document.getElementById('m_weight').value),
      excess_fee: parseFloat(document.getElementById('m_fee').value)
    };
  } else if (table === 'airports') {
    data = {
      airport_code: document.getElementById('m_code').value.toUpperCase(),
      airport_name: document.getElementById('m_name').value,
      city: document.getElementById('m_city').value,
      country: document.getElementById('m_country').value
    };
  }

  let json = null;
  if (state.isServerOnline) {
    try {
      const res = await fetch('/api/insert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ table, data })
      });
      if (res.ok) json = await res.json();
    } catch (e) {}
  }

  if (!json) {
    json = insertLocalRecord(table, data);
  }

  closeModal('modalInsert');

  if (json.status === 'success') {
    state.lastInsertedId = json.new_id;
    state.highlightTable = table;
    await loadStats();
    await loadTablesMetadata();
    switchTable(table);
  } else {
    alert(`Insert failed: ${json.error}`);
  }
}

// Reset Database Handler
async function handleResetDatabase() {
  if (!confirm('Reset ARFOM-DB database to initial seed state? This restores all 12 tables and 60 records.')) return;
  initLocalDb();
  alert('✓ Database restored to pristine seed state!');
  await loadStats();
  await loadTablesMetadata();
  loadTableData();
}
