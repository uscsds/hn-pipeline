export function render(jsonUrl) {
    d3.json(jsonUrl).then(data => {
      const svg = d3.select("#sentimentChart");
      const width = +svg.attr("width");
      const height = +svg.attr("height");
  
      const sentiments = data.map(d => d.sentiment);
      const x = d3.scaleLinear().domain([-1, 1]).range([0, width]);
      const histogram = d3.bin().domain(x.domain()).thresholds(20)(sentiments);
  
      const y = d3.scaleLinear()
        .domain([0, d3.max(histogram, d => d.length)])
        .range([height, 0]);
  
      const bar = svg.selectAll(".bar")
        .data(histogram)
        .enter().append("g")
        .attr("class", "bar")
        .attr("transform", d => `translate(${x(d.x0)}, ${y(d.length)})`);
  
      bar.append("rect")
        .attr("x", 1)
        .attr("width", d => x(d.x1) - x(d.x0) - 1)
        .attr("height", d => height - y(d.length))
        .style("fill", "#69b3a2");
  
      bar.append("text")
        .attr("dy", ".75em")
        .attr("y", -12)
        .attr("x", (d => (x(d.x1) - x(d.x0)) / 2))
        .attr("text-anchor", "middle")
        .text(d => d.length);
    });
  }
  