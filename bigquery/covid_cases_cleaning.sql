CREATE OR REPLACE TABLE `silver-lead-484519-r7.CovidCases.Covid_cases_cleaned` AS
SELECT
  
  date,
  
  
  county,
  state,
  

  LPAD(CAST(fips AS STRING), 5, '0') AS fips,
  
  
  cases,

  deaths

FROM `silver-lead-484519-r7.CovidCases.Covid Cases`;