from docx import Document
from ..controller import async_request


def assemble(report_data, requested_site):
    cash_planting = report_data.iloc[0].get("cash_crop_planting_date") \
        if report_data.iloc[0].get("cash_crop_planting_date") is not None else None
    cash_harvest = report_data.iloc[0].get("cash_crop_harvest_date") \
        if report_data.iloc[0].get("cash_crop_harvest_date") is not None else None
    cover_planting = report_data.iloc[0].get("cc_planting_date") \
        if report_data.iloc[0].get("cc_planting_date") is not None else None
    cover_termination = report_data.iloc[0].get("cc_termination_date") \
        if report_data.iloc[0].get("cc_termination_date") is not None else None

    lat = round(report_data.iloc[0].get("latitude"), 4)
    lon = round(report_data.iloc[0].get("longitude"), 4)

    affiliation = report_data.iloc[0].get("affiliation")
    doc = Document()
    document = async_request.AsyncRequest(doc, report_data, requested_site, \
        cash_planting, cash_harvest, cover_planting, cover_termination, \
            lat, lon, affiliation )
    document.doc_header()
    document.doc_main_para()
    document.doc_farmDetails()
    document.doc_cashcrop()
    document.doc_covercrop()
    document.doc_gdd()
    document.doc_precipitation
    document.doc_biomass()
    document.doc_cropquality()
    document.doc_yield()
    document.doc_vwc()
    document.doc_end_para()
    return document.conclude()