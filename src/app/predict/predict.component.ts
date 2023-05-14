import { Component,OnInit} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ChartDataset } from 'chart.js';


@Component({
  selector: 'app-predict',
  templateUrl: './predict.component.html',
  styleUrls: ['./predict.component.css']
})
export class PredictComponent implements OnInit {
  public labels: string[] = [];
public datas: number[] = [];
  chartData: any = [];

  constructor(private route: ActivatedRoute,private router: Router) { }
  
  
  chatdata = {
    labels: this.labels,
    datasets: [{
      label: 'Sales',
      data: this.datas,
      fill: false,
      borderColor: 'rgba(54, 162, 235, 1)',
      pointBorderColor: 'rgba(0,0,0, 1)',
      pointBackgroundColor: '#fff',
      pointBorderWidth: 3,
      pointHoverRadius: 5,
      pointHoverBackgroundColor: 'rgba(54, 162, 235, 1)',
      pointHoverBorderColor: 'rgba(220, 220, 220, 1)',
      pointHoverBorderWidth: 2,
      pointRadius: 1,
      pointHitRadius: 10,
      spanGaps: true,
      tension: 0.2
    }],
    options: {
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: true
          }
        }]
      },
      legend: {
        display: false
      }
    }
  };


  ngOnInit(): void {
    this.chartData = history.state.chartData.slice(1);
    
  
  this.chartData.map((row: any) => {
  // Check if the row is not an empty array
  if (row.length > 1) {
    this.labels.push(row[0] as string); // Cast row[0] to string and push onto labelss
    this.datas.push(Number(row[1]) as number);  // Add the second element of the row as a number to the data array
  }
});
    console.log('Chart Data:', this.chartData);
  
    
  }
  onSubmit() : void{
         this.router.navigate(['/powerbi']);
  }

}