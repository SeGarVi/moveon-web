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