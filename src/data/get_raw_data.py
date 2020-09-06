import os.path
import requests
import logging


def download_data(url, filename, path):
    '''
    method to extract data
    '''
    # get logger
    logger = logging.getLogger(__name__)

    logger.info('downloading from url: ' + url)
    r = requests.get(url, allow_redirects=True)
    open(os.path.join(path, filename), 'wb').write(r.content)
    logger.info('downloaded: ' + os.path.join(path, filename))


def create_directory_if_necessary(path):
    '''
    create a directory if necessary
    '''
    # get logger
    logger = logging.getLogger(__name__)

    # create folder if necessary
    logger.info('creating folder ' + path)
    try:
        os.mkdir(path)
    except OSError as error:
        logger.info('folder already exists: ' + path)


def main(project_dir):
    '''
    main method
    '''
    # get logger
    logger = logging.getLogger(__name__)
    logger.info('getting raw data')

    data_path = os.path.join(project_dir, 'data')
    raw_data_path = os.path.join(data_path, 'raw')
    metadata_raw_data_path = os.path.join(raw_data_path, 'metadata')

    # create folders if necessary
    create_directory_if_necessary(data_path)
    create_directory_if_necessary(raw_data_path)

    # Store the data to download in a list of tuples : (url, filename, path)
    data_list = []

    # Donnees hospitalieres
    data_list.append(('https://www.data.gouv.fr/fr/datasets/r/63352e38-d353-4b54-bfd1-f1b3ee1cabd7',
                      'donnees-hospitalieres-covid19-raw.csv', raw_data_path))

    # Donnees hospitalieres - nouveaux
    data_list.append(('https://www.data.gouv.fr/fr/datasets/r/6fadff46-9efd-4c53-942a-54aca783c30c',
                      'donnees-hospitalieres-nouveaux-covid19-raw.csv', raw_data_path))

    # Donnees hospitalieres - classe age
    data_list.append(('https://www.data.gouv.fr/fr/datasets/r/08c18e08-6780-452d-9b8c-ae244ad529b3',
                      'donnees-hospitalieres-classe-age-covid19-raw.csv', raw_data_path))

    # Donnees hospitalieres - etablissements
    data_list.append(('https://www.data.gouv.fr/fr/datasets/r/41b9bd2a-b5b6-4271-8878-e45a8902ef00',
                      'donnees-hospitalieres-etablissements-covid19-raw.csv', raw_data_path))

    # Metadata

    # create directory if necessary
    create_directory_if_necessary(metadata_raw_data_path)

    # Metadata - Donnees hospitalieres
    data_list.append(('https://www.data.gouv.fr/fr/datasets/r/3f0f1885-25f4-4102-bbab-edec5a58e34a',
                      'metadonnees-donnees-hospitalieres-covid19.csv', metadata_raw_data_path))

    # Metadata - Donnees hospitalieres nouveaux
    data_list.append(('https://www.data.gouv.fr/fr/datasets/r/4900f53f-750d-4c5a-9df7-2d4ceb018acf',
                      'metadonnees-donnees-hospitalieres-covid19-nouveaux.csv', metadata_raw_data_path))

    # Metadata - Donnees hospitalieres classe age
    data_list.append(('https://www.data.gouv.fr/fr/datasets/r/929dff1b-b07c-4637-9690-fb7219ad3eb8',
                      'metadonnees-donnees-hospitalieres-covid19-classes-age.csv', metadata_raw_data_path))

    # Metadata - services hospitaliers
    data_list.append(('https://www.data.gouv.fr/fr/datasets/r/415c852b-7898-40f8-8f71-b9171faf4516',
                      'metadonnees-services_hospitaliers-covid19.csv', metadata_raw_data_path))

    # Metadata - sexe
    data_list.append(('https://www.data.gouv.fr/fr/datasets/r/9f94a259-2a8a-441d-bd0b-d6b45697d477',
                      'metadonnees-sexe-covid19.csv', metadata_raw_data_path))

    for url, filename, path in data_list:
        download_data(url, filename, path)


if __name__ == '__main__':
    # getting root directory
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    # setup logger
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # call the main
    main(project_dir)
