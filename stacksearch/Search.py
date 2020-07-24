#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Bryan hu .

@Bryan hu .

Made with love by Bryan hu .

The primitive functions to use.
"""
from gevent import monkey as curious_george

curious_george.patch_all(thread=False, select=False)
import requests
import grequests
from bs4 import BeautifulSoup as bs
from typing import Any


async def fSearch(
    Query: str,
    print_prog: bool = True,
    search_on_site: str = "stackoverflow.com",
    # Including the "stackexchange.com" (if present) and/or the ".com" suffix
    *args: Any,
    **kwargs: Any,
) -> dict:
    """For getting very precise information on StackOverflow. The async (awaitable) version.

    This is 'supposed' to be faster than the normal 'Search' function for it abuses
    Asyncio. The thing is, this function will probably be deprecated unless there is a
    tested significant difference in performance. Use the 'search' function for it is
    more supported (all of the new features will be implemented in the Search function
    first).

    Returns
    -------
    dict
        A dict containing the raw data of the questions/answers gotten.

    """
    TEXT_REQUIREMENTS = {"class": "post-text", "itemprop": "text"}

    async def _full_questions(pages):
        if print_prog:
            print("Identifying question text...")
        return [page.find(attrs=TEXT_REQUIREMENTS).get_text() for page in pages]

    async def _answers(pages):
        if print_prog:
            print("Identifying answers...")
        return [
            [
                answer.find(attrs=TEXT_REQUIREMENTS).get_text()
                for answer in page.find_all(
                    attrs={"itemtype": "http://schema.org/Answer"}
                )
            ]
            for page in pages
        ]

    async def parsePages(_links_for_pages):
        return [  # Pages of all the questions related to Query
            bs(link.content, "lxml") for link in _links_for_pages
        ]

    if print_prog:
        print("Requesting results from StackOverflow...")
    r = requests.get(
        f"https://{search_on_site}/search?q={Query}"
    )  # NOTE: For python3.9, use the str.remove_suffix()
    if print_prog:
        print("Parsing response HTML...")
    soup = bs(r.content, "lxml")
    if print_prog:
        print("Collecting question links...")
    questions = {  # The raw ingredients
        question.string: question.get("href")
        for question in soup.find_all(
            attrs={"class": "question-hyperlink", "data-gps-track": None}
        )
    }
    if print_prog:
        print("Requesting questions found (This may take a while)...")
    _links_for_pages = grequests.map(
        (
            grequests.get(link)
            for link in map(
                lambda x: f"https://{search_on_site}" + x,
                iter(
                    questions.values()
                ),  # NOTE: For python3.9, use str.remove_suffix()
            )
        )
    )
    if print_prog:
        print("Parsing questions found (This may take a while)...")
    pages = await parsePages(_links_for_pages)
    full_questions = await _full_questions(pages)
    answers = await _answers(pages)

    return dict(zip(full_questions, answers))


def Search(
    Query: str,
    print_prog: bool = True,
    search_on_site: str = "stackoverflow.com",
    *args: Any,
    **kwargs: Any,
) -> dict:
    """For getting very precise information on StackOverflow. This is the function you should use.

    Returns
    -------
    dict
        A dict containing the raw data of the questions/answers gotten.

    """
    TEXT_REQUIREMENTS = {"class": "post-text", "itemprop": "text"}
    if print_prog:
        print("Requesting results from StackOverflow...")
    r = requests.get(
        f"https://{search_on_site}/search?q={Query}"
    )  # NOTE: For python3.9, use the str.remove_suffix()
    if print_prog:
        print("Parsing response HTML...")
    soup = bs(r.content, "lxml")
    if print_prog:
        print("Collecting question links...")
    questions = {  # The raw ingredients
        question.string: question.get("href")
        for question in soup.find_all(
            attrs={"class": "question-hyperlink", "data-gps-track": None}
        )
    }
    if print_prog:
        print("Requesting questions found (This may take a while)...")
    _links_for_pages = grequests.map(
        (
            grequests.get(link)
            for link in map(
                lambda x: f"https://{search_on_site}" + x,
                iter(
                    questions.values()
                ),  # NOTE: For python3.9, use str.remove_suffix()
            )
        )
    )
    if print_prog:
        print("Parsing questions found (This may take a while)...")
    pages = [  # Pages of all the questions related to Query
        bs(link.content, "lxml") for link in _links_for_pages
    ]
    if print_prog:
        print("Identifying question text...")
    full_questions = [page.find(attrs=TEXT_REQUIREMENTS).get_text() for page in pages]
    if print_prog:
        print("Identifying answers...")
    answers = [
        [
            answer.find(attrs=TEXT_REQUIREMENTS).get_text()
            for answer in page.find_all(attrs={"itemtype": "http://schema.org/Answer"})
        ]
        for page in pages
    ]
    return dict(zip(full_questions, answers))