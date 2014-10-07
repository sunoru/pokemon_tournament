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
    hashChange()
});

function hashChange() {
    var turn_number = location.hash.substr(1);
    $("#result-standings").load(turn_number+"/standings/");
    $("#result-bracket").load(turn_number+"/bracket/");
};
window.onhashchange = hashChange
