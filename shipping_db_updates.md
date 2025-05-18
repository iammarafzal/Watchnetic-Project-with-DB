# Shipping Information Display Fix

This document outlines the changes needed to fix the shipping information display on the order detail page.

## Issue Identified

The order detail page was not displaying shipping information correctly because:

1. The template expected fields like `address`, `city`, `state`, `postal_code`, and `country` that don't exist in the Shipping model.
2. The Shipping model stores address information in a single `shipping_address` field.
3. The template also references a `tracking_number` field that doesn't exist in the current database schema.

## Changes Made

1. Updated the `order_detail.html` template to correctly display shipping information using the fields that actually exist in the database.
2. Updated the `models.py` file to add a `tracking_number` column to the `Shipping` model.
3. Created a script (`add_tracking_number_to_shipping.py`) to add the tracking_number column to the database.

## Required Database Update

To complete the fix, you need to run the following SQL command on your MySQL database:

```sql
ALTER TABLE Shipping ADD COLUMN tracking_number VARCHAR(100);
```

You can execute this command using your MySQL administration tool (e.g., phpMyAdmin) or using the command line:

```bash
mysql -u root -p watchnetic_db -e "ALTER TABLE Shipping ADD COLUMN tracking_number VARCHAR(100);"
```

Or you can run the provided Python script:

```bash
python add_tracking_number_to_shipping.py
```

## Future Considerations

For better structure and more detailed shipping information, consider modifying the Shipping model to include separate fields for:

- Address line 1
- Address line 2 (optional)
- City
- State/Province
- Postal/Zip code
- Country

This would require:
1. Updating the database schema
2. Modifying the checkout form
3. Updating how shipping information is saved during checkout
4. Adjusting the order detail template 