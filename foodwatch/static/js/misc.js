
var $TABLE = $('#table');
var $BTN = $('#export-btn');
var $MSG_DB= $('msg_db');

$('.table-add').click(function () {
  let current_date = new Date();
  //An explanation for "current_date.getMonth()+1" can be found https://stackoverflow.com/questions/23161366/javascript-get-current-day-and-month-issue
  let date_str = `${current_date.getDate()}/${current_date.getMonth()+1}/${current_date.getFullYear()}`
  //.Step: Set the current date
  document.querySelector("#row_hiden").outerHTML = document.querySelector("#row_hiden").outerHTML.replace("placeholder",
                                                                                                          date_str)
  var $clone = $TABLE.find('tr.hide').clone(true).removeClass('hide table-line')

  $clone.insertAfter('#header_table')
});

$('.table-remove').click(function () {
  $(this).parents('tr').detach();
});

// A few jQuery helpers for exporting only
jQuery.fn.pop = [].pop;
jQuery.fn.shift = [].shift;

$BTN.click(function () {
  var $rows = $TABLE.find('tr:not(:hidden)');
  var headers = [];
  var data = [];

  // Get the headers (add special header logic here)
  $($rows.shift()).find('th:not(:empty)').each(function () {
    headers.push($(this).text().toLowerCase());
  });

  // Turn all existing rows into a loopable array
  $rows.each(function () {
    var $td = $(this).find('td');
    var h = {};

    // Use the headers from earlier to name our hash keys
    headers.forEach(function (header, i) {
      h[header] = $td.eq(i).text().trim();
    });

    data.push(h);
  });

  // Output the result
  //$EXPORT.text(JSON.stringify(data));
  post_misc_data(data)

});

function post_misc_data(data_json){
  /*
  @describtion:
   Sends all from the provied data_json to the backend
  @args:
    data_json(json)
  @return:
    Nothing
  */
  let bearer_str  = get_jwt(localStorage_jwt=true);
  fetch("/misc_data", {
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
    })
    .then(function(response){
            //Check status code
            if(response.ok==false){
                return response.text()
            }
            else{
               return "ok"
            }
        })
    .then(body=>process_fetch_body(body));
}

function get_misc_streak(callback){
  /*
  @describtion:
   Get the streak information (current streak, longsest streak, avg streak) from the db
  @args:
    callback: remaining_days()
  @return:
    Nothing
  */
  '#1.Step: Get weight and the weight range'
  let weight = document.querySelector("#input_weight").value;
  let weight_range = document.querySelector("#weight_range").value

  fetch(`/misc_streak/${weight}/${weight_range}`,
    )
  .then((response) => {
        return response.json();
      })
  .then((response)=>{
        //Write the msg that request was successfully
        document.querySelector("#current_streak span").innerText = response[0].current_streak;
        document.querySelector("#streak_attemps span").innerText = response[0].streak_attempts;
        document.querySelector("#longest_streak span").innerText = response[0].longest_seq;
        document.querySelector("#avg_streak span").innerText = response[0].avg_streak;
        callback();
    });


}

function highlight_row(){
    /*
    @description:
        Change the background color of a cell if the value is in a certain range
        (basied on value of weight and range)

    */
    //1.Step: Find the limit
    let input_weight = parseFloat(document.querySelector("#input_weight").value);
    let weight_range = parseFloat(document.querySelector("#weight_range").value);
    //1.1.Step: Define the upper and lower limit
    let upper_limit = input_weight + weight_range;
    let lower_limit = input_weight - weight_range;

    //1.Step: Find the table body
    let table_body = document.querySelector(".table tbody");
    //2.Step
    for (let el of table_body.children){
        //Check if header row
        if(el.id=="header_table"){
            continue
        }
        ///2.1.Step: Always the third cell contains the weight value
        let weight_value = parseFloat(el.querySelectorAll("td")[2].innerText);
        if (weight_value<=upper_limit && weight_value>=lower_limit){
            el.querySelectorAll("td")[2].style.backgroundColor="#33a7c1a6"
        }
    }
}

function weight_statistics(){
       /*
        Get the statics information about weight from db. (Avg. Mean for 7,14,30 days)
       */
      //1.Step: fetch "misc_weigth

      fetch('/misc_weigth')
      .then(response=>response.json())
      .then(response=>{
            [7,14,30].forEach(day_range=>{
                    ["mean","max","min"].forEach(static_op=>{
                    document.querySelector(`#weight_${day_range}_${static_op}`).innerText = response[`weight_${day_range}_${static_op}`]
                    })
                })
            })

}

function remaining_days(goal=66){
    /*
    Function calculate the difference between the goal and another number
    @args:
        goal(int): e.g. 66
    */
    //1.Step: Get the current streak
    let current_s = document.querySelector("#current_streak span").innerText;
    //2.Step: Calculate the remaining days
    let remaining_days = goal - current_s;
    //3.Step: Update the <p><span> remaining_days element
    document.querySelector("#remaining_days span").innerText = remaining_days;
}

function remove(x){
  /*
  @describtion:
    Removes the clicked data row from the database and front-end
  @args:
    x(html-element)
  @return:
    Nothing
  */
  let db_id = $(x).parent().parent()[0].querySelector(".db_id").innerText
  let bearer_str  = get_jwt(localStorage_jwt=true);
      fetch("/misc", {
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
               return "ok"
            }
        })
    .then(body=>process_fetch_body(body));


}