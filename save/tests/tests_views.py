#! /usr/bin/env python3
# coding: utf-8

"""
Author: [Nastyflav](https://github.com/Nastyflav) 2020-05-14
Licence: `GNU GPL v3` GNU GPL v3: http://www.gnu.org/licenses/

"""

from django.test import TestCase, Client
from django.urls import reverse

from search.models import Category, Product
from authentication.models import User
from save.models import Favorites


def db_init():
    """Create a temp user and temp products to perform tests"""
    user = User.objects.create(email='remy@purbeurre.fr')
    user.set_password('pixar2020')
    user.save()

    data = Category(name="Pate à tartiner")
    data.save()

    data = Product(
        name="Beurre de cacahuètes",
        category_id=Category.objects.get(name="Pate à tartiner"),
        store="Carrefour",
        nutriscore="c",
        barcode="012456870000",
        url="https://peanutbutter.fr",
        image="https://peanutbutter.fr/photo.jpg",
        lipids_for_100g="2.60",
        saturated_fats_for_100g="0.59",
        sugars_for_100g="0.11",
        salt_for_100g="3.51",
    )
    data.save()

    data = Product(
        name="Ovomaltine",
        category_id=Category.objects.get(name="Pate à tartiner"),
        store="Leclerc, BioCoop",
        nutriscore="a",
        barcode="0189654870000",
        url="https://ovomaltine.fr",
        image="https://ovomaltine.fr/photo.jpg",
        lipids_for_100g="4.59",
        saturated_fats_for_100g="0.02",
        sugars_for_100g="1.54",
        salt_for_100g="3.25",
    )
    data.save()

    data = Product(
        name="Nutella",
        category_id=Category.objects.get(name="Pate à tartiner"),
        store="Auchan",
        nutriscore="c",
        barcode="012232370000",
        url="https://nutella.fr",
        image="https://nutella.fr/photo.jpg",
        lipids_for_100g="1.64",
        saturated_fats_for_100g="0.33",
        sugars_for_100g="2.20",
        salt_for_100g="1.06",
    )
    data.save()


class TestViews(TestCase):
    """To test save views file"""
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.save_url = reverse('save:save')
        cls.favorites_url = reverse('save:favorites')
        db_init()

    def test_substitution_page_returns_200(self):
        """To test the status code and the login page"""
        response = self.client.get('/save/substitution/1')
        self.assertTemplateUsed(response, 'save/substitution.html')
        self.assertEqual(response.status_code, 200)

    def test_substitution_only_get_products_with_better_nutriscore(self):
        """To check if we get products better than the selected one"""
        response = self.client.get('/save/substitution/1')
        # careful here, we also take the products with the same nutriscore
        self.assertEqual(response.context_data["object_list"].count(), 2)
        self.assertEqual(response.status_code, 200)

    def test_substitution_no_better_nutriscore(self):
        """To check if we get zero product when there is no better one"""
        response = self.client.get('/save/substitution/2')
        self.assertEqual(response.context_data["object_list"].count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_substitution_context_data(self):
        """To check if the context method gets the right elements"""
        response = self.client.get('/save/substitution/1')
        self.assertEqual(response.status_code, 200)
        product = Product.objects.get(id=1)
        self.assertEqual(response.context_data["name"], product.name)
        self.assertEqual(response.context_data["id"], product.id)
        self.assertEqual(response.context_data["image"], product.image)

    def test_redirection_when_saving_product(self):
        """To check if the favorites page prints a product when it's saved"""
        self.client.login(
            username='remy@purbeurre.fr',
            password='pixar2020')

        user_id = User.objects.get(email='remy@purbeurre.fr').id
        response = self.client.post(
            self.save_url, {
                'original_product_id': Product.objects.get(id=1).id,
                'substitute_id': Product.objects.get(id=2).id,
                'user_id': user_id,
                'next': '/',
            }
        )
        response = self.client.get(self.favorites_url)
        self.assertEqual(response.context_data["object_list"].count(), 1)
        self.assertEqual(response.status_code, 200)

    def test_redirection_if_user_not_logged_in(self):
        """To check redirection when an unlogged user tries to save a prod"""
        user_id = User.objects.get(email='remy@purbeurre.fr').id
        response = self.client.post(
            self.save_url, {
                'original_product_id': Product.objects.get(id=1).id,
                'substitute_id': Product.objects.get(id=2).id,
                'user_id': user_id,
                'next': '/',
            }
        )
        self.assertRedirects(
            response, '/authentication?next=/save/save/',
            status_code=302, target_status_code=301)

    def test_user_without_any_savings_yet(self):
        """To check a fresh account with no saved products"""
        self.client.login(
            username='remy@purbeurre.fr',
            password='pixar2020')
        self.assertEqual(Favorites.objects.all().count(), 0)

    def test_method_and_redirection_saving_product(self):
        """To check if the POST method when a product is saved"""
        self.client.login(
            username='remy@purbeurre.fr',
            password='pixar2020')

        user_id = User.objects.get(email='remy@purbeurre.fr').id
        response = self.client.post(
            self.save_url, {
                'original_product_id': Product.objects.get(id=1).id,
                'substitute_id': Product.objects.get(id=2).id,
                'user_id': user_id,
                'next': '/',
            }
        )
        self.assertEqual(Favorites.objects.all().count(), 1)
        self.assertRedirects(
            response, '/save/favorites/',
            status_code=302, target_status_code=200)

    def test_favorites_page_returns_200(self):
        """To test the status code and the login page"""
        response = self.client.get(self.favorites_url)
        self.assertTemplateUsed(response, 'save/favorites.html')
        self.assertEqual(response.status_code, 200)

    def test_favorites_page_without_any_saving_yet(self):
        """
        To check the favorites page doesn't contains products
        when no one is already saved

        """
        self.client.login(
            username='remy@purbeurre.fr',
            password='pixar2020')
        response = self.client.get(self.favorites_url)
        self.assertEqual(response.context_data["object_list"].count(), 0)

    def test_favorite_deletion_success(self):
        """
        To check the redirection when a product is removed
        from the favorites list, and the products count
        
        """
        self.client.login(
            username='remy@purbeurre.fr',
            password='pixar2020')

        user_id = User.objects.get(email='remy@purbeurre.fr').id
        response = self.client.post(
            self.save_url, {
                'original_product_id': Product.objects.get(id=1).id,
                'substitute_id': Product.objects.get(id=2).id,
                'user_id': user_id,
                'next': '/',
            }
        )
        response = self.client.post("/save/delete/1")
        self.assertEqual(response.status_code, 302)

        response = self.client.get(self.favorites_url)
        self.assertEqual(response.context_data["object_list"].count(), 0)

    def test_favorite_deletion_when_unknown_product(self):
        """
        To check the favorites page when the delete product
        is unknown for the database
        
        """
        self.client.login(
            username='remy@purbeurre.fr',
            password='pixar2020')
        response = self.client.post("/save/delete/15")
        self.assertEqual(response.status_code, 404)
