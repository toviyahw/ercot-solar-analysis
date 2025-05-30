# Solar Energy Data Analysis and Predictive Modeling

## ⭐ Project Overview:
This notebook presents a comprehensive data analysis and machine learning project using solar energy generation and demand data from ERCOT (Electric Reliability Council of Texas) alongside weather data sourced from the NSRDB (National Solar Radiation Database). The primary goals are to explore patterns in solar power production and energy load demand across Texas regions and build predictive models using historical patterns, and weather features. This project was a collaborative effort amongst Katherine Mundey, Ruhama Kabir, Kayla Tran, and myself. Data extraction was done by Katherine Mundey, I executed the data transformation. Ruhama and I focused our efforts on solar energy data, and the rest of the team executed analysis and machine learning on the wind energy data from the same dataset. Though exploratory data analysis is performed, this project is **machine learning focused, with a main goal of accurately predicting solar energy generation**.

## 📊 Dataset Description:
The dataset includes:
- Hourly solar energy generation
- Temperature readings across regions (North, South, East, West)
- Timestamps, load demand data, and derived time features
- Engineered lag features and rolling statistics

**Key Columns**

- `timestamp`: Date and hour when the measurement was recorded (in `YYYY-MM-DD HH:MM:SS` format)
- `solar_system`: System-wide solar energy generation (in megawatts, MW)
- `solar_centereast`, `solar_centerwest`, `solar_farwest`, `solar_fareast`, `solar_farsoutheast`, `solar_northwest`: Regional solar generation values (MW)

**Temperature Features**

- `temp_2m_north`, `temp_2m_south`, `temp_2m_east`, `temp_2m_west`: Air temperature at 2 meters above ground (Kelvin converted to°F) by region

**Energy Load Columns**

- `coast_load`, `east_load`, `farwest_load`, `north_load`, `northcentral_load`, `south_load`, `southcentral_load`, `west_load`, `system_load`: Hourly electricity demand in each region and system-wide (MW)

**Time-Based Features (Engineered)**

- `hour`: Hour of the day (0–23)
- `dayofweek`: Day of the week (0 = Monday, 6 = Sunday)
- `month`: Month of the year (1–12)

**Lag & Rolling Features (Engineered)**

- `lag_1`, `lag_2`, `lag_3`...`lag_168`, .: Solar generation values from prior time steps (1 hour, 1 day, etc.)
- `rolling_mean_6`: Rolling mean of solar_system over the previous 6 hours
- `rolling_std_6`: Rolling standard deviation of solar_system over the previous 6 hours

## 📈 Modeling Approaches:
#### 1. **Recursive Forecasting** (Linear Regression and Gradient Boosting)
- Linear Regression for the baseline model
- Recursive forecast using Gradient Boosting predicts 1 hour at a time, feeds predictions back in
- Two iterations:
  - (1st) Baseline with limited features
  - (2nd) Improved with extended lags, and rolling stats

#### 2. **Direct Forecasting** (MultiOutput Gradient Boosting)
- Predicts the next 24 hours in one step
- Uses `MultiOutputRegressor` to simplify implementation and improve interpretability

## 📌 EDA Summary:
- Distribution of **system load is right-skewed**, and begins to flatten out in values above ~58,000 MW. This suggests that **higher energy demands occur less frequently**.
![Histogram Showing Distribution of System Load Demand](images/sys_load_dist.png) 
- The **NorthCentral and Coat areas had the highest grid demand**, but the **Farwest and Fareast areas generate the most solar energy**.
- The **relationship between temperature and load appears consistent across regions**, with the South region having the highest temperatures and load values.
![Scatter Plot Showing Temperature vs. Load Across 4 Regions](images/temp_vs_load.png) 
- The relationship between temperature and energy generation follows a similar trend across all regions.
- **Note: the regional data sourced from ERCOT (solar energy source) does not completely align with regions outlined by NSRDB (temperature source). ERCOT categorizes its regions as: North, FarWEst, West, South, Coast, etc. NSRDB defines its regions simply as North, South, East ('Houston'), and West. See how the regions overlap and compare below:**
<p align="center">
  <figure style="display: inline-block; text-align: center; margin: 0 10px;">
    <img src="images/ERCOT_region_map.png" alt="ERCOT Region Map" width="42%" />
    <figcaption>ERCOT Region Map</figcaption>
  </figure>
  <figure style="display: inline-block; text-align: center; margin: 0 10px;">
    <img src="images/NSRDB_region_map.png" alt="NSRDB Region Map" width="45%" />
    <figcaption>NSRDB Region Map</figcaption>
  </figure>
</p>

## 📌 Machine Learning Summary:
### Forecasting
- With recursive models, errors tend to compound, and they did not do a great job of accurately predicting solar energy generation. Adding more features did not necessarily result in better predictions.
- The direct models achieved higher stability and better short-horizon accuracy
- Temperature and rolling context features significantly improved performance
- Cross-validation revealed variability tied to seasonal solar dynamics
### Model Performance Comparison

| Forecast Type        | Model               | MAE     | RMSE     | R²     |
|----------------------|---------------------|---------|----------|--------|
| Recursive (v1)       | Linear Regression   | 738.96  | 1159.95  | 0.9330 |
|                      | Gradient Boosting   | 353.14  | 756.59   | 0.9715 |
| Recursive (v2)       | Linear Regression   | 702.36  | 1058.12  | 0.9435 |
|                      | Gradient Boosting   | 334.15  | 687.52   | 0.9762 |
| Direct               | Linear Regression   | 1988.06 | 2607.85  | 0.6429 |
|                      | Gradient Boosting   | 1282.23 | 2099.94  | 0.7738 |

### Evaluation
Cross-validation and test performance measured using:
- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- R² Score
#### Final Cross-Validation Results (Direct Forecasting):
- **Average MAE**: `1250.23`
- **Average R²**: `0.734`
- **Best fold MAE:** `946.74`
- **Best fold R²:** `0.932`

## 📊 Visualizations:
- Actual vs. predicted plot for 1st round of recursive forecasting:
![Forecast vs Actual](images/energy_forecast_vs_actual.png)
- Multi-panel 24-hour forecast comparisons:
![Multi-panel Direct Forecasting Windows 1-6](images/solar_forecast_multi_window.png)

## 🔭 Next Steps:

While I achieved my main goal for this project in executing an end-to-end solar energy forecasting pipeline, there are several directions for further improvement and experimentation:
- **Hyperparameter Tuning**: Perform grid search or randomized search to optimize GradientBoostingRegressor parameters for potentially improved performance.
- **Feature Expansion**: Explore additional weather-based features (cloud cover, humidity, etc. which heavily impact solar energy generation) or lag variables for better modeling of the patterns.
- **Model Comparison**: Evaluate additional models such as XGBoost and LightGBM, or even begin exploring deep learning methods for capturing nonlinear trends.
