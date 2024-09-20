var ctx1 = document.getElementById('chart1').getContext('2d');
var prevalenceData = {
    labels: ['Fake', 'Real'],
    datasets: [{
        data: [3, 4], // These will be dynamically populated
        backgroundColor: ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)'],
        borderColor: ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)'],
        borderWidth: 1
    }]
};

var chart1 = new Chart(ctx1, {
    type: 'pie',
    data: prevalenceData,
    options: {
        maintainAspectRatio: false,
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: 'Prevalence of Disinformation (Fake vs. Real)',
                font: {
                    weight: 'bold',
                    size: 18
                }
            },
            legend: {
                labels: {
                    font: {
                        weight: 'bold'
                    }
                }
            }
        }
    }
});

var ctx2 = document.getElementById('chart2').getContext('2d');
var chart2 = new Chart(ctx2, {
    type: 'bar',
    data: {
        labels: ['January', 'February', 'March', 'April', 'May', 'June'],
        datasets: [{
            label: 'Dataset 2',
            data: [10, 14, 7, 8, 5, 4],
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
        }]
    },
    options: {
      maintainAspectRatio: false,

    }
});

var ctx3 = document.getElementById('chart3').getContext('2d');
var chart3 = new Chart(ctx3, {
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

var ctx4 = document.getElementById('chart4').getContext('2d');
var chart4 = new Chart(ctx4, {
    type: 'radar',
    data: {
        labels: [
          'Eating',
          'Drinking',
          'Sleeping',
          'Designing',
          'Coding',
          'Cycling',
          'Running'
        ],
        datasets: [{
          label: 'My First Dataset',
          data: [65, 59, 90, 81, 56, 55, 40],
          fill: true,
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          borderColor: 'rgb(255, 99, 132)',
          pointBackgroundColor: 'rgb(255, 99, 132)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgb(255, 99, 132)'
        }, {
          label: 'My Second Dataset',
          data: [28, 48, 40, 19, 96, 27, 100],
          fill: true,
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: 'rgb(54, 162, 235)',
          pointBackgroundColor: 'rgb(54, 162, 235)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgb(54, 162, 235)'
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