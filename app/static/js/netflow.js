
/* logistic function to transport inflow/outflow counts into a normalized ratio 
    between 0 and 1.0
    https://en.wikipedia.org/wiki/Logistic_function
*/
function logistic(x, k) {
    // k is the steepness of the curve; smaller k (in abs val) means wider curve and more sensitivity
    var base = 1 + Math.pow(Math.E, -k*x);
    return 1 / base;
}

/*  given a zone feature object and a dictionary of zone codes => flow values,
    return color 

    k is the k value in logistic functions, defaults to 0.2
*/
var color_cold = [250, 250, 250];
var color_hot = [0,0,0];
function idToColor(p, vals, k=0.2) {
    var id = p['properties'][ZONE_ID];
    var percent = logistic(vals[id], k);

    var rgb = color_hot.map(function(val, i) {
        var diff = percent * (color_hot[i]-color_cold[i]) + color_cold[i];
        return Math.round(diff);
    });

    return 'rgb(' + rgb.join() + ')';
}


function zoneClick(d, i, paths) {

}

/* when you mouseover a zone */
function borderMouseover(d, i, paths) {
    var element = svgElement.getElementById(this.id);
    element.classList.add("hovered");

    var aggFlow = "";
    var name = "";
    if (curData) {
        var id = d['properties'][ZONE_ID];
        var name = d['properties'][ZONE_NAME];

        aggFlow = curData[id];
    }
    return tooltip.style("visibility", "visible")
        .html("<span class='name'>" + name + "</span><span class='net-flow value'> Net flow: " + aggFlow + "</span>");
}

/* when you move your mouse */
function borderMousemove(d, i, paths) {
    return tooltip.style("top", (event.pageY-10)+"px").style("left",(event.pageX+10)+"px");
}

/* when you mouseout (leave) a zone */
function borderMouseout(d, i, paths) {
    var element = svgElement.getElementById(this.id);
    element.classList.remove("hovered");

    return tooltip.style("visibility", "hidden");
}


/* turn aggregate data into ones specified by hours/days */
function getData(data, hours) {
    var days = Array.apply(null, Array(7)).map(function () {return 1;});
    var title = data[0];
    var filtered = data.slice(1, data.length).filter(function(row) {
        var d = parseInt(row["day"]);
        var h = parseInt(row["hour"]);
        return days[d] && hours[h];
    });

    var res = {};
    for (var i = 0; i < filtered.length; i++) {
        var row = filtered[i];
        for (var prop in row) {
            if (row.hasOwnProperty(prop) && res[prop] != undefined) {
                res[prop] += parseInt(row[prop]);
            }
            else if (row.hasOwnProperty(prop) && res[prop] == undefined) {
                res[prop] = parseInt(row[prop]);
            }
        }
    }

    return res;

}

/* read zone flow info and update the color gradients */
function updateColors(hours) {
    d3.csv('static/netflow.csv', function(err, data) {
        if (err) return console.log(err);

        // this is global
        curData = getData(data, hours);

        if (curData == undefined) {
            console.log(data);
            return console.log("data undefined");
        }

        hideLoading();

        svg.selectAll("path")
            .attr("fill", function(p) { return idToColor(p, curData, 0.0002); } );
    });
}

function hoursChanged(endpoints) {
    var hours = Array.apply(null, Array(24)).map(function () {return 0;});
    for (var i = 0; i < 24; i++) {
        if (i >= endpoints[0] && i < endpoints[1]) { hours[i] = 1; }
    }
    showLoading();
    updateColors(hours);    
}

// DATA SLIDERS
hour_slider.noUiSlider.on('update', function() {
    document.getElementById("hours").getElementsByClassName("res")[0].innerHTML = hour_slider.noUiSlider.get().join('-');
});

hour_slider.noUiSlider.on('change', function() {
    var endpoints = hour_slider.noUiSlider.get();
    endpoints[0] = parseInt(endpoints[0]);
    endpoints[1] = parseInt(endpoints[1]);
    hoursChanged(endpoints);
});
