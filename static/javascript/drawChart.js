function updateTable(articles) {
  // Get the table body where the articles are displayed
  var tableBody = document.querySelector('.custom-table tbody');
  
  // Clear existing rows
  tableBody.innerHTML = '';

  // Check if articles are returned, else show 'No data available'
  if (articles.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center;">No data available</td></tr>`;
      return;
  }

  // Iterate over the filtered articles and add them as new rows
  articles.forEach((article, index) => {
      var row = `<tr style="border-width: 3px">
          <th scope="row">${index + 1}</th>
          <td>${article.title}</td>
          <td>${article.interpretation}</td>
          <td>${article.confidence}%</td>
          <td>${article.deepfake || 'None'}</td>
          <td>${article.sentiment_explanation || 'None'}</td>
          <td>${article.target_Audience || 'None'}</td>
      </tr>`;
      tableBody.innerHTML += row;
  });
}


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
        responsive: true,
        onClick: function(evt, elements) {
            if (elements.length > 0) {
                var clickedIndex = elements[0].index;
                var selectedCategory = chart1.data.labels[clickedIndex];

                // Make an AJAX request to get filtered data based on the selected category
                fetch(`/get_articles_by_category?category=${selectedCategory}`)
                .then(response => response.json())
                .then(data => {
                    // Call the function to update the table with the filtered data
                    updateTable(data.articles);
                })
                .catch(error => console.error('Error fetching filtered data:', error));
            }
        }
    }
});

var ctx2 = document.getElementById('chart2').getContext('2d');
var chart2 = new Chart(ctx2, {
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
