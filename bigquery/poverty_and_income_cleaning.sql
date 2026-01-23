
CREATE OR REPLACE TABLE `silver-lead-484519-r7.CovidCases.Poverty_and_income_cleaned` AS
SELECT
  LPAD(CAST(`State FIPS Code` AS STRING), 2, '0') AS State_FIPS_Code,
  LPAD(CAST(`County FIPS Code` AS STRING), 3, '0') AS County_FIPS_Code,
  `Postal Code`,
  `Name`,
  

  SAFE_CAST(REPLACE(REPLACE(`Poverty Estimate_All Ages`, ' ', ''), ',', '.') AS INT64) AS poverty_estimate_all_ages,
  SAFE_CAST(REPLACE(REPLACE(`90% CI Lower Bound_All ages`, ' ', ''), ',', '.') AS INT64) AS ci_lower_all_ages,
  SAFE_CAST(REPLACE(REPLACE(`90% CI Upper Bound_All ages`, ' ', ''), ',', '.') AS INT64) AS ci_upper_all_ages,
  
  -- Poverty percentages jako FLOAT64 (procenta)
  SAFE_CAST(REPLACE(REPLACE(`Poverty Percent_All Ages`, ' ', ''), ',', '.') AS FLOAT64) AS poverty_percent_all_ages,
  SAFE_CAST(REPLACE(REPLACE(`90% CI Lower Bound_All ages_percentage`, ' ', ''), ',', '.') AS FLOAT64) AS ci_lower_all_ages_pct,
  SAFE_CAST(REPLACE(REPLACE(`90% CI Upper Bound_All ages_percentage`, ' ', ''), ',', '.') AS FLOAT64) AS ci_upper_all_ages_pct,
  
  -- Age 0-17 estimates
  SAFE_CAST(REPLACE(REPLACE(`Poverty Estimate_Age 0-17`, ' ', ''), ',', '.') AS INT64) AS poverty_estimate_age_0_17,
  SAFE_CAST(REPLACE(REPLACE(`90% CI Lower Bound_Age 0-17`, ' ', ''), ',', '.') AS INT64) AS ci_lower_age_0_17,
  SAFE_CAST(REPLACE(REPLACE(`90% CI Upper Bound_Age 0-17`, ' ', ''), ',', '.') AS INT64) AS ci_upper_age_0_17,
  
  -- Age 0-17 percentages
  SAFE_CAST(REPLACE(REPLACE(`Poverty Percent_Age 0-17`, ' ', ''), ',', '.') AS FLOAT64) AS poverty_percent_age_0_17,
  SAFE_CAST(REPLACE(REPLACE(`90% CI Lower Bound_Age 0-17_percentage`, ' ', ''), ',', '.') AS FLOAT64) AS ci_lower_age_0_17_pct,
  SAFE_CAST(REPLACE(REPLACE(`90% CI Upper Bound_Age 0-17_percentage`, ' ', ''), ',', '.') AS FLOAT64) AS ci_upper_age_0_17_pct,
  
  -- Age 5-17 in Families estimates
  SAFE_CAST(REPLACE(REPLACE(`Poverty Estimate_Age 5-17 in Families`, ' ', ''), ',', '.') AS INT64) AS poverty_estimate_age_5_17_families,
  SAFE_CAST(REPLACE(REPLACE(`90% CI Lower Bound_Age 5-17 in Families`, ' ', ''), ',', '.') AS INT64) AS ci_lower_age_5_17_families,
  SAFE_CAST(REPLACE(REPLACE(`90% CI Upper Bound_Age 5-17 in Families`, ' ', ''), ',', '.') AS INT64) AS ci_upper_age_5_17_families,
  
  -- Age 5-17 in Families percentages
  SAFE_CAST(REPLACE(REPLACE(`Poverty Percent_Age 5-17 in Families`, ' ', ''), ',', '.') AS FLOAT64) AS poverty_percent_age_5_17_families,
  SAFE_CAST(REPLACE(REPLACE(`90% CI Lower Bound_Age 5-17 in Families_percentage`, ' ', ''), ',', '.') AS FLOAT64) AS ci_lower_age_5_17_families_pct,
  SAFE_CAST(REPLACE(REPLACE(`90% CI Upper Bound_Age 5-17 in Families_percentage`, ' ', ''), ',', '.') AS FLOAT64) AS ci_upper_age_5_17_families_pct,
  
  -- Median Household Income
  SAFE_CAST(REPLACE(REPLACE(`Median Household Income`, ' ', ''), ',', '.') AS INT64) AS median_household_income,
  SAFE_CAST(REPLACE(REPLACE(`90% CI Lower Bound_Median Household Income`, ' ', ''), ',', '.') AS INT64) AS ci_lower_median_income,
  SAFE_CAST(REPLACE(REPLACE(`90% CI Upper Bound_Median Household Income`, ' ', ''), ',', '.') AS INT64) AS ci_upper_median_income,
  
  -- Age 0-4 estimates
  SAFE_CAST(REPLACE(REPLACE(`Poverty Estimate_Age 0-4`, ' ', ''), ',', '.') AS INT64) AS poverty_estimate_age_0_4,
  SAFE_CAST(REPLACE(REPLACE(`90% CI Lower Bound_Age 0-4`, ' ', ''), ',', '.') AS INT64) AS ci_lower_age_0_4,
  SAFE_CAST(REPLACE(REPLACE(`90% CI Upper Bound_Age 0-4`, ' ', ''), ',', '.') AS INT64) AS ci_upper_age_0_4,
  
  -- Age 0-4 percentages
  SAFE_CAST(REPLACE(REPLACE(`Poverty Percent_Age 0-4`, ' ', ''), ',', '.') AS FLOAT64) AS poverty_percent_age_0_4,
  SAFE_CAST(REPLACE(REPLACE(`90% CI Lower Bound_Age 0-4_percentage`, ' ', ''), ',', '.') AS FLOAT64) AS ci_lower_age_0_4_pct,
  SAFE_CAST(REPLACE(REPLACE(`90% CI Upper Bound_Age 0-4_percentage`, ' ', ''), ',', '.') AS FLOAT64) AS ci_upper_age_0_4_pct

FROM `silver-lead-484519-r7.CovidCases.Poverty and income`;