#!/usr/bin/env python

import unittest
from datetime import datetime

from persistence.in_memory.models.attachment import Attachment, AttachmentBase
from persistence.in_memory.models.task import Task


class AttachmentCleanTimestampTest(unittest.TestCase):
    def test_none_yields_none(self):
        # expect
        self.assertIsNone(AttachmentBase._clean_timestamp(None))

    def test_string_gets_parsed(self):
        # when
        result = AttachmentBase._clean_timestamp('2017-01-01')
        # then
        self.assertEqual(datetime(2017, 1, 1), result)

    def test_unicode_gets_parsed(self):
        # when
        result = AttachmentBase._clean_timestamp('2017-01-01')
        # then
        self.assertEqual(datetime(2017, 1, 1), result)

    def test_datetime_gets_set(self):
        # when
        result = AttachmentBase._clean_timestamp(datetime(2017, 1, 1))
        # then
        self.assertEqual(datetime(2017, 1, 1), result)


class AttachmentClearRelationshipsTest(unittest.TestCase):
    def test_clearing_nullifies_task(self):
        # given
        task = Task('task')
        attachment = Attachment('attachment')
        attachment.task = task
        # precondition
        self.assertIs(task, attachment.task)
        # when
        attachment.clear_relationships()
        # then
        self.assertIsNone(attachment.task)
