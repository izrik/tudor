from models.tag import Tag
from tests.in_memory_persistence_layer.in_memory_test_base import \
    InMemoryTestBase


# copied from ../test_db_interaction.py, with modifications


class DatabaseInteractionTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_changes_after_get_are_also_tracked(self):
        # given
        tag1 = Tag('tag', description='a')
        self.pl.add(tag1)
        self.pl.commit()
        tag = self.pl.get_tag_by_value('tag')
        # precondition
        self.assertEqual('a', tag.description)
        # when
        tag.description = 'b'
        # then
        self.assertEqual('b', tag.description)
        # when
        self.pl.commit()
        # then
        self.assertEqual('b', tag.description)
        self.assertEqual('b', tag1.description)
        # when
        self.pl.rollback()
        # then
        self.assertEqual('b', tag.description)
        self.assertEqual('b', tag1.description)
