#! /usr/bin/env python3
# coding: utf-8

"""
Author: [Nastyflav](https://github.com/Nastyflav) 2020-04-23
Licence: `GNU GPL v3` GNU GPL v3: http://www.gnu.org/licenses/

"""

from django.core.management.base import BaseCommand

from .database import Database


class Command(BaseCommand):
    """Command class for custom django commands"""
    help = "Load datas from the OFF API to our database"

    def handle(self, *args, **options):
        self.db = Database()
        self.db.add_categories()
        self.db.add_products()
