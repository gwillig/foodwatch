
function get_data_today(){

     fetch('/data_today')
      .then((response) => {
        return response.json();
      })
      .then((data) => {
          proc_backend(data)
      });

}


function proc_backend(data){

    data[0].food.forEach(function(el){
        table_today = document.querySelector("#today_food")
        row = table_today.insertRow(1);
        var cell_Timestamp = row.insertCell(0);
        cell_Timestamp.innerHTML = el.timestamp_unix;
        cell_Timestamp.className="td_timestamp";
        var cell_Time = row.insertCell(1);
        cell_Time.innerHTML = convert_unix_datatime(el.timestamp_unix);
        cell_Time.className ="td_food_time";
        var cell_Name = row.insertCell(2);
        cell_Name.innerHTML = el.name;
        cell_Name.className="td_food_name"
        var cell_cal = row.insertCell(3);
        cell_cal.innerHTML = el.calorie;
        cell_cal.className = "td_food_amount";

    });


}

function current_time_string(){
  let currentdate = new Date();
  let datetime =   currentdate.getHours() + ":"
                  + currentdate.getMinutes()+ ":"
                + currentdate.getSeconds();

  return datetime

}

function convert_unix_datatime(unix_int){
  let date_obj = new Date(unix_int*1000);
  let converted_obj =   date_obj.getHours() + ":"
                  + date_obj.getMinutes()+ ":"
                + date_obj.getSeconds();

  return converted_obj
}



function replaceAll(str, find, replace) {
  //inspired by https://stackoverflow.com/questions/1144783/how-can-i-replace-all-occurrences-of-a-string
  return str.replace(new RegExp(find, 'g'), replace);
}


function insert_new_row(){

  table_today =document.querySelector("#today_food")
  newRow = table_today.insertRow(1);
  let cell_current = newRow.insertCell(0);
  cell_current.innerHTML = convert_unix_datatime(Date.now());
  let cell_timestamp = newRow.insertCell(1);
  cell_timestamp.innerHTML = Date.now();
  cell_timestamp.className = "td_timestamp";
  let cell_name = newRow.insertCell(2);
  cell_name.innerHTML = document.querySelector("#input_name").value
  let cell_cal = newRow.insertCell(3);
  cell_cal.innerHTML = document.querySelector("#input_cal").value


  post_data_today({
      timestamp_epoch:Date.now(),
      name:document.querySelector("#input_name").value,
      calorie:document.querySelector("#input_cal").value
  })
}

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

function convert_table_array(){
    table_array =[]
    table_today =document.querySelector("#today_food")
    var child = table_today.getElementsByTagName('tr');

    for(el of child){
        //To eleminate the headline
        console.log("hllo")
        if (isNaN(el.cells[0].innerText) == false &&
            el.name!=""&typeof(el.name)!="undefined"){
               table_array.push({"timestamp_epoch":el.cells[0].innerText,
                   "name":el.cells[2].innerText,
                    "calorie":el.cells[3].innerText})
        }

    }

    return table_array


}


function post_data_today(data_json){

    fetch("/data_today", {
        mode:"cors",
      method: "post",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },

      //make sure to serialize your JSON body
      body: JSON.stringify({
        data:  data_json
      })
    })
    .then( (response) => {
       console.log("data sent")
       document.querySelector("#input_cal").value = ""
       document.querySelector("#input_name").value = ""

    });

}