from models.changeable import Changeable
from persistence.in_memory.models.option import Option
from persistence.in_memory.models.task import Task
from tests.persistence_t.sqlalchemy.util import PersistenceLayerTestBase


class DbOptionMakeChangeTest(PersistenceLayerTestBase):
    def setUp(self):
        self.pl = self.generate_pl()
        self.pl.create_all()
        self.option = self.pl.DbOption('a', 'b')

    def test_setting_key_sets_key(self):
        # precondition
        self.assertEqual('a', self.option.key)
        # when
        self.option.make_change(Option.FIELD_KEY, Changeable.OP_SET, 1)
        # then
        self.assertEqual(1, self.option.key)

    def test_adding_key_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.option.make_change,
            Option.FIELD_KEY, Changeable.OP_ADD, 1)

    def test_removing_key_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.option.make_change,
            Option.FIELD_KEY, Changeable.OP_REMOVE, 1)

    def test_changing_key_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.option.make_change,
            Option.FIELD_KEY, Changeable.OP_CHANGING, 1)

    def test_setting_value_sets_value(self):
        # precondition
        self.assertEqual('b', self.option.value)
        # when
        self.option.make_change(Option.FIELD_VALUE, Changeable.OP_SET,
                                'something')
        # then
        self.assertEqual('something', self.option.value)

    def test_adding_value_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.option.make_change,
            Option.FIELD_VALUE, Changeable.OP_ADD, 'something')

    def test_removing_value_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.option.make_change,
            Option.FIELD_VALUE, Changeable.OP_REMOVE, 'something')

    def test_changing_value_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.option.make_change,
            Option.FIELD_VALUE, Changeable.OP_CHANGING, 'something')

    def test_non_option_field_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.option.make_change,
            Task.FIELD_SUMMARY, Changeable.OP_SET, 'value')

    def test_invalid_field_raises(self):
        # expect
        self.assertRaises(
            ValueError,
            self.option.make_change,
            'SOME_OTHER_FIELD', Changeable.OP_SET, 'value')
