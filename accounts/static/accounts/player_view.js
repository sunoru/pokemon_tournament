/**
 * Created by sunoru on 2016/2/16.
 */
$(document).ready(function () {
    $.get("logs", function (data, e) {
        if (e != "success")
            return;
        var single_counts = [data.single['轮空'].length, 0, 0, 0, 0];
        var swiss_counts = [data.swiss['轮空'].length, 0, 0, 0, 0];
        delete(data.single['轮空']);
        delete(data.swiss['轮空']);
        var single_logs = [];
        var swiss_logs = [];
        for (var player in data.single) {
            var log = [player, 0, 0, 0, 0];
            data.single[player].forEach(function (x) {
                log[x.status] += 1;
                single_counts[x.status] += 1;
            });
            log[4] = log[1] + log[2] + log[3];
            single_logs.push(log);
        }
        single_counts[4] = single_counts[1] + single_counts[2] + single_counts[3];
        for (var player in data.swiss) {
            var log = [player, 0, 0, 0, 0];
            data.swiss[player].forEach(function (x) {
                log[x.status] += 1;
                swiss_counts[x.status] += 1;
            });
            log[4] = log[1] + log[2] + log[3];
            swiss_logs.push(log);
        }
        swiss_counts[4] = swiss_counts[1] + swiss_counts[2] + swiss_counts[3];
        single_logs.sort(function (a, b) {
            return a[4] - b[4];
        });
        swiss_logs.sort(function (a, b) {
            return a[4] - b[4];
        });
        var log_single = $('#log-single');
        log_single.after($('<div></div>').addClass('log-logs row row-last')
            .append($('<div></div>').addClass('col-md-3 info-col').text('轮空'))
            .append($('<div></div>').addClass('col-md-2 info-col').text(single_counts[0])));
        single_logs.forEach(function (x) {
            var single_log_div = $('<div></div>').addClass('log-logs row');
            single_log_div.append($('<div></div>').addClass('col-md-3 info-col').text(x[0]));
            for (var i = 1; i <= 3; i++)
                single_log_div.append($('<div></div>').addClass('col-md-2 info-col')
                    .text(x[i] + '（' + (x[i] / x[4] * 100).toFixed(2) + '%）'));
            single_log_div.append($('<div></div>').addClass('col-md-2 info-col')
                .text(x[i]));
            log_single.after(single_log_div);
        });
        var log_swiss = $('#log-swiss');
        log_swiss.after($('<div></div>').addClass('log-logs row')
            .append($('<div></div>').addClass('col-md-3 info-col').text('轮空'))
            .append($('<div></div>').addClass('col-md-2 info-col').text(swiss_counts[0])));
        swiss_logs.forEach(function (x) {
            var swiss_log_div = $('<div></div>').addClass('log-logs row');
            swiss_log_div.append($('<div></div>').addClass('col-md-3 info-col').text(x[0]));
            for (var i = 1; i <= 3; i++)
                swiss_log_div.append($('<div></div>').addClass('col-md-2 info-col')
                    .text(x[i] + '（' + (x[i] / x[4] * 100).toFixed(2) + '%）'));
            swiss_log_div.append($('<div></div>').addClass('col-md-2 info-col')
                .text(x[i]));
            log_swiss.after(swiss_log_div);
        });
        var swiss_log_div = $('<div></div>').addClass('log-logs row');
        swiss_log_div.append($('<div></div>').addClass('col-md-3 info-col').text("合计"));
        for (var i = 1; i <= 3; i++)
            swiss_log_div.append($('<div></div>').addClass('col-md-2 info-col')
                .text(swiss_counts[i] + '（' + (swiss_counts[i] / swiss_counts[4] * 100).toFixed(2) + '%）'));
        swiss_log_div.append($('<div></div>').addClass('col-md-2 info-col')
            .text(swiss_counts[i]));
        log_swiss.after(swiss_log_div);
        var single_log_div = $('<div></div>').addClass('log-logs row');
        single_log_div.append($('<div></div>').addClass('col-md-3 info-col').text("合计"));
        for (var i = 1; i <= 3; i++)
            single_log_div.append($('<div></div>').addClass('col-md-2 info-col')
                .text(single_counts[i] + '（' + (single_counts[i] / single_counts[4] * 100).toFixed(2) + '%）'));
        single_log_div.append($('<div></div>').addClass('col-md-2 info-col')
            .text(single_counts[i]));
        log_single.after(single_log_div);
        $("#played-logs-count").text(single_counts[4] + swiss_counts[4]);
        hashChange()
    });
});

function hashChange() {
    var hash = location.hash.substr(1);
    if (hash == "logs") {
        $('.tour-logs').addClass("control-hidden");
        $('.log-logs').removeClass("control-hidden");
        $('.other-logs').addClass("control-hidden")
    } else if (hash == "others") {
        $('.tour-logs').addClass("control-hidden");
        $('.log-logs').addClass("control-hidden");
        $('.other-logs').removeClass("control-hidden")
    } else {
        $('.tour-logs').removeClass("control-hidden");
        $('.log-logs').addClass("control-hidden");
        $('.other-logs').addClass("control-hidden")
    }
}
window.onhashchange = hashChange;
