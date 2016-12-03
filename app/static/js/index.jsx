
// MENU
class Menu extends React.Component {
  constructor(props) {
    super(props);

    this.handleClick = this.handleClick.bind(this);
  }

  handleClick(e) {
    var mode_value = e.currentTarget.getAttribute("data-mode")
    this.props.stateHandler(mode_value);
  }

  render () {
    return (
      <div className="wrapper">
        <span onClick={this.handleClick} data-mode="NET_FLOW" className={this.props.mode == "NET_FLOW" ? "selected" : ""}>
          net flow
        </span>
        <span onClick={this.handleClick} data-mode="DEST_COUNT" className={this.props.mode == "DEST_COUNT" ? "selected" : ""}>
          destination count
        </span>
      </div>
    );
  }

}

// HOUR SLIDER
class HourSlider extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div id="hour-slider">
      </div>
    );
  }
}

// DAY PICKER
class DayPicker extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div id="day-picker">
      </div>
    );
  }
}



// ENTIRE APP
class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      mode: "NET_FLOW",
      hours: Array.apply(null, Array(24)).map(function () {return 1;}),
      days: Array.apply(null, Array(7)).map(function () {return 1;})
    };

    document.body.classList = [];
    document.body.classList.add("mode-net-flow");

    this.stateHandler = this.stateHandler.bind(this);
  }

  stateHandler(mode_value) {
    this.setState({
      mode: mode_value
    });
    if (mode_value == "NET_FLOW") {
      document.body.classList = [];
      document.body.classList.add("mode-net-flow");
    }
    else if (mode_value == "DEST_COUNT") {
      document.body.classList = [];
      document.body.classList.add("mode-dest-count");
    }
  }

  componentDidMount() {
    document.getElementById("reactRoot").classList.add("mounted")
  }

  render() {
    return (
      <div>
        <div id="menu">
          <Menu stateHandler={this.stateHandler} mode={this.state.mode} />
        </div>
        <div className="sliders">
            <HourSlider hours={this.state.hours} />
            <DayPicker days={this.state.days} />
        </div>
        <Map width={window.innerWidth} 
              height={window.innerHeight} 
              stateHandler={this.stateHandler}
              mode={this.state.mode}
              hours={this.state.hours} 
              days={this.state.days} />
      </div>
      );
  }
}

ReactDOM.render(
  <App />,
  document.getElementById("reactRoot")
);