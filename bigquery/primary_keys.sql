ALTER TABLE `silver-lead-484519-r7.CovidCases.Poverty_and_income_cleaned`
ADD COLUMN fips STRING;

UPDATE `silver-lead-484519-r7.CovidCases.Poverty_and_income_cleaned`
SET fips = CONCAT(State_FIPS_Code, County_FIPS_Code)
WHERE TRUE;

ALTER TABLE `silver-lead-484519-r7.CovidCases.Poverty_and_income_cleaned`
ADD PRIMARY KEY (fips) NOT ENFORCED;

ALTER TABLE `silver-lead-484519-r7.CovidCases.Covid_cases_cleaned`
ADD PRIMARY KEY (fips, date) NOT ENFORCED;

ALTER TABLE `silver-lead-484519-r7.CovidCases.Population_cleaned`
ADD PRIMARY KEY (fips, estimate_date, age_group) NOT ENFORCED;