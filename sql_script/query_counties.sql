-- query_counties.sql

tee output_file.txt;
-- List each county and its subcounties

SELECT
    c.name AS county_name,
    sc.name AS subcounty_name,  -- Added a comma here
    sc.code AS subcounty_code
FROM
    counties c
LEFT JOIN
    subcounties sc ON c.code = sc.county_code
ORDER BY
    c.name, sc.name, sc.code;


-- List each county, its constituencies, and their codes
SELECT 
    c.name AS county_name,
    con.constituency_name AS constituency_name,
    con.constituency_code AS constituency_code
FROM 
    counties c
LEFT JOIN 
    constituencies con ON c.code = con.county_code
ORDER BY 
    c.name, con.constituency_name, con.constituency_code;

notee;