CREATE EXTERNAL TABLE samhsa_master_db.teds_a_fact_raw (
  ADMYR INT,
  AGE INT,
  SEX INT,
  SUB1 INT,
  ROUTE1 INT,
  FREQ1 INT,
  FRSTUSE1 INT,
  SERVICES INT,
  PSYPROB INT,
  STFIPS INT,
  RACE INT,
  ETHNIC INT,
  EDUC INT,
  EMPLOY INT,
  MARSTAT INT,
  PSOURCE INT,
  PRIMPAY INT,
  HLTHINS INT,
  DAYWAIT INT,
  DSMCRIT INT,
  SUB2 INT,
  SUB3 INT,
  ALCFLG INT,
  MARFLG INT,
  COKEFLG INT,
  HERFLG INT,
  METHFLG INT,
  BENZFLG INT,
  OTHERFLG INT,
  VET INT
)
STORED AS PARQUET
LOCATION 's3://samhsa-datalake-2021-2023-depi/teds_a_data/';

------------------------------------------------------------------------
CREATE OR REPLACE VIEW samhsa_master_db.teds_a_decoded_view AS
SELECT 
    ADMYR AS Admission_Year,

    -- 1. Age Groups (AGE)
    CASE 
        WHEN AGE = 1 THEN '12-14 years'
        WHEN AGE = 2 THEN '15-17 years'
        WHEN AGE = 3 THEN '18-20 years'
        WHEN AGE = 4 THEN '21-24 years'
        WHEN AGE = 5 THEN '25-29 years'
        WHEN AGE = 6 THEN '30-34 years'
        WHEN AGE = 7 THEN '35-39 years'
        WHEN AGE = 8 THEN '40-44 years'
        WHEN AGE = 9 THEN '45-49 years'
        WHEN AGE = 10 THEN '50-54 years'
        WHEN AGE = 11 THEN '55-64 years'
        WHEN AGE = 12 THEN '65 years and older'
        ELSE 'Unknown'
    END AS Age_Group,
    
    -- 2. Sex (SEX)
    CASE 
        WHEN SEX = 1 THEN 'Male'
        WHEN SEX = 2 THEN 'Female'
        ELSE 'Unknown'
    END AS Gender,

    -- 3. Primary Substance (SUB1)
    CASE 
        WHEN SUB1 = 1 THEN 'None'
        WHEN SUB1 = 2 THEN 'Alcohol'
        WHEN SUB1 = 3 THEN 'Cocaine/crack'
        WHEN SUB1 = 4 THEN 'Marijuana/hashish'
        WHEN SUB1 = 5 THEN 'Heroin'
        WHEN SUB1 = 6 THEN 'Non-prescription methadone'
        WHEN SUB1 = 7 THEN 'Other opiates and synthetics'
        WHEN SUB1 = 8 THEN 'PCP'
        WHEN SUB1 = 9 THEN 'Hallucinogens'
        WHEN SUB1 = 10 THEN 'Methamphetamine/speed'
        WHEN SUB1 = 11 THEN 'Other amphetamines'
        WHEN SUB1 = 12 THEN 'Other stimulants'
        WHEN SUB1 = 13 THEN 'Benzodiazepines'
        WHEN SUB1 = 14 THEN 'Other tranquilizers'
        WHEN SUB1 = 15 THEN 'Barbiturates'
        WHEN SUB1 = 16 THEN 'Other sedatives or hypnotics'
        WHEN SUB1 = 17 THEN 'Inhalants'
        WHEN SUB1 = 18 THEN 'Over-the-counter medications'
        WHEN SUB1 = 19 THEN 'Other drugs'
        ELSE 'Unknown'
    END AS Primary_Substance,

    -- 4. Route of Administration Primary (ROUTE1)
    CASE 
        WHEN ROUTE1 = 1 THEN 'Oral'
        WHEN ROUTE1 = 2 THEN 'Smoking'
        WHEN ROUTE1 = 3 THEN 'Inhalation'
        WHEN ROUTE1 = 4 THEN 'Injection'
        WHEN ROUTE1 = 5 THEN 'Other'
        ELSE 'Unknown'
    END AS Primary_Route,

    -- 5. Frequency of Use Primary (FREQ1)
    CASE 
        WHEN FREQ1 = 1 THEN 'No use in the past month'
        WHEN FREQ1 = 2 THEN 'Some use'
        WHEN FREQ1 = 3 THEN 'Daily use'
        ELSE 'Unknown'
    END AS Primary_Frequency,

    -- 6. Age at First Use Primary (FRSTUSE1)
    CASE 
        WHEN FRSTUSE1 = 1 THEN '11 years and under'
        WHEN FRSTUSE1 = 2 THEN '12-14 years'
        WHEN FRSTUSE1 = 3 THEN '15-17 years'
        WHEN FRSTUSE1 = 4 THEN '18-20 years'
        WHEN FRSTUSE1 = 5 THEN '21-24 years'
        WHEN FRSTUSE1 = 6 THEN '25-29 years'
        WHEN FRSTUSE1 = 7 THEN '30 years and older'
        ELSE 'Unknown'
    END AS Primary_Age_At_First_Use,

    -- 7. Type of Treatment Service/Setting (SERVICES)
    CASE 
        WHEN SERVICES = 1 THEN 'Detox, 24-hour, hospital inpatient'
        WHEN SERVICES = 2 THEN 'Detox, 24-hour, free-standing residential'
        WHEN SERVICES = 3 THEN 'Rehab/residential, hospital (non-detox)'
        WHEN SERVICES = 4 THEN 'Rehab/residential, short term (30 days or fewer)'
        WHEN SERVICES = 5 THEN 'Rehab/residential, long term (more than 30 days)'
        WHEN SERVICES = 6 THEN 'Ambulatory, intensive outpatient'
        WHEN SERVICES = 7 THEN 'Ambulatory, non-intensive outpatient'
        WHEN SERVICES = 8 THEN 'Ambulatory, detoxification'
        ELSE 'Unknown'
    END AS Service_Setting,

    -- 8. Co-occurring Mental and Substance Use Disorders (PSYPROB)
    CASE 
        WHEN PSYPROB = 1 THEN 'Yes'
        WHEN PSYPROB = 2 THEN 'No'
        ELSE 'Unknown'
    END AS Co_Occurring_Mental_Disorder,

    -- 9. Census State FIPS Code (STFIPS)
    CASE 
        WHEN STFIPS = 1 THEN 'Alabama'
        WHEN STFIPS = 2 THEN 'Alaska'
        WHEN STFIPS = 4 THEN 'Arizona'
        WHEN STFIPS = 5 THEN 'Arkansas'
        WHEN STFIPS = 6 THEN 'California'
        WHEN STFIPS = 8 THEN 'Colorado'
        WHEN STFIPS = 9 THEN 'Connecticut'
        WHEN STFIPS = 11 THEN 'District of Columbia'
        WHEN STFIPS = 12 THEN 'Florida'
        WHEN STFIPS = 13 THEN 'Georgia'
        WHEN STFIPS = 15 THEN 'Hawaii'
        WHEN STFIPS = 16 THEN 'Idaho'
        WHEN STFIPS = 17 THEN 'Illinois'
        WHEN STFIPS = 18 THEN 'Indiana'
        WHEN STFIPS = 19 THEN 'Iowa'
        WHEN STFIPS = 20 THEN 'Kansas'
        WHEN STFIPS = 21 THEN 'Kentucky'
        WHEN STFIPS = 22 THEN 'Louisiana'
        WHEN STFIPS = 23 THEN 'Maine'
        WHEN STFIPS = 24 THEN 'Maryland'
        WHEN STFIPS = 25 THEN 'Massachusetts'
        WHEN STFIPS = 26 THEN 'Michigan'
        WHEN STFIPS = 27 THEN 'Minnesota'
        WHEN STFIPS = 28 THEN 'Mississippi'
        WHEN STFIPS = 29 THEN 'Missouri'
        WHEN STFIPS = 30 THEN 'Montana'
        WHEN STFIPS = 31 THEN 'Nebraska'
        WHEN STFIPS = 32 THEN 'Nevada'
        WHEN STFIPS = 33 THEN 'New Hampshire'
        WHEN STFIPS = 34 THEN 'New Jersey'
        WHEN STFIPS = 35 THEN 'New Mexico'
        WHEN STFIPS = 36 THEN 'New York'
        WHEN STFIPS = 37 THEN 'North Carolina'
        WHEN STFIPS = 38 THEN 'North Dakota'
        WHEN STFIPS = 39 THEN 'Ohio'
        WHEN STFIPS = 40 THEN 'Oklahoma'
        WHEN STFIPS = 41 THEN 'Oregon'
        WHEN STFIPS = 42 THEN 'Pennsylvania'
        WHEN STFIPS = 44 THEN 'Rhode Island'
        WHEN STFIPS = 46 THEN 'South Dakota'
        WHEN STFIPS = 47 THEN 'Tennessee'
        WHEN STFIPS = 48 THEN 'Texas'
        WHEN STFIPS = 49 THEN 'Utah'
        WHEN STFIPS = 50 THEN 'Vermont'
        WHEN STFIPS = 51 THEN 'Virginia'
        WHEN STFIPS = 53 THEN 'Washington'
        WHEN STFIPS = 55 THEN 'Wisconsin'
        WHEN STFIPS = 56 THEN 'Wyoming'
        WHEN STFIPS = 72 THEN 'Puerto Rico'
        ELSE 'Unknown'
    END AS State_Name,

    -- 10. Race (RACE)
    CASE 
        WHEN RACE = 1 THEN 'Alaska Native (Aleut, Eskimo)'
        WHEN RACE = 2 THEN 'American Indian (other than Alaska Native)'
        WHEN RACE = 3 THEN 'Asian or Pacific Islander'
        WHEN RACE = 4 THEN 'Black or African American'
        WHEN RACE = 5 THEN 'White'
        WHEN RACE = 6 THEN 'Asian'
        WHEN RACE = 7 THEN 'Other single race'
        WHEN RACE = 8 THEN 'Two or more races'
        WHEN RACE = 9 THEN 'Native Hawaiian or Other Pacific Islander'
        ELSE 'Unknown'
    END AS Race_Category,

    -- 11. Ethnicity (ETHNIC)
    CASE 
        WHEN ETHNIC = 1 THEN 'Puerto Rican'
        WHEN ETHNIC = 2 THEN 'Mexican'
        WHEN ETHNIC = 3 THEN 'Cuban or other specific Hispanic'
        WHEN ETHNIC = 4 THEN 'Not of Hispanic or Latino origin'
        WHEN ETHNIC = 5 THEN 'Hispanic or Latino, specific origin not specified'
        ELSE 'Unknown'
    END AS Ethnicity,

    -- 12. Education (EDUC)
    CASE 
        WHEN EDUC = 1 THEN 'Kindergarten to Grade 8'
        WHEN EDUC = 2 THEN 'Grades 9 to 11'
        WHEN EDUC = 3 THEN 'Grade 12 (or GED)'
        WHEN EDUC = 4 THEN '1-3 years of college, university, or vocational school'
        WHEN EDUC = 5 THEN '4 years of college, university, BA/BS, or more'
        ELSE 'Unknown'
    END AS Education_Level,

    -- 13. Employment Status (EMPLOY)
    CASE 
        WHEN EMPLOY = 1 THEN 'Full-time'
        WHEN EMPLOY = 2 THEN 'Part-time'
        WHEN EMPLOY = 3 THEN 'Unemployed'
        WHEN EMPLOY = 4 THEN 'Not in labor force'
        ELSE 'Unknown'
    END AS Employment_Status,

    -- 14. Marital Status (MARSTAT)
    CASE 
        WHEN MARSTAT = 1 THEN 'Never married'
        WHEN MARSTAT = 2 THEN 'Now married'
        WHEN MARSTAT = 3 THEN 'Separated'
        WHEN MARSTAT = 4 THEN 'Divorced, widowed'
        ELSE 'Unknown'
    END AS Marital_Status,

    -- 15. Referral Source (PSOURCE)
    CASE 
        WHEN PSOURCE = 1 THEN 'Individual (includes self-referral)'
        WHEN PSOURCE = 2 THEN 'Alcohol/drug use care provider'
        WHEN PSOURCE = 3 THEN 'Other health care provider'
        WHEN PSOURCE = 4 THEN 'School (educational)'
        WHEN PSOURCE = 5 THEN 'Employer/EAP'
        WHEN PSOURCE = 6 THEN 'Other community referral'
        WHEN PSOURCE = 7 THEN 'Court/criminal justice referral/DUI/DWI'
        ELSE 'Unknown'
    END AS Referral_Source,

    -- 16. Payment Source, Primary (PRIMPAY)
    CASE 
        WHEN PRIMPAY = 1 THEN 'Self-pay'
        WHEN PRIMPAY = 2 THEN 'Private insurance'
        WHEN PRIMPAY = 3 THEN 'Medicare'
        WHEN PRIMPAY = 4 THEN 'Medicaid'
        WHEN PRIMPAY = 5 THEN 'Other government payments'
        WHEN PRIMPAY = 6 THEN 'No charge (free, charity)'
        WHEN PRIMPAY = 7 THEN 'Other'
        ELSE 'Unknown'
    END AS Primary_Payment_Source,

    -- 17. Health Insurance (HLTHINS)
    CASE 
        WHEN HLTHINS = 1 THEN 'Private insurance, Blue Cross/Blue Shield, HMO'
        WHEN HLTHINS = 2 THEN 'Medicaid'
        WHEN HLTHINS = 3 THEN 'Medicare, other (e.g. TRICARE, CHAMPUS)'
        WHEN HLTHINS = 4 THEN 'None'
        ELSE 'Unknown'
    END AS Health_Insurance,

    -- 18. Days Waiting to Enter Treatment (DAYWAIT)
    CASE 
        WHEN DAYWAIT = 0 THEN '0 days'
        WHEN DAYWAIT = 1 THEN '1-7 days'
        WHEN DAYWAIT = 2 THEN '8-14 days'
        WHEN DAYWAIT = 3 THEN '15-30 days'
        WHEN DAYWAIT = 4 THEN '31 or more days'
        ELSE 'Unknown'
    END AS Days_Waiting_Group,

    -- 19. DSM Diagnosis (DSMCRIT)
    CASE 
        WHEN DSMCRIT = 1 THEN 'Alcohol-induced disorder'
        WHEN DSMCRIT = 2 THEN 'Substance-induced disorder'
        WHEN DSMCRIT = 3 THEN 'Alcohol intoxication'
        WHEN DSMCRIT = 4 THEN 'Alcohol dependence'
        WHEN DSMCRIT = 5 THEN 'Opioid dependence'
        WHEN DSMCRIT = 6 THEN 'Cocaine dependence'
        WHEN DSMCRIT = 7 THEN 'Cannabis dependence'
        WHEN DSMCRIT = 8 THEN 'Other substance dependence'
        WHEN DSMCRIT = 9 THEN 'Alcohol abuse'
        WHEN DSMCRIT = 10 THEN 'Cannabis abuse'
        WHEN DSMCRIT = 11 THEN 'Other substance abuse'
        WHEN DSMCRIT = 12 THEN 'Opioid abuse'
        WHEN DSMCRIT = 13 THEN 'Cocaine abuse'
        WHEN DSMCRIT = 14 THEN 'Anxiety disorders'
        WHEN DSMCRIT = 15 THEN 'Depressive disorders'
        WHEN DSMCRIT = 16 THEN 'Schizophrenia/other psychotic disorders'
        WHEN DSMCRIT = 17 THEN 'Bipolar disorders'
        WHEN DSMCRIT = 18 THEN 'Attention deficit/disruptive behavior disorders'
        WHEN DSMCRIT = 19 THEN 'Other mental health condition'
        ELSE 'Unknown'
    END AS DSM_Diagnosis,

    -- 20. Secondary Substance (SUB2)
    CASE 
        WHEN SUB2 = 1 THEN 'None'
        WHEN SUB2 = 2 THEN 'Alcohol'
        WHEN SUB2 = 3 THEN 'Cocaine/crack'
        WHEN SUB2 = 4 THEN 'Marijuana/hashish'
        WHEN SUB2 = 5 THEN 'Heroin'
        WHEN SUB2 = 6 THEN 'Non-prescription methadone'
        WHEN SUB2 = 7 THEN 'Other opiates and synthetics'
        WHEN SUB2 = 8 THEN 'PCP'
        WHEN SUB2 = 9 THEN 'Hallucinogens'
        WHEN SUB2 = 10 THEN 'Methamphetamine/speed'
        WHEN SUB2 = 11 THEN 'Other amphetamines'
        WHEN SUB2 = 12 THEN 'Other stimulants'
        WHEN SUB2 = 13 THEN 'Benzodiazepines'
        WHEN SUB2 = 14 THEN 'Other tranquilizers'
        WHEN SUB2 = 15 THEN 'Barbiturates'
        WHEN SUB2 = 16 THEN 'Other sedatives or hypnotics'
        WHEN SUB2 = 17 THEN 'Inhalants'
        WHEN SUB2 = 18 THEN 'Over-the-counter medications'
        WHEN SUB2 = 19 THEN 'Other drugs'
        ELSE 'Unknown'
    END AS Secondary_Substance,

    -- 21. Tertiary Substance (SUB3)
    CASE 
        WHEN SUB3 = 1 THEN 'None'
        WHEN SUB3 = 2 THEN 'Alcohol'
        WHEN SUB3 = 3 THEN 'Cocaine/crack'
        WHEN SUB3 = 4 THEN 'Marijuana/hashish'
        WHEN SUB3 = 5 THEN 'Heroin'
        WHEN SUB3 = 6 THEN 'Non-prescription methadone'
        WHEN SUB3 = 7 THEN 'Other opiates and synthetics'
        WHEN SUB3 = 8 THEN 'PCP'
        WHEN SUB3 = 9 THEN 'Hallucinogens'
        WHEN SUB3 = 10 THEN 'Methamphetamine/speed'
        WHEN SUB3 = 11 THEN 'Other amphetamines'
        WHEN SUB3 = 12 THEN 'Other stimulants'
        WHEN SUB3 = 13 THEN 'Benzodiazepines'
        WHEN SUB3 = 14 THEN 'Other tranquilizers'
        WHEN SUB3 = 15 THEN 'Barbiturates'
        WHEN SUB3 = 16 THEN 'Other sedatives or hypnotics'
        WHEN SUB3 = 17 THEN 'Inhalants'
        WHEN SUB3 = 18 THEN 'Over-the-counter medications'
        WHEN SUB3 = 19 THEN 'Other drugs'
        ELSE 'Unknown'
    END AS Tertiary_Substance,

    -- 22. Flag Variables (Transformed into Substance Reported / Not Reported)
    CASE WHEN ALCFLG = 1 THEN 'Alcohol Reported' ELSE 'Alcohol Not Reported' END AS Alcohol_Flag,
    CASE WHEN MARFLG = 1 THEN 'Marijuana Reported' ELSE 'Marijuana Not Reported' END AS Marijuana_Flag,
    CASE WHEN COKEFLG = 1 THEN 'Cocaine Reported' ELSE 'Cocaine Not Reported' END AS Cocaine_Flag,
    CASE WHEN HERFLG = 1 THEN 'Heroin Reported' ELSE 'Heroin Not Reported' END AS Heroin_Flag,
    CASE WHEN METHFLG = 1 THEN 'Methadone Reported' ELSE 'Methadone Not Reported' END AS Methadone_Flag,
    CASE WHEN BENZFLG = 1 THEN 'Benzodiazepines Reported' ELSE 'Benzodiazepines Not Reported' END AS Benzodiazepine_Flag,
    CASE WHEN OTHERFLG = 1 THEN 'Other Drug Reported' ELSE 'Other Drug Not Reported' END AS Other_Drug_Flag,

    -- 23. Veteran Status (VET)
    CASE 
        WHEN VET = 1 THEN 'Veteran'
        WHEN VET = 2 THEN 'Non-Veteran'
        ELSE 'Unknown'
    END AS Veteran_Status

FROM samhsa_master_db.teds_a_fact_raw;