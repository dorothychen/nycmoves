
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
  }

  componentDidMount() {
    document.getElementById("reactRoot").classList.add("mounted")
  }

  render() {
    return (
      <div>
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