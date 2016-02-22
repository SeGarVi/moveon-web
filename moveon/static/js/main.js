// Function to retrieve information and send a 
function testCode(key, value) {
    var info = '{"osmline": {"'+ key +'": '+value+'}}';
    var url  = window.location.href;
    $( ".spinner" ).toggle();
    $.post( url, info, 
        function( data ) {
            $(".spinner").toggle();
            alert("Success" + url);
            if (key === 'accept') { window.location = url; }
            else{ window.location = url + value; }
        }
    ).fail(
        function(data){
            $(".spinner").toggle();
            alert("Error " + data.status + " " + url + " " + info);
        }
    );
}
/*Get GPS coordinates of the user*/
function getLocation() {

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(redirectToPosition);
    } else { 
        alert("Geolocation is not supported by this browser.");
    }
}

function redirectToPosition(position) {
    window.location=window.location.href+'stations/nearby?userpos='+position.coords.latitude+','+position.coords.longitude;
    //debug
    console.log(position.coords.latitude + "," + position.coords.longitude);
}

/*Tooggle on the icons*/
function toggleCodes(on) {
    var obj = document.getElementById('icons');

    if (on) {
        obj.className += ' codesOn';
    } else {
        obj.className = obj.className.replace(' codesOn', '');
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
    console.log(serialize_ids.length);
    for (var i = 0; i < serialize_ids.length; i++) {
        console.log(serialize_ids[i]);
        $( "#timetable-column-" + timetableColumn_counter).append('<input class="input" name="time-' + timetableColumn_counter + '-' + serialize_ids[i] + '" type="text"/><br>');
    }
    timetableColumn_counter++;
}

function send_timetableCalculation(route_id, stretch_id) {
    var mean_speed = $( "input[name='mean_speed']" ).val();
    var timetable_form_empties = $('form').serialize();
    var timetable_form = timetable_form_empties.replace(/[^&]+=\.?(?:&|$)/g, '')
    var timetable = {
        "mean_speed":mean_speed,
        "times": timetable_form,
        "route_id": route_id,
    };

    $.ajax({
      type: "PUT",
      url: "/moveon/stretches/"+stretch_id,
      data: JSON.stringify(timetable)
    });
}

function send_timetableAcceptation(route_id, stretch_id) {
    var mean_speed = $( "input[name='mean_speed']" ).val();
    var start = $( "input[name='start-date']" ).val();
    var end = $( "input[name='end-date']" ).val();
    var days = $("input[name=day]:checked").map(function () {return this.value;}).get().join(",");
    var timetable_form_empties = $('form').serialize();
    var timetable_form = timetable_form_empties.replace(/[^&]+=\.?(?:&|$)/g, '')
    var timetable = {
        "mean_speed":mean_speed,
        "times": timetable_form,
        "route_id": route_id,
        "day": days,
        "start": start,
        "end": end
    };
    console.log(timetable + " - " + start + " - " + end + " - " + days);

    $.ajax({
      type: "PUT",
      url: "/moveon/stretches/"+stretch_id,
      data: JSON.stringify(timetable)//,
      //success: console.log("success"),
      //dataType: json
    });
}