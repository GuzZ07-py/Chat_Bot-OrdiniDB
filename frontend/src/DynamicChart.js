import { Line,Bar,Pie} from "react-chartjs-2";

export default function DynamicChart({ chart })
{
  const chartData = {
    labels: chart.data.map(
      item => item[chart.xAxis]
    ),

    labels: chart.data.map(
      item => item[chart.xAxis]
    ),

    datasets: [
      {
        label: chart.yAxis,

        data: chart.data.map(
          item => item[chart.yAxis]
        )
      }
    ]
  };
   switch (chart.type) {

    case "line":
      return <Line data={chartData} />;

    case "bar":
      return <Bar data={chartData} />;

    case "pie":
      return <Pie data={chartData} />;

    default:
      return null;
  }

}

export default DynamicChart;