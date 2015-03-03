/**
 * Created by sunoru on 2014/10/4.
 */
$(document).ready(function(){
    $(".editable").mouseover(function (event) {
        this.
    });
    document.onkeydown = function (e) {
        var theEvent = window.event || e;
        var code = theEvent.keyCode || theEvent.which;
        if (code == 13) {
            $("#add_name").click();
        }
    };
});
