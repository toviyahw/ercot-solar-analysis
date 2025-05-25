# ERCOT Solar Data Analysis and Predictive Modeling

## ⭐ Project Overview:
This notebook presents a comprehensive data analysis and machine learning project using solar energy generation and demand data from ERCOT (Electric Reliability Council of Texas). The primary goals are to explore patterns in solar power production and energy load demand across Texas regions and build predictive models using historical patterns, and weather features. This project was a collaborative effort amongst Katherine Mundey, Ruhama Kabir, Kayla Tran, and myself. Data extraction was done by Katherine Mundey, I executed the data transformation. Ruhama and I focused our efforts on solar energy data, and the rest of the team executed analysis and machine learning on the wind energy data from the same dataset. Though exploratory data analysis is performed, this project is **machine learning focused**.

## 📊 Dataset Description:
This dataset contains **hourly solar energy generation data** across various regions in Texas, along with corresponding **temperature**, **energy load**, and **time-based features**. The data is used to explore solar generation patterns and build predictive machine learning models.

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
- `is_weekend`: Binary flag indicating whether the day is a weekend (1) or not (0)

**Lag & Rolling Features (Engineered)**

- `lag_1`, `lag_2`, `lag_3`, `lag_24`, `lag_48`, `lag_168`: Solar generation values from prior time steps (1 hour, 1 day, etc.)
- `rolling_mean_6`: Rolling mean of solar_system over the previous 6 hours
- `rolling_std_6`: Rolling standard deviation of solar_system over the previous 6 hours

## 📌 EDA Summary:

## 📌 Machine Learning Summary:
