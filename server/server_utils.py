def get_db_filename(is_test):
    prod_db_filename = 'octavio_prod.db'
    test_db_filename = 'octavio_test.db'
    db_filename = test_db_filename if is_test else prod_db_filename
    return db_filename
