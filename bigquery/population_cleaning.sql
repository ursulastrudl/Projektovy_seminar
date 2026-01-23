
CREATE OR REPLACE TABLE `silver-lead-484519-r7.CovidCases.Population_cleaned` AS
SELECT
  -- STATE a COUNTY jako STRING s vedoucími nulami
  LPAD(CAST(STATE AS STRING), 2, '0') AS state_fips,
  LPAD(CAST(COUNTY AS STRING), 3, '0') AS county_fips,
  
  -- Vytvoření kombinovaného FIPS kódu (5 číslic)
  CONCAT(LPAD(CAST(STATE AS STRING), 2, '0'), LPAD(CAST(COUNTY AS STRING), 3, '0')) AS fips,
  
  -- Názvy států a okresů
  STNAME AS state_name,
  CTYNAME AS county_name,
  
  -- Datum odhadu populace (převedeno z YEAR kódu)
  DATE('2020-07-01') AS estimate_date,
  
  YEAR AS year_code, 
  AGEGRP AS age_group,
  

  
  -- Celková populace
  TOT_POP AS total_population,
  TOT_MALE AS total_male,
  TOT_FEMALE AS total_female,
  
  -- White Alone (WA)
  WA_MALE AS white_alone_male,
  WA_FEMALE AS white_alone_female,
  
  -- Black or African American Alone (BA)
  BA_MALE AS black_alone_male,
  BA_FEMALE AS black_alone_female,
  
  -- American Indian and Alaska Native Alone (IA)
  IA_MALE AS indian_alaska_alone_male,
  IA_FEMALE AS indian_alaska_alone_female,
  
  -- Asian Alone (AA)
  AA_MALE AS asian_alone_male,
  AA_FEMALE AS asian_alone_female,
  
  -- Native Hawaiian and Other Pacific Islander Alone (NA)
  NA_MALE AS hawaiian_pacific_alone_male,
  NA_FEMALE AS hawaiian_pacific_alone_female,
  
  -- Two or More Races (TOM)
  TOM_MALE AS two_or_more_races_male,
  TOM_FEMALE AS two_or_more_races_female,
  
  -- White Alone or in Combination (WAC)
  WAC_MALE AS white_combination_male,
  WAC_FEMALE AS white_combination_female,
  
  -- Black or African American Alone or in Combination (BAC)
  BAC_MALE AS black_combination_male,
  BAC_FEMALE AS black_combination_female,
  
  -- American Indian and Alaska Native Alone or in Combination (IAC)
  IAC_MALE AS indian_alaska_combination_male,
  IAC_FEMALE AS indian_alaska_combination_female,
  
  -- Asian Alone or in Combination (AAC)
  AAC_MALE AS asian_combination_male,
  AAC_FEMALE AS asian_combination_female,
  
  -- Native Hawaiian and Other Pacific Islander Alone or in Combination (NAC)
  NAC_MALE AS hawaiian_pacific_combination_male,
  NAC_FEMALE AS hawaiian_pacific_combination_female,
  
  -- Not Hispanic (NH)
  NH_MALE AS not_hispanic_male,
  NH_FEMALE AS not_hispanic_female,
  
  -- Not Hispanic, White Alone (NHWA)
  NHWA_MALE AS not_hispanic_white_alone_male,
  NHWA_FEMALE AS not_hispanic_white_alone_female,
  
  -- Not Hispanic, Black or African American Alone (NHBA)
  NHBA_MALE AS not_hispanic_black_alone_male,
  NHBA_FEMALE AS not_hispanic_black_alone_female,
  
  -- Not Hispanic, American Indian and Alaska Native Alone (NHIA)
  NHIA_MALE AS not_hispanic_indian_alaska_alone_male,
  NHIA_FEMALE AS not_hispanic_indian_alaska_alone_female,
  
  -- Not Hispanic, Asian Alone (NHAA)
  NHAA_MALE AS not_hispanic_asian_alone_male,
  NHAA_FEMALE AS not_hispanic_asian_alone_female,
  
  -- Not Hispanic, Native Hawaiian and Other Pacific Islander Alone (NHNA)
  NHNA_MALE AS not_hispanic_hawaiian_pacific_alone_male,
  NHNA_FEMALE AS not_hispanic_hawaiian_pacific_alone_female,
  
  -- Not Hispanic, Two or More Races (NHTOM)
  NHTOM_MALE AS not_hispanic_two_or_more_races_male,
  NHTOM_FEMALE AS not_hispanic_two_or_more_races_female,
  
  -- Not Hispanic, White Alone or in Combination (NHWAC)
  NHWAC_MALE AS not_hispanic_white_combination_male,
  NHWAC_FEMALE AS not_hispanic_white_combination_female,
  
  -- Not Hispanic, Black or African American Alone or in Combination (NHBAC)
  NHBAC_MALE AS not_hispanic_black_combination_male,
  NHBAC_FEMALE AS not_hispanic_black_combination_female,
  
  -- Not Hispanic, American Indian and Alaska Native Alone or in Combination (NHIAC)
  NHIAC_MALE AS not_hispanic_indian_alaska_combination_male,
  NHIAC_FEMALE AS not_hispanic_indian_alaska_combination_female,
  
  -- Not Hispanic, Asian Alone or in Combination (NHAAC)
  NHAAC_MALE AS not_hispanic_asian_combination_male,
  NHAAC_FEMALE AS not_hispanic_asian_combination_female,
  
  -- Not Hispanic, Native Hawaiian and Other Pacific Islander Alone or in Combination (NHNAC)
  NHNAC_MALE AS not_hispanic_hawaiian_pacific_combination_male,
  NHNAC_FEMALE AS not_hispanic_hawaiian_pacific_combination_female,
  
  -- Hispanic (H)
  H_MALE AS hispanic_male,
  H_FEMALE AS hispanic_female,
  
  -- Hispanic, White Alone (HWA)
  HWA_MALE AS hispanic_white_alone_male,
  HWA_FEMALE AS hispanic_white_alone_female,
  
  -- Hispanic, Black or African American Alone (HBA)
  HBA_MALE AS hispanic_black_alone_male,
  HBA_FEMALE AS hispanic_black_alone_female,
  
  -- Hispanic, American Indian and Alaska Native Alone (HIA)
  HIA_MALE AS hispanic_indian_alaska_alone_male,
  HIA_FEMALE AS hispanic_indian_alaska_alone_female,
  
  -- Hispanic, Asian Alone (HAA)
  HAA_MALE AS hispanic_asian_alone_male,
  HAA_FEMALE AS hispanic_asian_alone_female,
  
  -- Hispanic, Native Hawaiian and Other Pacific Islander Alone (HNA)
  HNA_MALE AS hispanic_hawaiian_pacific_alone_male,
  HNA_FEMALE AS hispanic_hawaiian_pacific_alone_female,
  
  -- Hispanic, Two or More Races (HTOM)
  HTOM_MALE AS hispanic_two_or_more_races_male,
  HTOM_FEMALE AS hispanic_two_or_more_races_female,
  
  -- Hispanic, White Alone or in Combination (HWAC)
  HWAC_MALE AS hispanic_white_combination_male,
  HWAC_FEMALE AS hispanic_white_combination_female,
  
  -- Hispanic, Black or African American Alone or in Combination (HBAC)
  HBAC_MALE AS hispanic_black_combination_male,
  HBAC_FEMALE AS hispanic_black_combination_female,
  
  -- Hispanic, American Indian and Alaska Native Alone or in Combination (HIAC)
  HIAC_MALE AS hispanic_indian_alaska_combination_male,
  HIAC_FEMALE AS hispanic_indian_alaska_combination_female,
  
  -- Hispanic, Asian Alone or in Combination (HAAC)
  HAAC_MALE AS hispanic_asian_combination_male,
  HAAC_FEMALE AS hispanic_asian_combination_female,
  
  -- Hispanic, Native Hawaiian and Other Pacific Islander Alone or in Combination (HNAC)
  HNAC_MALE AS hispanic_hawaiian_pacific_combination_male,
  HNAC_FEMALE AS hispanic_hawaiian_pacific_combination_female

FROM `silver-lead-484519-r7.CovidCases.Population`
WHERE YEAR = 2; 
