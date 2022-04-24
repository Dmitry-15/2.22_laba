#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Для индивидуального задания лабораторной работы 2.21 добавьте тесты с использованием
модуля unittest, проверяющие операции по работе с базой данных.
"""

import sqlite3
import typing as t
from pathlib import Path
import argparse


def add_human(
        database_path: Path,
        name: str,
        zodiac: str,
        year: str
):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    # Получить идентификатор человека в базе данных.
    # Если такой записи нет, то добавить информацию о человеке
    cursor.execute(
        """
        SELECT human_id FROM human_name WHERE name = ?
        """,
        (name,)
    )
    row = cursor.fetchone()
    if row is None:
        cursor.execute(
            """
            INSERT INTO human_name (name) VALUES (?)
            """,
            (name,)
        )
        human_id = cursor.lastrowid
    else:
        human_id = row[0]

        # Добавить информацию о новом человеке
    cursor.execute(
        """
        INSERT INTO people (human_id, zodiac, year)
        VALUES (?, ?, ?)
        """,
        (human_id, zodiac, year)
    )
    cursor.execute(
        """
        SELECT human_name.name, people.zodiac, people.year
        FROM people
        INNER JOIN human_name ON people.human_id = human_name.human_id 
        ORDER BY people.human_id DESC LIMIT 1
        """
    )
    conn.commit()
    conn.close()


def display_people(people: t.List[t.Dict[str, t.Any]]) -> None:
    if people:
        line = '+-{}-+-{}-+-{}-+-{}-+'.format(
            '-' * 4,
            '-' * 30,
            '-' * 20,
            '-' * 20
        )
        print(line)
        print(
            '| {:^4} | {:^30} | {:^20} | {:^20} |'.format(
                "№",
                "ФИО",
                "Знак зодиака",
                "Дата рождения"
            )
        )
        print(line)
        for idx, human in enumerate(people, 1):
            print(
                '| {:>4} | {:<30} | {:<20} | {:>20} |'.format(

                    idx,
                    human.get('name', ''),
                    human.get('groupt', ''),
                    human.get('grade', 0)

                )
            )
            print(line)


def select_humans(database_path):
    """
    Выбрать всех людей
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT human_name.name, people.zodiac, people.year
        FROM people
        INNER JOIN human_name ON human_name.human_id = people.human_id
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "name": row[0],
            "zodiac": row[1],
            "year": row[2],

        }
        for row in rows
    ]


def select_human(database_path, name) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать человека по фамилии
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT human_name.name, people.zodiac, people.year
        FROM people
        INNER JOIN human_name ON human_name.human_id = people.human_id
        WHERE human_name.name == ?
        """,
        (name,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "name": row[0],
            "zodiac": row[1],
            "year": row[2],
        }
        for row in rows
    ]


def create_db(database_path: Path):
    """
    Создать базу данных
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    # Создать таблицу людей по фамилиям
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS human_name (
        human_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
        )
        """
    )
    # Создать таблицу людей с полной информацией
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS people (
        human_id INTEGER PRIMARY KEY AUTOINCREMENT,
        zodiac INTEGER NOT NULL,
        year TEXT NOT NULL,
        FOREIGN KEY(human_id) REFERENCES human_name(human_id)
        )
        """
    )


def load():
    args = str(Path.home() / "people.db")
    db_path = Path(args)
    return db_path


def main(command_line=None):
    """
    Основная функция программы
    """
    # Создать родительский парсер для определения имени файла
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "--db",
        action="store",
        required=False,
        default=str(Path.home() / "people.db"),
        help="The data file name"
    )
    # Создать основной парсер командной строки
    parser = argparse.ArgumentParser("humans")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    subparsers = parser.add_subparsers(dest="command")
    # Создать субпарсер для добавления человека
    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Add a new human"
    )
    add.add_argument(
        "-n",
        "--name",
        action="store",
        required=True,
        help="The human's name"
    )
    add.add_argument(
        "-z",
        "--zodiac",
        action="store",
        required=True,
        help="The human's zodiac"
    )
    add.add_argument(
        "-yr",
        "--year",
        action="store",
        required=True,
        help="The human's year"
    )
    _ = subparsers.add_parser(
        "display",
        parents=[file_parser],
        help="Display all people"
    )
    # Создать субпарсер для выбора человека
    select = subparsers.add_parser(
        "select",
        parents=[file_parser],
        help="Select the human"
    )
    select.add_argument(
        "-s",
        "--select",
        action="store",
        required=True,
        help="The human's name"
    )
    args = parser.parse_args(command_line)
    create_db(load())
    if args.command == "add":
        add_human(load(), args.name, args.zodiac, args.year)
    elif args.command == "select":
        display_people(select_human(load(), args.name))
    elif args.command == "display":
        display_people(select_humans(load()))
    pass


if __name__ == '__main__':
    main()