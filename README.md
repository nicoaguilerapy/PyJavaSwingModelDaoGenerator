# PyJavaSwingModelDaoGenerator

PyJavaSwingModelDaoGenerator is a Python application that generates models and DAO (Data Access Object) classes for Java Swing based on a PostgreSQL database.

## How it Works

1. Connects to a PostgreSQL database: Provide the necessary database credentials in file main.py to establish a connection with your PostgreSQL database.

2. Reads column data: PyJavaSwingModelDaoGenerator retrieves information about the columns of the specified database tables. It reads the column names, types, and other relevant details.

3. Generates models: Based on the column information, the application automatically generates Java Swing model classes representing the tables in your database. These model classes encapsulate the table structure and provide convenient methods for accessing and manipulating the data.

4. Generates DAO classes: PyJavaSwingModelDaoGenerator also generates DAO classes corresponding to each model. These DAO classes provide methods to interact with the database, including CRUD (Create, Read, Update, Delete) operations. They encapsulate the database queries and operations required for data manipulation.

5. Ready for integration: Once the models and DAO classes are generated, you can integrate them into your Java Swing application. The generated code provides a foundation for building a Java Swing-based UI and accessing the database seamlessly.

## Getting Started

1. Clone the repository:
git clone https://github.com/nicoaguilerapy/PyJavaSwingModelDaoGenerator.git

2. Install the required dependencies:
pip install -r requirements.txt

3. Change db values in main.py:
db_name = ''
db_host = ''
db_port = 5411
db_user = ''
db_password = ''

4. Run the application:
python main.py


5. Check the generated files:

After the application finishes running, you will find the generated Java Swing model and DAO classes in the specified output directory.

## Contributions

Contributions are welcome! If you encounter any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).


