function initDistributionChart(canvasEl, labels, data) {
    if (!canvasEl) return;
    const ctx = canvasEl.getContext('2d');
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Площа (га)',
                data: data,
                backgroundColor: [
                    '#0d6efd', 
                    '#ffc107', 
                    '#198754', 
                    '#6c757d', 
                    '#17a2b8', 
                    '#6f42c1'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Гектари (га)'
                    }
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const chartCanvas = document.getElementById('distributionChart');
    
    if (chartCanvas) {
        const labels = JSON.parse(chartCanvas.dataset.labels || '[]');
        const data = JSON.parse(chartCanvas.dataset.data || '[]');
        
        console.log("Отримані культури:", labels);
        console.log("Отримана площа:", data);
        
        initDistributionChart(chartCanvas, labels, data);
    }
});