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
});
