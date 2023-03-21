import requests
import json
from urllib.parse import urlparse, parse_qs, quote_plus, unquote_plus
from PIL import Image
import os
import pandas as pd
import os.path
import time
from tqdm import tqdm

DATA_FOLDER = 'data/'

def load_data():
    taxon_paths = {
        # "armillaria_mellea": "66576, 60212, 60059, 66090, 66108, 60012, 60011, 66244, 50126, 10526",
        # "boletus_edulis": "66576, 60212, 60059, 66090, 66108, 60012, 60066, 60065, 50226, 11069",
        # "suillus_luteus": "66576, 60212, 60059, 66090, 66108, 60012, 60066, 60556, 51902, 20734",
        # "cantharellus_cibarius": "66576, 60212, 60059, 66090, 66108, 60083, 60082, 50309, 11317"
        # "russula_vesca": "66576, 60212, 60059, 66090, 66108, 60509, 60508, 51729, 20093",
        # "amanita_phalloides": "66576, 60212, 60059, 66090, 66108, 60012, 60011, 66237, 50051, 63478",
        # "rubroboletus_satanas": "66576, 60212, 60059, 66090, 66108, 60012, 60066, 60065, 65782, 65783",
        # "amanita_muscaria": "66576, 60212, 60059, 66090, 66108, 60012, 60011, 66237, 50051, 10252",
        # "inocybe_geophylla": "66576, 60212, 60059, 66090, 66108, 60012, 60011, 66269, 62302, 15371",
        # "chalciporus_piperatus": "66576, 60212, 60059, 66090, 66108, 60012, 60066, 60065, 50371, 11573",
        # "hypholoma_fasciculare": "66576, 60212, 60059, 66090, 66108, 60012, 60011, 60555, 62263, 15078",
        # "agaricus_xanthodermus": "66576, 60212, 60059, 66090, 66108, 60012, 60011, 60010, 50030, 10116",
        # "russula_emetica": "66576, 60212, 60059, 66090, 66108, 60509, 60508, 51729, 19964",
        # "hygrophoropsis_aurantiaca": "66576, 60212, 60059, 66090, 66108, 60012, 60066, 60261, 62245, 14886"
    }
    limit = 500
    offset = 0

    visited_path = os.path.join(DATA_FOLDER, 'visited_records.csv')
    visited_df = open_visited_df(visited_path)
    new_df = pd.DataFrame(columns=['id', 'species'])

    for species, taxon_path in taxon_paths.items():
        print(f'Species {species} started')
        root_url, query_str = parse_url(taxon_path, limit, offset)

        resp = requests.get(root_url, params=query_str)
        data = resp.json()

        create_species_folder(species)

        cur_visited = set(visited_df[visited_df['species'] == species]['id'])
        cur_new = []
        for record in tqdm(data):
            time.sleep(0.01)

            if record["_id"] in cur_visited:
                continue
            else:
                cur_new.append(record["_id"])

            if "Images" not in record:
                continue

            for img in record["Images"]:
                img_id = img["_id"]
                img_name = img["name"]

                # start = time.time()
                img_url = """https://svampe.databasen.org/uploads/""" + img_name + """.JPG"""
                img = Image.open(requests.get(img_url, stream=True).raw)
                # stop = time.time()
                # print(f'img: {img_name}, load time: {stop-start}')
                
                # start = time.time()
                img_path = os.path.join(DATA_FOLDER, 'raw', species, f'{img_name}.png')
                img.save(img_path)
                # stop = time.time()
                # print(f'img: {img_name}, save time: {stop-start}')

        cur_new_df = pd.DataFrame(cur_new, columns=['id'])
        cur_new_df['species'] = species
        new_df = pd.concat([new_df, cur_new_df])
    
    save_visited_df(visited_path, visited_df, new_df)

def open_visited_df(visited_path):
    if os.path.exists(visited_path):
        visited_df = pd.read_csv(visited_path)
    else:
        visited_df = pd.DataFrame(columns=['id', 'species'])
    return visited_df

def save_visited_df(visited_path, visited_df, new_df):
    visited_df = pd.concat([visited_df, new_df])
    visited_df.to_csv(visited_path, index=False)

def create_species_folder(species):
    species_path = os.path.join(DATA_FOLDER, 'raw', species)
    if not os.path.exists(species_path):
        os.mkdir(species_path)

def parse_url(taxon_path, limit, offset):
    initial_url = """https://svampe.databasen.org/api/observations?_order=%5B%5B%22observationDate%22,%22DESC%22,%22ASC%22%5D,%5B%22_id%22,%22DESC%22%5D%5D&include=%5B%22%7B%5C%22model%5C%22:%5C%22DeterminationView%5C%22,%5C%22as%5C%22:%5C%22DeterminationView%5C%22,%5C%22attributes%5C%22:%5B%5C%22Taxon_id%5C%22,%5C%22Recorded_as_id%5C%22,%5C%22Taxon_FullName%5C%22,%5C%22Taxon_vernacularname_dk%5C%22,%5C%22Taxon_RankID%5C%22,%5C%22Determination_validation%5C%22,%5C%22Taxon_redlist_status%5C%22,%5C%22Taxon_path%5C%22,%5C%22Recorded_as_FullName%5C%22,%5C%22Determination_user_id%5C%22,%5C%22Determination_score%5C%22,%5C%22Determination_validator_id%5C%22,%5C%22Determination_species_hypothesis%5C%22,%5C%22Determination_notes%5C%22%5D,%5C%22where%5C%22:%7B%5C%22$and%5C%22:%7B%5C%22$or%5C%22:%5B%5D%7D,%5C%22$or%5C%22:%5B%7B%5C%22Taxon_path%5C%22:%7B%5C%22like%5C%22:%5C%2266576,+60212,+60059,+66090,+66108,+60012,+60066,+60065,+50226,+11069%25%5C%22%7D%7D%5D%7D%7D%22,%22%7B%5C%22model%5C%22:%5C%22User%5C%22,%5C%22as%5C%22:%5C%22PrimaryUser%5C%22,%5C%22required%5C%22:false,%5C%22where%5C%22:%7B%7D%7D%22,%22%7B%5C%22model%5C%22:%5C%22Locality%5C%22,%5C%22as%5C%22:%5C%22Locality%5C%22,%5C%22attributes%5C%22:%5B%5C%22_id%5C%22,%5C%22name%5C%22%5D,%5C%22where%5C%22:%7B%7D,%5C%22required%5C%22:true%7D%22,%22%7B%5C%22model%5C%22:%5C%22GeoNames%5C%22,%5C%22as%5C%22:%5C%22GeoNames%5C%22,%5C%22where%5C%22:%7B%7D,%5C%22required%5C%22:false%7D%22,%22%7B%5C%22model%5C%22:%5C%22ObservationUser%5C%22,%5C%22as%5C%22:%5C%22userIds%5C%22,%5C%22where%5C%22:%7B%7D,%5C%22required%5C%22:false%7D%22,%22%7B%5C%22model%5C%22:%5C%22ObservationImage%5C%22,%5C%22as%5C%22:%5C%22Images%5C%22,%5C%22where%5C%22:%7B%7D,%5C%22required%5C%22:false%7D%22,%22%7B%5C%22model%5C%22:%5C%22ObservationForum%5C%22,%5C%22as%5C%22:%5C%22Forum%5C%22,%5C%22where%5C%22:%7B%7D,%5C%22required%5C%22:false%7D%22,%22%7B%5C%22model%5C%22:%5C%22ObservationArea%5C%22,%5C%22as%5C%22:%5C%22areaIds%5C%22,%5C%22where%5C%22:%7B%7D,%5C%22required%5C%22:false%7D%22,%22%7B%5C%22model%5C%22:%5C%22Determination%5C%22,%5C%22as%5C%22:%5C%22Determinations%5C%22,%5C%22where%5C%22:%7B%7D,%5C%22attributes%5C%22:%5B%5C%22_id%5C%22,%5C%22score%5C%22%5D,%5C%22required%5C%22:false%7D%22,%22%7B%5C%22model%5C%22:%5C%22DnaSequence%5C%22,%5C%22as%5C%22:%5C%22DnaSequence%5C%22,%5C%22where%5C%22:%7B%7D,%5C%22attributes%5C%22:%5B%5C%22_id%5C%22,%5C%22marker%5C%22,%5C%22geneticAccessionNumber%5C%22%5D,%5C%22required%5C%22:false%7D%22%5D&limit=5&offset=0&where=%7B%7D"""

    parsed = urlparse(initial_url)
    query = parse_qs(parsed.query)
    root_url = parsed._replace(query=None).geturl()

    taxon_path = quote_plus(taxon_path)
    include_param = """%5B%22%7B%5C%22model%5C%22:%5C%22DeterminationView%5C%22,%5C%22as%5C%22:%5C%22DeterminationView%5C%22,%5C%22attributes%5C%22:%5B%5C%22Taxon_id%5C%22,%5C%22Recorded_as_id%5C%22,%5C%22Taxon_FullName%5C%22,%5C%22Taxon_vernacularname_dk%5C%22,%5C%22Taxon_RankID%5C%22,%5C%22Determination_validation%5C%22,%5C%22Taxon_redlist_status%5C%22,%5C%22Taxon_path%5C%22,%5C%22Recorded_as_FullName%5C%22,%5C%22Determination_user_id%5C%22,%5C%22Determination_score%5C%22,%5C%22Determination_validator_id%5C%22,%5C%22Determination_species_hypothesis%5C%22,%5C%22Determination_notes%5C%22%5D,%5C%22where%5C%22:%7B%5C%22$and%5C%22:%7B%5C%22$or%5C%22:%5B%5D%7D,%5C%22$or%5C%22:%5B%7B%5C%22Taxon_path%5C%22:%7B%5C%22like%5C%22:%5C%22""" + taxon_path + """%25%5C%22%7D%7D%5D%7D%7D%22,%22%7B%5C%22model%5C%22:%5C%22User%5C%22,%5C%22as%5C%22:%5C%22PrimaryUser%5C%22,%5C%22required%5C%22:false,%5C%22where%5C%22:%7B%7D%7D%22,%22%7B%5C%22model%5C%22:%5C%22Locality%5C%22,%5C%22as%5C%22:%5C%22Locality%5C%22,%5C%22attributes%5C%22:%5B%5C%22_id%5C%22,%5C%22name%5C%22%5D,%5C%22where%5C%22:%7B%7D,%5C%22required%5C%22:true%7D%22,%22%7B%5C%22model%5C%22:%5C%22GeoNames%5C%22,%5C%22as%5C%22:%5C%22GeoNames%5C%22,%5C%22where%5C%22:%7B%7D,%5C%22required%5C%22:false%7D%22,%22%7B%5C%22model%5C%22:%5C%22ObservationUser%5C%22,%5C%22as%5C%22:%5C%22userIds%5C%22,%5C%22where%5C%22:%7B%7D,%5C%22required%5C%22:false%7D%22,%22%7B%5C%22model%5C%22:%5C%22ObservationImage%5C%22,%5C%22as%5C%22:%5C%22Images%5C%22,%5C%22where%5C%22:%7B%7D,%5C%22required%5C%22:false%7D%22,%22%7B%5C%22model%5C%22:%5C%22ObservationForum%5C%22,%5C%22as%5C%22:%5C%22Forum%5C%22,%5C%22where%5C%22:%7B%7D,%5C%22required%5C%22:false%7D%22,%22%7B%5C%22model%5C%22:%5C%22ObservationArea%5C%22,%5C%22as%5C%22:%5C%22areaIds%5C%22,%5C%22where%5C%22:%7B%7D,%5C%22required%5C%22:false%7D%22,%22%7B%5C%22model%5C%22:%5C%22Determination%5C%22,%5C%22as%5C%22:%5C%22Determinations%5C%22,%5C%22where%5C%22:%7B%7D,%5C%22attributes%5C%22:%5B%5C%22_id%5C%22,%5C%22score%5C%22%5D,%5C%22required%5C%22:false%7D%22,%22%7B%5C%22model%5C%22:%5C%22DnaSequence%5C%22,%5C%22as%5C%22:%5C%22DnaSequence%5C%22,%5C%22where%5C%22:%7B%7D,%5C%22attributes%5C%22:%5B%5C%22_id%5C%22,%5C%22marker%5C%22,%5C%22geneticAccessionNumber%5C%22%5D,%5C%22required%5C%22:false%7D%22%5D"""
    

    query['include'] = [include_param]
    query['limit'] = [str(limit)]
    query['offset'] = [str(offset)]

    # for (k, v) in query.items():
    #     print(k, v)

    query_str = '&'.join([f'{k}={v[0]}' for (k, v) in query.items()])

    return root_url, query_str

if __name__ == "__main__":
    load_data()

# 1. don't resize before saving - may want to apply another algorithm
# 2. doesn't worth to parallel saving - 1 bus is used
# 3. rewrite to save if exception