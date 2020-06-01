
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

function get_misc_streak(){
  /*
  @describtion:
   Get the streak information (current streak, longsest streak, avg streak) from the db
  @args:

  @return:
    Nothing
  */
  '#1.Step: Get weight and the weight range'
  let weight = document.querySelector("#input_weight").value;
  let weight_range = document.querySelector("#weight_range").value
  let bearer_str  = get_jwt(localStorage_jwt=true);
  fetch("/misc_streak", {
        mode:"cors",
        method: "get",
        headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization':bearer_str
        },

      //make sure to serialize your JSON body
      body: JSON.stringify({
        "weight_range":  weight_range,
        "weight": weight
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
    .then(body=>console.log(body));
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