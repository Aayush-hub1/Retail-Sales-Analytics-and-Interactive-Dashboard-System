# Viva Questions and Answers

## Q1. Why does `sale_items` store `unit_price` when `products` already has a price?
Prices change over time. Storing the price at the time of sale keeps past revenue correct. If we joined to the current product price, old sales would change whenever a price was edited.

## Q2. Why are sales and sale_items separate tables?
One sale (order) can contain many products. Putting the order details (customer, date, payment) in `sales` and one row per product in `sale_items` avoids repeating data. This is a one-to-many relationship and follows normalisation.

## Q3. Why does the server read the price from the database instead of the browser?
The browser can be edited by the user, so a price sent from it cannot be trusted. The server looks up the price in `products`, so the stored revenue is always correct. The server also validates the product, quantity and discount.

## Q4. What is the difference between INNER JOIN and LEFT JOIN, and where did you use each?
INNER JOIN returns only rows that match in both tables. LEFT JOIN returns every row from the left table, with NULL where there is no match. In `analysis.sql`, INNER JOIN builds revenue by category (query 2.2), and LEFT JOIN lists products and customers that may have no sales (queries 2.6 and 2.7).

## Q5. What is an outlier, and how did you handle sale 37?
An outlier is a value far from the rest. Sale 37 has bulk quantities (20 and 30 units) and about 10157.50 total, which lifts October revenue and the mean. In Excel it is found with the IQR method: values above Q3 + 1.5 × IQR are flagged. It is kept in the data because it is a real sale, but reported separately so it does not mislead the averages.