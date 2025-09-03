- clock on / clock off only happen at the start and end of working hours
- break start must be start earliest after 3 hours of working and end before 6 hours of working


In this problem, you need to export the start and end time for verification process. The json format would be 
```bash
{
    trips: [{
        nr: int,
        driver: str,
        train: str,
        departure: int,  
        arrival: int     
    }, ... ],
    drivers: [{
        name: str,
        work_start: int,  
        work_end: int     
    }
}
```