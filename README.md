# bedroser
`bedroser` is a CLI executable application packaged by pyInstaller to extract product attributes from pdf catalogue of a specific format and to produce csv files required by the client.

It is intended to automate entry of data arriving from its supplier into the ERP system of their client who cannot obtain product and price data in machine readable format.

`bedroser` uses tabula-java as an engine for reading the pdf catalog one page at a time.

## Requirements
- Java 8
- Windows 10, 64-bit
- System PATH variable set for Java runtime environment 
- Tabula
 

Java installation links:  
https://www.java.com/en/download/  
https://www.java.com/en/download/help/path.html
Tabula installation link:
https://tabula.technology/

## Usage
Before running `bedroser`, export tabula-template.json of the pdf catalog with the help of Tabula for Windows.
Each table in the document must have its own selection.
Table titles must be selected distinctly from the tables themselves.
Titles may correspond to Series, Group, Color.

Follow interactive input/output instructions of the application.



## Input
pdf file containing pages with tables from Bedrosians catalog
tabula-template.json file

## Output
product_table.csv - *structured data extracted from all fields of tables*   
target.csv - *client's template for upload in ERP*  
uom.csv - *another client's template containing units conversion for upload in ERP*  

###### Notes
Current catalog contains Sequel Encore on pp 88-113  
Double spaced page: 104