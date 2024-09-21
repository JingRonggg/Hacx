var ctx1 = document.getElementById('chart1').getContext('2d');
var chart1 = new Chart(ctx1, {
    type: 'doughnut',
    data: {
        labels: Object.keys(interpretationCounts), 
        datasets: [{
            label: 'Interpretation Counts',
            data: Object.values(interpretationCounts), 
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',   
                'rgba(54, 162, 235, 0.2)',   
                'rgba(255, 206, 86, 0.2)',   
                'rgba(75, 192, 192, 0.2)',  
                'rgba(153, 102, 255, 0.2)'   
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',     
                'rgba(54, 162, 235, 1)',     
                'rgba(255, 206, 86, 1)',     
                'rgba(75, 192, 192, 1)',     
                'rgba(153, 102, 255, 1)'     
            ],
            borderWidth: 1
        }]
    },
    options: {
        maintainAspectRatio: false,
        responsive: true
    }
});
console.log(interpretationCounts2);

var ctx2 = document.getElementById('chart2').getContext('2d');
var chart2 = new Chart(ctx2, {
    type: 'line',
    data: {
        labels: Object.keys(interpretationCounts2),
        datasets: [{
          label: 'My First Dataset',
          data: Object.values(interpretationCounts2),
          fill: true,
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          borderColor: 'rgb(255, 99, 132)',
          pointBackgroundColor: 'rgb(255, 99, 132)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgb(255, 99, 132)'
        }]
      },
      options: {
        maintainAspectRatio: false,
        elements: {
          line: {
            borderWidth: 2,
          }
        }
      }
});