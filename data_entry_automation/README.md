# Web Automation of Academic Records Reporting

## Overview

This project aims to upload programatically the academic results of several students to the Mexico's educational authority platform using python and Selenium Webdriver. The code has been used with three different schools for over three years. A video example of the program running can be found in the repository. 

## Background

The educational authority in Mexico City requires K-12 schools to report periodically the academic results of all their students to a web application that does not support automation or bulk uploads of any kind. The reporting dates are usually not known with enough time for appropriate planning. This script intends to solve two main problems:

1) The manual work is error-prone and schools and teachers are punished severely when the reports have to be corrected after upload.

2) The usual capture and verification process takes a few days and it restricts severely the time available for teachers to actually grade students since the notification for updating the information is usually made with less than a weeks notice.

## Structure

The script has a main function called llenar_sep that takes the following parameters:

- nivel: String for identification of the educational level, since the platform has a different structure for different levels.
- usuario: String username for accessing the platform.
- password: String password for accesing the platform.
- i_bim: Integer indicating the period of the school year that is being reported.
- fname: String with the name of the Excel file where grades to report are to be found.
- nom_hoja: String with the name of the sheet inside fname.
- sologrupos: List that contains the groups to be reported.
- mats: List that contains the subjects to be reported.
- con_interrupciones: Boolean to indicate wether the script should make a pause and wait for user input after each group.

The script will open a browser, login with the credentials provided, navigate to the correct place in the platform, iterate over groups, upload and save the grades for the selected subjects and print the names of the students that weren't found in the Excel file.

## Additional information

Since the use of this file cannot be replicated without access to the platform, this repository contains:

1) An Excel file with an example of the structure of the information that the Selenium script expects to read.
2) An mp4 video that shows part of the execution of an upload process.
