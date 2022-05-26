# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase

# from equipment.forms import EquipmentForm
from equipment.models import Equipment, EquipmentUser


class EquipmentViewsIntegrationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """We need following Measurement roles:
        - User 1 READ_ONLY on Equipment 1
        - User 2 USER on Equipment 2
        - User 3 ADMIN on Equipment 3
        """
        cls.user1 = User.objects.create_user(
            username="testuser1@foo.bar", password="top_secret1"
        )
        cls.user2 = User.objects.create_user(
            username="testuser2@foo.bar", password="top_secret2"
        )
        cls.user3 = User.objects.create_user(
            username="testuser3@foo.bar", password="top_secret3"
        )
        cls.equipment1 = Equipment.objects.create(
            name="TestRO", register_number="TEST-RO"
        )
        cls.equipment2 = Equipment.objects.create(
            name="TestUSER", register_number="TEST-USER"
        )
        cls.equipment3 = Equipment.objects.create(
            name="TestADMIN", register_number="TEST-ADMIN"
        )
        cls.equipmentuser1 = EquipmentUser.objects.create(
            user=cls.user1, equipment=cls.equipment1, role="READ_ONLY"
        )
        cls.equipmentuser2 = EquipmentUser.objects.create(
            user=cls.user2, equipment=cls.equipment2, role="USER"
        )
        cls.equipmentuser3 = EquipmentUser.objects.create(
            user=cls.user3, equipment=cls.equipment3, role="ADMIN"
        )

        # Create groups and permissions
        ct = ContentType.objects.get_for_model(Equipment)
        cls.permissions = dict()
        cls.permissions["add"], _ = Permission.objects.get_or_create(
            codename="add_equipment", content_type=ct
        )
        cls.permissions["edit"], _ = Permission.objects.get_or_create(
            codename="edit_equipment", content_type=ct
        )
        cls.permissions["view"], _ = Permission.objects.get_or_create(
            codename="view_equipment", content_type=ct
        )
        cls.permissions["delete"], _ = Permission.objects.get_or_create(
            codename="delete_equipment", content_type=ct
        )

    def setUp(self):
        self.client = Client()

    def test_respond_with_200_for_url_equipment(self):
        """Response 200 should be given on url /equipment/"""
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.get("/equipment/")

        self.assertEqual(response.status_code, 200)

    def test_redirects_to_login_for_non_logged_in_user_on_equipment(self):
        """Non-logged-in users should get redirected to login on equipment view"""
        response = self.client.get("/equipment/")

        self.assertRedirects(response, "/accounts/login/?next=/equipment/")

    def test_respond_with_200_for_url_equipment_correct_pk(self):
        """Response 200 should be given on url /equipment/1"""
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.get(f"/equipment/{self.equipment1.id}/")

        self.assertEqual(response.status_code, 200)

    def test_equipment_index_has_add_button_for_user_with_permission(self):
        """Equipment index page should have add button for user with permission"""
        self.user1.user_permissions.add(self.permissions["add"])
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        # This is enough since we only want to test if a link exists,
        # not that it's actually valid HTML or anything.
        expected_html = """
            <a href="/equipment/add/" role="button">
                Add new equipment
            </a>
        """

        response = self.client.get("/equipment/")

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_equipment_index_no_add_button_for_user_with_no_permission(self):
        """Equipment index page should not have add button for user with no permission"""
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.get("/equipment/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Add new equipment")

    def test_respond_with_200_for_get_equipment_add(self):
        """Response 200 should be given on get /equipment/add/"""
        self.user1.user_permissions.add(self.permissions["add"])
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.get("/equipment/add/")

        self.assertEqual(response.status_code, 200)

    def test_redirects_to_login_for_non_logged_in_user_on_equipment_add(self):
        """Non-logged-in users should get redirected to login on equipment/add view"""
        response = self.client.get("/equipment/add/")

        self.assertRedirects(response, "/accounts/login/?next=/equipment/add/")

    def test_redirect_to_equipment_detail_view_after_successful_addition(self):
        """User should be redirected to Equipment detail view after successful equipment addition"""
        self.user1.user_permissions.add(self.permissions["add"])
        data = {
            "name": "New Test Equipment EQ1",
            "register_number": "TEST-EQ1",
        }
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.post("/equipment/add/", data=data, follow=True)

        self.assertContains(response, data["name"])

    def test_returned_to_equipmentform_on_invalid_data(self):
        """User should be returned to add_equipment view on posting invalid data"""
        self.user1.user_permissions.add(self.permissions["add"])
        data = {}
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.post("/equipment/add/", data=data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "equipment/add.html")

    def test_permissions_saved_on_form_save(self):
        """Permissions should be saved when a new Equipment is added"""
        self.user1.user_permissions.add(self.permissions["add"])
        data = {
            "name": "test-1",
            "register_number": "REG-T1",
        }
        data[f"perm-{self.user1.id}"] = "NOACCESS"
        data[f"perm-{self.user2.id}"] = "NOACCESS"
        data[f"perm-{self.user3.id}"] = "READ_ONLY"

        self.client.login(username="testuser1@foo.bar", password="top_secret1")
        response = self.client.post("/equipment/add/", data=data)

        saved_equipment = Equipment.objects.get(register_number="REG-T1")
        saved_perms = EquipmentUser.objects.filter(equipment=saved_equipment)

        # Login user should get ADMIN privs since no admin is assigned at post data.
        expected_perms = [
            str(
                EquipmentUser(
                    user=self.user3, equipment=saved_equipment, role="READ_ONLY"
                )
            ),
            str(
                EquipmentUser(user=self.user1, equipment=saved_equipment, role="ADMIN")
            ),
        ]

        self.assertQuerysetEqual(list(saved_perms), expected_perms, transform=str)

    def test_permissions_removed_only_for_current_equipment(self):
        """Permissions should be removed only from current equipment on save"""
        self.user1.user_permissions.add(self.permissions["edit"])
        data = {
            "name": "test-2",
            "register_number": "REG-T2",
        }
        data[f"perm-{self.user1.id}"] = "NOACCESS"
        data[f"perm-{self.user2.id}"] = "NOACCESS"
        data[f"perm-{self.user3.id}"] = "NOACCESS"

        saved_equipment = Equipment.objects.create(
            name=data["name"], register_number=data["register_number"]
        )

        self.client.login(username="testuser1@foo.bar", password="top_secret1")
        response = self.client.post(f"/equipment/{saved_equipment.id}/edit/", data=data)

        saved_perms = EquipmentUser.objects.filter(equipment=self.equipment1)
        expected_perms = [str(self.equipmentuser1)]

        self.assertQuerysetEqual(list(saved_perms), expected_perms, transform=str)

    def test_permissions_updated_on_form_save(self):
        """Permissions should be updated when a Equipment is modified"""
        self.user1.user_permissions.add(self.permissions["edit"])
        data = {
            "name": "test-2",
            "register_number": "REG-T2",
        }
        data[f"perm-{self.user1.id}"] = "USER"
        data[f"perm-{self.user2.id}"] = "NOACCESS"
        data[f"perm-{self.user3.id}"] = "ADMIN"

        saved_equipment = Equipment.objects.create(
            name=data["name"], register_number=data["register_number"]
        )
        self.create_dummy_equipment_users(saved_equipment)

        self.client.login(username="testuser1@foo.bar", password="top_secret1")
        response = self.client.post(f"/equipment/{saved_equipment.id}/edit/", data=data)

        # Update our equipment var with new data from form save
        saved_equipment = Equipment.objects.get(register_number="REG-T2")
        saved_perms = EquipmentUser.objects.filter(equipment=saved_equipment)
        expected_perms = [
            str(EquipmentUser(user=self.user1, equipment=saved_equipment, role="USER")),
            str(
                EquipmentUser(user=self.user3, equipment=saved_equipment, role="ADMIN")
            ),
        ]

        self.assertRedirects(response, f"/equipment/{saved_equipment.id}/")
        self.assertQuerysetEqual(
            list(saved_perms), expected_perms, ordered=False, transform=str
        )

    def test_old_permissions_deleted_on_form_save_and_admin_assigned(self):
        """Old permissions should be deleted when a Equipment is modified and ADMIN added"""
        self.user1.user_permissions.add(self.permissions["edit"])
        data = {
            "name": "test-2",
            "register_number": "REG-T2",
        }
        data[f"perm-{self.user1.id}"] = "NOACCESS"
        data[f"perm-{self.user2.id}"] = "NOACCESS"
        data[f"perm-{self.user3.id}"] = "NOACCESS"

        saved_equipment = Equipment.objects.create(
            name=data["name"], register_number=data["register_number"]
        )
        self.create_dummy_equipment_users(saved_equipment)

        self.client.login(username="testuser1@foo.bar", password="top_secret1")
        response = self.client.post(f"/equipment/{saved_equipment.id}/edit/", data=data)

        # Update our equipment var with new data from form save
        saved_equipment = Equipment.objects.get(register_number="REG-T2")
        saved_perms = EquipmentUser.objects.filter(equipment=saved_equipment)
        expected_perms = [
            str(EquipmentUser(user=self.user1, equipment=saved_equipment, role="ADMIN"))
        ]

        self.assertRedirects(response, f"/equipment/{saved_equipment.id}/")
        self.assertQuerysetEqual(
            list(saved_perms), expected_perms, ordered=False, transform=str
        )

    def test_current_user_does_not_get_admin_if_admin_already_present(self):
        """Current user should not get automatic admin privs if another user has admins"""
        self.user1.user_permissions.add(self.permissions["edit"])
        data = {
            "name": "test-2",
            "register_number": "REG-T2",
        }
        data[f"perm-{self.user1.id}"] = "NOACCESS"
        data[f"perm-{self.user2.id}"] = "ADMIN"
        data[f"perm-{self.user3.id}"] = "NOACCESS"

        saved_equipment = Equipment.objects.create(
            name=data["name"], register_number=data["register_number"]
        )
        self.create_dummy_equipment_users(saved_equipment)

        self.client.login(username="testuser1@foo.bar", password="top_secret1")
        response = self.client.post(f"/equipment/{saved_equipment.id}/edit/", data=data)

        # Update our equipment var with new data from form save
        saved_equipment = Equipment.objects.get(register_number="REG-T2")
        saved_perms = EquipmentUser.objects.filter(equipment=saved_equipment)
        expected_perms = [
            str(EquipmentUser(user=self.user2, equipment=saved_equipment, role="ADMIN"))
        ]

        self.assertRedirects(response, f"/equipment/{saved_equipment.id}/")
        self.assertQuerysetEqual(
            list(saved_perms), expected_perms, ordered=False, transform=str
        )

    def test_edit_permission_allows_edit(self):
        """Response 200 should be given on url /equipment/<pk>/edit/ for ADMIN"""
        self.user3.user_permissions.add(self.permissions["edit"])
        self.client.login(username="testuser3@foo.bar", password="top_secret3")

        response = self.client.get(f"/equipment/{self.equipment3.id}/edit/")

        self.assertEqual(response.status_code, 200)

    def test_edit_permission_required(self):
        """User with no perms should receive 403"""
        self.client.login(username="testuser2@foo.bar", password="top_secret2")

        response = self.client.get(f"/equipment/{self.equipment3.id}/edit/")

        self.assertEqual(response.status_code, 403)

    def test_permissions_get_prepopulated_on_edit(self):
        """Permission radio buttons should get prepopulated on edit"""
        self.user1.user_permissions.add(self.permissions["edit"])
        data = {
            "name": "test-2",
            "register_number": "REG-T2",
        }

        saved_equipment = Equipment.objects.create(
            name=data["name"], register_number=data["register_number"]
        )
        self.create_dummy_equipment_users(saved_equipment)

        self.client.login(username="testuser1@foo.bar", password="top_secret1")
        response = self.client.get(f"/equipment/{saved_equipment.id}/edit/")

        self.assertInHTML(
            f'<input type="radio" id="{self.user1.id}-READ_ONLY" name="perm-{self.user1.id}" value="READ_ONLY" checked>',
            response.content.decode(),
            1,
        )
        self.assertInHTML(
            f'<input type="radio" id="{self.user2.id}-ADMIN" name="perm-{self.user2.id}" value="ADMIN" checked>',
            response.content.decode(),
            1,
        )
        self.assertInHTML(
            f'<input type="radio" id="{self.user3.id}-READ_ONLY" name="perm-{self.user3.id}" value="READ_ONLY" checked>',
            response.content.decode(),
            1,
        )

    # @TODO: Test for add and edit buttons in index and detail views (permissions)
    # @TODO: Test role edit permissions on edit form
    # @TODO: Test role edit permissions on edit and add views

    def create_dummy_equipment_users(self, equipment):
        """Create dummy equipment users for equipment"""
        EquipmentUser.objects.create(
            user=self.user1, equipment=equipment, role="READ_ONLY"
        )
        EquipmentUser.objects.create(user=self.user2, equipment=equipment, role="ADMIN")
        EquipmentUser.objects.create(
            user=self.user3, equipment=equipment, role="READ_ONLY"
        )
