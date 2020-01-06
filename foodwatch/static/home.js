var person = 3


function create_pieChart(current_angle){
    //inspired by https://stackoverflow.com/questions/31912686/how-to-draw-gradient-arc-using-d3-js

    //Remove old svg
    if (document.querySelector(".chart-container svg")!=null){
        document.querySelector(".chart-container svg").remove()
    }

var container = document.querySelector(".chart-container"),
    tau = 2 * Math.PI,
    width = container.offsetWidth,
    height = container.offsetHeight,
    outerRadius = Math.min(width,height)/2,
    innerRadius = (outerRadius/5)*4,
    fontSize = (Math.min(width,height)/4);
    fontSize_amout = (Math.min(width,height)/8);

var arc = d3.svg.arc()
    .innerRadius(innerRadius)
    .outerRadius(outerRadius)
    .startAngle(0);

var svg = d3.select('.chart-container').append("svg")
    .attr("width", '100%')
    .attr("height", '100%')
    .attr('viewBox','0 0 '+Math.min(width,height) +' '+Math.min(width,height) )
    .attr('preserveAspectRatio','xMinYMin')
    .append("g")
    .attr("transform", "translate(" + Math.min(width,height) / 2 + "," + Math.min(width,height) / 2 + ")");

var percent = svg.append("text")
    .text('0%')
    .attr("id","percent")
    .attr("text-anchor", "middle")
    .style("font-size",fontSize+'px')
    .attr("dy",fontSize/3)
    .attr("dx",2);

var total = svg.append("text")
    .text('0%')
    .attr("id","absolut")
    .attr("text-anchor", "middle")
    .style("font-size",fontSize_amout+'px')
    .attr("dy",60+fontSize_amout/3)
    .attr("dx",2);

var description = svg.append("text")
    .text('Total amount')
    .attr("id","absolut")
    .attr("text-anchor", "middle")
    .style("font-size",fontSize_amout/2+'px')
    .attr("dy",fontSize_amout/3-60)
    .attr("dx",2);


var background = svg.append("path")
    .datum({endAngle: tau})
    .style("fill", "#fff")
    .attr("d", arc);

var foreground = svg.append("path")
    .datum({endAngle: 0 * tau})
    .style("fill", "#E73B02")
    .attr("d", arc);

foreground.transition()
      .duration(750)
      .call(arcTween, current_angle);

function arcTween(transition, newAngle) {

    transition.attrTween("d", function(d) {

        var interpolate = d3.interpolate(d.endAngle, newAngle);

        return function(t) {

            d.endAngle = interpolate(t);

            percent.text(Math.round((d.endAngle/tau)*100)+'%');
            total.text("19")

            return arc(d);
        };
    });
}

}

