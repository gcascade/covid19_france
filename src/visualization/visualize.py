import os.path
import logging
import pandas as pd
import numpy as np
import re
from datetime import date, timedelta
from dotenv import find_dotenv, load_dotenv
from PIL import Image, ImageFilter

from src.enum.PlotType import PlotType


def main(project_dir):
    '''
    main method
    '''
    # get logger
    logger = logging.getLogger(__name__)
    logger.info('visualizing data')
    today = date.today().strftime('%Y-%m-%d')
    create_directory_if_necessary(os.path.join(project_dir, 'reports/figures/' + today))

    covid_df = pd.read_csv('../../data/raw/donnees-hospitalieres-covid19-raw.csv', sep=';')
    classe_age_df = pd.read_csv('../../data/raw/donnees-hospitalieres-classe-age-covid19-raw.csv', sep=';')
    nouveau_df = pd.read_csv('../../data/raw/donnees-hospitalieres-nouveaux-covid19-raw.csv', sep=';')

    # edit the following days : 2020-06-27, 2020-06-28, 2020-06-29
    covid_df['jour'] = covid_df['jour'].replace('27/06/2020', '2020-06-27')
    covid_df['jour'] = covid_df['jour'].replace('28/06/2020', '2020-06-28')
    covid_df['jour'] = covid_df['jour'].replace('29/06/2020', '2020-06-29')

    # Edit ages: todo properly
    classe_age_df['cl_age90'] = classe_age_df['cl_age90'].replace(0, 'inconnu')
    classe_age_df['cl_age90'] = classe_age_df['cl_age90'].replace(9, '0 - 9')
    classe_age_df['cl_age90'] = classe_age_df['cl_age90'].replace(19, '10 - 19')
    classe_age_df['cl_age90'] = classe_age_df['cl_age90'].replace(29, '20 - 29')
    classe_age_df['cl_age90'] = classe_age_df['cl_age90'].replace(39, '30 - 39')
    classe_age_df['cl_age90'] = classe_age_df['cl_age90'].replace(49, '40 - 49')
    classe_age_df['cl_age90'] = classe_age_df['cl_age90'].replace(59, '50 - 59')
    classe_age_df['cl_age90'] = classe_age_df['cl_age90'].replace(69, '60 - 69')
    classe_age_df['cl_age90'] = classe_age_df['cl_age90'].replace(79, '70 - 79')
    classe_age_df['cl_age90'] = classe_age_df['cl_age90'].replace(89, '80 - 89')
    classe_age_df['cl_age90'] = classe_age_df['cl_age90'].replace(90, '90 et + ')

    # create a filter for all genders
    all_gender_filter = covid_df['sexe'] == 0

    date_pattern = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}")
    pattern_matcher_filter = covid_df['jour'].str.match(pat=date_pattern)

    last_month = date.today() - timedelta(days=30)
    last_month_filter = covid_df['jour'] >= last_month.strftime('%Y-%m-%d')
    last_month_df = covid_df.where(last_month_filter & all_gender_filter & pattern_matcher_filter).dropna()
    last_month_df = last_month_df.groupby(['jour'])

    yesterday = date.today() - timedelta(days=1)

    last_month_title = 'Tendances du ' + last_month.strftime('%d/%m/%Y') + ' au ' + yesterday.strftime('%d/%m/%Y')

    # Tendances
    tend_hosp_plot = last_month_df.sum()['hosp'].plot(title=last_month_title + ' - Hospitalisations', figsize=(10, 10))
    tend_hosp_plot.get_figure().savefig(
        os.path.join(project_dir, 'reports/figures/' + today + '/hospitalisations-tendances.png'))
    tend_hosp_plot.get_figure().clear()

    tend_rea_plot = last_month_df.sum()['rea'].plot(title=last_month_title + ' - Réanimations', figsize=(10, 10))
    tend_rea_plot.get_figure().savefig(
        os.path.join(project_dir, 'reports/figures/' + today + '/reanimations-tendances.png'))
    tend_rea_plot.get_figure().clear()

    tend_rad_plot = last_month_df.sum()['rad'].plot(title=last_month_title + ' - Retours à domicile', figsize=(10, 10))
    tend_rad_plot.get_figure().savefig(
        os.path.join(project_dir, 'reports/figures/' + today + '/retours-a-domicile-tendances.png'))
    tend_rad_plot.get_figure().clear()

    tend_dc_plot = last_month_df.sum()['dc'].plot(title=last_month_title + ' - Décès', figsize=(10, 10))
    tend_dc_plot.get_figure().savefig(os.path.join(project_dir, 'reports/figures/' + today + '/deces-tendances.png'))
    tend_dc_plot.get_figure().clear()

    # All time
    covid_df_grouped = covid_df.where(all_gender_filter).groupby('jour')
    at_hosp_plot = covid_df_grouped.sum()['hosp'].plot(title='Hospitalisations dues au COVID-19',
                                                       figsize=(10, 10))
    at_hosp_plot.get_figure().savefig(os.path.join(project_dir, 'reports/figures/' + today + '/hospitalisations.png'))
    at_hosp_plot.get_figure().clear()

    at_rea_plot = covid_df_grouped.sum()['rea'].plot(title='Réanimations dues au COVID-19',
                                                     figsize=(10, 10))
    at_rea_plot.get_figure().savefig(os.path.join(project_dir, 'reports/figures/' + today + '/reanimations.png'))
    at_rea_plot.get_figure().clear()

    at_rad_plot = covid_df_grouped.sum()['rad'].plot(title='Retours à domicile', figsize=(10, 10))
    at_rad_plot.get_figure().savefig(os.path.join(project_dir, 'reports/figures/' + today + '/retours-a-domicile.png'))
    at_rad_plot.get_figure().clear()

    at_dc_plot = covid_df_grouped.sum()['dc'].plot(title='Décès dus au COVID-19', figsize=(10, 10))
    at_dc_plot.get_figure().savefig(os.path.join(project_dir, 'reports/figures/' + today + '/deces.png'))
    at_hosp_plot.get_figure().clear()

    ca_hosp_plot = classe_age_df.groupby(['jour', 'cl_age90']).sum()['hosp'].unstack(-1) \
        .plot(kind='area', title='Hospitalisations en fonction de l''âge', figsize=(10, 10)) \
        .legend(loc='upper right', title='Âge', ncol=3)
    ca_hosp_plot.get_figure().savefig(
        os.path.join(project_dir, 'reports/figures/' + today + '/hospitalisations-par-age.png'))
    ca_hosp_plot.get_figure().clear()

    ca_rea_plot = classe_age_df.groupby(['jour', 'cl_age90']).sum()['rea'].unstack(-1) \
        .plot(kind='area', title='Réanimations en fonction de l''âge', figsize=(10, 10)) \
        .legend(loc='upper right', title='Âge', ncol=3)
    ca_rea_plot.get_figure().savefig(
        os.path.join(project_dir, 'reports/figures/' + today + '/reanimations-par-age.png'))
    ca_rea_plot.get_figure().clear()

    ca_dc_plot = classe_age_df.groupby(['jour', 'cl_age90']).sum()['dc'].unstack(-1) \
        .plot(kind='area', title='Décès en fonction de l''âge', figsize=(10, 10)) \
        .legend(loc='upper right', title='Âge', ncol=3)
    ca_dc_plot.get_figure().savefig(os.path.join(project_dir, 'reports/figures/' + today + '/deces-par-age.png'))
    ca_dc_plot.get_figure().clear()

    # removed unknown age
    fixed_classe_age_df = classe_age_df.where(classe_age_df['cl_age90'] != 'inconnu').groupby(['jour', 'cl_age90'])
    f_ca_hosp_plot = fixed_classe_age_df.sum()['hosp'].unstack(
        -1).plot(kind='area', title='Hospitalisations en fonction de l''âge', figsize=(10, 10)).legend(
        loc='upper right', title='Âge', ncol=3)
    f_ca_hosp_plot.get_figure().savefig(
        os.path.join(project_dir, 'reports/figures/' + today + '/hospitalisations-par-age-v2.png'))
    f_ca_hosp_plot.get_figure().clear()

    f_ca_rea_plot = fixed_classe_age_df.sum()['rea'].unstack(-1) \
        .plot(kind='area', title='Réanimations en fonction de l''âge', figsize=(10, 10)) \
        .legend(loc='upper right', title='Âge', ncol=3)
    f_ca_rea_plot.get_figure().savefig(
        os.path.join(project_dir, 'reports/figures/' + today + '/reanimations-par-age-v2.png'))
    f_ca_rea_plot.get_figure().clear()

    f_ca_dc_plot = fixed_classe_age_df.sum()['dc'].unstack(-1) \
        .plot(kind='area', title='Décès en fonction de l''âge', figsize=(10, 10)) \
        .legend(loc='upper right', title='Âge', ncol=3)
    f_ca_dc_plot.get_figure().savefig(os.path.join(project_dir, 'reports/figures/' + today + '/deces-par-age-v2.png'))
    f_ca_dc_plot.get_figure().clear()

    new_hosp_plot = nouveau_df.groupby(['jour']).sum()['incid_hosp'].plot(title='Hospitalisations - Nouveaux cas',
                                                                          figsize=(10, 10))
    new_hosp_plot.get_figure().savefig(
        os.path.join(project_dir, 'reports/figures/' + today + '/hospitalisations-nouveaux.png'))
    new_hosp_plot.get_figure().clear()

    new_rea_plot = nouveau_df.groupby(['jour']).sum()['incid_rea'].plot(title='Réanimations - Nouveaux cas',
                                                                        figsize=(10, 10))
    new_rea_plot.get_figure().savefig(
        os.path.join(project_dir, 'reports/figures/' + today + '/reanimations-nouveaux.png'))
    new_rea_plot.get_figure().clear()

    new_dc_plot = nouveau_df.groupby(['jour']).sum()['incid_dc'].plot(title='Nouveaux décès', figsize=(10, 10))
    new_dc_plot.get_figure().savefig(os.path.join(project_dir, 'reports/figures/' + today + '/deces-nouveaux.png'))
    new_dc_plot.get_figure().clear()

    # 1 - 95
    french_departments = []
    french_departments.extend(range(1, 20))
    french_departments.extend(['2A', '2B'])
    french_departments.extend(range(21, 96))
    for dep in french_departments:
        if isinstance(dep, int):
            plot_for_department("{:02d}".format(dep), covid_df, nouveau_df)
        else:
            plot_for_department(dep, covid_df, nouveau_df)

    # 971 - 976
    for dep in range(971, 977):
        plot_for_department(str(dep), covid_df, nouveau_df)

    generate_gifs(project_dir)

    logger.info('Done')


def plot_for_department(department, all_time_df, new_df):
    today = date.today().strftime('%Y-%m-%d')
    create_directory_if_necessary(os.path.join(project_dir, 'reports/figures/' + today + '/departements/'))
    create_directory_if_necessary(os.path.join(project_dir, 'reports/figures/' + today + '/departements/' + department))

    if all_time_df is not None:
        plot_all_time(department, all_time_df)

    if new_df is not None:
        plot_new(department, new_df)


def plot_all_time(department, all_time_df):
    today = date.today().strftime('%Y-%m-%d')
    all_gender_filter = all_time_df['sexe'] == 0
    plot_and_save(department,
                  'Hospitalisations dues au COVID-19',
                  os.path.join(project_dir,
                               'reports/figures/' + today + '/departements/' + department + '/hospitalisations.png'),
                  all_time_df.where(all_gender_filter),
                  'hosp',
                  PlotType.ALL_TIME)

    plot_and_save(department,
                  'Réanimations dues au COVID-19',
                  os.path.join(project_dir,
                               'reports/figures/' + today + '/departements/' + department + '/reanimations.png'),
                  all_time_df.where(all_gender_filter),
                  'rea',
                  PlotType.ALL_TIME)

    plot_and_save(department,
                  'Décès dues au COVID-19',
                  os.path.join(project_dir,
                               'reports/figures/' + today + '/departements/' + department + '/deces.png'),
                  all_time_df.where(all_gender_filter),
                  'dc',
                  PlotType.ALL_TIME)

    plot_and_save(department,
                  'Retours à domicile',
                  os.path.join(project_dir,
                               'reports/figures/' + today + '/departements/' + department + '/retours-a-domicile.png'),
                  all_time_df.where(all_gender_filter),
                  'rad',
                  PlotType.ALL_TIME)


def plot_new(department, new_df):
    today = date.today().strftime('%Y-%m-%d')
    plot_and_save(department,
                  'Hospitalisations - Nouveaux cas',
                  os.path.join(project_dir,
                               'reports/figures/' + today + '/departements/' + department + '/hospitalisations-nouveaux.png'),
                  new_df,
                  'incid_hosp',
                  PlotType.NEW)

    plot_and_save(department,
                  'Réanimations - Nouveaux cas',
                  os.path.join(project_dir,
                               'reports/figures/' + today + '/departements/' + department + '/reanimations-nouveaux.png'),
                  new_df,
                  'incid_rea',
                  PlotType.NEW)

    plot_and_save(department,
                  'Nouveaux décès',
                  os.path.join(project_dir,
                               'reports/figures/' + today + '/departements/' + department + '/deces-nouveaux.png'),
                  new_df,
                  'incid_dc',
                  PlotType.NEW)


def plot_and_save(department, plot_title, filename, df, prop, plot_type):
    if plot_type == PlotType.ALL_TIME:
        if department is None:
            plot = df.groupby('jour').sum()[prop].plot(title=plot_title, figsize=(10, 10))
        else:
            # pour classes-age dep = reg
            plot = df.where(df['dep'] == department).groupby('jour').sum()[prop] \
                .plot(title=plot_title + ' - ' + department, figsize=(10, 10))
        plot.get_figure().savefig(filename)
        plot.get_figure().clear()
    elif plot_type == PlotType.NEW:
        if department is None:
            plot = df.groupby(['jour']).sum()[prop].plot(title=plot_title, figsize=(10, 10))
        else:
            plot = df.where(df['dep'] == department).groupby(['jour']).sum()[prop] \
                .plot(title=plot_title + ' - ' + department, figsize=(10, 10))
        plot.get_figure().savefig(filename)
        plot.get_figure().clear()


def create_directory_if_necessary(path):
    '''
    create a directory if necessary
    '''
    # get logger
    logger = logging.getLogger(__name__)

    # create folder if necessary
    logger.info('creating folder ' + path)
    try:
        os.makedirs(path)
    except OSError as error:
        logger.info('folder already exists: ' + path)

def generate_gifs(project_dir):
    today = date.today().strftime('%Y-%m-%d')
    figure_directory = 'reports/figures/' + today
    gifs_directory = 'reports/gifs/' + today
    new_hospitalisations_filename = 'hospitalisations-nouveaux.png'
    new_intensive_filename = 'reanimations-nouveaux.png'
    new_deaths_filename = 'deces-nouveaux.png'
    hospitalisations_filename = 'hospitalisations.png'
    intensive_filename = 'reanimations.png'
    deaths_filename = 'deces.png'
    cured_filename = 'retours-a-domicile.png'

    new_hospitalisations_filenames = [os.path.join(project_dir, figure_directory + '/' + new_hospitalisations_filename)]
    new_intensive_filenames = [os.path.join(project_dir, figure_directory + '/' + new_intensive_filename)]
    new_deaths_filenames = [os.path.join(project_dir, figure_directory + '/' + new_deaths_filename)]
    hospitalisations_filenames = [os.path.join(project_dir, figure_directory + '/' + hospitalisations_filename)]
    intensive_filenames = [os.path.join(project_dir, figure_directory + '/' + intensive_filename)]
    deaths_filenames = [os.path.join(project_dir, figure_directory + '/' + deaths_filename)]
    cured_filenames = [os.path.join(project_dir, figure_directory + '/' + cured_filename)]

    french_departments = []
    french_departments.extend(range(1, 20))
    french_departments.extend(['2A', '2B'])
    french_departments.extend(range(21, 96))
    for dep in french_departments:
        if (isinstance(dep, int)):
            new_hospitalisations_filenames.append(os.path.join(project_dir, figure_directory +'/departements/' + "{:02d}".format(dep) + '/' + new_hospitalisations_filename))
            new_intensive_filenames.append(os.path.join(project_dir, figure_directory + '/departements/' + "{:02d}".format(dep) + '/' + new_intensive_filename))
            new_deaths_filenames.append(os.path.join(project_dir, figure_directory + '/departements/' + "{:02d}".format(dep) + '/' + new_deaths_filename))
            hospitalisations_filenames.append(os.path.join(project_dir, figure_directory + '/departements/' + "{:02d}".format(dep) + '/' + hospitalisations_filename))
            intensive_filenames.append(os.path.join(project_dir, figure_directory + '/departements/' + "{:02d}".format(dep) + '/' + intensive_filename))
            deaths_filenames.append(os.path.join(project_dir, figure_directory + '/departements/' + "{:02d}".format(dep) + '/' + deaths_filename))
            cured_filenames.append(os.path.join(project_dir, figure_directory + '/departements/' + "{:02d}".format(dep) + '/' + cured_filename))
        else:
            new_hospitalisations_filenames.append(os.path.join(project_dir, figure_directory +'/departements/' + dep + '/' + new_hospitalisations_filename))
            new_intensive_filenames.append(os.path.join(project_dir, figure_directory + '/departements/' + dep + '/' + new_intensive_filename))
            new_deaths_filenames.append(os.path.join(project_dir, figure_directory + '/departements/' + dep + '/' + new_deaths_filename))
            hospitalisations_filenames.append(os.path.join(project_dir, figure_directory + '/departements/' + dep + '/' + hospitalisations_filename))
            intensive_filenames.append(os.path.join(project_dir, figure_directory + '/departements/' + dep + '/' + intensive_filename))
            deaths_filenames.append(os.path.join(project_dir, figure_directory + '/departements/' + dep + '/' + deaths_filename))
            cured_filenames.append(os.path.join(project_dir, figure_directory + '/departements/' + dep + '/' + cured_filename))
    dom_tom = [971, 972, 973, 974, 976]
    for dep in dom_tom:
        new_hospitalisations_filenames.append(os.path.join(project_dir, figure_directory + '/departements/' + str(dep) + '/' + new_hospitalisations_filename))
        new_intensive_filenames.append(os.path.join(project_dir, figure_directory + '/departements/' + str(dep) + '/' + new_intensive_filename))
        new_deaths_filenames.append(os.path.join(project_dir, figure_directory + '/departements/' + str(dep) + '/' + new_deaths_filename))
        hospitalisations_filenames.append(os.path.join(project_dir, figure_directory + '/departements/' + str(dep) + '/' + hospitalisations_filename))
        intensive_filenames.append(os.path.join(project_dir, figure_directory + '/departements/' + str(dep) + '/' + intensive_filename))
        deaths_filenames.append(os.path.join(project_dir, figure_directory + '/departements/' + str(dep) + '/' + deaths_filename))
        cured_filenames.append(os.path.join(project_dir, figure_directory + '/departements/' + str(dep) + '/' + cured_filename))
    create_gif(new_hospitalisations_filenames, os.path.join(project_dir, gifs_directory), 'hospitalisations-nouveaux.gif', 60000)
    create_gif(new_intensive_filenames, os.path.join(project_dir, gifs_directory), 'reanimations-nouveaux.gif', 60000)
    create_gif(new_deaths_filenames, os.path.join(project_dir, gifs_directory), 'deces-nouveaux.gif', 60000)
    create_gif(hospitalisations_filenames, os.path.join(project_dir, gifs_directory), 'hospitalisations.gif', 60000)
    create_gif(intensive_filenames, os.path.join(project_dir, gifs_directory), 'reanimations.gif', 60000)
    create_gif(deaths_filenames, os.path.join(project_dir, gifs_directory), 'deces.gif', 60000)
    create_gif(cured_filenames, os.path.join(project_dir, gifs_directory), 'retours-a-domicile.gif', 60000)


def create_gif(filenames, dest_path, dest_filename, total_duration):
    # get logger
    logger = logging.getLogger(__name__)

    images = []

    for filename in filenames:
        images.append(Image.open(filename))

    create_directory_if_necessary(dest_path)

    logger.info('saving '+ os.path.join(dest_path, dest_filename))

    images[0].save(os.path.join(dest_path, dest_filename),
                   save_all=True, append_images=images[1:], optimize=False, duration=total_duration / len(images), loop=0)


if __name__ == '__main__':
    # getting root directory
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    # setup logger
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automatically by walking up directories until it's found
    dotenv_path = find_dotenv()
    # load up the entries as environment variables
    load_dotenv(dotenv_path)

    # call the main
    main(project_dir)
