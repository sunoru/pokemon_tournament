/**
 * Created by sunoru on 2014/10/3.
 */

$(document).ready(function(){
    $("#round-standing").click(function () {
        $("#result-standings").removeClass("control-hidden");
        $("#result-bracket").addClass("control-hidden");
    })
    $("#round-bracket").click(function () {
        $("#result-standings").addClass("control-hidden");
        $("#result-bracket").removeClass("control-hidden");
    })
});

window.onhashchange = function () {
    var turn_number = location.hash.substr(1);
    $.get(turn_number+"/standings/", function(data, status){
        if(status == "success")
            $("#result-standings").load(data)
    });
    $.get(turn_number+"/bracket/", function(data, status){
        if(status == "success")
            $("#result-bracket").load(data)
    });
};
