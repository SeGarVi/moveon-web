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
