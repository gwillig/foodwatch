
function get_data_today(){
     /*
     @description:
        Gets all records of current day from the database.
        Then it execute the function  proc_backend
     @args:
     return:
        None
     */
     fetch('/data_today')
      .then((response) => {
        return response.json();
      })
      .then((data) => {
          proc_backend(data)
      });

}


function proc_backend(data,base_total=1600){
    /*
    @description:
        Use the output from get_data_today() and processe the data.
        After the data is processsed the data will be insert into the table today_food
    @args:
        data(array): from the function get_data_today()
    @return:
        None
    */


    // Update  pie chart the total_sum of the day:
     current_angle = 2*Math.PI/base_total*data[0].total_sum_today
     create_pieChart(current_angle,data[0].total_sum_today)

    //Process every element of the data array. Every element is an record in the database
    data[0].food.forEach(function(el){
        //1.Step: Get the table today_food by id
        table_today = document.querySelector("#today_food")
        //2.Step: Insert a empty row
        row = table_today.insertRow(1);

        //3.Step: Inject a cell into the empty row
        //3.1.Step: Inject a cell with the timestampe (in unix)
        let cell_Timestamp = row.insertCell(0);
        cell_Timestamp.innerHTML = el.timestamp_unix;
        cell_Timestamp.className="td_timestamp";
        //3.1.Step: Inject a cell with the timestampe (in unix)
        let cell_Time = row.insertCell(1);
        cell_Time.innerHTML = convert_unix_datatime(el.timestamp_unix);
        cell_Time.className ="td_food_time";
        //3.2.Step: Inject a cell name of the food
        let cell_Name = row.insertCell(2);
        cell_Name.innerHTML = el.name;
        cell_Name.className="td_food_name"
        //3.3.Step: Inject a cell name of the food
        let cell_cal = row.insertCell(3);
        cell_cal.innerHTML = el.calorie;
        cell_cal.className = "td_food_amount";
        //3.4.Step: Add red x
        let cell_del = row.insertCell(4);
        cell_del.outerHTML =`<td onclick="delete_current_row(this)" data-database-id="${el.id}"=>&#10060</td>`
        cell_cal.className = "td_food_amount";


    });


}

function current_time_string(){
 /*
 @description:
 Return a string which contains the current time e.g. '13:15:16'
 @args:
    None
 @return
    datetime(string): current time e.g. '13:15:16'
 */
  let current_date = new Date();
  let datetime =   current_date.getHours() + ":"
                  + current_date.getMinutes()+ ":"
                + current_date.getSeconds();

  return datetime

}

function convert_unix_datatime(unix_int){
  /*
  @description:
    Converts unix timestampe into a string e.g. '13:13:40'. Is need because the data in the database is saved as
    unix timestampe but javascript require epoch.
  @args:
    unix_int (int):

  @return:
    datetime_string (string): e.g. '13:13:40'
  */
  let date_obj = new Date(unix_int*1000);
  let datetime_string =   date_obj.getHours() + ":"
                  + date_obj.getMinutes()+ ":"
                + date_obj.getSeconds();

  return datetime_string
}


function replaceAll(original_string, find, replace) {
  /*
  @description:
    Replaces in a given string(original_string) all occurrences for the key_word
    inspired by https://stackoverflow.com/questions/1144783/how-can-i-replace-all-occurrences-of-a-string
  @args:
    original_string(string): is the string which will be changed
    find (string): is the keyword which will be replaced
    replace (string): is the string which will replace the find string in the original_string
  @return:
    modified_string(string): the modified original_string
  */
    modified_string = original_string.replace(new RegExp(find, 'g'), replace);
    return modified_string
}


function create_pieChart(current_angle,total_sum_today){
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
            total.text(total_sum_today+" cal")

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


function insert_new_row(){
  /*
  @description:
  Convert the input from name and calorie to the row in the table #today_food
  @args:
  @return
  */
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
  //.Step: Calculate the input_cal
  //.Step: Get the value and replace comma with .dot
  let input_value = document.querySelector("#input_cal").value.replace(",",".")

  //Step:Execute the input as cmd and convert to String
  result_cal = String(Math.round(eval(input_value)))
  cell_cal.innerHTML = result_cal


  post_data_today({
      timestamp_epoch:Date.now(),
      name:document.querySelector("#input_name").value,
      calorie:result_cal
  })
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
    });

}


function delete_current_row(self){

    //1.Step: Get the data-database-id
    db_id = self.getAttribute("data-database-id")
    //2.Step: delete in data base
    fetch("/data_today", {
        mode:"cors",
        method: "delete",
        headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        },

      //make sure to serialize your JSON body
      body: JSON.stringify({
        data:  db_id
      })
    })
    .then( (response) => {
        //Delete the row
        self.parentElement.outerHTML="";
    });

}