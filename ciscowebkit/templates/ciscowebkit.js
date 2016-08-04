{{ pfm }}

$(document).ready(function() {
	show_dashboard();
});

var now_feature = null; 
var now_url = null;
var now_cmd = null;
var now_sched = null;
var pwr_sched = false;
var spinner = null;
var prev_html_md5 = null;

function pwr_sched_toggle() {
	if (pwr_sched == true) {
		pwr_sched = false;
		document.getElementById("cw-progress-bar").innerHTML = '<div class="progress-bar progress-bar-danger" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width:100%;"><span class="sr-only">100% Complete</span></div>';
	} else {
		pwr_sched = true;
		do_scheduler();
	}
}

function set_sched() {
	if (now_feature["_tick"] > 0) { now_sched = {tick: now_feature["_tick"], exp: now_feature["_tick"]}; }
	else { now_sched = null; }
}

function del_sched() {
	now_sched = null;
}

function do_scheduler() {
	if (pwr_sched == true) {
		if (now_sched != null) {
			sched = now_sched;
			sched["exp"] = sched["exp"] - 500;
			var pct = ((sched["tick"] - sched["exp"]) * 100) / sched["tick"]
			if (pct >= 100) { document.getElementById("cw-progress-bar").innerHTML = '<div class="progress-bar progress-bar-info" role="progressbar" aria-valuenow="' + pct + '" aria-valuemin="0" aria-valuemax="100" style="width:' + pct + '%;"><span class="sr-only">' + pct + '% Complete</span></div>'; }
			else { document.getElementById("cw-progress-bar").innerHTML = '<div class="progress-bar progress-bar-success" role="progressbar" aria-valuenow="' + pct + '" aria-valuemin="0" aria-valuemax="100" style="width:' + pct + '%;"><span class="sr-only">' + pct + '% Complete</span></div>'; }
			if (sched["exp"] <= 0) {
				sched["exp"] = sched["tick"];
				$.ajax({
			        url: now_url,
			        async: false,
			        dataType: "json",
			        success: function(data) { show_ux(data); },
					error: function(e) { show_error(e); }
			    });
			}
		} else { document.getElementById("cw-progress-bar").innerHTML = '<div class="progress-bar progress-bar-info" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width:100%;"><span class="sr-only">100% Complete</span></div>'; }
		setTimeout(do_scheduler, 500);
	}
}

function show_spinner() {
	if (spinner == null) {
		spinner = new Spinner({length: 40, width: 30, radius: 70, color: '#fff', speed: 2, top: '45%'}).spin()
		$('#cw-spinner').fadeTo(0, 1, function() {
			document.getElementById("cw-click-guard").style.display = "block";
			cw_spinner = document.getElementById("cw-spinner");
			cw_spinner.appendChild(spinner.el);
			cw_spinner.style.display = "block";
		});
	}
}

function hide_spinner() {
	if (spinner != null) {
		$('#cw-spinner').fadeTo(50, 1).fadeTo(250, 0, function() {
			cw_spinner = document.getElementById("cw-spinner");
			cw_spinner.style.display = "none";
			cw_spinner.innerHTML = "";
			delete spinner;
			spinner = null;
			document.getElementById("cw-click-guard").style.display = "none";
		});
	}
}

function clear_products() {
	var pnavs = document.getElementsByClassName("cw-pnav");
	for (var i=0, pnav; pnav=pnavs[i]; i++) { pnav.classList.remove("cw-pnav-active"); }
	var fnavs = document.getElementsByClassName("cw-fnav");
	for (var i=0, fnav; fnav=fnavs[i]; i++) { fnav.style.display = "none"; }
}

function clear_features() {
	var pages = document.getElementsByClassName("cw-page");
	for (var i=0, page; page=pages[i]; i++) { page.style.display = "none"; }
	var fnav_items = document.getElementsByClassName("cw-fnavitem");
	for (var i=0, fnav_item; fnav_item=fnav_items[i]; i++) { fnav_item.classList.remove("cw-fnavitem-active"); }
}

function active_feature(code) {
	document.getElementById("cw-page-" + code).style.display = "block";
	document.getElementById("cw-fnav-" + code).classList.add("cw-fnavitem-active");
}

function show_dashboard() {
	clear_products();
	clear_features();
	document.getElementById("cw-feature-page").style.display = "none";
	document.getElementById("cw-page-dashboard").style.display = "block";
	recv_view(pfm["dashboard"], null, pfm["dashboard"]["_url"]);
}

function show_product(code) {
	clear_products();
	document.getElementById("cw-page-dashboard").style.display = "none";
	document.getElementById("cw-feature-page").style.display = "block";
	document.getElementById("cw-pnav-" + code).classList.add("cw-pnav-active");
	document.getElementById("cw-fnav-" + code).style.display = "block";
	show_feature(code, '');
}

function show_feature(code, cmd) {
	clear_features();
	if (code != '') { feature = pfm[code]; }
	else { feature = now_feature; }
	document.getElementById("cw-page_title").innerHTML = feature["_title"] + " <small> " + feature["_desc"] + "</small>";
	active_feature(feature["_code"]);
	recv_view(feature, cmd, feature["_url"] + cmd);
}

function show_error(e) {
	del_sched();
	document.getElementById("cw-page_title").innerHTML = "Internal Error <small> " + e + "</small>";
	hide_spinner();
}

function get_cookie(c_name)
{
	if (document.cookie.length > 0) {
		c_start = document.cookie.indexOf(c_name + "=");
		if (c_start != -1) {
			c_start = c_start + c_name.length + 1;
			c_end = document.cookie.indexOf(";", c_start);
			if (c_end == -1) c_end = document.cookie.length;
			return unescape(document.cookie.substring(c_start,c_end));
		}
	}
	return "";
}

function recv_view(feature, cmd, url) {
	show_spinner();
	del_sched();
	now_feature = feature;
	now_cmd = cmd;
	now_url = url;
	var get_processing = function () {
		$.ajax({
	        url: now_url,
	        async: false,
	        dataType: "json",
	        success: function(data) { show_ux(data); },
	        error: function(e) { show_error(e); }
	    });
	}
	set_sched();
	setTimeout(get_processing, 0);
}

function send_form(data) {
	show_spinner();
	var post_processing = function () {
		$.ajax({
			type: "POST",
			url: now_url,
			contentType: "application/json; charset=utf-8",
			async: false,
			headers: { "X-CSRFToken": get_cookie("csrftoken") },
			dataType: "json",
			data: JSON.stringify(data),
			success: function(data) { show_ux(data); },
			error: function(e) { show_error(e); }
		});
	}
	setTimeout(post_processing, 0);
}

function del_data(id) {
	show_spinner();
	var del_processing = function () {
		$.ajax({
			type: "DELETE",
			url: now_url,
			contentType: "application/json; charset=utf-8",
			async: false,
			headers: { "X-CSRFToken": get_cookie("csrftoken") },
			dataType: "json",
			data: id,
			success: function(data) { show_ux(data); },
			error: function(e) { show_error(e); }
		});
	}
	setTimeout(del_processing, 0);
}



//////////////////// UX Render Functions ////////////////////

function show_ux(data) {
	var code = now_feature["_code"];
	if (prev_html_md5 != data["_md5"]) {
		document.getElementById("cw-page-" + code).innerHTML = data["_html"];
		prev_html_md5 = data["_md5"];
	}
	try {
		window["show_ux_" + data["_ux"]](data);
	} catch (e) {
		console.log(e);
		show_error(e);
	}
	hide_spinner();
}

///////////////////////// UX Basic //////////////////////////
function show_ux_none(data) {}
function show_ux_empty(data) {}
function show_ux_form(data) {}
function show_ux_error(data) {
	document.getElementById("cw-page_title").innerHTML = "Internal Error";
	window["show_ux_infodoc"](data)
}

function show_ux_layout(data) {
	var rows = data["rows"];
	for (var i=0, row; row=rows[i]; i++) {
		window["show_ux_" + row["_ux"]](row)
	}
}

function show_ux_layout_row(data) {
	var cols = data["cols"];
	for (var i=0, col; col=cols[i]; i++) {
		window["show_ux_" + col["_ux"]](col)
	}
}

function show_ux_layout_col(data) {
	var view = data["view"];
	window["show_ux_" + view["_ux"]](view)
}

function show_ux_panel(data) {
	var view = data["view"];
	window["show_ux_" + view["_ux"]](view);
}

function show_ux_plain(data) {
	var view = data["view"];
	window["show_ux_" + view["_ux"]](view);
}

function show_ux_text(data) {
	document.getElementById("cw-view-" + data["_id"]).innerHTML = data["text"];
}

function show_ux_vlist(data) {
	var items = data["item"];
	var html = '';
	for (var i=0, item; item=items[i]; i++) {
		html += '<a' + item["link"]
		if (now_cmd == item["cmd"]) { html += ' class="list-group-item active">'; }
        else { html += ' class="list-group-item">'; }
        if (item["badge"] != null) { html += '<span class="badge">' + item["badge"] + '</span>'; }
        if (item["icon"] != null) { html += '<i class="fa fa-fw ' + item["icon"] + '"></i>'; }
        html += item["title"] + '</a>';
	}
	document.getElementById("cw-view-" + data["_id"]).innerHTML = html;
}

function show_ux_hlist(data){
	var items = data["item"];
	var html = '';
	for (var i=0, item; item=items[i]; i++) {
		html += '<button type="button"' + item["link"]
        if (now_cmd == item["cmd"]) { html += ' class="btn btn-default active">'; }
        else { html += ' class="btn btn-default">'; }
        if (item["badge"] != null) { html += '<span class="badge">' + item["badge"] + '</span>'; }
        if (item["icon"] != null) { html += '<i class="fa fa-fw ' + item["icon"] + '"></i>'; }
        html += item["title"] + '</button>';
	}
	document.getElementById("cw-view-" + data["_id"]).innerHTML = html;
}

function show_ux_infoblock(data) {
	var html = '<div class="alert alert-info alert-dismissable">';
	html += '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>';
	html += '<i class="fa ' + data["icon"] + '"></i><strong> ' + data["title"] + ' </strong>' + data["msg"] + '</div>';
	document.getElementById("cw-view-" + data["_id"]).innerHTML = html;
}

function show_ux_infopanel(data) {
	var html = '<div class="panel panel-' + data["panel"]+ '"><div class="panel-heading"><div class="row"><div class="col-xs-3">';
	html += '<i class="fa ' + data["icon"] + ' fa-5x"></i></div><div class="col-xs-9 text-right">';
	html += '<div class="huge">' + data["count"] + '</div><div>' + data["title"] + '</div></div></div></div><a' + data["link"] + '>';
	html += '<div class="panel-footer"><span class="pull-left">' + data["desc"] + '</span>';
	html += '<span class="pull-right">View Details <i class="fa fa-arrow-circle-right"></i></span><div class="clearfix"></div></div></a></div>';
	document.getElementById("cw-view-" + data["_id"]).innerHTML = html;
}

function show_ux_infodoc(data) {
	document.getElementById("cw-view-" + data["_id"]).innerHTML = data["doc"];
}

function show_ux_table(data) {
	var table = document.getElementById("cw-view-" + data["_id"]);
	var html = '<table id="cw-view-T-' + data["_id"] + '"class="table table-bordered table-hover' + (data["_stripe"] ? ' table-striped' : '') + '"' + data["_link"] + '><thead><tr role="row">';
    var heads = data["heads"];
    for (var i=0, head; head=heads[i]; i++) { html += "<th>" + head + "</th>"; }
    html += "</tr></thead><tbody>";
    var recs = data["recs"];
    for (var i=0, rec; rec=recs[i]; i++) {
        html += "<tr" + rec["type"] + rec["link"] + ">";
        for (var j=0, col; col=rec["cols"][j]; j++) {
        	if (j == 0) { html += "<td>" + rec["did"] + col + "</td>"; }
        	else { html += "<td>" + col + "</td>"; }
        }
        html += "</tr>";
    }
    html += "</tbody></table>";
    table.innerHTML = html
    
    var dt = $("#cw-view-T-" + data["_id"]).DataTable({
        dom: 'Bfrtip',
        lengthMenu: [
            [ 10, 25, 50, -1 ],
            [ '10 rows', '25 rows', '50 rows', 'Show all' ]
        ],
        buttons: ['pageLength', 'colvis', 'excelHtml5', 'pdfHtml5', 'print'],
        search: { "regex": false },
        destroy: true
    });
    table.style.width = "100%";
}

function show_ux_ctst_line(data) {
	try { var dlen = data["series"][0].length; } catch(e) { return null; }
    var option = {
            showArea: false,
            showPoint: true,
            fullWidth: true,
            height: 200,
            axisX: { labelInterpolationFnc: function(value) { return value.slice(11,16); } },
            axisY: {onlyInteger: true},
            chartPadding: {right: 40},
            plugins: [Chartist.plugins.tooltip()]
        }
    for (var key in data["opts"]) { option[key] = data["opts"][key]; }
    var chart = new Chartist.Line(
    		document.getElementById("cw-view-" + data["_id"]),
    		{labels: data["labels"], series: data["series"]}, 
    		option);
    if (data["anima"] == true) {
	    chart.on('draw', function(ct) {
	        if(ct.type === 'line' || ct.type === 'area') {
	            ct.element.animate({opacity:{begin:(200/dlen)*ct.index+300,dur:1000,from:0,to:1}});
	        } else if(ct.type === 'point') {
	            ct.element.animate({
	            	x1:{begin:(300/dlen)*ct.index,dur:200,from:ct.x-200,to:ct.x,easing:'easeOutQuart'},
	                opacity:{begin:(300/dlen)*ct.index,dur:200,from:0,to:1,easing:'easeOutQuart'}
	            });
	        }
	    });
    }
}

function show_ux_ctst_area(data) {
	try { var dlen = data["series"][0].length; } catch(e) { return null; }
    var option = {
            showArea: true,
            showPoint: true,
            fullWidth: true,
            height: 200,
            axisX: { labelInterpolationFnc: function(value) { return value.slice(11,16); } },
            axisY: {onlyInteger: true},
            chartPadding: {right: 40},
            plugins: [Chartist.plugins.tooltip()]
        }
    for (var key in data["opts"]) { option[key] = data["opts"][key]; }
    var chart = new Chartist.Line(
    		document.getElementById("cw-view-" + data["_id"]),
    		{labels: data["labels"], series: data["series"]}, 
    		option);
    if (data["anima"] == true) {
    	chart.on('draw', function(ct) {
            if(ct.type === 'line' || ct.type === 'area') {
                ct.element.animate({
                    d:{begin:(200/dlen)*ct.index+300,dur:500,from:ct.path.clone().scale(1,0).translate(0,ct.chartRect.height()).stringify(),to:ct.path.clone().stringify(),easing:Chartist.Svg.Easing.easeOutQuint},
                    opacity:{begin:(200/dlen)*ct.index+300,dur:500,from:0,to:1}
                });
            } else if(ct.type === 'point') {
                ct.element.animate({
                    y1:{begin:(300/dlen)*ct.index,dur:200,from:ct.y+200,to:ct.y,easing:'easeOutQuart'},
                    opacity:{begin:(300/dlen)*ct.index,dur:200,from:0,to:1,easing:'easeOutQuart'}
                });
            }
        });
    }
}

function show_ux_ctst_bar(data) {
    var option = {
        fullWidth: true,
        height: 200,
        chartPadding: {right: 40},
        axisX: {showLabel: false},
        axisY: {onlyInteger: true},
        plugins: [Chartist.plugins.tooltip()]
    }
    for (var key in data["opts"]) { option[key] = data["opts"][key]; }
    var chart = new Chartist.Bar(
    		document.getElementById("cw-view-" + data["_id"]),
    		{labels: data["labels"], series: data["series"]},
    		option)
    chart.on('draw', function(ct) {
    	if(ct.type === 'bar') {
    		ct.element.attr({
    			style: "stroke-width:" + data["size"] + ';stroke: hsl(' + Math.floor(Chartist.getMultiValue(ct.value)) + ', 50%, 50%);'
    		});
    	}
    });
    if (data["anima"] == true) {
	    chart.on('draw', function(ct) {
	        if (ct.type === 'bar') {
	            ct.element.animate({
	                y1:{begin:100*ct.index,dur:500,from:ct.y1+500,to:ct.y1,easing:Chartist.Svg.Easing.easeOutQuart},
	                y2:{begin:100*ct.index,dur:500,from:ct.y1,to:ct.y2,easing:Chartist.Svg.Easing.easeOutQuart},
	                opacity:{begin:100*ct.index,dur:500,from:0,to:1,easing:'easeOutQuart'}
	            });
	        }
	    });
    }
}

function show_ux_ctst_slide(data) {
    var option = {
        fullWidth: true,
        height: 200,
        horizontalBars: true,
        reverseData: true,
        chartPadding: {right: 40},
        axisX: {onlyInteger: true},
        axisY: {showLabel: true},
        plugins: [Chartist.plugins.tooltip()]
    }
    for (var key in data["opts"]) { option[key] = data["opts"][key]; }
    var chart = new Chartist.Bar(
    		document.getElementById("cw-view-" + data["_id"]),
    		{labels: data["labels"], series: data["series"]},
    		option).on('draw',function(ct){if(ct.type === 'bar'){ct.element.attr({style: "stroke-width:" + data["size"]});}});
    if (data["anima"] == true) {
	    chart.on('draw', function(ct) {
	    	if (ct.type === 'bar') {
	            ct.element.animate({
	                x1:{begin:100*ct.index,dur:500,from:ct.x1-500,to:ct.x1,easing:Chartist.Svg.Easing.easeOutQuart},
	                x2:{begin:100*ct.index,dur:500,from:ct.x1,to:ct.x2,easing:Chartist.Svg.Easing.easeOutQuart},
	                opacity:{begin:100*ct.index,dur:500,from:0,to:1,easing:'easeOutQuart'}
	            });
	        }
	    });
    }
}

function show_ux_ctst_donut(data) {
    var labels = data["labels"];
    var series = data["series"];
    var totalValue = 0;
    for (var i = 0; i < series.length; i++) { totalValue += series[i]["value"] }
    var tag = function(value) {
        var idx = 0;
        for (; idx < labels.length; idx++) { if (labels[idx] == value) break; }
        return value + " : " + Math.round((series[idx]["value"] * 100) / totalValue) + '%';
    };
    var option = {
        donut:true,
        fullWidth: true,
        height: 200,
        labelInterpolationFnc: tag,
        plugins: [Chartist.plugins.tooltip()]
    };
    for (var key in data["opts"]) { option[key] = data["opts"][key]; }
    var chart = new Chartist.Pie(
    		document.getElementById("cw-view-" + data["_id"]),
    		{labels: labels, series: series},
    		option);
    if (data["anima"] == true) {
	    chart.on('draw', function(ct) {
	        if(ct.type === 'slice') {
	            var pathLength = ct.element._node.getTotalLength();
	            ct.element.attr({'stroke-dasharray': pathLength + 'px ' + pathLength + 'px'});
	            var animationDefinition = {
	                'stroke-dashoffset':{begin:0,dur:800,from:-pathLength + 'px',to:'0px',easing:Chartist.Svg.Easing.easeOutQuint,fill:'freeze'}
	            };
	            ct.element.animate(animationDefinition, false);
	        }
	    });
	}
}

function show_ux_morr_line(data) {
	var view_name = "cw-view-" + data["_id"];
    document.getElementById(view_name).innerHTML = "";
    var desc = {
		element: view_name,
	    data: data["data"],
	    xkey: "tstamp",
	    ykeys: data["lines"],
	    labels: data["lines"],
	    hideHover:"auto",
	    smooth:true,
	    resize: true
    };
    for (var key in data["opts"]) { desc[key] = data["opts"][key]; }
    Morris.Line(desc);
}

function show_ux_morr_area(data) {
	var view_name = "cw-view-" + data["_id"];
    document.getElementById(view_name).innerHTML = "";
    var desc = {
		element: view_name,
	    data: data["data"],
	    xkey: "tstamp",
	    ykeys: data["lines"],
	    labels: data["lines"],
	    hideHover:"auto",
	    smooth:true,
	    resize: true
    };
    for (var key in data["opts"]) { desc[key] = data["opts"][key]; }
    Morris.Area(desc);
}

function show_ux_morr_bar(data) {
	var view_name = "cw-view-" + data["_id"];
    document.getElementById(view_name).innerHTML = "";
    var desc = {
		element: view_name,
	    data: data["data"],
	    xkey: "tstamp",
	    ykeys: data["lines"],
	    labels: data["lines"],
	    hideHover: "auto",
	    barRatio: 0.4,
	    xLabelAngle: 90,
        resize: true
    };
    for (var key in data["opts"]) { desc[key] = data["opts"][key]; }
    Morris.Bar(desc);
}

function show_ux_morr_donut(data) {
	var view_name = "cw-view-" + data["_id"];
    document.getElementById(view_name).innerHTML = "";
    Morris.Donut({
        element: view_name,
        data : data["data"],
        hideHover: "auto",
        resize: true
    });
}

function show_ux_justgage(data) {
	document.getElementById("cw-view-" + data["_id"]).innerHTML = "";
	var desc = {
		id: "cw-view-" + data["_id"],
	    value: data["value"],
	    min: data["min"],
	    max: data["max"],
	}
	for (var key in data["opts"]) { desc[key] = data["opts"][key]; }
	var g = new JustGage(desc);
}



//#3498DB