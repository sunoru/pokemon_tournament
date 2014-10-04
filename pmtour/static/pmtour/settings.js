/**
 * Created by sunoru on 2014/10/3.
 */

$(document).ready(function(){
    $("#tour_type").change(function () {
        if (this.selectedIndex == 0 || this.selectedIndex == 2) {
            $("#control-turns").removeClass("control-disabled");
            $("#tour_turns")[0].disabled = false;
        }else{
            $("#control-turns").addClass("control-disabled");
            $("#tour_turns")[0].disabled = true;
        }
        if (this.selectedIndex == 2){
            $("#control-elims").removeClass("control-disabled");
            $("#tour_elims")[0].disabled = false
        }else{
            $("#control-elims").addClass("control-disabled");
            $("#tour_elims")[0].disabled = true;
        }
    });
    $("#tour_get_turns").click(function () {
        $.get("get_turns", function(data, status){
            if(status == "success")
                $("#tour_turns")[0].value = data;
        });
        if (this.selectedIndex == 2)
            $.get("get_elims", function(data, status){
                if(status == "success")
                    $("#tour_elims")[0].value = data;
            });
    })
});
