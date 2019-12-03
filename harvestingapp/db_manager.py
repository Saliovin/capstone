import psycopg2
import logger

logger = logger.ini_logger(__name__)


def connect_to_db(username, hostname, password, database):
    logger.info(f"Connecting to {database} database")

    try:
        connection = psycopg2.connect(user=username,
                                      password=password,
                                      host=hostname,
                                      port="5432",
                                      database=database)
        connection.autocommit = True
        logger.info(f"Connected to {database} database")
        return connection

    except (Exception, psycopg2.Error) as error:
        logger.error(f"Error while connecting to PostgreSQL: {error}")


def create_db(db_name, username, hostname, password):
    connection = connect_to_db(username, hostname, password, "postgres")
    cursor = connection.cursor()

    logger.info("Checking for existing database")
    cursor.execute(f"SELECT datname FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
    if cursor.fetchone():
        logger.info("Database exists")
    else:
        logger.info("Database does not exist, creating new one")
        cursor.execute(f"CREATE DATABASE {db_name}")
    cursor.close()
    connection.close()
    logger.info("Closed connection")

    return connect_to_db(username, hostname, password, db_name)


def create_tables(connection):
    cursor = connection.cursor()
    logger.info("Checking for existing programs table")
    query = "SELECT to_regclass('public.programs')"
    cursor.execute(query)
    if cursor.fetchone()[0]:
        logger.info("Table found")
    else:
        logger.info("Table missing, creating new one")
        query = f'''CREATE TABLE programs
                        (ID                 SERIAL PRIMARY KEY,
                        PROGRAM_NAME        TEXT    NOT NULL,
                        PROGRAM_VERSION     TEXT    NOT NULL);'''
        cursor.execute(query)
        logger.info("Table created")

    logger.info("Checking for existing translations table")
    query = f"SELECT to_regclass('public.translations');"
    cursor.execute(query)
    if cursor.fetchone()[0]:
        logger.info("Table found")
    else:
        logger.info("Table missing, creating new one")
        query = f'''CREATE TABLE translations
                        (ID                 SERIAL PRIMARY KEY,
                        TRANSLATION            TEXT    NOT NULL,
                        TRANSLATION_VERSION    TEXT    NOT NULL);'''
        cursor.execute(query)
        logger.info("Table created")

    cursor.close()


def find_program(connection, program):
    name = program['program_name']
    version = program['program_version']
    cursor = connection.cursor()

    query = f'''SELECT * FROM
                    programs WHERE
                        program_name = \'{name}\' and
                        program_version = \'{version}\''''
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()

    if result:
        logger.info(f'{name} {version} exists')
        return True
    else:
        logger.info(f'{name} {version} does not exist')
        return False


def find_translation(connection, translation):
    translation_name = translation['translation']
    version = translation['translation_version']
    cursor = connection.cursor()

    query = f'''SELECT * FROM
                    translations WHERE
                        translation = \'{translation_name}\' and
                        translation_version = \'{version}\''''
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()

    if result:
        logger.info(f'{translation_name} {version} exists')
        return True
    else:
        logger.info(f'{translation_name} {version} does not exist')
        return False


def write_to_db(program_info_list, database, username, hostname, password):
    connection = create_db(database, username, hostname, password)
    create_tables(connection)
    cursor = connection.cursor()
    download_list = []

    logger.info("Writing to database")
    for program in program_info_list:
        if not find_program(connection, program):
            query = '''INSERT INTO
                            programs
                                (PROGRAM_NAME, PROGRAM_VERSION)
                            VALUES
                                (%(program_name)s, %(program_version)s)'''
            cursor.execute(query, program)
            main_files = [{'link': link,
                           'version': program['program_version']}
                          for link in program['downloads']]
            download_list.extend(main_files)
        else:
            logger.info(f'Skipping {program["program_name"]}')
        for translation in program['translations']:
            if not find_translation(connection, translation):
                query = f'''INSERT INTO
                                translations
                                    (TRANSLATION, TRANSLATION_VERSION)
                                VALUES
                                    (%(translation)s, %(translation_version)s)'''
                cursor.execute(query, translation)
                download_list.append({'link': translation['link'],
                                      'version': translation['translation_version']})
            else:
                logger.info(f'Skipping {translation["translation"]}')
    logger.info("Finished writing to database")

    cursor.close()
    connection.close()
    logger.info("Closed connection")
    return download_list
