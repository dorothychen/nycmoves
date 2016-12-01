var ZONE_FILE = "static/zones_taxi.geojson";
var FLOW_FILE = "static/zones_2016-01-03.json";
var DEST_COUNT_FILE = "static/dest_zones_2016.json";
var CALLBACKS = {};

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


/* setup tooltip for info */
var tooltip = d3.select("body")
		.append("div")
		.attr("class", "tooltip")
		.style("position", "absolute")
		.style("z-index", "10")
		.style("visibility", "hidden");

// MAP
class Map extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			map_data: false,
			color_data: false,
			selected_zone: false,
		}

		this.mouseover = this.mouseover.bind(this);
		this.mouseout = this.mouseout.bind(this);
		this.mousemove = this.mousemove.bind(this);
		this.onclick = this.onclick.bind(this);
	}

	componentWillMount() {
		// for some reason this syntax preserves the "this"!!
		CALLBACKS.getMapData = (data) => {
			this.setState({map_data: data});
		}

		CALLBACKS.getColorData = (data) => {
			// TODOOOOO; keep only the days of weeks and hours of day that we need

			this.setState({color_data: data});
		}

		// load zone shapes
		d3.json(ZONE_FILE, function(err, data) {
			if (err) { console.log(err); }
			CALLBACKS.getMapData(data);
		});

		this.getColorData(this.props.mode);
	}

	// componentDidMount() {
 //    // Get the components DOM node
	// 	var elem = ReactDOM.findDOMNode(this);
	// 	elem.style.opacity = 0;

	// 	window.requestAnimationFrame(function() {
	// 		// Now set a transition on the opacity
	// 		elem.style.transition = "opacity 250ms";
	// 		// and set the opacity to 1
	// 		elem.style.opacity = 1;
	// 	});
	// }

	componentWillReceiveProps(nextProps) {
		// if mode changes, update color scheme
		if (this.props.mode !== nextProps.mode) {
			this.getColorData(nextProps.mode);
		}
		
	}

	/**	Given mode <DEST_COUNT | NET_FLOW>, assign appropriate color json data to
			this.state.color_data
	*/
	getColorData(mode) {
		// load data for colors
		var COLOR_FILE = "";
		if (mode == "DEST_COUNT") {
			COLOR_FILE = DEST_COUNT_FILE;
		}
		else if (mode == "NET_FLOW") {
			COLOR_FILE = FLOW_FILE;
		}

		d3.json(COLOR_FILE, function(err, data) {
			if (err) { console.log(err); }
			CALLBACKS.getColorData(data);			
		});
	}

	/** logistic function for gradient
			k is the steepness of the curve; smaller k (in abs val) means wider curve and more sensitivity
	*/
	logistic(x, k) {
    var base = 1 + Math.pow(Math.E, -k*x);
    return 1 / base;
	}

	/*  given a zone feature object and a dictionary of zone codes => flow values,
	    return color.

			p is the zone object (from the GeoJSON file)
			vals is a dictionary mapping each zone id to a numeric value
	    k is the k value in logistic functions, defaults to 0.2
	*/
	idToColor(p, vals, k=0.2) {
		var color_cold = [250, 250, 250];
		var color_hot = [0,0,0];

    var id = p['properties'][ZONE_ID];
    var percent = this.logistic(vals[id], k);

    var rgb = color_hot.map(function(val, i) {
        var diff = percent * (color_hot[i]-color_cold[i]) + color_cold[i];
        return Math.round(diff);
    });

    return 'rgb(' + rgb.join() + ')';
	}

	/**	Tooltip contents for NET_FLOW
	*/
	getTooltipHTML(zoneid, mode) {
		if (!this.state.map_data.features) {
			console.err("no map data for tooltip");
			return;
		}

		// var zone_data = this.state.map_data.features[zoneid];
		// var name = zone_data['properties'][ZONE_NAME];

		// if (mode == "NET_FLOW") {
		// 	var aggFlow = this.state.color;
		// 	return tooltip.style("visibility", "visible")
		// 			.html("<span class='name'>" + name + "</span><span class='agg-flow'>" + aggFlow + "</span>");
		// }
	}

	mouseover (e) {
		e.target.classList.add("hovered");
		var zoneid = e.target.getAttribute("data-id");

		this.getTooltipHTML(this.props.mode);
	}

	mouseout (e) {
		e.target.classList.remove("hovered");

		return tooltip.style("visibility", "hidden");
	}

	mousemove(e) {
		return tooltip.style("top", (e.pageY-10)+"px").style("left",(e.pageX+10)+"px");
	}

	onclick (e) {
		this.props.stateHandler("DEST_COUNT");
		this.setState({selected_zone: e.target.getAttribute("data-id")});
	}

	// if this.props.mode == "NET_FLOW" then state.filename is something, otherwise is something else
	render() {
		if (!this.state.map_data) {
			return false;
		}

		var width = this.props.width;
		var height = this.props.height;
		var data = this.state.map_data;

		// unit projection 
		// can also be d3.geoAlbersUsa
		var projection = d3.geoMercator() 
			.scale("1")
			.translate([0, 0]);

		// set path
		var path = d3.geoPath().projection(projection);

		// compute bounds
		// http://stackoverflow.com/questions/14492284/center-a-map-in-d3-given-a-geojson-object
		var b = path.bounds(data),
				s = .95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height),
				t = [(width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2];

		// resize and move projection
		projection.scale(s).translate(t);

		// for coloring: what is the set of zoneids => number we are using?
		// TODOOOOOO can get rid of most of this after standardizing color_data
		var color_vals = this.state.color_data;
		var k = 0.2;
		if (this.props.mode == "NET_FLOW" && color_vals != undefined && color_vals != false) {
			color_vals = this.state.color_data["12:30"];
			k = 0.2;
		}
		else if (this.props.mode == "DEST_COUNT" && this.state.selected_zone) {
			color_vals = this.state.color_data[this.state.selected_zone];
			k = 0.001;
		}

		var paths = data.features.map((zone, i) => {
			var zoneId = zone['properties'][ZONE_ID];
			var isSelected = this.state.selected_zone == zoneId ? " selected" : "";
			return (<path key={i} 
										data-id={zoneId} 
										className={"zone id-" + zoneId + isSelected} 
										d={path(zone)}
										fill={this.idToColor(zone, color_vals, k)}
										onMouseOver={this.mouseover}
										onMouseMove={this.mousemove}
										onMouseOut={this.mouseout}
										onClick={this.onclick} />
				);
		});

		return (
			<svg id="map" 
					width={this.props.width} 
					height={this.props.height} >
				{paths}
			</svg>
		);

	}

}

