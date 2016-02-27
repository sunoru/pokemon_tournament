/**
 * Created by sunoru on 2014/10/3.
 */

$(document).ready(function(){
    $("#round-standings").click(function () {
        $("#result-standings").removeClass("control-hidden");
        $("#result-brackets").addClass("control-hidden");
    });
    $("#round-brackets").click(function () {
        $("#result-standings").addClass("control-hidden");
        $("#result-brackets").removeClass("control-hidden");
    });
    hashChange()
});

function hashChange() {
    var turn_number = location.hash.substr(1);
    $("#result-standings").load(turn_number+"/standings/");
    $("#result-brackets").load(turn_number+"/bracket/");
}
window.onhashchange = hashChange;
