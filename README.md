# ERPNext Custom App for Apparel Manufacturing

## Features
- Cutting Matrix for Work Orders
- BOM without raw materials (Service BOM)
- Dynamic Job Card Batch Creation
- A8 Job Card Print with Barcode
- Custom Fields and Print Formats

## Installation
cd frappe-bench
bench --site [site_name] install-app PFI
bench export-fixtures
bench clear-cache
bench --site [site_name] migrate
bench build



## Post-Install
- Apply Fixtures (Custom Fields & Print Formats)
