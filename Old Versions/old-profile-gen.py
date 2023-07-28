import argparse
import csv
import gzip
import hashlib
import json
import os
import random
import shutil
import uuid
from typing import Dict, List, Union

class Identity:
    ID_TYPES = ["email", "idfa", "gaid", "c0", "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9"]
    FILE_TYPES = ["csv", "json"]
    TRAITS = ["colour", "car", "age", "gender"]
    COLOURS = ["red", "green", "blue", "yellow", "orange", "purple", "pink", "brown", "black", "white"]
    CAR_MANUFACTURERS = ["Ford", "Toyota", "Honda", "GM", "Tesla", "VW", "Mercedes", "BMW", "Audi", "Fiat"]
    GENDERS = ["male", "female"]

    def __init__(self, args):
        self.id_types = args.id_types
        self.file_type = args.file_type
        self.count = args.count
        self.partners = args.partners
        self.ppid_count = 32 if args.ppid_count is None else args.ppid_count
        self.add_traits = args.add_traits
        self.gzip = args.gzip

    # Generate hashed emails.
    def _generate_email_hash(self) -> str:
        email_bytes = random.getrandbits(128).to_bytes(16, byteorder="big")
        return hashlib.sha3_256(email_bytes).hexdigest()

    # Generate MAIDs
    def _generate_idfa(self) -> str:
        return str(uuid.uuid4()).upper()

    def _generate_gaid(self) -> str:
        return str(uuid.uuid4()).upper()

    # Generate custom IDs.
    def _generate_csv_id_c(self) -> str:
        return ''.join(random.choices('0123456789abcdef', k=self.ppid_count))

    # Generate the profile(s).
    def _create_profiles(self) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        identity_cluster = {}
        id_c = self._generate_csv_id_c()

        for id_type in self.id_types:
            if id_type == "email":
                identity_cluster["id_e"] = self._generate_email_hash()
            elif id_type == "gaid":
                identity_cluster["id_g"] = self._generate_gaid()
            elif id_type == "idfa":
                identity_cluster["id_a"] = self._generate_idfa()
            else:
                identity_cluster[f"id_{id_type}"] = id_c

        if self.add_traits:
            identity_cluster |= {
                "trait_colour": random.choice(self.COLOURS),
                "trait_car": random.choice(self.CAR_MANUFACTURERS),
                "trait_age": str(random.randint(18, 45)),
                "trait_gender": random.choice(self.GENDERS),
            }

        return identity_cluster

    def _create_profiless(self) -> List[Dict[str, Union[str, List[Dict[str, str]]]]]:
        return [self._create_profiles() for _ in range(self.count)]

    def _gzip_file(self, file_name):
        with open(file_name, 'rb') as f_in, gzip.open(f'{file_name}.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    def write_clusters(self):
        clusters = self._create_profiless()
        file_name = f"clusters.{self.file_type}"

        if self.file_type == "csv":
            self._write

    def _write_clusters_csv(self, clusters, file_name):
        with open(file_name, 'w') as csvfile:
            fieldnames = clusters[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(clusters)

    def _write_clusters_json(self, clusters, file_name):
        with open(file_name, 'w') as jsonfile:
            for cluster in clusters:
                jsonfile.write(json.dumps(cluster))
                jsonfile.write('\n')

    def write_clusters(self):
        clusters = self._create_profiless()
        file_name = f"clusters.{self.file_type}"

        if self.file_type == "csv":
            self._write_clusters_csv(clusters, file_name)
        elif self.file_type == "json":
            self._write_clusters_json(clusters, file_name)

        if self.gzip:
            self._gzip_file(file_name)

        # This part for creating partner files.
        for _ in range(self.partners):
            with open(file_name, 'r') as input_file:
                lines = input_file.readlines()
                num_rows = len(lines)
                rand_match_perc = random.randint(23, 43) / 100
                num_rows_to_take = int(num_rows * rand_match_perc)
                random_rows = random.sample(lines, num_rows_to_take)
                with open(f"{int(rand_match_perc * 100)}% match rate.{self.file_type}", 'w') as output_file:
                    output_file.writelines(random_rows)

def parse_arguments():
    parser = argparse.ArgumentParser(description='A cluster/record generator.')
    parser.add_argument("-id_types", required=True, choices= Identity.ID_TYPES, nargs='*')
    parser.add_argument("-file_type", required=True, choices= Identity.FILE_TYPES)
    parser.add_argument("-count", required=True, type=int)
    parser.add_argument("-partners", default=0, type=int)
    parser.add_argument("-ppid_count", default=36, type=int)
    parser.add_argument("-add_traits", action=argparse.BooleanOptionalAction)
    parser.add_argument("-gzip", action=argparse.BooleanOptionalAction)

    return parser.parse_args()

def main():
    args = parse_arguments()
    identity = Identity(args)
    identity.write_clusters()

if __name__ == "__main__":
    main()
