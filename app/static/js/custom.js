// top 6 most taxi-active zones, per borough
curData = [168,  247,  69,  159,  119,  235,  
    181,  255,  256,  97,  112,  33,  
    161,  236,  237,  170,  162,  230,  
    138,  132,  7,  129,  82,  226,  
    206,  221,  115,  6,  23,  245];

function initMapColors(hours) {
    hideLoading();

    svg.selectAll("path")
        .attr("fill", colorZone);
}

function colorZone(p) {
    if (curData.indexOf(p["properties"][ZONE_ID]) >= 0) {
        if (p["properties"]["borough"] == "Manhattan") {
            return "rgba(136,14,79 ,1)";
        }
        else if (p["properties"]["borough"] == "Bronx") {
            return "rgba(0,150,136 ,1)";
        }
        else if (p["properties"]["borough"] == "Brooklyn") {
            return "rgba(255,160,0 ,1)";
        }
        else if (p["properties"]["borough"] == "Queens") {
            return "rgba(94,53,177 ,1)";
        }
        else if (p["properties"]["borough"] == "Staten Island") {
            return "rgba(26,35,126 ,1)";
        }
        else {
            return "rgba(0, 0, 0, 1)";
        }
    }
    else {
        return "rgba(0, 0, 0, 0)";
    }
}

// DISABLE
function zoneClick(d, i, paths) {
//     var id = d['properties'][ZONE_ID];
//     if (curData.indexOf(id) >= 0) { // remove if in cuData
//         var index = curData.indexOf(id);
//         curData.splice(index, 1);
//     }
//     else {
//         curData.push(id);
//     }

//     svg.selectAll("path")
//         .attr("fill", colorZone);
}

/* when you mouseover a zone */
function borderMouseover(d, i, paths) {
    var element = svgElement.getElementById(this.id);
    element.classList.add("hovered");

    var name = "";
    var id = d['properties'][ZONE_ID];
    var name = d['properties'][ZONE_NAME];
    return tooltip.style("visibility", "visible")
        .html("<span class='name'>" + name + "</span><span class=' value'>" + "</span>");
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
            .attr("fill", function(p) { console.log(p); return "rgb(0, 0, 0)"; } );
    });
}
