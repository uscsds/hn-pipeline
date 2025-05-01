

//const S3_BASE = "https://YOUR_BUCKET.s3.amazonaws.com/analysis";
const S3_BASE = "http://localhost:8000";
const modules = [
  ['sentimentChart', 'sentiment_analysis'],
  ['keywordsChart', 'keyword_extraction'],
  ['trendingChart', 'trending_detection'],
  ['scoreChart', 'score_dynamics'],
  ['titleLengthChart', 'title_length_distribution'],
  ['commentsChart', 'comment_count_analysis']
];

async function loadTimestamps() {
  const response = await fetch(`${S3_BASE}/state/processed_files.json`);
  const states = await response.json();
  const timestamps = states["processed_files"];
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
    loadViewContents(timestamp);
  });
  if (timestamps.length > 0) {
    const initialTimestamp = timestamps[0];
    selector.value = initialTimestamp;
    loadViewContents(initialTimestamp)
  }
}

document.getElementById('refreshTimestamps').addEventListener('click', loadTimestamps);

async function load_stories_analysis(timestamp) {
  const response = await fetch(`${S3_BASE}/analysis/stories_analysis_${timestamp}.json`);
  const stories_analysis = await response.json();
  return stories_analysis;
}

async function loadViewContents(timestamp) {
  //modules.forEach(([chartId, filename]) => {}
  const [stories_analysis/*, other_data*/] = await Promise.all([
      load_stories_analysis(timestamp),
      //load_other_data(timestamp)
    ]);
  updateMetadata(timestamp);
  loadStoryTable(stories_analysis);
  updateSummaryInfo(stories_analysis);
  loadSentimentChart(stories_analysis);
  renderSwitchableCorrelationChart(stories_analysis.stories);
  drawHistogramChart(stories_analysis.stories);
}

function updateMetadata(timestamp) {
  const metaDiv = document.getElementById('timestampMeta');
  metaDiv.textContent = `Currently showing analysis for: ${timestamp}`;
}

function updateSummaryInfo(stories_analysis) {
  const summaryTotalStories = document.querySelector('#summaryTotalStories span');
  summaryTotalStories.innerHTML = stories_analysis.score_summary.total_stories;
  const summaryAverageScore = document.querySelector('#summaryAverageScore span');
  summaryAverageScore.innerHTML = Math.round(stories_analysis.score_summary.average_score);

  const list = document.getElementById('topKeywordsList');
  list.innerHTML = '';
  stories_analysis.top_keywords.forEach(([keyword, count]) => {
    const li = document.createElement('li');
    li.innerHTML = `${keyword}`;
    list.appendChild(li);
  });
}

function loadStoryTable(stories_analysis) {
  const tableBody = document.querySelector('#storyTable tbody');
  tableBody.innerHTML = '';

  const topStories = stories_analysis["score_summary"]["top_stories"];
  const sentimentColorMap = {
    positive: '#16a34a', // green
    neutral: '#6b7280',  // gray
    negative: '#dc2626'  // red
  };

  if (Array.isArray(topStories) && topStories.length > 0) {
    topStories.forEach(story => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${story.title}</td>
        <td>${story.score}</td>
        <td>${story.kidsSize}</td>
        <td>${story.sentiment}</td>
      `;
      row.querySelector('td:first-child').style.setProperty('--bullet-color', sentimentColorMap[story.sentiment] || '#0d9488');
      tableBody.appendChild(row);
    });
  } else {
    const row = document.createElement('tr');
    row.innerHTML = '<td colspan="4" style="color:red;">No story data available.</td>';
    tableBody.appendChild(row);
  }
}


function loadSentimentChart(stories_analysis) {
  const sentimentData = stories_analysis["sentiment_summary"];

  // Convert object into array
  const sentimentArray = Object.entries(sentimentData).map(([sentiment, count]) => ({
    sentiment,
    count
  }));

  // Colors for sentiments
  const sentimentColors = {
    positive: '#4CAF50',  // Green
    neutral: '#FFC107',   // Amber
    negative: '#F44336'   // Red
  };

  const svg = d3.select('#summarySentimentChart');
  const width = +svg.attr('width');
  const height = +svg.attr('height');
  const margin = { top: 20, right: 20, bottom: 40, left: 40 };

  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  svg.selectAll('*').remove();  // Clear previous chart before redrawing

  const chart = svg.append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  const x = d3.scaleBand()
    .domain(sentimentArray.map(d => d.sentiment))
    .range([0, chartWidth])
    .padding(0.3);

  const y = d3.scaleLinear()
    .domain([0, d3.max(sentimentArray, d => d.count) * 1.1])
    .range([chartHeight, 0]);

  // X Axis
  chart.append('g')
    .attr('transform', `translate(0,${chartHeight})`)
    .call(d3.axisBottom(x));

  // Y Axis
  chart.append('g')
    .call(d3.axisLeft(y).ticks(5));

  // Bars
  chart.selectAll('.bar')
    .data(sentimentArray)
    .enter()
    .append('rect')
    .attr('class', 'bar')
    .attr('x', d => x(d.sentiment))
    .attr('y', d => y(d.count))
    .attr('width', x.bandwidth())
    .attr('height', d => chartHeight - y(d.count))
    .attr('fill', d => sentimentColors[d.sentiment]);

  // Labels on bars
  chart.selectAll('.label')
    .data(sentimentArray)
    .enter()
    .append('text')
    .attr('x', d => x(d.sentiment) + x.bandwidth() / 2)
    .attr('y', d => y(d.count) - 5)
    .attr('text-anchor', 'middle')
    .attr('fill', '#333')
    .attr('font-size', '12px')
    .text(d => d.count);
}

function renderSwitchableCorrelationChart(stories) {
  const svg = d3.select('#correlationChart');
  svg.selectAll('*').remove();  // Clear existing chart before re-render
  const width = +svg.attr('width') - 100;
  const height = +svg.attr('height');
  const margin = { top: 40, right: 20, bottom: 50, left: 60 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  const chart = svg.append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  const xAxisGroup = chart.append('g')
    .attr('transform', `translate(0,${chartHeight})`);
  const yAxisGroup = chart.append('g');

  const title = svg.append('text')
    .attr('x', margin.left + chartWidth / 2)
    .attr('y', margin.top - 15)
    .attr('text-anchor', 'middle')
    .attr('font-size', '14px')
    .attr('font-weight', 'bold');

  const xLabel = svg.append('text')
    .attr('x', margin.left + chartWidth / 2)
    .attr('y', height - 5)
    .attr('text-anchor', 'middle')
    .attr('font-size', '12px');

  const yLabel = svg.append('text')
    .attr('transform', `rotate(-90)`)
    .attr('x', - (margin.top + chartHeight / 2))
    .attr('y', 15)
    .attr('text-anchor', 'middle')
    .attr('font-size', '12px')
    .text('Score');

  const color = 'red';

  function updateChart(xKey, xLabelText, titleText) {
    const processedData = stories.map(d => ({
      ...d,
      [xKey]: xKey === 'hour' ? +d[xKey] : d[xKey]
    }));

    const x = d3.scaleLinear()
      .domain([0, d3.max(processedData, d => d[xKey]) * 1.1 || 10])
      .range([0, chartWidth]);

    const y = d3.scaleLinear()
      .domain([0, d3.max(processedData, d => d.score) * 1.1 || 10])
      .range([chartHeight, 0]);

    const xAxis = d3.axisBottom(x).ticks(6);
    const yAxis = d3.axisLeft(y).ticks(6);

    xAxisGroup.transition().duration(500).call(xAxis);
    yAxisGroup.transition().duration(500).call(yAxis);

    title.text(titleText);
    xLabel.text(xLabelText);

    // Bind data
    const circles = chart.selectAll('circle').data(processedData, d => d.id);

    // ENTER new circles
    circles.enter()
      .append('circle')
      .attr('cx', d => x(d[xKey]))
      .attr('cy', d => y(d.score))
      .attr('r', 5)
      .attr('fill', color)
      .attr('opacity', 0.7)
      .append('title')
      .text(d => `${d.title}\n${xLabelText}: ${d[xKey]}\nScore: ${d.score}`);

    // UPDATE existing circles
    circles.transition().duration(500)
      .attr('cx', d => x(d[xKey]))
      .attr('cy', d => y(d.score));

    // Remove old
    circles.exit().remove();
  }

  // Switch chart on dropdown change
  document.getElementById('chartSelector').addEventListener('change', e => {
    if (e.target.value === 'textLength') {
      updateChart('textLength', 'Text Length', 'Score vs Text Length');
    } else {
      updateChart('hour', 'Hour (0-23)', 'Score vs Hour');
    }
  });

  // Trigger the change event for the dropdown on page load to initialize the chart with the default metric
  d3.select("#chartSelector").property('value', 'textLength').dispatch('change');
}

function drawHistogramChart(stories) {
  // Data
  const dataset = stories;

  dataset.forEach(d => {
    d.score = +d.score.toString().replace(/,/g, '');
    d.textLength = +d.textLength.toString().replace(/,/g, '');
    d.hour = +d.hour.toString().replace(/,/g, '');
  });

  // Dimensions
  let dimensions = {
    width: 700,
    height: 400,
    margins: 50
  };

  dimensions.ctrWidth = dimensions.width - dimensions.margins * 2;
  dimensions.ctrHeight = dimensions.height - dimensions.margins * 2;

  // Draw Image
  const chartArea = d3.select('#histogramChart')
  chartArea.selectAll('*').remove();  // Clear existing chart before re-render

  const svg = d3.select('#histogramChart')
    .append("svg")
    .attr("width", dimensions.width)
    .attr("height", dimensions.height);

  const ctr = svg.append("g") // Center group
    .attr("transform", `translate(${dimensions.margins}, ${dimensions.margins})`);

  const labelsGroup = ctr.append('g')
    .classed('bar-labels', true);

  const xAxisGroup = ctr.append('g')
    .style('transform', `translateY(${dimensions.ctrHeight}px)`);

  const meanLine = ctr.append('line')
    .classed('mean-line', true);

  function histogram(metric) {
    const xAccessor = d => d[metric];
    const yAccessor = d => d.length;

    // Scales
    const xScale = d3.scaleLinear()
      .domain(d3.extent(dataset, xAccessor))
      .range([0, dimensions.ctrWidth])
      .nice();

    const bin = d3.bin()
      .domain(xScale.domain())
      .value(xAccessor)
      .thresholds(30);

    const newDataset = bin(dataset);
    const padding = 1;

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(newDataset, yAccessor)])
      .range([dimensions.ctrHeight, 0])
      .nice();

    const exitTransition = d3.transition().duration(500);
    const updateTransition = exitTransition.transition().duration(500);

    // Draw Bars
    ctr.selectAll('rect')
      .data(newDataset)
      .join(
        (enter) => enter.append('rect')
          .attr('width', d => d3.max([0, xScale(d.x1) - xScale(d.x0) - padding]))
          .attr('height', 0)
          .attr('x', d => xScale(d.x0))
          .attr('y', dimensions.ctrHeight)
          .attr('fill', '#b8de6f'),
        (update) => update,
        (exit) => exit.attr('fill', '#f39233')
          .transition(exitTransition)
          .attr('y', dimensions.ctrHeight)
          .attr('height', 0)
          .remove()
      )
      .transition(updateTransition)
      .attr('width', d => d3.max([0, xScale(d.x1) - xScale(d.x0) - padding]))
      .attr('height', d => dimensions.ctrHeight - yScale(yAccessor(d)))
      .attr('x', d => xScale(d.x0))
      .attr('y', d => yScale(yAccessor(d)))
      .attr('fill', '#01c5c4');

    // Draw Labels
    labelsGroup.selectAll('text')
      .data(newDataset)
      .join(
        (enter) => enter.append('text')
          .attr('x', d => xScale(d.x0) + (xScale(d.x1) - xScale(d.x0)) / 2)
          .attr('y', dimensions.ctrHeight)
          .text(d => yAccessor(d)),
        (update) => update,
        (exit) => exit.transition(exitTransition)
          .attr('y', dimensions.ctrHeight)
          .remove()
      )
      .transition(updateTransition)
      .attr('x', d => xScale(d.x0) + (xScale(d.x1) - xScale(d.x0)) / 2)
      .attr('y', d => yScale(yAccessor(d)) - 10)
      .text(d => yAccessor(d));

    // Draw Mean Line
    const mean = d3.mean(dataset, xAccessor);

    meanLine.raise()
      .transition(updateTransition)
      .attr('x1', xScale(mean))
      .attr('y1', 0)
      .attr('x2', xScale(mean))
      .attr('y2', dimensions.ctrHeight);

    // Draw Axis
    const xAxis = d3.axisBottom(xScale);

    xAxisGroup.transition()
      .call(xAxis);
  }

  d3.select("#histogramMetric").on('change', function (e) {
    e.preventDefault();

    histogram(this.value);
  });

  // Trigger the change event for the dropdown on page load to initialize the chart with the default metric
  d3.select("#histogramMetric").property('value', 'score').dispatch('change');
}


loadTimestamps();