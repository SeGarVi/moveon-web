///Global variables

// Function to retrieve information and send a 
function testCode(key, value) {
    var info = '{"osmline": {"'+ key +'": '+value+'}}';
    var url  = window.location.href;
    $( ".code" ).addClass( "is-loading" );
    $( "input[type='code']" ).addClass( "is-loading" );
    $.post( url, info, 
        function( data ) {
            if (key === 'accept') { window.location = url; }
            else{ window.location = url + value; }
        }
    ).fail(
        function(data){
            alert("Error " + data.status + " " + url + " " + info);
        }
    );
    $( ".code" ).removeClass( "is-loading" );
    $( "input[type='code']" ).removeClass( "is-loading" );
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
    ///$( " form ").append('<div id="timetable-column-' + timetableColumn_counter + '" class="moveon-company timetable--form"></div>');
    $( " #timetable--form").append('<fieldset id="timetable-column-' + timetableColumn_counter + '"  class="moveon-company"></fieldset>');
    for (var i = 0; i < serialize_ids.length; i++) {
        $( "#timetable-column-" + timetableColumn_counter).append('<input class="input" name="time-' + timetableColumn_counter + '-' + serialize_ids[i] + '" type="text"/><br>');
    }
    timetableColumn_counter++;
}

function send_timetableCalculation(route_id, stretch_id) {
    var mean_speed = $( "input[name='mean_speed']" ).val();

    /*Only for non empty values*/
    var timetable_form_empties = $('form').serializeArray();
    for (i=0; i<timetable_form_empties.length;) {
        var obj = timetable_form_empties[i]
        if(obj.value == "") {
            timetable_form_empties.splice(i, 1);
        } else {
            i++;
        }
    }
    
    var timetable = {
        "mean_speed":mean_speed,
        "times": timetable_form_empties,
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
            $("input[name="+time.name+"]").val(time.value);
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
        for (i=0; i<timetable_form_empties.length;) {
            var obj = timetable_form_empties[i]
            if(obj.value == "") {
                timetable_form_empties.splice(i, 1);
            } else {
                i++;
            }
        }

        var timetable = {
            "mean_speed":mean_speed,
            "times": timetable_form,
            "route_id": route_id,
            "day": days,
            "start": start,
            "end": end
        };

        $.ajax({
          type: "PUT",
          url: "/moveon/stretches/"+stretch_id,
          data: JSON.stringify(timetable)//,
          //success: console.log("success"),
          //dataType: json
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
    var res = input.match(/^([01]?[0-9]|2[0-3]):[0-5][0-9]/);
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