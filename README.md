# Peaky-Finders

This peak load forecasting application provides two resources for New York City building owners, facility managers, and residents interested in tomorrow's total electricity grid demand. The first model is a next-day hourly load curve for the NYISO. The second is a confidence interval representing the percent chance that tomorrow will be a peak load event. 

## Tech Stack

- Python 
- Pandas
- Matplotlib
- Scikit-Learn
- Flask
- Dash 

## Data

For data collection, I used the PYISO open-source library to scrape hourly electricity load data from the NYISO website and the DarkSky API to gather hourly weather data. The models were trained on peak load seasons from 2013 through 2018 and tested on the 2019 peak load season. I defined a peak load season as the days between June 15 and September 15. 

Shown below is the distribution of days and the peak load recorded during that day. 

![Distribution of Summer Days](images/peak_day_distribution.png)

## Load Curve 

The dataset was framed a supervised learning problem in order to compare the performance of a Regression Tree, Random Forest Regressor, and XG Boost algorithms. XG Boost performed the best with a Root Mean Squared Error (RMSE) of 895.14 Megawatts (MW) for the 2019 peak season. As a benchmark, the official NYISO Forecast had a RMSE of 901.05 MW for the first two weeks of September 2019.

# Features


## Peak Day Confidence Interval 

# Features

## Front End App

## Conclusion


- Link to [slideshow](https://docs.google.com/presentation/d/1AdA7OE8VJQxQF6DAVs81xLXPfjvnHUb99oBfRkqpB7M/edit#slide=id.g6bd401033a_0_275) 

## Coming Soon 
- Blog Post 
- Higher accuracy load curve for non-peak season days 
- More nuanced weather inputs
- More ISOs (PJM will be next)
- Customized amount of peak days targeting based on each utility's ICAP tag 
