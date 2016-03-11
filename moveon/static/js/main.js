///Global variables

// Function to retrieve information and send a 
function getOSMLine(key, value, url) {
    var info = '{"osmline": {"'+ key +'": '+value+'}}';
    $( "button" ).addClass( "is-loading" );
    $.post( url, info, 
        function( data ) {
            if (key === 'accept') { window.location = url; }
            else{ window.location = url + value; }
            $( "button" ).removeClass( "is-loading" );
        }
    ).fail(
        function(data){
            alert("Error " + data.status + " " + url + " " + info);
            $( "button" ).removeClass( "is-loading" );
        }
    );
}

/*Get GPS coordinates of the user*/
function getLocationRedirection(url) {
    function redirectToPosition(position) {
        window.location= url+'?userpos='+position.coords.latitude+','+position.coords.longitude;
        console.log('redirected to: ' + url+'?userpos='+position.coords.latitude+','+position.coords.longitude);
    }

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(redirectToPosition);
    } else { 
        alert("Geolocation is not supported by this browser.");
    }
}



/*Validate email*/
function validateEmail(email) {
    var re = /\S+@\S+\.\S+/;
    return re.test(email);
}

/*Opens a dialog page to insert the email to recover the password*/
function recover_password() {
    var email=window.prompt("Please enter your email");
    if (validateEmail(email)) {
        window.alert("An email has been sent to " + email);
    } else {
        window.alert("Your email was invalid -> " + email);
    }
}

/*Show signup*/
function show_signup() {
    $( ".log-card.is-hidden" ).removeClass( "is-hidden" );
    $( ".login-card" ).addClass( "is-hidden" );
}

var timetableColumn_counter = 1;
/*Timetable add form column*/
function add_timetableColumn(serialize_ids) {
    $( " #timetable--form").append('<fieldset id="timetable-column-' + timetableColumn_counter + '"  class="moveon-company"></fieldset>');
    for (var i = 0; i < serialize_ids.length; i++) {
        $( "#timetable-column-" + timetableColumn_counter).append('<input class="input" name="time-' + timetableColumn_counter + '-' + serialize_ids[i] + '" type="text"/>');
    }
    timetableColumn_counter++;
}

function send_timetableCalculation(route_id, stretch_id) {
    var mean_speed = $( "input[name='mean_speed']" ).val();
    /*Only for non empty values*/
    var timetable_form_empties = $('form').serializeArray();
    
    classified_times = []
    for (i=0; i<timetableColumn_counter; i++) {
    	classified_times.push([]);
    }
    
    for (i=0; i<timetable_form_empties.length;) {
        var obj = timetable_form_empties[i]
        if(obj.value == "") {
            timetable_form_empties.splice(i, 1);
        } else {
        	col = parseInt(obj.name.split("-")[1]);
        	station_id = parseInt(obj.name.split("-")[2]);
        	
        	hour_str=obj.value.split(":")[0];
        	min_str=obj.value.split(":")[1];
        	
        	hour = (parseInt(hour_str)%24) * 60 * 60; 
        	min = parseInt(min_str) * 60;
        	
        	classified_times[col].push(
        			{
        				"station_id" : station_id,
        				"time" : hour + min
        			});
        	
            i++;
        }
    }
    
    prefix = obj.name.split("-")[0];
    data = {"prefix" : prefix, "time_list" : classified_times}
    
    var timetable = {
        "mean_speed":parseFloat(mean_speed)/3.6,
        "times": data,
        "route_id": route_id
    };

    $.ajax({
      type: "PUT",
      url: "/moveon/stretches/"+stretch_id,
      data: JSON.stringify(timetable),
      success: function(data) {
        decoded_data = JSON.parse(data);
        for (index in decoded_data) {
            time = decoded_data[index];
            hours = parseInt(time.value / 60 / 60)
            minutes = parseInt(time.value / 60) % 60
            final_value = hours.toString() + ":";
            
            if (minutes < 10) {
            	final_value += "0" + minutes.toString()
            } else {
            	final_value += minutes.toString()
            }
            
            $("input[name="+time.name+"]").val(final_value);
        }
      }
    });
}

function verify_last(var1, selector, alert_text){
    if (var1==""){
        $( selector ).addClass("redborder");
        alert(alert_text);
        return false;
    }else{
        $( selector ).removeClass("redborder");
        return true;
    }
}

function send_timetableAcceptation(route_id, stretch_id) {
    var days = $("input[name=day]:checked").map(function () {return this.value;}).get().join(",");
    var start = $( "input[name='start-date']" ).val();
    var end = $( "input[name='end-date']" ).val();
    var send = true;

    send = verify_last(days, '.moveon-company_day', 'Please, select at least one day in the week checkbox.');
    send = verify_last(start, 'input[name="start"]', 'Please, select the start date for the timetable');
    send = verify_last(end, 'input[name="end"]', 'Please, select the end date for the timetable');

    if (send) {
        var mean_speed = $( "input[name='mean_speed']" ).val();
        /*Only for non empty values*/
        var timetable_form_empties = $('form').serializeArray();

        var stationSignatureByCol=[]
        var timeSignatureByCol=[]
        var initialTimesPerCol=[]
        for (i=0; i<timetableColumn_counter; i++) {
        	stationSignatureByCol.push("");
        	timeSignatureByCol.push("");
        }
        
        var previousCol = -1;
        var first
        for (i=0; i<timetable_form_empties.length;) {
            var obj = timetable_form_empties[i]
            if(obj.value != "") {
            	var col = parseInt(obj.name.split("-")[1]);
            	var station_id_str = parseInt(obj.name.split("-")[2]);
            	var station_id = parseInt(station_id_str);
            	
            	var hour_str=obj.value.split(":")[0];
            	var min_str=obj.value.split(":")[1];
            	
            	var hour = (parseInt(hour_str)%24) * 60 * 60; 
            	var min = parseInt(min_str) * 60;
            	
            	var timestamp = hour + min;
            	
            	if (col != previousCol) {
            		initialTimesPerCol.push(timestamp)
            	}
            	var previousCol = col;
            	
            	var timeDifference = timestamp - initialTimesPerCol[col];
            	
            	stationSignatureByCol[col] = stationSignatureByCol[col].concat(station_id_str).concat(".");
            	timeSignatureByCol[col] = timeSignatureByCol[col].concat(timeDifference.toString()).concat(".");
            	
                i++;
            }
        }
        
        var initialtimesPerStretch={};
        for (i=0; i<timetableColumn_counter; i++) {
        	var stretchSignature = stationSignatureByCol[i].concat("-").concat(timeSignatureByCol[i]);
        	
        	if (!(stretchSignature in initialtimesPerStretch)) {
        		initialtimesPerStretch[stretchSignature] = [];
        	}
        	initialtimesPerStretch[stretchSignature].push(initialTimesPerCol[i])
        }
        
        var timetable = {
            "stretch_info_list": initialtimesPerStretch,
            "route_id": route_id,
            "day": days,
            "start": start,
            "end": end
        };

        $.ajax({
          type: "PUT",
          url: "/moveon/stretches/"+stretch_id,
          data: JSON.stringify(timetable),
          statusCode: {
            200: function() { alert( "It worked! 200 " ); },
            201: function() { alert( "It worked! 201 " ); },
            404: function() { alert( "Something was missing" ); }
          }
        });
    }
}

var verification = [];
function verify(class_name, res) {
    if (res==null) {
        $( "input[name='"+class_name+"']" ).addClass("redborder");
        verification.push(class_name);
        $( "button" ).prop('disabled', true);
    }else{
        $( "input[name='"+class_name+"']" ).removeClass("redborder");
        verification.splice(verification.indexOf(class_name), 1);
        if (verification.length==0) {
            $( "button" ).prop('disabled', false);
        }
    }
}
function verify_time(class_name) {
    var input = $( "input[name='"+class_name+"']" ).val();
    var res = input.match(/^(([01]?[0-9]|2[0-3]):[0-5][0-9]|\s*)$/);
    verify(class_name, res);
}

function verify_speed(class_name) {
    var input = $( "input[name='"+class_name+"']" ).val();
    var res = input.match(/^[01]?[0-9]?[0-9]\.?[0-9]?[0-9]?/);
    verify(class_name, res);
}

function verify_date(class_name) {
    var input = $( "input[name='"+class_name+"']" ).val();
    var res = input.match(/^[0-9]{2}\/[0-9]{2}\/[0-9]{4}/);
    verify(class_name, res);
}

function csv_json(serialize_ids) {
    $("#csv").parse({
        skipEmptyLines: true,
        config: {
            complete: function(results, file) {
                //Calculate total of cycles before to avoid inconsistent results
                var total = results.data[0].length - timetableColumn_counter;
                for (var i = 0; i < total; i++) {
                    add_timetableColumn(serialize_ids);
                }
                //Writing in the user timetable
                for (var i = 0; i < results.data.length; i++) {
                    for (var j = 0; j < results.data[i].length; j++) {
                        $("input[name=time-"+ j + "-" + serialize_ids[i] + "]").val(results.data[i][j]);
                        verify_time("time-"+ j + "-" + serialize_ids[i]);
                    }
                }
            }
        },
        complete: function() {
            console.log("All times added!");
        }
    });
}

