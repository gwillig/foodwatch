
      // Source: https://jsfiddle.net/u3zk1rtm/2/
      // Create the chart
      	color=["#304f85","#b12f85","#e73b02","green","orange"]
      $('#container').highcharts('StockChart', {
        chart: {

          zoomType: 'x'
        },

        rangeSelector: {
          buttons: [{
            type: 'day',
            count: 1,
            text: '24h'
          }, {
            type: 'week',
            count: 1,
            text: '1w'
          }, {
            type: 'week',
            count: 2,
            text: '2w'
          }, {
            type: 'month',
            count: 1,
            text: '6m'
          }, {
            type: 'year',
            count: 1,
            text: '1y'
          }, {
            type: 'all',
            text: 'All'
          }],
          selected: 5
        },

        xAxis: {
          ordinal: false
        },

        yAxis: [
          {
           // 0. yAxis
            visible: false,
            title: {
              text: 'Steps' //Define here
            },
          },
          {
          // 1. yAxis
            visible: false,
            title: {
              text: 'Cal' //Define here
            },
          },
          {//2.Axsis
        	opposite: false,
            title: {
              ordinal: false,
              color:color[0],
              softMin: -10
            }
          },
          {//3.Axsis: Weight diff
            min: -2,
            max: 1,
        	opposite: false,
        	visible: false,
          },
          {//4.Axsis: Weight ratio
        	opposite: false,
        	visible: false,

          }
        ],

        title: {
          text: 'Weight | Cal | Steps'
        },
        legend: {
        enabled: true
        },

 series: [
         {
            name: 'Steps',
            alignticks: false,
            yAxis: 0,

            type: 'column',
            data:  data_steps,
          },
        {
            name: 'Cal',
            alignticks: false,
            yAxis: 1,
            data:  data_calorie,
          },
        {
            name: 'Weight',
            alignticks: false,
            yAxis: 2,
            type: 'spline',
            color:color[1],
            data: data_weight,
          },
           {
            name: 'Diff',
            alignticks: false,
            yAxis: 3,
            type: 'spline',
            color:color[3],
            data: data_diff,
          },
          {
            name: 'Ratio',
            alignticks: false,
            yAxis: 4,
            type: 'spline',
            color:color[4],
            data: data_ratio,
          },


        ]
      });
