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


// MODE
var MODE = document.getElementById("menu").getAttribute("data-mode");

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
			mode: MODE;
		}

		this.mouseover = this.mouseover.bind(this);
		this.mouseout = this.mouseout.bind(this);
		this.mousemove = this.mousemove.bind(this);
		this.onclick = this.onclick.bind(this);
	}

	componentWillMount() {
		// ()=> syntax preserves the "this"!!
		CALLBACKS.getMapData = (data) => {
			this.setState({map_data: data});

			// get mapping of zoneid => {"name": "", etc.}
			var zone_metadata = {} 
			data['features'].forEach(function(zone) {
				var zoneid = zone['properties'][ZONE_ID];
				zone_metadata[zoneid] = zone['properties'];
			});

			this.setState({zone_metadata: zone_metadata});
		}

		// this.state.color_data should map zoneid => {to_zoneid=>value, etc.}
		CALLBACKS.getColorData = (data) => {
			console.log(data)
			this.setState({color_data: data});
		}

		// load zone shapes
		d3.json(ZONE_FILE, function(err, data) {
			if (err) { console.log(err); }
			CALLBACKS.getMapData(data);
		});

		this.getColorData(this.state.mode);
	}


	componentWillReceiveProps(nextProps) {
		// if mode changes, update color scheme
		if (this.state.mode !== nextProps.mode) {
			this.getColorData(nextProps.mode);
			if (nextProps.mode == "NET_FLOW") {
				this.setState({selected_zone: false});
			}
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

		$.get('/api/get_color_data', {
			hours: this.props.hours.join(),
			days: this.props.days.join(),
			mode: mode
		}, function(data) {
			var parsed = JSON.parse(data);
			CALLBACKS.getColorData(parsed);
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
		if (!this.state.zone_metadata) {
			console.error("no map data for tooltip");
			return;
		}

		var name = this.state.zone_metadata[zoneid][ZONE_NAME];
		var value = "none"
		if (this.state.mode == "NET_FLOW") {
			value = this.state.color_data[zoneid]
		}
		else if (this.state.mode == "DEST_COUNT") {
			value = this.state.color_data[this.state.selected_zone][zoneid]
		} 
		 
		return tooltip.style("visibility", "visible")
				.html("<span class='name'>" + name + "</span><span class='value'> value: " + value + "</span>");
	}

	mouseover (e) {
		e.target.classList.add("hovered");
		var zoneid = e.target.getAttribute("data-id");

		this.getTooltipHTML(zoneid, this.state.mode);
	}

	mouseout (e) {
		e.target.classList.remove("hovered");

		return tooltip.style("visibility", "hidden");
	}

	mousemove(e) {
		return tooltip.style("top", (e.pageY-10)+"px").style("left",(e.pageX+10)+"px");
	}

	onclick (e) {
		this.setState({selected_zone: e.target.getAttribute("data-id")});
	}

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
		var color_vals = this.state.color_data;
		var k = 0.2;
		if (this.state.mode == "NET_FLOW" && color_vals != undefined && color_vals != false) {
			color_vals = this.state.color_data;
			k = 0.0002;
		}
		else if (this.state.mode == "DEST_COUNT" && this.state.selected_zone) {
			color_vals = this.state.color_data[this.state.selected_zone];
			k = 0.001;
		}
		else {
			color_vals = false;
		}

		var paths = data.features.map((zone, i) => {
			var zoneId = zone['properties'][ZONE_ID];
			var isSelected = this.state.selected_zone == zoneId ? " selected" : "";
			return (<path key={i} 
										data-id={zoneId} 
										className={"zone id-" + zoneId + isSelected} 
										d={path(zone)}
										fill={color_vals ? this.idToColor(zone, color_vals, k) : "None"}
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

