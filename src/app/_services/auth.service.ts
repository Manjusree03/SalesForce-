import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor(private router:Router,private http:HttpClient) { }
  isAuthenticated():boolean{
    if(sessionStorage.getItem('token')!==null){
      return true;
    }
    return false;
  }
  canAccess(){
    if(!this.isAuthenticated()){
      //redirect to login
      this.router.navigate(['/login']); 

    }
  }
  register(name:string,email:string,password:string){
     return this.http
     .post<{idToken:string}>('https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=AIzaSyBQUH3BgzD-daKmmRDOAweg_j8cVA8XcRY',
     {displayName:name,email:email,password:password} 
     );
  }
  storeToken(token:string){
    sessionStorage.setItem('token',token);
  }
  login(email:string,password:string){
       return this.http 
       .post<{idToken:string}>('https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyBQUH3BgzD-daKmmRDOAweg_j8cVA8XcRY',
       {email:email,password:password}
       );
  }
  canAuthenticate(){
    if(this.isAuthenticated()){
      //redirect to dashboard
      this.router.navigate(['/dashboard']); 

    }
  }
  removeToken(){
    sessionStorage.removeItem('token');
  }
}
