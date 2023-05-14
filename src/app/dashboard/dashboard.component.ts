import { Component , OnInit} from '@angular/core';
import { AuthService } from '../_services/auth.service';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { timer } from 'rxjs';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit{
  private file!: File;
  private periodicity!: string;
  private periods!: number;
  csvData: string[][]=[]
  timerValue: number = 120; // time in seconds
  timerId: any;

  

constructor(private auth:AuthService,private http: HttpClient,private router: Router){

}

  ngOnInit(): void{
this.auth.canAccess();
this.startTimer();
  }

  startTimer() {
    this.timerId = setInterval(() => {
      this.timerValue--;
      const timerElement = document.getElementById("timer");
      if (timerElement) {
        const minutes = Math.floor(this.timerValue / 60);
        const seconds = this.timerValue % 60;
        const displayValue = minutes.toString().padStart(2, '0') + ":" + seconds.toString().padStart(2, '0');
        timerElement.innerText = displayValue;
        if (this.timerValue <= 0) {
          clearInterval(this.timerId);
        }
      }
    }, 1000); // interval of 1 second
  }
  
  onFileSelected(event: any): void {
    this.file = event.target.files[0];
  }

  onSubmit(): void {
    const formData = new FormData();
    formData.append('csvFile', this.file);
    formData.append('periodicity', this.periodicity);
    formData.append('periods', this.periods.toString());

    this.http.post('http://127.0.0.1:5000/', formData, { responseType: 'text' }).subscribe(
      (response) => {
        console.log('File uploaded successfully');
        this.csvData = this.parseCSV(response)
       
        this.router.navigate(['/predict'], { state: { chartData: this.csvData } });
    
      },
      (error) => {
        console.error('File upload failed',error.message);
      }
    );
  }
  onPeriodicityChange(event: any): void {
    this.periodicity = event.target.value;
  }

  onPeriodsChange(event: any): void {
    this.periods = event.target.value;
  }
  private parseCSV(csv: string): string[][] {
    const rows: string[] = csv.split('\n');
    const data: string[][] = [];
    rows.forEach(row => {
      data.push(row.split(','));
    });
    return data;
  }

  

  
}