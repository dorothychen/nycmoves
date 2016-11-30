// MENU
class Menu extends React.Component {
  constructor(props) {
    super(props);

    this.handleClick = this.handleClick.bind(this);
  }

  handleClick(e) {
    this.props.stateHandler(e);
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
      hours: Array.apply(null, Array(24)).map(function (_, i) {return i;}),
      days: ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"]
    };

    this.stateHandler = this.stateHandler.bind(this);
  }

  stateHandler(e) {
    this.setState({
      mode: e.currentTarget.getAttribute("data-mode")
    });
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
      </div>
      );
  }
}

ReactDOM.render(
  <App />,
  document.getElementById("reactRoot")
);