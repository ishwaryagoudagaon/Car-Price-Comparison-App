 Car Price Comparison App

A data-driven web application built with Python, Pandas and Streamlit that allows users to explore car listings, filter vehicles based on their preferences, and compare two cars side by side.

The application helps users make more informed decisions when exploring car prices and vehicle specifications.
📌 Project Overview

Buying a car involves comparing several factors, including price, mileage, fuel type, transmission and engine power.

This project provides an interactive platform where users can search for available cars, apply filters and compare two selected vehicles to understand their differences.
✨ Key Features
1. Dashboard Overview

    Displays the total number of car listings.
    Shows the number of available car brands.
    Displays the minimum and maximum car prices.
    Provides an overview of available brands.

2. Search Your Car

Users can filter car listings based on:

    Brand
    Model
    Fuel type
    Budget range

The application displays matching vehicles with relevant specifications and seller information where available.
3. Compare Two Cars

    Select two cars independently.
    Apply different filters for each car.
    Find matching listings.
    Select the exact vehicles to compare.
    View prices and specifications side by side.
    Identify the price difference between the selected cars.

4. Data Quality and Cleaning

Data quality checks were performed to improve the reliability of the dataset.

The cleaning process included:

    Removing car listings priced below €2,500.
    Checking and removing duplicate records.
    Identifying missing brand values.
    Checking invalid mileage values.
    Analysing missing values across columns.
    Validating important data fields used in the application.

🛠️ Technologies Used
Technology 	Purpose
Python 	Programming language
Pandas 	Data cleaning and manipulation
Streamlit 	Interactive web application
CSV 	Dataset storage
Git & GitHub 	Version control and project hosting
📂 Project Structure

car_price_app/
│
├── app.py
├── cars_cleaned_final.csv.gz
├── requirements.txt
└──inspect_car_details.ipynb
└── README.md
└── .gitattributes



⚙️ Installation and Setup
Step 1: Clone the repository

git clone YOUR_GITHUB_REPOSITORY_URL

Step 2: Navigate to the project folder

cd car_price_app

Step 3: Install dependencies

pip install -r requirements.txt

Step 4: Run the Streamlit application

streamlit run app.py

Skills demonstrated: Python | Pandas | Data Cleaning | Streamlit | Data Analytics | GitHub

The application will open in your browser.
📊 Dataset

The application uses a cleaned car listings dataset stored in:

cars_cleaned_final.csv

The dataset contains information about car listings, including vehicle brands, models, prices and specifications.

A minimum price threshold of €2,500 is applied to exclude lower-priced listings from the cleaned dataset.
🎯 Project Objectives

    Apply Python and Pandas skills to a real-world dataset.
    Perform data cleaning and data quality checks.
    Build an interactive dashboard using Streamlit.
    Develop practical car search and comparison functionality.
    Present data in a clear and user-friendly format.

🚀 Future Improvements

Potential enhancements include:

    Adding car images.
    Introducing additional search and sorting options.
    Adding interactive price distribution charts.
    Providing more detailed vehicle comparisons.
    Deploying the application online.
    Improving the user interface and experience.
