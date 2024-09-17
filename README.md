# Product Management System

This project is a RESTful API built using **Flask** to manage products. It integrates **Firebase Realtime Database** for storing product data and **Firebase Authentication** for managing user authentication. The system allows users to register, upload products, retrieve their products, delete products, and perform other CRUD operations.

## Features

- **User Registration**: Users can register using their email and password, which are stored and authenticated via Firebase Authentication.
  - **Endpoint**: `[POST] /register`
  
- **Product Upload**: Registered users can upload products, and the data will be stored in the Firebase Realtime Database.
  - **Endpoint**: `[POST] /upload_product`
  
- **View User Products**: Users can retrieve all the products they have uploaded.
  - **Endpoint**: `[GET] /user_products`
  
- **Delete Product**: Users can delete a specific product they uploaded by its ID.
  - **Endpoint**: `[DELETE] /delete_product/<product_id>`
  
- **View Product Details**: Retrieve detailed information about a specific product by its ID.
  - **Endpoint**: `[GET] /product_info/<product_id>`
  
- **View All Products**: Retrieve a list of all products in the system.
  - **Endpoint**: `[GET] /all_products`
  
- **Update Product**: Update the details of a specific product by its ID.
  - **Endpoint**: `[PUT] /update_product/<product_id>`
  
- **Search Products**: Search for products based on a query string.
  - **Endpoint**: `[GET] /search_products?query=<search_query>`
  
- **Filter Products by Category**: Retrieve products filtered by a specific category.
  - **Endpoint**: `[GET] /products_by_category/<category_name>`

## Key Requirements

- **Authentication**: Ensure that all endpoints are secured with Firebase Authentication, allowing only registered users to perform actions on products.
  
- **Authorization**: Ensure that users can only update or delete the products they have uploaded.
  
- **Validation**: Ensure data sent to Firebase Realtime Database is properly validated and stored in a correct format.
  
- **Error Handling**: Handle authentication errors, authorization errors, and general errors appropriately.

## Tools & Frameworks

- **Flask**: Used to develop the RESTful API.
- **Firebase Realtime Database**: Used to store product data.
- **Firebase Authentication**: Used to manage user authentication.
