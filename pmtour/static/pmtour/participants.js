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
                var md = JSON.parse(data);
                if(md.status)
                    $(".edited#p_"+md.playerid).text(md.name);
            });
        }
    });
    $(".exit-button").click(function(){
        $.post("#",
            {
                method: this.value,
                playerid: this.id.substr(2),
                csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']")[0].value
            },
            function(data,status){
                var md = JSON.parse(data);
                if(md.status);
                    //$(".exit-button#p_"+md.playerid).remove();
                    //TODO: exit
            });
    })
});
