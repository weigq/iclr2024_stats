#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sqlite3

import numpy as np
import requests
from termcolor import colored


class DataBase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.database = None
        self.cursor = None

    def initialize(self, create: bool = False):
        self.database = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.database.cursor()

        if create:
            _cmd = (
                f"CREATE TABLE submissions "
                f"(url text PRIMARY KEY, title text, keywords text, "
                f"rating_0_cnt int, rating_0_avg float, rating_0_std float, ratings_0 text,"
                f"decision text, withdraw int )"
            )
            self.cursor.execute(_cmd)

    def write_item_rating(
        self,
        suf: int,
        item_id: str,
        ratings: list,
        withdraw: int,
        decision: str,
        title: str,
        pdf: str,
        keywords: list,
        authors: list,
    ):
        if suf == 0:
            title = title.replace("\\", "").replace('"', "'")
            authors = [a.replace("\\", "").replace('"', "'") for a in authors]
            authors = ", ".join(authors)
            keywords = [k.replace("\\", "").replace('"', "'") for k in keywords]
            keywords = ", ".join(keywords)
            pdf = pdf.replace("\\", "").replace('"', "'")

            num_rating = len(ratings)
            rating_avg = np.mean(ratings).item()
            rating_std = np.std(ratings).item()
            ratings = ", ".join(map(str, ratings))
            _cmd = (
                f"INSERT INTO submissions "
                f"(url_id, r_{suf}_cnt, r_{suf}_avg, r_{suf}_std, r_{suf}, "
                f"withdraw, decision, title, authors, pdf, keywords) "
                f'VALUES ("{item_id}", {num_rating}, {rating_avg}, '
                f"{rating_std}, "
                f'"{ratings}", {withdraw}, "{decision}", '
                f'"{title}", "{authors}", "{pdf}", "{keywords}" '
                f") "
            )
        else:
            num_rating = len(ratings)
            rating_avg = np.mean(ratings).item()
            rating_std = np.std(ratings).item()
            ratings = ", ".join(map(str, ratings))
            _cmd = (
                f"UPDATE submissions "
                f"SET "
                f"r_{suf}_cnt = {num_rating}, r_{suf}_avg = {rating_avg}, "
                f"r_{suf}_std = {rating_std}, "
                f'r_{suf} = "{ratings}", withdraw = {withdraw}, decision = "{decision}" '
                f'WHERE url_id = "{item_id}"'
            )
        try:
            self.cursor.execute(_cmd)
            self.database.commit()
        except sqlite3.Error as e:
            print(f"error: {e.args[0]}")

    def close(self):
        self.cursor.close()
        self.database.close()


def parse_item(i, suf, url, db_path):
    print(colored(f"+++ {i}/{url}", "light_red"))
    item_id = url.split("id=")[-1]
    rqst_url = f"https://api2.openreview.net/notes?forum={item_id}"
    rqst_data = requests.get(rqst_url)
    rqst_data = json.loads(rqst_data.text)

    # parse each note

    # filter meta note
    meta_note = [d for d in rqst_data["notes"] if "replyto" not in d]
    # check withdrawn
    withdraw = 1 if "Withdrawn_Submission" in meta_note[0]["invitations"] else 0

    # === decision ===
    decision = ""
    # only after final decision
    # if withdraw == 0:
    #     decision_note = [d for d in rqst_data['notes'] if 'Decision' in d['invitation']]
    #     decision = decision_note[0]['content']['decision']
    # else:
    #     decision = ''

    # meta data
    title = meta_note[0]["content"]["title"]["value"]
    pdf = meta_note[0]["content"]["pdf"]["value"]
    keywords = meta_note[0]["content"]["keywords"]["value"]
    authors = []

    # filter reviewer comments
    comment_notes = [
        d
        for d in rqst_data["notes"]
        if "Official_Review" in d["invitations"][0] and "rating" in d["content"].keys()
    ]
    comment_notes = sorted(comment_notes, key=lambda d: d["number"])[::-1]
    ratings = [
        int(note["content"]["rating"]["value"].split(":")[0]) for note in comment_notes
    ]

    db = DataBase(db_path)
    db.initialize(create=False)
    db.write_item_rating(
        suf=suf,
        item_id=item_id,
        authors=authors,
        ratings=ratings,
        withdraw=withdraw,
        decision=decision,
        title=title,
        pdf=pdf,
        keywords=keywords,
    )
    print(colored(f"--- {i}/{url}", "light_green"))
    db.close()
