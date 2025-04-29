import * as d3 from 'd3'

//const S3_BASE = "https://YOUR_BUCKET.s3.amazonaws.com/analysis";
const S3_BASE = "http://localhost:8000/example_data";
const modules = [
  ['sentimentChart', 'sentiment_analysis'],
  ['keywordsChart', 'keyword_extraction'],
  ['trendingChart', 'trending_detection'],
  ['scoreChart', 'score_dynamics'],
  ['titleLengthChart', 'title_length_distribution'],
  ['commentsChart', 'comment_count_analysis']
];

async function loadTimestamps() {
  const response = await fetch(`${S3_BASE}/index.json`);
  const timestamps = await response.json();
  const selector = document.getElementById('timestampSelector');
  selector.innerHTML = '';
  timestamps.forEach(ts => {
    const option = document.createElement('option');
    option.value = ts;
    option.textContent = ts;
    selector.appendChild(option);
  });
  selector.addEventListener('change', () => {
    const timestamp = selector.value;
    loadCharts(timestamp);
    updateMetadata(timestamp);
    loadStoryTable(timestamp);
  });
  if (timestamps.length > 0) {
    const initialTimestamp = timestamps[0];
    selector.value = initialTimestamp;
    loadCharts(initialTimestamp);
    updateMetadata(initialTimestamp);
    loadStoryTable(initialTimestamp);
  }
}

document.getElementById('refreshTimestamps').addEventListener('click', loadTimestamps);

function updateMetadata(timestamp) {
  const metaDiv = document.getElementById('timestampMeta');
  metaDiv.textContent = `Currently showing analysis for: ${timestamp}`;
}

function loadCharts(timestamp) {
  modules.forEach(([chartId, filename]) => {
    console.log(chartId + "  " + filename)
    const sectionId = chartId.replace("Chart", "");
    console.log(sectionId)
    const toggle = document.querySelector(`.analysis-toggle[data-section="${sectionId}"]`);
    console.log(toggle)
    const chartContainer = document.getElementById(chartId);

    if (!toggle.checked) {
      d3.select(chartContainer).selectAll("*").remove();
      return;
    }

    d3.json(`${S3_BASE}/${filename}_${timestamp}.json`).then(data => {
      const svg = d3.select(chartContainer);
      svg.selectAll("*").remove();
      const width = +svg.attr("width");
      const height = +svg.attr("height");

      if (Array.isArray(data) && typeof data[0] === 'number') {
        const x = d3.scaleLinear().domain([0, d3.max(data)]).range([0, width]);
        const bins = d3.bin().domain(x.domain()).thresholds(20)(data);
        const y = d3.scaleLinear().domain([0, d3.max(bins, d => d.length)]).range([height, 0]);

        svg.selectAll(".bar")
          .data(bins)
          .enter().append("rect")
          .attr("x", d => x(d.x0))
          .attr("width", d => Math.max(0, x(d.x1) - x(d.x0) - 1))
          .attr("y", d => y(d.length))
          .attr("height", d => height - y(d.length))
          .style("fill", "#69b3a2");

      } else if (Array.isArray(data) && data[0].id) {
        const yValue = d => d.sentiment ?? d.score ?? d.descendants ?? 0;
        const x = d3.scaleBand().domain(data.map(d => d.id)).range([0, width]).padding(0.1);
        const y = d3.scaleLinear().domain([0, d3.max(data, yValue)]).range([height, 0]);

        svg.selectAll(".bar")
          .data(data)
          .enter().append("rect")
          .attr("x", d => x(d.id))
          .attr("width", x.bandwidth())
          .attr("y", d => y(yValue(d)))
          .attr("height", d => height - y(yValue(d)))
          .style("fill", "#4682b4");

      } else if (Array.isArray(data) && typeof data[0] === 'object') {
        const getX = d => d[0] ?? d.time;
        const getY = d => d[1] ?? d.count;
        const x = d3.scaleBand().domain(data.map(getX)).range([0, width]).padding(0.1);
        const y = d3.scaleLinear().domain([0, d3.max(data, getY)]).range([height, 0]);

        svg.selectAll(".bar")
          .data(data)
          .enter().append("rect")
          .attr("x", d => x(getX(d)))
          .attr("width", x.bandwidth())
          .attr("y", d => y(getY(d)))
          .attr("height", d => height - y(getY(d)))
          .style("fill", "#ff8c00");
      }
    }).catch(e => {
      d3.select(chartContainer).selectAll("*").remove();
      const svg = d3.select(chartContainer);
      svg.append("text")
        .attr("x", 10)
        .attr("y", 30)
        .text(`Data not available for ${filename}`)
        .attr("fill", "red");
    });
  });
}

function loadStoryTable(timestamp) {
  const tableBody = document.querySelector('#storyTable tbody');
  tableBody.innerHTML = '';
  d3.json(`${S3_BASE}/story_table_${timestamp}.json`).then(data => {
    data.forEach(story => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${story.title}</td>
        <td>${story.score}</td>
        <td>${story.comments}</td>
        <td>${story.sentiment}</td>
      `;
      tableBody.appendChild(row);
    });
  }).catch(err => {
    const row = document.createElement('tr');
    row.innerHTML = '<td colspan="4" style="color:red;">No story data available.</td>';
    tableBody.appendChild(row);
  });
}

document.querySelectorAll('.analysis-toggle').forEach(toggle => {
  toggle.addEventListener('change', () => {
    const timestamp = document.getElementById('timestampSelector').value;
    loadCharts(timestamp);
  });
});

loadTimestamps();