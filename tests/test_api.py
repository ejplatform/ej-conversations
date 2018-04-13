class TestRoutes:
    def test_categories_endpoint(self, category_db, api):
        assert api.get('/categories/category/') == {
            'links': {'self': 'http://testserver/categories/category/'},
            'name': 'Category',
            'slug': 'category',
            'image': None,
            'image_caption': '',
        }
        assert api.get('/categories/bad-category/', raw=True).status_code == 404
