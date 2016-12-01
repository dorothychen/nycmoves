// different zones
var ZONES = {
    "nta": {
        "filename": "zones_nta.geojson",
        "id": "ntacode",
        "name": "ntaname"
        },
    "taxi": {
        "filename": "zones_taxi.geojson",
        "id": "LocationID",
        "name": "zone"
        },
    "zipcode": {
        "filename": "zones_zipcode.geojson",
        "id": "ZIPCODE",
        "name": "PO_NAME"
        }
};

// chosen zone
var ZONE_TYPE = "taxi";
var ZONE_FILENAME = "static/" + ZONES[ZONE_TYPE]["filename"];
var ZONE_ID = ZONES[ZONE_TYPE]["id"];
var ZONE_NAME = ZONES[ZONE_TYPE]["name"];


// width of window
var width = window.innerWidth;

// height of window
var height = window.innerHeight;

// global dictionary of zone flow info for current time frame
var curData;

/* setup svg for map */
var svg = d3.select("body").append("svg")
    .attr("id", "map")
    .attr("width", width)
    .attr("height", height);

var svgElement = document.getElementById("map");

/* setup tooltip for info */
var tooltip = d3.select("body")
    .append("div")
    .attr("class", "tooltip")
    .style("position", "absolute")
    .style("z-index", "10")
    .style("visibility", "hidden");

/* make map from json zones file */
d3.json(ZONE_FILENAME, function(error, nyc) {
    if (error) return console.log(error);

    // unit projection 
    // can also be d3.geoAlbersUsa
    var projection = d3.geoMercator() 
        .scale("1")
        .translate([0, 0]);

    // set path
    var path = d3.geoPath().projection(projection);

    // compute bounds
    // http://stackoverflow.com/questions/14492284/center-a-map-in-d3-given-a-geojson-object
    var b = path.bounds(nyc),
        s = .95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height),
        t = [(width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2];

    projection.scale(s).translate(t)

    svg.selectAll("path")
        .data(nyc.features)
        .enter()
        .append("path")
        .attr("d", path)
        .attr("id", function(d) { return "id-" + d['properties'][ZONE_ID]; })
        .attr("class", "border")
        .attr("fill", "None") // hide at first
        .on("mouseover", borderMouseover)
        .on("mousemove", borderMousemove)
        .on("mouseout", borderMouseout)
        .on("click", zoneClick);

    updateColorsFlow();
});

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
    var zoneId = this.id.substring(3);
    updateColorsDest(zoneId);
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
        .html("<span class='name'>" + name + "</span><span class='agg-flow'>" + aggFlow + "</span>");
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
