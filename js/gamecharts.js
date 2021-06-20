let stockData = {};
let chart;


function createChart() {
    const labels = [
        '1d',
        '2d',
        '3d'
    ];

    const data = {
        labels: labels,
        datasets: [{
            label: 'My First dataset',
            backgroundColor: 'rgb(255, 99, 132)',
            borderColor: 'rgb(255, 99, 132)',
            data: [0, 10, 5, 2, 20, 30, 45],
        }]
    };

    const config = {
        type: 'line',
        data,
        options: {
            parsing: {
                xAxisKey: 'timestamp',
                yAxisKey: 'balance'
            },
            scales: {
                xAxes: [{
                    type: 'time'
                }]
            }
        }
    };

    chart = new Chart(
        document.getElementById('chart'),
        config
    );
}

function renderChart(datasets) {
    chart.data.datasets = datasets;
    chart.update();
    console.log(datasets);
}

async function getHistoricalData(game) {
    datasets = [];
    game.players.forEach(p => {
        let data = [];
        getGameHistory(p.id).then(r => {
            r.history.forEach( hist => {
                data.push({
                    balance: hist.balance,
                    timestamp: new Date(hist.timestamp)
                });
            })
        });

        dataset = {
            label: p.user.displayname,
            backgroundColor: 'rgb(255, 99, 132)',
            borderColor: 'rgb(255, 99, 132)',
            data
        };
        datasets.push(dataset);
    });

    renderChart(datasets)
}