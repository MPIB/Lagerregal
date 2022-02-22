import pytest

from devices import views


class Test_Search_Parse_boolean:
    
    @pytest.fixture()
    def search(self):
        return views.Search()
    

    def test_parse_boolean_1(self, search):
        search.parse_boolean(false)


class Test_Search_Parse_boolean:
    
    @pytest.fixture()
    def search(self):
        return views.Search()
    

    def test_parse_boolean_1(self, search):
        search.parse_boolean(false)

    def test_parse_boolean_2(self, search):
        search.parse_boolean("no")

    def test_parse_boolean_3(self, search):
        search.parse_boolean("")

