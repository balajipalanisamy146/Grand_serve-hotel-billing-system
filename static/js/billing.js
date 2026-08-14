let allFoods = [];
let currentBill = [];
let taxRate = 5;

document.addEventListener('DOMContentLoaded', function () {
    loadFoods();
    loadSettings();
    updateDateTime();
    setInterval(updateDateTime, 1000);

    const dropZone = document.getElementById('billItems');

    dropZone.addEventListener('dragover', function (e) {
        e.preventDefault();
        this.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', function (e) {
        this.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', function (e) {
        e.preventDefault();
        this.classList.remove('drag-over');
        const foodId = e.dataTransfer.getData('text/plain');
        const food = allFoods.find(f => f.id == foodId);
        if (food) {
            addItemToBill(food);
        }
    });

    document.getElementById('foodSearch').oninput = filterFoods;
    document.getElementById('categoryFilter').onchange = filterFoods;
    document.getElementById('clearBill').onclick = () => {
        if (currentBill.length === 0) return;
        Swal.fire({
            title: 'Clear Order?',
            text: 'This will remove all items from the current folio.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#F44336',
            confirmButtonText: 'Yes, Clear'
        }).then((result) => {
            if (result.isConfirmed) {
                currentBill = [];
                renderBill();
            }
        });
    };
    document.getElementById('saveAndPrint').onclick = saveBill;
});

async function loadFoods() {
    try {
        const res = await fetch('/api/bills/foods');
        allFoods = await res.json();
        renderFoods(allFoods);
    } catch (err) {
        console.error('Error loading foods:', err);
    }
}

async function loadSettings() {
    try {
        const res = await fetch('/api/settings/');
        const settings = await res.json();
        taxRate = settings.tax_percentage || 5;
        const el = document.getElementById('taxRate');
        if (el) el.innerText = taxRate;
    } catch (err) {
        console.error('Error loading settings:', err);
    }
}

function renderFoods(foods) {
    const container = document.getElementById('foodContainer');
    if (!container) return;
    container.innerHTML = '';

    if (foods.length === 0) {
        container.innerHTML = `
            <div class="col-12 text-center py-5 text-muted opacity-50">
                <i class="fas fa-search fa-3x mb-3"></i>
                <p>No matching delicacies found.</p>
            </div>`;
        return;
    }

    foods.forEach(food => {
        const col = document.createElement('div');
        col.className = 'col';
        col.innerHTML = `
            <div class="lux-card" draggable="true">
                <div class="food-img-lux">
                    <img src="${food.image_url}" onerror="this.src='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400'">
                    <span class="badge-lux">${food.category}</span>
                </div>
                <div class="p-3">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="fw-bold text-dark mb-0 text-truncate" style="max-width: 140px;">${food.name}</h6>
                        <span class="text-primary fw-bold">₹${food.price}</span>
                    </div>
                    <div class="d-flex align-items-center mb-3">
                        <div class="text-warning x-small me-2">
                            <i class="fas fa-star"></i>
                            <i class="fas fa-star"></i>
                            <i class="fas fa-star"></i>
                            <i class="fas fa-star"></i>
                            <i class="fas fa-star"></i>
                        </div>
                        <span class="text-muted" style="font-size: 0.65rem;">(4.9 Rating)</span>
                    </div>
                    <button class="btn btn-primary btn-sm w-100 rounded-pill py-2 fw-bold" 
                            onclick='addItemToBill(${JSON.stringify(food)})'>
                        <i class="fas fa-plus me-1"></i> ADD
                    </button>
                </div>
            </div>
        `;

        const card = col.querySelector('.lux-card');
        card.addEventListener('dragstart', function (e) {
            e.dataTransfer.setData('text/plain', food.id);
            this.classList.add('dragging');
        });
        card.addEventListener('dragend', function () {
            this.classList.remove('dragging');
        });

        container.appendChild(col);
    });
}

function filterFoods() {
    const query = document.getElementById('foodSearch').value.toLowerCase();
    const cat = document.getElementById('categoryFilter').value;

    const filtered = allFoods.filter(f => {
        const matchesQuery = f.name.toLowerCase().includes(query);
        const matchesCat = cat === 'all' || f.category === cat;
        return matchesQuery && matchesCat;
    });

    renderFoods(filtered);
}

function addItemToBill(food) {
    const existing = currentBill.find(item => item.id === food.id);
    if (existing) {
        existing.quantity++;
    } else {
        currentBill.push({
            id: food.id,
            name: food.name,
            price: food.price,
            quantity: 1
        });
    }
    renderBill();
    /* showLuxToast(`${food.name} added`); */
}

function updateQty(id, delta) {
    const item = currentBill.find(i => i.id === id);
    if (item) {
        item.quantity += delta;
        if (item.quantity <= 0) {
            currentBill = currentBill.filter(i => i.id !== id);
        }
        renderBill();
    }
}

function renderBill() {
    const list = document.getElementById('billItems');
    if (!list) return;

    // Clear only bill items, keep empty state if needed
    const items = list.querySelectorAll('.bill-item');
    items.forEach(i => i.remove());

    const empty = list.querySelector('.empty-msg');
    if (currentBill.length === 0) {
        if (empty) empty.style.display = 'flex';
        updateTotals(0, 0, 0);
        return;
    }

    if (empty) empty.style.display = 'none';

    let subtotal = 0;
    currentBill.forEach((item) => {
        const itemTotal = item.price * item.quantity;
        subtotal += itemTotal;

        const div = document.createElement('div');
        div.className = 'bill-item p-2 mb-2 bg-light rounded';
        div.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="fw-bold small">${item.name}</span>
                <span class="small">₹${itemTotal.toFixed(2)}</span>
            </div>
            <div class="d-flex justify-content-between align-items-center">
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-secondary btn-xs py-0 px-2" onclick="updateQty(${item.id}, -1)">-</button>
                    <span class="btn btn-outline-secondary disabled text-dark py-0 px-2" style="min-width: 30px;">${item.quantity}</span>
                    <button class="btn btn-outline-secondary btn-xs py-0 px-2" onclick="updateQty(${item.id}, 1)">+</button>
                </div>
                <button class="btn btn-sm btn-link text-danger p-0" onclick="updateQty(${item.id}, -${item.quantity})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        list.appendChild(div);
    });

    const gst = (subtotal * taxRate) / 100;
    const total = subtotal + gst;
    updateTotals(subtotal, gst, total);
}

function updateTotals(sub, gst, total) {
    document.getElementById('subtotal').innerText = sub.toLocaleString('en-IN', { minimumFractionDigits: 2 });
    document.getElementById('gstAmount').innerText = gst.toLocaleString('en-IN', { minimumFractionDigits: 2 });
    document.getElementById('grandTotal').innerText = total.toLocaleString('en-IN', { minimumFractionDigits: 2 });
}

async function saveBill() {
    if (currentBill.length === 0) {
        Swal.fire({ icon: 'warning', title: 'Empty Order', text: 'Please add items before printing.', confirmButtonColor: '#FF9800' });
        return;
    }

    const data = {
        customer_name: document.getElementById('custName').value || 'Guest',
        table_number: document.getElementById('tableNo').value || '-',
        items: currentBill,
        subtotal: parseFloat(document.getElementById('subtotal').innerText.replace(/,/g, '')),
        gst: parseFloat(document.getElementById('gstAmount').innerText.replace(/,/g, '')),
        grand_total: parseFloat(document.getElementById('grandTotal').innerText.replace(/,/g, '')),
        payment_method: document.querySelector('input[name="payment"]:checked').value
    };

    try {
        Swal.fire({ title: 'Finalizing Folio...', allowOutsideClick: false, didOpen: () => Swal.showLoading() });

        const res = await fetch('/api/bills/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await res.json();
        Swal.close();

        if (result.success) {
            showModernInvoice(result.bill);
            currentBill = [];
            renderBill();
            document.getElementById('custName').value = '';
            document.getElementById('tableNo').value = '';
        } else {
            Swal.fire('Error', result.message || 'Transaction failed.', 'error');
        }
    } catch (err) {
        Swal.fire('Network Error', 'Check your connection.', 'error');
    }
}

function showModernInvoice(bill) {
    const modal = new bootstrap.Modal(document.getElementById('invoiceModal'));
    const container = document.getElementById('printableInvoice');

    const itemsHtml = bill.items.map(i => `
        <tr style="border-bottom: 1px solid #f1f5f9;">
            <td class="py-2 ps-3 text-dark small">${i.name}</td>
            <td class="text-center py-2 text-dark small">${i.quantity}</td>
            <td class="text-end py-2 text-dark small">₹${i.price}</td>
            <td class="text-end py-2 pe-3 text-dark fw-bold small">₹${(i.price * i.quantity).toFixed(2)}</td>
        </tr>
    `).join('');

    container.innerHTML = `
        <div class="p-4" style="font-family: 'Outfit', sans-serif; background: #fff;">
            <div class="text-center mb-3">
                <div class="mb-2">
                    <i class="fas fa-utensils fa-2x text-primary"></i>
                </div>
                <h5 class="fw-bold text-dark mb-1">GRANDSERVE KITCHEN</h5>
                <p class="text-muted small mb-0" style="font-size: 0.7rem;">Premium Dining Experience</p>
                <div class="d-flex align-items-center justify-content-center mt-3">
                    <div class="flex-grow-1 border-top" style="border-color: #f1f5f9 !important;"></div>
                    <span class="mx-3 text-muted fw-bold" style="font-size: 0.65rem; letter-spacing: 1px;">INVOICE</span>
                    <div class="flex-grow-1 border-top" style="border-color: #f1f5f9 !important;"></div>
                </div>
            </div>
            
            <div class="row mb-3">
                <div class="col-6">
                    <div class="text-muted x-small mb-0" style="font-size: 0.6rem;">CUSTOMER</div>
                    <div class="text-dark fw-bold small">${bill.customer_name || 'Guest'}</div>
                    <div class="text-muted" style="font-size: 0.7rem;">Table: ${bill.table_number || '-'}</div>
                </div>
                <div class="col-6 text-end">
                    <div class="text-muted x-small mb-0" style="font-size: 0.6rem;">BILL NUMBER</div>
                    <div class="text-dark fw-bold small">#${bill.bill_number}</div>
                    <div class="text-muted" style="font-size: 0.7rem;">${new Date(bill.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}</div>
                </div>
            </div>

            <table class="table mb-3 border-top" style="border-color: #f1f5f9 !important;">
                <thead>
                    <tr class="bg-light">
                        <th class="border-0 text-muted small py-2 ps-3" style="font-size: 0.7rem;">ITEM</th>
                        <th class="border-0 text-muted small py-2 text-center" style="font-size: 0.7rem;">QTY</th>
                        <th class="border-0 text-muted small py-2 text-end" style="font-size: 0.7rem;">RATE</th>
                        <th class="border-0 text-muted small py-2 text-end pe-3" style="font-size: 0.7rem;">TOTAL</th>
                    </tr>
                </thead>
                <tbody>
                    ${itemsHtml}
                </tbody>
            </table>

            <div class="row justify-content-end mb-4">
                <div class="col-12">
                    <div class="p-3 rounded-4" style="background: #f8fafc; border: 1px solid #f1f5f9;">
                        <div class="d-flex justify-content-between mb-1">
                            <span class="text-muted" style="font-size: 0.75rem;">Subtotal</span>
                            <span class="text-dark fw-bold small">₹${bill.subtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                        </div>
                        <div class="d-flex justify-content-between mb-2">
                            <span class="text-muted" style="font-size: 0.75rem;">GST (${taxRate}%)</span>
                            <span class="text-dark fw-bold small">₹${bill.gst.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                        </div>
                        <div class="d-flex justify-content-between border-top pt-2" style="border-color: #e2e8f0 !important;">
                            <span class="text-dark fw-bold fs-6">TOTAL</span>
                            <span class="text-primary fw-800 fs-5">₹${bill.grand_total.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="text-center pt-3 border-top" style="border-color: #f1f5f9 !important;">
                <p class="text-muted mb-3" style="font-size: 0.7rem;">Thank you for dining with us!</p>
                <div class="mx-auto" style="width: 60px; height: 60px; background: #f8fafc; display: flex; align-items: center; justify-content: center; border: 1px solid #f1f5f9; border-radius: 0.75rem;">
                    <i class="fas fa-qrcode fa-2x opacity-25"></i>
                </div>
                <div class="mt-3 text-muted" style="font-size: 0.65rem;">Paid via <span class="text-dark fw-bold">${bill.payment_method}</span></div>
            </div>
        </div>
    `;

    modal.show();
}

function updateDateTime() {
    const el = document.getElementById('billDateTime');
    if (el) {
        const now = new Date();
        el.innerText = now.toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'short', year: 'numeric' }) + ' | ' + now.toLocaleTimeString();
    }
}

function showLuxToast(msg) {
    const toast = document.createElement('div');
    toast.className = 'position-fixed bottom-0 end-0 p-3';
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        <div class="toast show shadow-lg border-0" role="alert" style="border-radius: 1rem; background: #fff; border-left: 4px solid var(--primary-color) !important;">
            <div class="d-flex p-2">
                <div class="toast-body fw-bold small text-dark">
                    <i class="fas fa-check-circle text-primary me-2"></i>${msg}
                </div>
                <button type="button" class="btn-close ms-auto me-2 m-auto" onclick="this.closest('.position-fixed').remove()"></button>
            </div>
        </div>`;
    document.body.appendChild(toast);
    setTimeout(() => { if (toast.parentNode) toast.remove(); }, 3000);
}
