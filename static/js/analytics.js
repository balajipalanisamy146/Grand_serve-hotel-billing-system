document.addEventListener('DOMContentLoaded', function () {
    fetchStats();
    fetchChartData();
    fetchRecentOrders();
});

/* ─── Stats Cards ─────────────────────────────────────────── */
async function fetchStats() {
    try {
        const res = await fetch('/api/reports/daily');
        const data = await res.json();

        animateCounter('stat-total-sales', data.total_sales || 0);
        animateCounter('stat-num-bills', data.num_bills || 0);
        animateCounter('stat-avg-value', Math.round(data.avg_order_value || 0));
        document.getElementById('stat-best-selling').innerText =
            data.best_selling || '—';
    } catch (err) {
        console.error('Stats error:', err);
    }
}

/* ─── Revenue Chart ───────────────────────────────────────── */
async function fetchChartData() {
    try {
        const res = await fetch('/api/reports/analytics');
        const data = await res.json();

        // Format date labels: "Mon 12" style
        const labels = (data.labels || []).map(d => {
            const dt = new Date(d);
            return dt.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric' });
        });

        const values = data.values || [];
        const canvas = document.getElementById('revenueChart');
        const ctx = canvas.getContext('2d');

        // Gradient fill
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(255,152,0,0.25)');
        gradient.addColorStop(1, 'rgba(255,152,0,0)');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Revenue (₹)',
                    data: values,
                    borderColor: '#FF9800',
                    backgroundColor: gradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.45,
                    pointBackgroundColor: '#fff',
                    pointBorderColor: '#FF9800',
                    pointBorderWidth: 3,
                    pointRadius: 5,
                    pointHoverRadius: 8,
                    pointHoverBackgroundColor: '#FF9800',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,   // ← chart fills its container div
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        titleColor: '#94a3b8',
                        bodyColor: '#fff',
                        padding: 12,
                        cornerRadius: 10,
                        callbacks: {
                            label: ctx => '  Revenue: ₹' + ctx.parsed.y.toLocaleString('en-IN')
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0,0,0,0.04)', drawBorder: false },
                        border: { display: false },
                        ticks: {
                            color: '#94a3b8',
                            font: { size: 12 },
                            callback: v => '₹' + (v >= 1000 ? (v / 1000).toFixed(1) + 'k' : v)
                        }
                    },
                    x: {
                        grid: { display: false },
                        border: { display: false },
                        ticks: { color: '#94a3b8', font: { size: 12 } }
                    }
                }
            }
        });
    } catch (err) {
        console.error('Chart error:', err);
        // Show empty state if no data
        document.querySelector('.chart-wrapper').innerHTML = `
            <div class="h-100 d-flex flex-column align-items-center justify-content-center text-muted">
                <i class="fas fa-chart-line fa-3x mb-3 opacity-25"></i>
                <p class="small">No sales data yet. Start billing to see trends!</p>
            </div>`;
    }
}

/* ─── Recent Orders List ──────────────────────────────────── */
async function fetchRecentOrders() {
    try {
        const res = await fetch('/api/bills/');
        const data = await res.json();

        const list = document.getElementById('recentOrdersList');
        const badge = document.getElementById('orders-count-badge');
        list.innerHTML = '';

        // Count today's bills
        const today = new Date().toDateString();
        const todayBills = data.filter(b => new Date(b.created_at).toDateString() === today);

        if (badge) {
            badge.innerText = todayBills.length + ' today';
            badge.style.display = todayBills.length > 0 ? '' : 'none';
        }

        if (data.length === 0) {
            list.innerHTML = `
                <div class="text-center py-5 text-muted">
                    <i class="fas fa-receipt fa-3x mb-3 opacity-25"></i>
                    <p class="small mb-0">No orders yet.<br>Go to Billing to create one!</p>
                </div>`;
            return;
        }

        // Payment method color map
        const pmColor = { Cash: 'success', Card: 'info', UPI: 'warning' };

        data.slice(0, 6).forEach((bill, i) => {
            const time = new Date(bill.created_at)
                .toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
            const color = pmColor[bill.payment_method] || 'secondary';
            const row = document.createElement('div');
            row.className = 'order-row d-flex align-items-center gap-2';
            row.setAttribute('data-aos', 'fade-up');
            row.setAttribute('data-aos-delay', i * 50);
            row.innerHTML = `
                <div class="rounded-circle d-flex align-items-center justify-content-center flex-shrink-0"
                     style="width:38px;height:38px;background:rgba(255,152,0,.1);">
                    <i class="fas fa-utensils" style="color:#FF9800;font-size:.85rem;"></i>
                </div>
                <div class="flex-grow-1 min-width-0">
                    <div class="fw-semibold small text-truncate">${bill.bill_number}</div>
                    <div class="text-muted" style="font-size:.75rem;">${bill.customer_name || 'Guest'} · ${time}</div>
                </div>
                <div class="text-end flex-shrink-0">
                    <div class="fw-bold small">₹${Number(bill.grand_total).toLocaleString('en-IN')}</div>
                    <span class="badge bg-${color} bg-opacity-10 text-${color} rounded-pill" style="font-size:.65rem;">
                        ${bill.payment_method}
                    </span>
                </div>`;
            list.appendChild(row);
        });
    } catch (err) {
        console.error('Recent orders error:', err);
    }
}

/* ─── Smooth Counter Animation ────────────────────────────── */
function animateCounter(id, target) {
    const el = document.getElementById(id);
    if (!el) return;
    const duration = 800;
    const step = 16;
    const steps = duration / step;
    const inc = target / steps;
    let current = 0;

    const timer = setInterval(() => {
        current += inc;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        el.innerText = Math.round(current).toLocaleString('en-IN');
    }, step);
}
