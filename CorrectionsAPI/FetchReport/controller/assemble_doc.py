from ..controller import create_doc
from docx import Document
from datetime import datetime


def assemble(report_data, requested_site):
    cash_planting = report_data.iloc[0].get("cash_crop_planting_date") \
        if report_data.iloc[0].get("cash_crop_planting_date") is not None else None
    cash_harvest = report_data.iloc[0].get("cash_crop_harvest_date") \
        if report_data.iloc[0].get("cash_crop_harvest_date") is not None else None
    cover_planting = report_data.iloc[0].get("cc_planting_date") \
        if report_data.iloc[0].get("cc_planting_date") is not None else None
    cover_termination = report_data.iloc[0].get("cc_termination_date") \
        if report_data.iloc[0].get("cc_termination_date") is not None else None

    lat = round(report_data.iloc[0].get("latitude"), 4) \
        if report_data.iloc[0].get("latitude") is not None else None
    lon = round(report_data.iloc[0].get("longitude"), 4) \
        if report_data.iloc[0].get("latitude") is not None else None

    affilition = report_data.iloc[0].get("affiliation")

    doc = Document()
    doc = create_doc.doc_header(doc)

    # PSA paragraph
    doc.add_paragraph("\nThe Precision Sustainable Agriculture (PSA)" +
                      "On-Farm network deploys common research protocols that study the " +
                      "short-term effects of cover crops on farms that currently use cover" +
                      " crops. By utilizing farms with different management practices, the data" +
                      " collected can account for a wide range of factors such as termination " +
                      "timing, specific selections, and climate impacts. The data is used to " +
                      "build tools to aid in site-specific management decisions.\n")

    doc.add_heading('Farm Details', 2)
    doc = create_doc.doc_farmDetails(doc, report_data)

    # Dates this report summarizes
    doc.add_heading('Dates this report summarizes:', 4)
    current_date = datetime.now()
    doc.add_paragraph(current_date.strftime("%m/%d/%Y"))

    # Summary of Activities and Management
    doc.add_heading('Summary of Activities and Management', 2)

    # Dates
    doc = create_doc.doc_cashcrop(doc, cash_planting, cash_harvest)
    doc = create_doc.doc_covercrop(doc, cover_planting, cover_termination)

    # GDD
    doc = create_doc.doc_gdd(
        doc, cash_planting, cash_harvest, cover_planting, cover_termination, lat, lon)

    # Precipitation
    doc = create_doc.doc_precipitation(
        doc, cash_planting, cash_harvest, cover_planting, cover_termination, lat, lon)

    # Biomass
    doc = create_doc.doc_biomass(doc, affilition, requested_site)

    # Composition
    doc = create_doc.doc_cropquality(doc, affilition, requested_site)

    # Yield
    doc = create_doc.doc_yield(doc, requested_site)

    # Temperature, Water and Moisture
    doc = create_doc.doc_vwc(doc, requested_site, cash_planting, cash_harvest)

    # Decision Support Tools
    doc.add_heading('Decision Support Tools:', 3)
    dst_para = doc.add_paragraph()
    dst_para.add_run('The Decision Support Tools (DSTs) are designed for farmers' +
                     ' to input their data and receive custom generated information on how to ' +
                     'address their management strategies. The Cover Crop Nitrogen Calculator ' +
                     '(CC-NCALC) calculates the amount of nitrogen available after the planting ' +
                     'and termination of a cover crop. ')

    return doc
