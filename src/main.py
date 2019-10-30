from src.data.cems import download_cems
from src.data.eia_bulk_extract import extract_all_bulk_data
from src.data.region_labels import write_region_labels
from src.website.data_prep import make_web_files


def main():

    download_cems()
    extract_all_bulk_data()
    # write_region_labels()

    from src.analysis.calc_national_nerc_index import CarbonIndex

    ci = CarbonIndex()
    ci.calc_national_index()
    ci.calc_national_gen_intensity()
    # ci.calc_nerc_index()
    ci.save_files()

    from src.analysis.calc_state_index import calc_state_index_gen

    calc_state_index_gen()

    from src.website.blog_generator import write_blog_text
    make_web_files()
    write_blog_text()


if __name__ == "__main__":
    main()
