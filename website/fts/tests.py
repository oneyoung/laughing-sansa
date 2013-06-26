"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By

EMAIL_ADDR = "xxx@example.com"


def start_selenium_server():
    import os
    import time
    import subprocess
    import shlex
    from os import path
    jar_name = 'selenium-server.jar'
    if os.system('pgrep -f %s' % jar_name):
        # server not running
        jar_path = path.join(path.abspath(path.dirname(__name__)),
                             'fts', 'bin', jar_name)
        cmd = 'java -jar %s &' % jar_path
        p = subprocess.Popen(shlex.split(cmd), close_fds=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5)
        return p.pid

start_selenium_server()


class AccountTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Remote("http://localhost:4444/wd/hub",
                                        webdriver.DesiredCapabilities.FIREFOX)
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def _test_can_browse_homepage_and_register(self):
        # someone opens his browser, and goes to the admin page
        self.browser.get(self.fullurl('/'))

        # he finds a banner to input email address, and a button to go
        email_input = self.browser.find_element(By.NAME, 'email')
        email_input.send_keys(EMAIL_ADDR)
        email_input.submit()

        # TODO: use the admin site to create a Poll
        self.fail('finish this test')

    def fullurl(self, path):
        return '%s%s' % (self.live_server_url, path)

    def fill_register_form(self, username, password, password_confirm=None):
        # open login page
        self.browser.get(self.fullurl(reverse('memo.views.register')))
        # fill in the email filed
        tag = self.browser.find_element_by_name('username')
        tag.send_keys(username)
        # input the passowrd
        tag = self.browser.find_element_by_name('password')
        tag.send_keys(password)
        # comfirm the passowrd
        tag = self.browser.find_element_by_name('password_confirm')
        tag.send_keys(password_confirm if password_confirm else password)
        # submit
        tag = self.browser.find_element_by_name('submit')
        tag.click()

    def fill_login_form(self, username, password, next='', openpage=True):
        if openpage:
            url_base = reverse('memo.views.login')
            url_para = '?next=%s' % next if next else ''
            self.browser.get(self.fullurl(url_base + url_para))
        # fill the username and password field
        tag = self.browser.find_element_by_name('username')
        tag.send_keys(username)
        tag = self.browser.find_element_by_name('password')
        tag.send_keys(password)
        # submit
        tag = self.browser.find_element_by_name('submit')
        tag.click()

    def test_user_register(self):
        def body_contain(string):
            body = self.browser.find_element_by_tag_name('body')
            self.assertIn(string, body.text)

        username = 'xxxx@gmail.com'
        password = 'xxxxxxxx'

        # new user register
        self.fill_register_form(username, password)
        # should say that you are successful.
        body_contain('account has been created')

        # repeat register should failed if the same username
        self.fill_register_form(username, password)
        # should say account has exists
        body_contain('taken')

        # after registion, we can login now
        self.fill_login_form(username, password)
        # TODO: successful login should redirect to other page

        # wrong login should say 'didn't match'
        self.fill_login_form(username, 'wrong passowrd')
        body_contain('didn\'t match')

    def test_login_redirect(self):
        # create a user
        username = 'loginredirect@gmail.com'
        password = 'xxxxxxxx'
        # new user register
        self.fill_register_form(username, password)

        # test begin
        target_url = self.fullurl(reverse('memo.views.post_io'))
        self.browser.get(target_url)
        # we should redirect to login page, and fill login page
        self.fill_login_form(username, password, openpage=False)
        # then we should redirect to the same target_url
        self.assertEquals(self.browser.current_url, target_url)
