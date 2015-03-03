/**
 * Created by sunoru on 2014/10/4.
 */
$(document).ready(function(){
    $(".editing").keypress(function (event) {
        if (event.keyCode == 13){
            $.post("edit_name/",
            {
                name: this.value,
                playerid: this.id.substr(2),
                csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']")[0].value
            },
            function(data,status){
                md = JSON.parse(data);
                if(md.status)
                    $(".edited#p_"+md.playerid).text(md.name);
            });
        }
    });
    document.onkeydown = function (e) {
        var theEvent = window.event || e;
        var code = theEvent.keyCode || theEvent.which;
        if (code == 13) {
            $("#add_name").click();
        }
    };
});
