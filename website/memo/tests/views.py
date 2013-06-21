from django.test import TestCase
from django.core.urlresolvers import reverse


class HomeViewTest(TestCase):
    def test_home_access(self):
        response = self.client.get(reverse('home'))

        # check we use the right template
        self.assertTemplateUsed(response, 'home.html')

        # check status code
        self.assertEqual(response.status_code, 200)