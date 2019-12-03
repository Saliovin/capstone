from harvester_app.harvester import *
from harvester_app.db_manager import *


def test_get_parser():
    parser = get_parser('http://54.174.36.110/')
    assert parser


def test_nirsoft_scraper():
    program_list = nirsoft_scraper('http://54.174.36.110/')
    assert program_list


def test_create_db():
    connection = create_db('test', 'postgres', 'localhost', 'docker')
    assert connection


def test_create_tables():
    connection = create_db('test', 'postgres', 'localhost', 'docker')
    assert create_tables(connection)


def test_find_program():
    connection = create_db('test', 'postgres', 'localhost', 'docker')
    create_tables(connection)
    cursor = connection.cursor()
    query = '''INSERT INTO
                                programs
                                    (PROGRAM_NAME, PROGRAM_VERSION)
                                VALUES
                                    ('test', '123')'''
    cursor.execute(query)
    assert find_program(connection, {'program_name': 'test', 'program_version': '123'})


def test_find_program_fail():
    connection = create_db('test', 'postgres', 'localhost', 'docker')
    create_tables(connection)
    cursor = connection.cursor()
    query = '''INSERT INTO
                                programs
                                    (PROGRAM_NAME, PROGRAM_VERSION)
                                VALUES
                                    ('test', '123')'''
    cursor.execute(query)
    assert not find_program(connection, {'program_name': 'test123', 'program_version': '123'})


def test_find_translation():
    connection = create_db('test', 'postgres', 'localhost', 'docker')
    create_tables(connection)
    cursor = connection.cursor()
    query = '''INSERT INTO
                                    translations
                                        (TRANSLATION, TRANSLATION_VERSION)
                                    VALUES
                                        ('test', '123')'''
    cursor.execute(query)
    assert find_translation(connection, {'translation': 'test', 'translation_version': '123'})


def test_find_translation_fail():
    connection = create_db('test', 'postgres', 'localhost', 'father')
    create_tables(connection)
    cursor = connection.cursor()
    query = '''INSERT INTO
                                    translations
                                        (TRANSLATION, TRANSLATION_VERSION)
                                    VALUES
                                        ('test', '123')'''
    cursor.execute(query)
    assert not find_translation(connection, {'translation': 'test123', 'translation_version': '123abc'})


def test_write_to_db():
    program_list = nirsoft_scraper('http://54.174.36.110/')
    assert write_to_db(program_list, 'test', 'postgres', 'localhost', 'docker')
