# CRM-410 Export customer list

As a sales manager, I want to export the customer list to CSV so that I can analyse it in Excel.

## Acceptance criteria
- AC-1: Given I am on the Customers page, when I click "Export", then a CSV file downloads containing the customers in the current filter.
- AC-2: The CSV contains columns: name, email, phone, region, created date.
- AC-3: Given no customers match the filter, the export button is disabled.
