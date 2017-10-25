
from swap.db.db import Schema
from swap.db.classifications import Schema as ClSchema

from unittest.mock import MagicMock, patch


class TestSchema:

    def test_validate(self):
        assert Schema.validate_field('user_id', '100', int) is False
        assert Schema.validate_field('user_id', '100', str) is True
        assert Schema.validate_field('user_id', 100, int) is True

    def test_validate_nontype(self):
        assert Schema.validate_field('user_id', 100, 'timestamp') is True

    def test_validate_userid_None(self):
        assert ClSchema.validate_field('user_id', 100, int) is True
        assert ClSchema.validate_field('user_id', None, int) is True
        assert ClSchema.validate_field('user_id', '1234', int) is False
