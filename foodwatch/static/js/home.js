
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


function proc_backend(data){
    /*
    @description:
        Use the output from get_data_today() and processe the data.
        After the data is processsed the data will be insert into the table today_food
    @args:
        data(array): from the function get_data_today()
    @return:
        None
    */
    let base_total = data[0].total_calories_plan;

    // Update  pie chart the total_sum of the day:
     current_angle = 2*Math.PI/base_total*data[0].total_sum_today
     create_pieChart(current_angle,data[0].total_sum_today,base_total)

    //Process every element of the data array. Every element is an record in the database
    data[0].food.forEach(function(el){
        insert_new_row(el.timestamp_unix,el.name,el.calorie,el.id)
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

function convert_unix_datatime(timestamp,unix=true){
  /*
  @description:
    Converts  timestampe into a string e.g. '13:13:40'
  @args:
    timestamp (int): e.g. 1588149907472
    unix (boolean)
  @return:
    datetime_string (string): e.g. '13:13:40'
  */
  let date_obj = null;
  if(unix==true){
    //To process date from the backend when the page is new loaded
    //7200000 is the offset of 2 hours because, Date.now is always UTC
    date_obj = new Date(timestamp*1000-7200000);

  }
  else{
    //To process date which is sended to the backend after the button "Add" is clicked
    //7200000 is the offset of 2 hours because, Date.now is always UTC
    date_obj = new Date(timestamp-7200000);
  }

  let datetime_string =   date_obj.getHours() + ":"
                        + date_obj.getMinutes()

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


function create_pieChart(current_angle,total_sum_today,base_total,color_pie="#3C6B9E"){
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

var remaining = svg.append("text")
    .text('1600 cal')
    .attr("id","remaining")
    .attr("text-anchor", "middle")
    .style("font-size",fontSize_amout/1.2+'px')
    .attr("dy",80+fontSize_amout/3)
    .attr("dx",2);

var total = svg.append("text")
    .text('0%')
    .attr("id","absolut")
    .attr("text-anchor", "middle")
    .style("font-size",fontSize_amout+'px')
    .attr("dy",50+fontSize_amout/3)
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
    .style("fill", color_pie)
    .attr("d", arc);

//1.Step: Check the available screen width for style
    if (screen.availWidth>600){
        description.style("font-size",fontSize_amout/2+'px')
                    .attr("dy",fontSize_amout/8-60);
        percent.style("font-size",fontSize/2+'px')
                .attr("dy",fontSize/10)
                .attr("dx",2);

        total.style("font-size",fontSize_amout+'px')
            .attr("dy",50+fontSize_amout/7)


        remaining.style("font-size",fontSize_amout/1.2+'px')
                  .attr("dy",80+fontSize_amout/3)

     }
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
            remaining.text(base_total-total_sum_today +" cal")
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


function inject_array_db(){
    /*
    @description:
        Injest a array into the database
    @args:
    */
    //1.Step: The the values from the textarea
    let textarea  = document.querySelector("#bulk_textarea")
    let bulk_items = textarea.value
    let textarea_array = bulk_items.replace(/\r\n/g,"\n").split("\n");
    let array_finish = textarea_array.map((el)=>el.split(","))
    let total_calorie_plan = document.querySelector("#total_calorie").value;
    for([food_name,calorie] of array_finish){
        console.log(food_name,": ",calorie)

        post_data_today({
          //7200000 is the offset of 2 hours because, Date.now is always UTC
          timestamp_epoch: Date.now()+7200000,
          name: food_name,
          calorie: calorie,
          total_calorie_plan:total_calorie_plan,
      })
    }

    }

function last_time_eat(){
    /*
        @description:
        Calculate and shows the last time, when something was eaten
    */
    setInterval(function(){
        //1.Step: Get table today_food
        table_today = document.querySelector("#today_food")
        //1.1.Get the first cell of the row with the datetime in unix
        let last_time_meal = table_today.rows[1].cells[0].textContent;
        if (last_time_meal!=""){
            //1.2.Convert to epoch
            last_time_meal_epoch = last_time_meal*1000 ;
            // Add offset to time now
            let time_now = Date.now()+7200000
            //1.2. Cal diff in h
            let diff = time_now-last_time_meal_epoch;
            let diff_h = diff/1000/60/60;
            //1.3.Step: Round to mins
            let diff_h_round = Math.round(diff_h*100)/100
            //2.Step: change the innerText of div_last_time p
            document.querySelector("#div_last_time p").innerText = `Time since last meal: ${diff_h_round} h`
            //3.Step: Check if the differnce is smaller 1 h
            if (diff_h_round<1){
               document.querySelector("#div_last_time p").style.cssText ="color:red;font-size:large"
            }
            else{
            document.querySelector("#div_last_time p").style.cssText ="color:green"
            }
        }
    }, 3000)

}


function insert_bulktextarea(content){

    /*
    @description
        The content for bulk textarea is a string, because
         line breaks (\n\r?) are not the same as HTML <br/> tags
         it is neccessary to set the value via js
    @args:

    */
    document.querySelector("#bulk_textarea").value = content
}

function get_bulk_items(){

    /*
    @description
        Loads the items in the bulk textarea to the slot
    @args:

    */
    let bulk_slot = document.querySelector("#bulk_slot").value

    fetch(`/bulk_items/${bulk_slot}`)
    .then(function(response){
                //Check status code
                if(response.ok==false){
                    //
                    return response.text()
                }
                else{

                   return response.json()
                }
            })
    .then((data)=>{
    document.querySelector("#bulk_textarea").value = data[0]["bulk_slot_items"]
    })

}

function post_bulk_items(){

    /*
    @description
        Saves the items in the bulk textarea to a slot
    @args:

    */
    let bulk_slot = document.querySelector("#bulk_slot").value
    let bulk_items = document.querySelector("#bulk_textarea").value
    let bearer_str  = get_jwt();
    fetch(`/bulk_items`,{
        mode:"cors",
        method: "post",
        headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization':bearer_str
        },

      //make sure to serialize your JSON body
      body: JSON.stringify({
        "bulk_items": bulk_items,
        "bulk_slot":bulk_slot
      })
    })
    .then(function(response){
                //Check status code
                if(response.ok==false){
                    //
                    return response.text()
                }
                else{

                   return "Items successfuly posted to database"
                }
            })
    .then((data)=>{
    document.querySelector("#bulk_msg").innerText = data
    })

}
function post_insert_data(){
  /*
  @description:
  Posts new data to database and insert new row
  @args:
  @return
  */
  let input_value = document.querySelector("#input_cal").value.replace(",",".")
  let food_name = document.querySelector("#input_name").value;
  let total_calorie_plan = document.querySelector("#total_calorie").value;
  //1.2.Step:Execute the input as cmd and convert to String
  let result_cal = String(Math.round(eval(input_value)))


  post_data_today({
      //7200000 is the offset of 2 hours because, Date.now is always UTC
      timestamp_epoch: Date.now()+7200000,
      name: food_name,
      calorie: result_cal,
      total_calorie_plan:total_calorie_plan
  },
  unix=false)
}
function insert_new_row(timestamp_unix,food_name,calorie,db_id){
    /*
    @description:
    Convert the input from name and calorie to the row in the table #today_food
    @args:
    @return
    */
    //1.Step: Get the table today_food by id
    let table_today = document.querySelector("#today_food")
    //2.Step: Insert a empty row
    row = table_today.insertRow(1);

    //3.Step: Inject a cell into the empty row
    //3.1.Step: Inject a cell with the timestampe (in unix)
    let cell_Timestamp = row.insertCell(0);
    cell_Timestamp.innerHTML = timestamp_unix;
    cell_Timestamp.className="td_timestamp";
    //3.1.Step: Inject a cell with the timestampe (in unix)
    let cell_Time = row.insertCell(1);
    cell_Time.innerHTML = convert_unix_datatime(timestamp_unix,unix=true);
    cell_Time.className ="td_food_time";
    //3.2.Step: Inject a cell name of the food
    let cell_Name = row.insertCell(2);
    cell_Name.innerHTML = food_name;
    cell_Name.className="td_food_name"
    //3.3.Step: Inject a cell name of the food
    let cell_cal = row.insertCell(3);
    cell_cal.innerHTML = calorie;
    cell_cal.className = "td_food_amount";
    //3.4.Step: Add red x
    let cell_del = row.insertCell(4);
    cell_del.outerHTML =`<td onclick="delete_current_row(this)" data-database-id="${db_id}"=>&#10060</td>`
    cell_cal.className = "td_food_amount";
}

function post_data_today(data_json,unix=true){
    /*
    @description:
        Function posts food data to the back end
    */
    //1.step: Convert data_json.timestamp_epoch to unix
    data_json.timestamp_unix = data_json.timestamp_epoch/1000
    let bearer_str  = get_jwt();
    fetch("/data_today", {
        mode:"cors",
        method: "post",
        headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization':bearer_str
        },

      //make sure to serialize your JSON body
      body: JSON.stringify({
        data:  data_json
      })
    }).then(function(response){
            //Check status code
            if(response.ok==false){
                return response.text()
            }
            else{
                insert_new_row(data_json.timestamp_unix,data_json.name,data_json.calorie,9999)
               return "ok"
            }
        })
      .then(body=>process_fetch_body(body));

}

function process_fetch_body(body){
        /*
        Process the reponse of a fetch, because a fetch is a pending promise it is not
        possible to simple access the response
        See: https://stackoverflow.com/questions/49784371/fetch-api-get-error-messages-from-server-rather-than-generic-messages/49794801
        */
        let p_msg_db= document.querySelector("#msg_db")
        if(body!="ok"){
            //Parse the response string to an html object
            let parser = new DOMParser()
            let doc = parser.parseFromString(body, "text/html");
            '#1.Step: Check if auth error or other'
            '#1.1.Step: If auth error, an element with the class errormsg will be found'
             let error_details_raw = doc.querySelector(".errormsg");
             let error_detail_str=null;
            if (error_details_raw != null){
                let error_details_msg_raw = error_details_raw.innerText.split("foodwatch.auth.AuthError: (")[1];
                //remove Error code
                let error_details = error_details_msg_raw.split(", 401)")[0];
                error_detail_str = replaceAll(error_details,"'",'"');
                let error_json = JSON.parse(error_detail_str);
            }
            else{
                error_detail_str = JSON.parse(body).message;
            }




            //Show error msg

            p_msg_db.innerHTML=error_detail_str;
            p_msg_db.style.cssText += 'color:red;font-size: large;';

        }
        else{
           p_msg_db.innerHTML="Successfully submitted to database";
           p_msg_db.style.cssText += 'color:green;font-size: large;';
        }

      }
function delete_current_row(self_row){
    /*
    @description:
        Delete the current row
    @args:
       self_row (html-obj)
    */
    //1.Step: Get the data-database-id
    db_id = self_row.getAttribute("data-database-id")
    //2.Step: delete in data base
    let bearer_str  = get_jwt();
    fetch("/data_today", {
        mode:"cors",
        method: "delete",
        headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization':bearer_str
        },

      //make sure to serialize your JSON body
      body: JSON.stringify({
        data:  db_id
      })
    })
    .then(function(response){
            //Check status code
            if(response.ok==false){
                return response.text()
            }
            else{
               self_row.parentElement.outerHTML="";
               return "ok"
            }
        })
      .then(body=>process_fetch_body(body));

}

function calculate_ratio(self_btn){
    /*
    Calculate the ratio between total steps and calories
    @args:
       self_btn(html-object)
    */
     '#1.Step: The parent element of self_btn'
     let parent = self_btn.closest("div");
     '#2.Step: The the current value of total_calorie and total_steps'
     let total_calorie_plan = parent.querySelector("#total_calorie").value;
     '#3.Step: Calculate the ratio'
     let total_steps = parent.querySelector("#total_steps").value;;
     let ratio = Math.round(total_calorie_plan/total_steps*10000,2)/100

     let cal_output = document.querySelector("#cal_output")
     '3.1.Step: Check ratio'
     if(ratio>5.6){

        cal_output.style.color="red"
        cal_output.innerHTML = ratio +" Over 5.6. BAD, go more steps!!"
     }
     else if (ratio>4.8){
             cal_output.style.color="green"
        cal_output.innerHTML = ratio +" very good!"
     }
     else if (ratio<4.8){
             cal_output.style.color="red"
        cal_output.innerHTML = ratio +" Lower then 4.8, eat more!!"
     }


}

function hide_motivation_div(self_div){
    /*
    Hide the motivation div
    */
    self_div.style.display="none"


}
function hide_bulk_div(x){
    /*
    @description:
        Hides the bulk_div
    @args:
        x(html-object): e.g. p tag #close_bulk_div
    */
    x.closest("#bulk_div").style.display="none"

}
function show_bulk_add(id_div){
    /*
    Show the bulk div
    */
    let bulk_div = document.querySelector("#"+id_div);
    if ((bulk_div.style.display=="")||bulk_div.style.display=="none")
        bulk_div.style.display="block"
    else if(bulk_div.style.display=="block"){
        bulk_div.style.display=""
        inject_array_db()
    }
}
function show_motivation_div(id_div){
    /*
    Show the motivation div
    */

     document.querySelector("#"+id_div).style.display="block"



    let mot_content=[
        "Traumgewicht: 80 kg=> NICHT MEHR 10 kg!"+
         "Sondern nur noch 4 kg!",
        `
        Warum jetzt ?
        Damit ich endlich den Kreislauf aus Diäten durchbreche!<br />
        Es muss endlich ein Ende haben! Seit rund 360 Tagen<br />
        machen ich jetzt schon erfolgslos Diet!<br />
        Das ist das erste Mal das ich wieder unter 85 kg bin!<br />
        `,
        "Endlich neue Kleider kaufen können!",
        "Schlankes Gesicht, meinte mein Papa",
        "Schlaffe Haut!",
    ]
    let rand_int = Math.floor((Math.random() * mot_content.length))

    let motivation_txt = document.querySelector("#motivation_txt")
    motivation_txt.innerHTML = mot_content[rand_int]

}

function replaceAll(str, find, replace) {
  //Source: https://stackoverflow.com/questions/1144783/how-to-replace-all-occurrences-of-a-string
  return str.replace(new RegExp(find, 'g'), replace);
}

function addCalorie(){
   /*
   @description:
    Add the food_cal to the input_cal based on selected input_value food_name
   */

   //1.Step: Query input_name and the corresponding  datalist
  const Value = document.querySelector('#input_name').value;
  const datalist = document.querySelector("#list_name")
  //2.Step: If emtpy the function should stop
  if(!Value) return;
  //
  //2.
  const food_cal = datalist.querySelector('option[value="' + Value + '"]').text
  const input_cal = document.querySelector("#input_cal")
  input_cal.value = food_cal
}


function jwt_localStorage(){
    /*
    @describe:
        Saves the jwt to the localStorage
    @return:
        Nothing
    */
    //1.Step: Gets the current url
    let url_string  = window.location.href
    //2.Step: Check if a token is in url and save it to the local storage
    if(url_string.includes("access_token")==true){

        const fragment = window.location.hash.substr(1).split('&')[0].split('=');
        let access_token = fragment[1]
        localStorage.setItem('jwt', `bearer ${access_token}`);
        console.log("Saved jwt to localStorage")
    }


}

function get_jwt(localStorage_jwt=true){
    /*
    @describe:
        Gets the jwt from url and return as string with Bearer
    @return:
        str:(str)
    */

    if(localStorage_jwt == false){
        let url_string  = window.location.href
        const fragment = window.location.hash.substr(1).split('&')[0].split('=');
        let access_token = fragment[1];
        return `bearer ${access_token}`
    }
    else{
        return localStorage["jwt"]
    }


}

