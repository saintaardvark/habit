(function() {

}).call(this);

$(document).ready(function() {
});

async function deleteHabit(id){
  console.log("Deleting habit", id);
  const url = `/habit/${id}`;
  console.log("URL is", url);

  const response = await fetch(url, {
    method: 'DELETE'
  });
  const myJson = await response.json();  // converting to json

  console.log(myJson);
  location.href="/";
};

async function incrementHabit(id){
  console.log("Incrementing habit", id);
  const url = `/log/${id}`;
  console.log("URL is", url);

  const response = await fetch(url, {
    method: 'POST'
  });
  const myJson = await response.json();  // converting to json

  console.log(myJson);
  location.href="/";
};

async function showHeatMap(id) {
  let startTime = new Date();
  startTime.setMonth(startTime.getMonth() - 6);
  let domain = "month";
  let subDomain = "day";
  let range = 12;
  // See https://cal-heatmap.com/#legend for details, but this assumes
  // a habit frequency of 1-3 times a day, with anything over that a
  // wonderful bonus.
  let legend = [0, 1, 2, 3, 4];
  if (/Mobi/.test(navigator.userAgent)) {
    startTime = new Date();
    range = 1;
  }
  var cal = new CalHeatMap();
  cal.init({
    start: startTime,
    range: range,
    domain: domain,
    subDomain: subDomain,
    legend: legend,
    data: `/log/${id}`,
    highlight: "now",
    itemSelector: `#cal-heatmap-${id}`
  });
}
