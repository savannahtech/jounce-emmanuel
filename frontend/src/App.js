import React, { useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import axios from "axios";

const LLMChart = ({ defaultMetricName }) => {
  const [metricName, setMetricName] = useState(defaultMetricName);
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [
      {
        label: `Performance of LLMs on ${metricName}`,
        data: [],
        borderWidth: 1,
      },
    ],
  });

  useEffect(() => {
    axios
      .get(`http://localhost:8000/api/rank/${metricName}`)
      .then((response) => {
        const llmNames = response.data?.map((llm) => llm[0]);
        const metricValues = response.data?.map((llm) => llm[1]);
        console.log({ llmNames, metricValues });
        setChartData({
          labels: llmNames,
          datasets: [
            {
              label: `Performance of LLMs on ${metricName}`,
              data: metricValues,
              backgroundColor: "rgba(75,192,192,1)",
              borderColor: "rgba(0,0,0,1)",
              borderWidth: 2,
            },
          ],
        });
      })
      .catch((e) => {
        console.log(e);
      });
  }, [metricName]);
  return (
    <div style={{ padding: 15 }}>
      <div style={{ paddingBottom: 15, paddingTop: 15, float: "right" }}>
        <select
          onChange={(item) => {
            console.log(item);
            setMetricName(item.target.value);
          }}
        >
          {["TTFT", "TPS", "e2e_latency", "RPS"].map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
      </div>
      <Bar
        data={chartData}
        options={{
          title: {
            display: true,
            text: `LLM Performance for ${metricName}`,
            fontSize: 20,
          },
          legend: { display: true, position: "right" },
        }}
      />
    </div>
  );
};

export default LLMChart;
