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
                if (md.status)
                    $(".edited#p_"+md.playerid).text(md.name);
            });
        }
    });
    $(".exit-button").click(function(){
        if (!confirm("确认退出？")) return;
        $.post("#",
            {
                commit: this.value,
                playerid: this.id.substr(2),
                csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']")[0].value
            },
            function(data,status){
                var md = JSON.parse(data);
                if (md.status) {
                    var b = $(".exit-button#q_" + md.playerid);
                    b.text("已退出");
                    b.prop("disabled", true);
		}
            });
    })
});
