#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import individ1
import unittest
from pathlib import Path
import tempfile
import shutil


class IndTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path_dir = Path(self.tmp.name)
        shutil.copyfile(individ1.load(), self.path_dir / 'test.db')
        self.fullpath = self.path_dir / 'test.db'
        self.conn = sqlite3.connect(self.fullpath)
        self.cursor = self.conn.cursor()
        self.cursor.execute(
                        """
                        SELECT human_name.name, people.zodiac, people.year
                        FROM people
                        INNER JOIN human_name ON human_name.human_id = people.human_id
                        WHERE human_name.human_id == 1
                        """
        )
        rows = self.cursor.fetchall()
        self.result = [
            {
                "name": row[0],
                "zodiac": row[1],
                "year": row[2],
            }
            for row in rows
        ]

    def test_create_db(self):
        self.cursor.execute(
            """
            SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'people' OR name = 'human_name'
            """
        )
        table = self.cursor.fetchall()
        self.assertEqual(table, [('human_name',), ('people',)])

    def test_add_student(self):
        individ1.add_human(self.fullpath, 'text', 'text', 'text')
        self.cursor.execute(
                        """
                        SELECT human_name.name, people.zodiac, people.year
                        FROM people
                        INNER JOIN human_name ON human_name.human_id = people.human_id
                        WHERE people.human_id = (SELECT MAX(human_id)  FROM people)
                        """
        )
        rows = self.cursor.fetchall()
        self.last = [
            {
                "name": row[0],
                "zodiac": row[1],
                "year": row[2],
            }
            for row in rows
        ]
        self.assertEqual(self.last, [{'name': 'text', 'zodiac': 'text', 'year': 'text'}])

    def test1_select_human_1(self):
        self.assertListEqual(self.result, [{'name': 'Плотников Д. В.', 'zodiac': 'Лев', 'year': '15.08.2002'}])

    def test1_select_human_2(self):
        self.assertNotEqual(self.result, [{'name': 'Бобров Н. В.', 'zodiac': 'Стрелец', 'year': '19.12.2002'}])

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()


if __name__ == '__main__':
    unittest.main()