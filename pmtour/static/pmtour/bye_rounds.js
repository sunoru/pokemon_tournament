$(document).ready(function () {
  $(".submit-button").click(function () {
    const playerid = this.id.substr(2);
    const v = $(".rounds#e_" + playerid)[0].value;
    if (!confirm("确认轮空" + v + "轮？")) return;
    $.post(
      "#",
      {
        commit: this.value,
        playerid,
        value: v,
        csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']")[0].value,
      },
      function (data, status) {
        var md = JSON.parse(data);
        if (md.status) {
          alert("设置成功！");
        }
      }
    );
  });
});
