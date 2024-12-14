# stratosphere
Cloud Service Access Management System

## CPSC 449 Web Backend Engineering 

## Authors: 
         Kiran Sukumar, kiransukumar@csu.fullerton.edu
         Hisham Panamthodi Kajahussain, hisham.pk@csu.fullerton.edu

## Installation and setup:
Instal the packages listed in requirements.txt file in the terminal using
``` 
pip install -r /path/to/requirements.txt
```
## Database Configuration:
Configure the MySQL database using the below code
```
DATABASE_URL = "mysql+pymysql://username:password@localhost:3306/stratosphere"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

## Authentication and Authorization:
Implemented authentication and authorization using JWT. Related implementation is available in auth.py

## Run the application:
In the terminal, run the following command. The application will run on localhost port 8000
```
uvicorn app:app --reload
```
## Endpoints:
![image](image.png)
![image](image-1.png)