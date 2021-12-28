#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definition of the Salt model
"""

import peewee as pw

from tools.db import db


class CardSalt(pw.Model):
    """
    Represent the yearly salt of a card_id
    Because the card_id can't give easily the information on which user is the owner we have to search in every user.
    Here it's a compromise between the time of computation for each salt to find the user and security.
    With a fixed total time for let's say all salt (ie for one search_user(card_id)).
    With more salt the round must be decreased and the security per salt is decreased. We have have 4 possibility :
    - no salt : there is no time benefice (or very little) but allow rainbowtable
    - a unique salt : difficult to bruteforce one person but if the salt is leak it's game over
    - a yearly salt : limit problems in case of a leaked database at some point.
        But still difficult to attack one person
    - a salt per user : easy to attack one user (if they have a lot of money it will be interesting to attack one user
        in particular)

    Here we have chosen the yearly salt solution. As we are in a school and student leave it at some point.
    Like that, we can favor the more recent user/student.
    """
    year = pw.IntegerField(primary_key=True)
    salt = pw.CharField()

    class Meta:
        database = db
