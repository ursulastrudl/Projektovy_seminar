CREATE OR REPLACE TABLE `silver-lead-484519-r7.CovidCases.master_data_for_cleverminer` AS
SELECT 

  c.date,
  c.county,
  c.state,
  c.fips,
  c.cases,
  c.deaths,
  
  p.State_FIPS_Code,
  p.County_FIPS_Code,
  p.poverty_estimate_all_ages,
  p.poverty_percent_all_ages,
  p.ci_lower_all_ages,
  p.ci_upper_all_ages,
  p.ci_lower_all_ages_pct,
  p.ci_upper_all_ages_pct,
  p.median_household_income,
  p.ci_lower_median_income,
  p.ci_upper_median_income,
  
  p.poverty_estimate_age_0_17,
  p.poverty_percent_age_0_17,
  p.ci_lower_age_0_17,
  p.ci_upper_age_0_17,
  p.ci_lower_age_0_17_pct,
  p.ci_upper_age_0_17_pct,

  p.poverty_estimate_age_5_17_families,
  p.poverty_percent_age_5_17_families,
  p.ci_lower_age_5_17_families,
  p.ci_upper_age_5_17_families,
  p.ci_lower_age_5_17_families_pct,
  p.ci_upper_age_5_17_families_pct,

  p.poverty_estimate_age_0_4,
  p.poverty_percent_age_0_4,
  p.ci_lower_age_0_4,
  p.ci_upper_age_0_4,
  p.ci_lower_age_0_4_pct,
  p.ci_upper_age_0_4_pct,
  

  pop.age_group,  
  pop.estimate_date AS population_estimate_date,
  pop.year_code AS population_year_code,
  pop.total_population,
  pop.total_male,
  pop.total_female,
  
  pop.white_alone_male,
  pop.white_alone_female,
  pop.black_alone_male,
  pop.black_alone_female,
  pop.asian_alone_male,
  pop.asian_alone_female,
  pop.indian_alaska_alone_male,
  pop.indian_alaska_alone_female,
  pop.hawaiian_pacific_alone_male,
  pop.hawaiian_pacific_alone_female,
  pop.two_or_more_races_male,
  pop.two_or_more_races_female,
  
  -- Hispanská populace
  pop.hispanic_male,
  pop.hispanic_female,
  pop.not_hispanic_male,
  pop.not_hispanic_female,
  

  -- COVID metriky na 100,000 obyvatel
  ROUND(SAFE_DIVIDE(c.cases * 100000, pop.total_population), 2) AS cases_per_100k,
  ROUND(SAFE_DIVIDE(c.deaths * 100000, pop.total_population), 2) AS deaths_per_100k,
  
  -- Case Fatality Rate (CFR) - procento úmrtí z případů
  ROUND(SAFE_DIVIDE(c.deaths * 100, NULLIF(c.cases, 0)), 2) AS case_fatality_rate_pct,
  
  -- Populační metriky
  ROUND(SAFE_DIVIDE(pop.total_female * 100, pop.total_population), 2) AS female_percentage,
  ROUND(SAFE_DIVIDE(pop.total_male * 100, pop.total_population), 2) AS male_percentage,
  
  -- Rasové složení (procenta z celkové populace)
  ROUND(SAFE_DIVIDE((pop.white_alone_male + pop.white_alone_female) * 100, pop.total_population), 2) AS white_alone_pct,
  ROUND(SAFE_DIVIDE((pop.black_alone_male + pop.black_alone_female) * 100, pop.total_population), 2) AS black_alone_pct,
  ROUND(SAFE_DIVIDE((pop.asian_alone_male + pop.asian_alone_female) * 100, pop.total_population), 2) AS asian_alone_pct,
  ROUND(SAFE_DIVIDE((pop.hispanic_male + pop.hispanic_female) * 100, pop.total_population), 2) AS hispanic_pct,
  
  -- Kategorie chudoby 
  CASE 
    WHEN p.poverty_percent_all_ages IS NULL THEN 'Unknown'
    WHEN p.poverty_percent_all_ages < 10 THEN 'Low (<10%)'
    WHEN p.poverty_percent_all_ages < 15 THEN 'Medium (10-15%)'
    WHEN p.poverty_percent_all_ages < 20 THEN 'High (15-20%)'
    ELSE 'Very High (20%+)'
  END AS poverty_category,
  
  -- Kategorie příjmu
  CASE 
    WHEN p.median_household_income IS NULL THEN 'Unknown'
    WHEN p.median_household_income < 40000 THEN 'Low (<40k)'
    WHEN p.median_household_income < 60000 THEN 'Medium (40-60k)'
    WHEN p.median_household_income < 80000 THEN 'High (60-80k)'
    ELSE 'Very High (80k+)'
  END AS income_category,
  

  EXTRACT(YEAR FROM c.date) AS year,
  EXTRACT(MONTH FROM c.date) AS month,
  EXTRACT(QUARTER FROM c.date) AS quarter,
  EXTRACT(DAYOFWEEK FROM c.date) AS day_of_week,
  EXTRACT(WEEK FROM c.date) AS week_of_year

FROM `silver-lead-484519-r7.CovidCases.Covid_cases_cleaned` c


LEFT JOIN `silver-lead-484519-r7.CovidCases.Poverty_and_income_cleaned` p
  ON p.fips = c.fips

LEFT JOIN `silver-lead-484519-r7.CovidCases.Population_cleaned` pop
  ON pop.fips = c.fips
  AND pop.year_code = 2  -- 1/2 roku 2020
  AND pop.age_group = 0  -- Celková populace (všechny věky dohromady)

-- FILTR: Jen rok 2020
WHERE EXTRACT(YEAR FROM c.date) = 2020;
