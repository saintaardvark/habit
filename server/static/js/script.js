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
    data: `/log/${id}`,
    itemSelector: `#cal-heatmap-${id}`
  });
}
