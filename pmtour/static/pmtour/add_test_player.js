/**
 * Created by sunoru on 2014/11/7.
 */
$(document).ready(function(){
    $("#add_name").click(function () {
        r = $("#test_name")[0].value;
        $("<option selected='selected' value='" + r + "'>" + r + "</option>").appendTo($("#players_from"));
        $("#test_name")[0].value="";
        $("#test_name")[0].focus();
    });
    document.onkeydown = function (e) {
        var theEvent = window.event || e;
        var code = theEvent.keyCode || theEvent.which;
        if (code == 13) {
            $("#add_name").click();
        }
    };
});
