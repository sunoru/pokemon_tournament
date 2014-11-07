/**
 * Created by sunoru on 2014/11/7.
 */
$(document).ready(function(){
    $("#add_name").click(function () {
        r = $("#test_name")[0].value;
        $("<option value='" + r + "'>" + r + "</option>").appendTo($("#players_from"));
    });
});
