# AgroSphere
AgroSphere is a comprehensive web platform for agricultural automation based on Django and GeoDjango technologies. 
The system allows farmers and agronomists to plan sowing campaigns, manage warehouse stocks, and visualize data on interactive maps.

## Basic functionality
* Geoanalytics and GIS: Visualization of fields, warehouses and crop areas on a map.
* Smart Planning: Optimization of the cropping plan using mathematical algorithms to maximize profit.
* Inventory Management: Transaction log to monitor inventory values ​​in warehouses.

## Technologies
- Backend: Python 3.12, Django 5.0, Django REST Framework.
- Database:PostgreSQL with PostGIS extension for geodata.
- Frontend: HTML5, Bootstrap 5, Chart.js, OpenStreetMap (Leaflet).
- Infrastructure: Docker, Docker Compose.

## Installation
1) Clone the repository:
```Bash
git clone <repository_link>
cd <path_to_clone>
```

2) Run the project:
```Bash
docker compose up --build
```

3) Open the system in a browser:
```markdown
http://localhost:8000/
```

## Project structure
- users/ — authentication and user profiles.
- geo_analytics/ — logic for working with fields and GIS data.
- warehousing/ — warehouse and inventory management.
- smart_planning/ — crop optimization module (Solver).
- frontend/ — templates and user interface.
