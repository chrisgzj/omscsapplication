# Sales Web Application

## Overview

This is a web application developed in Django and designed to coordinate the administrative tasks of the sales team of a building company in Mexico. It is currently deployed in Google Cloud Platform.

The main functions of the application are:

1) Keeping track of the availability of houses and applying policies related to the individual permissions for blocking houses in behalf of clients.

2) Uploading and retrieving documents necessary for the sales process.

3) Documenting the sales prospects and updating their status.

## Structure

The main objects in models.py are:

- Clients
- Houses
- Sales (contains all the documents related to the sale process)
- Files (contains the documents related to the client)

The main urls in urls.py are:

- casa: shows all the relevant information and documentos of a house.
- altacliente: registration of new clients.
- modifcliente: modification of existing clients.
- listaclientes: shows a list of clients and asociated houses.
- seguimientocliente: shows the updates of sales prospects.

## Additional information

The functionality and design of this version have not been completed yet. 


