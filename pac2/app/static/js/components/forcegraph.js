function _chart(d3,data,invalidation)
{
  // Specify the dimensions of the chart.
  const width = 928;
  const height = 680;
  // Specify the color scale.
  const color = d3.scaleOrdinal(d3.schemeCategory10);

  // The force simulation mutates links and nodes, so create a copy
  // so that re-evaluating this cell produces the same result.
  const links = data.links.map(d => ({...d}));
  const nodes = data.nodes.map(d => ({...d}));

  // Create a simulation with several forces.
  const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id))
      .force("charge", d3.forceManyBody().strength(function(d, i) {
        var a = i == 0 ? -1500 : -150;
        return a;
    }).distanceMin(30).distanceMax(500))
      .force("x", d3.forceX())
      .force("y", d3.forceY());

  // Create the SVG container.
  const svg = d3.create("svg")
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", [-width / 2, -height / 2, width, height])
      .attr("style", "max-width: 100%; height: auto;");

  // Add a line for each link, and a circle for each node.
  const link = svg.append("g")
      .attr("stroke", "#999")		// line color
      .attr("stroke-opacity", 0.6)	// line thickness
    .selectAll("line")
    .data(links)
    .join("line")
      .attr("stroke-width", d => Math.sqrt(d.value));

  const node = svg.append("g")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
    .selectAll("circle")
    .data(nodes)
    .join("circle")
      .attr("r", 8)
	//      .attr("r", 5)	# size of the circle
      .attr("fill", d => color(d.group));

  node.append("title")
      .text(d => d.title);

  node.on("click", function(data,idx) {
    if(idx.group == "V PAC2 Project") {
      window.location.href = '/portal/messages?client_id=' + idx.client_id + '&channel_id=' + idx.id + '&team_name=' + idx.teamname + '&channel_name=' + idx.channelname;
    }
  });

  // Add a drag behavior.
  node.call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

  // Set the position attributes of links and nodes each time the simulation ticks.
  simulation.on("tick", () => {
    link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);
  });

  // Reheat the simulation when drag starts, and fix the subject position.
  function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
  }

  // Update the subject (dragged node) position during drag.
  function dragged(event) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
  }

  // Restore the target alpha so the simulation cools after dragging ends.
  // Unfix the subject position now that it’s no longer being dragged.
  function dragended(event) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
  }

  // When this cell is re-run, stop the previous simulation. (This doesn’t
  // really matter since the target alpha is zero and the simulation will
  // stop naturally, but it’s a good practice.)
  invalidation.then(() => simulation.stop());

  return svg.node();
}


async function fetchData(apiUrl) {
  const response = await fetch(apiUrl);
  if (!response.ok) {
    throw new Error('Network response was not ok ' + response.statusText);
  }
  return response.json();
}

// データを取得する関数
async function _data() {
  let client_id = new URL(window.location.href).searchParams.get("client_id");
  let apiUrl = "/api/teams/graph?client_id=" + client_id;
  return fetchData(apiUrl);
}

export default function define(runtime, observer) {
  const main = runtime.module();
  main.variable(observer("chart")).define("chart", ["d3", "data", "invalidation"], _chart);

  // 'data' の定義を更新
  main.variable(observer("data")).define("data", ["invalidation"], async function(invalidation) {
    const data = await _data();
    invalidation.then(() => { /* Error handling : Not Implemented yet.*/ });
    return data;
  });

  return main;
}
