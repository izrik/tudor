
from persistence.in_memory.models.tag import Tag
from tests.persistence_t.in_memory_persistence_layer.in_memory_test_base \
    import InMemoryTestBase


# copied from ../test_get_tag.py, with removals


class GetTagTest(InMemoryTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()

    def test_get_tag_none_raises(self):
        # expect
        self.assertRaises(ValueError, self.pl.get_tag, None)

    def test_get_tag_non_existent_yields_none(self):
        # expect
        self.assertIsNone(self.pl.get_tag(1))

    def test_get_tag_existing_yields_that_tag(self):
        # given
        tag = Tag('tag')
        self.pl.add(tag)
        self.pl.commit()
        # precondition
        self.assertIsNotNone(tag.id)
        # when
        result = self.pl.get_tag(tag.id)
        # then
        self.assertIsNotNone(result)
        self.assertIs(tag, result)
