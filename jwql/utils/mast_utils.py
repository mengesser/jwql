"""Various utility functions for interacting with MAST

Authors
-------

    - Bryan Hilbert

Use
---

    This module can be imported as such:

    >>> import mast_utils
    results = mast_utils.mast_query('nircam', 'NRCA1_FULL', 'NRC_DARK', 53005.1, 53005.2)

 """
import datetime
import os

from jwql.database.database_interface import Monitor
from jwql.jwql_monitors import monitor_mast
from jwql.utils.constants import INSTRUMENT_MONITOR_DATABASE_TABLES, JWST_DATAPRODUCTS
from jwql.utils.logging_functions import configure_logging, get_log_status


def initialize_instrument_monitor(module):
    """Configures a log file for the instrument monitor run and
    captures the start time of the monitor

    Parameters
    ----------
    module : str
        The module name (e.g. ``dark_monitor``)

    Returns
    -------
    start_time : datetime object
        The start time of the monitor
    log_file : str
        The path to where the log file is stored
    """
    start_time = datetime.datetime.now()
    log_file = configure_logging(module)

    return start_time, log_file


def mast_query_orig(instrument, aperture, templates, start_date, end_date):
    """Use ``astroquery`` to search MAST for data for given observation
    templates over a given time range

    Parameters
    ----------
    instrument : str
        Instrument name (e.g. ``nircam``)

    aperture : str
        Detector aperture to search for (e.g. ``NRCA1_FULL``)

    templates : str or list
        Single, or list of, templates for the query (e.g. ``NRC_DARK``, ``MIR_FLATMRS``)

    start_date : float
        Starting date for the search in MJD

    end_date : float
        Ending date for the search in MJD

    Returns
    -------
    query_results : list
        List of dictionaries containing the query results
    """
    # If a single template name is input as a string, put it in a list
    if isinstance(templates, str):
        templates = [templates]

    # Make sure instrument is correct case
    if instrument.lower() == 'nircam':
        instrument = 'NIRCam'
    elif instrument.lower() == 'niriss':
        instrument = 'NIRISS'
    elif instrument.lower() == 'nirspec':
        instrument = 'NIRSpec'
    elif instrument.lower() == 'fgs':
        instrument = 'FGS'
    elif instrument.lower() == 'miri':
        instrument = 'MIRI'

    # monitor_mast.instrument_inventory does not allow list inputs to
    # the added_filters input (or at least if you do provide a list, then
    # it becomes a nested list when it sends the query to MAST. The
    # nested list is subsequently ignored by MAST.)
    # So query once for each flat template, and combine outputs into a
    # single list.
    query_results = []
    for template_name in templates:

        # Create dictionary of parameters to add
        parameters = {"date_obs_mjd": {"min": start_date, "max": end_date},
                      "apername": aperture, "exp_type": template_name}

        query = monitor_mast.instrument_inventory(instrument, dataproduct=JWST_DATAPRODUCTS,
                                                  add_filters=parameters, return_data=True, caom=False)
        if len(query['data']) > 0:
            query_results.extend(query['data'])

    return query_results


def mast_query(instrument, templates, start_date, end_date, aperture=None, detector=None, filter_name=None,
               pupil=None, grating=None, readpattern=None, lamp=None):
    """Use ``astroquery`` to search MAST for data for given observation
    templates over a given time range

    Parameters
    ----------
    instrument : str
        Instrument name (e.g. ``nircam``)

    templates : str or list
        Single, or list of, templates for the query (e.g. ``NRC_DARK``, ``MIR_FLATMRS``)

    start_date : float
        Starting date for the search in MJD

    end_date : float
        Ending date for the search in MJD

    aperture : str
        Detector aperture to search for (e.g. ``NRCA1_FULL``)

    detector : str
        Detector name (e.g. MIRIMAGE)

    filter_name : str
        Fitler element (e.g. F200W)

    pupil : str
        Pupil element (e.g. F323N)

    grating : str
        Grating element (e.g. MIRROR)

    readpattern : str
        Detector read out pattern (e.g. NISRAPID)

    lamp : str
        Lamp name (e.g. LINE2)

    Returns
    -------
    query_results : list
        List of dictionaries containing the query results
    """
    # If a single template name is input as a string, put it in a list
    if isinstance(templates, str):
        templates = [templates]

    # Make sure instrument is correct case
    if instrument.lower() == 'nircam':
        instrument = 'NIRCam'
    elif instrument.lower() == 'niriss':
        instrument = 'NIRISS'
    elif instrument.lower() == 'nirspec':
        instrument = 'NIRSpec'
    elif instrument.lower() == 'fgs':
        instrument = 'FGS'
    elif instrument.lower() == 'miri':
        instrument = 'MIRI'

    # monitor_mast.instrument_inventory does not allow list inputs to
    # the added_filters input (or at least if you do provide a list, then
    # it becomes a nested list when it sends the query to MAST. The
    # nested list is subsequently ignored by MAST.)
    # So query once for each flat template, and combine outputs into a
    # single list.
    query_results = []
    for template_name in templates:

        # Create dictionary of parameters to add
        parameters = {"date_obs_mjd": {"min": start_date, "max": end_date},
                      "exp_type": template_name}

        if detector is not None:
            parameters["detector"] = detector
        if aperture is not None:
            parameters["apername"] = aperture
        if filter_name is not None:
            parameters["filter"] = filter_name
        if pupil is not None:
            parameters["pupil"] = pupil
        if grating is not None:
            parameters["grating"] = grating
        if readpattern is not None:
            parameters["readpatt"] = readpattern
        if lamp is not None:
            parameters["lamp"] = lamp
        #if lamp_power is not None:
        #    parameters["???"] = lamp_power

        query = monitor_mast.instrument_inventory(instrument, dataproduct=JWST_DATAPRODUCTS,
                                                  add_filters=parameters, return_data=True, caom=False)
        if len(query['data']) > 0:
            query_results.extend(query['data'])

    return query_results


def mast_query_miri(detector, aperture, templates, start_date, end_date):
    """Use ``astroquery`` to search MAST for data for given observation
    templates over a given time range for MIRI. Miri is different than
    the other instruments in that (to find full frame flats and darks at
    least) you need to use the detector name rather than the aperture
    name. There is no full frame aperture name for the MRS detectors.

    Parameters
    ----------
    detector : str
        Name of the detector to search for. One of MIRIMAGE, MIRIFULONG, MIRIFUSHORT.

    aperture : str
        Aperture name on the detector (e.g. MIRIM_FULL)

    templates : str or list
        Single, or list of, templates for the query (e.g. ``NRC_DARK``, ``MIR_FLATMRS``)

    start_date : float
        Starting date for the search in MJD

    end_date : float
        Ending date for the search in MJD

    Returns
    -------
    query_results : list
        List of dictionaries containing the query results
    """
    # If a single template name is input as a string, put it in a list
    if isinstance(templates, str):
        templates = [templates]

    instrument = 'MIRI'

    # monitor_mast.instrument_inventory does not allow list inputs to
    # the added_filters input (or at least if you do provide a list, then
    # it becomes a nested list when it sends the query to MAST. The
    # nested list is subsequently ignored by MAST.)
    # So query once for each flat template, and combine outputs into a
    # single list.
    query_results = []
    for template_name in templates:

        # Create dictionary of parameters to add
        if aperture.lower() != 'none':
            parameters = {"date_obs_mjd": {"min": start_date, "max": end_date},
                          "detector": detector, "apername": aperture, "exp_type": template_name}
        else:
            parameters = {"date_obs_mjd": {"min": start_date, "max": end_date},
                          "detector": detector, "exp_type": template_name}

        query = monitor_mast.instrument_inventory(instrument, dataproduct=JWST_DATAPRODUCTS,
                                                  add_filters=parameters, return_data=True, caom=False)
        if len(query['data']) > 0:
            query_results.extend(query['data'])

    return query_results


def update_monitor_table(module, start_time, log_file):
    """Update the ``monitor`` database table with information about
    the instrument monitor run

    Parameters
    ----------
    module : str
        The module name (e.g. ``dark_monitor``)
    start_time : datetime object
        The start time of the monitor
    log_file : str
        The path to where the log file is stored
    """
    new_entry = {}
    new_entry['monitor_name'] = module
    new_entry['start_time'] = start_time
    new_entry['end_time'] = datetime.datetime.now()
    new_entry['status'] = get_log_status(log_file)
    new_entry['affected_tables'] = INSTRUMENT_MONITOR_DATABASE_TABLES[module]
    new_entry['log_file'] = os.path.basename(log_file)

    Monitor.__table__.insert().execute(new_entry)
