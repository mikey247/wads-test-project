from django_auth_ldap.backend import populate_user
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.dispatch import receiver

@receiver(populate_user)
def map_groupmembership_to_wagtail_groups(sender, **kwargs):
    '''
    Summary:
    Defines a user_callback method which is triggered by django_auth_ldap "populate_user"
    events to check and map LDAP groupMembership to Django/Wagtail groups using auxillary
    settings.
   
    Background:
    The UoM/ITS implementation of LDAP groups is not compatible with the group types
    that django_auth_ldap supports by default. The siteconfig/auth.py file implements
    a new LDAPGroupType that accomplishes the needs to determine groupMembership for
    basic authentication. However, there is no immediate way to map those memberships
    to named Django/Wagtail groups.

    Solution:
    Setup django_auth_ldap settings as required for user authentication and basic
    groupMembership checks. This callback then uses additional settings to help map
    LDAP groupMembership to Django groups.

    Settings:
    XAUTH_LDAP_GROUPS_FROM_MEMBERSHIP provides a mechanism to ASSIGN group membership
    based on the user being AUTHENTICATED AS A MEMBER of one or more LDAP groups.

    It should be defined as a dictionary, with Django group names as keys, each with values
    as arrays of LDAP DNs (as used in AUTH_* settings.

    (Example)
    XAUTH_LDAP_GROUPS_FROM_MEMBERSHIP = {
        'Moderators': [
            'cn=admin-mc-ResearchIT-webadmin,ou=mc,ou=admin,ou=uman,o=ac,c=uk',
        ],
    }

    XAUTH_LDAP_GROUPS_FROM_NON_MEMBERSHIP provides a mechanism to ASSIGN group membership
    based on the user being FAILING AUTHENTICATION AS A MEMBER of one or more LDAP groups.

    (Example)
    XAUTH_LDAP_GROUPS_FROM_NON_MEMBERSHIP = {
        'Editors': [
            'cn=admin-mc-ResearchIT-webadmin,ou=mc,ou=admin,ou=uman,o=ac,c=uk',
        ]
    }
    '''

    # Debug prints that appear in ./manage.py runserver logs
    print("siteconfig/signals.py: @receiver(populate_user) / map_groupmembership_to_wagtail_groups()")
    print(f'kwargs["user"]: {kwargs["user"]}')

    # Save user model so we have a user ID; this is required for group assignment (a many-to-may relationship)
    kwargs['user'].save()

    # Empty sets to hold groups to add/revoke from user.groups
    assign_groups = set()
    revoke_groups = set()

    # settings.XAUTH_LDAP_GROUPS_FROM_MEMBERSHIP is a dict containing keys that should match existing Django/Wagtail groups
    # Each value is an array of acceptable LDAP dn entries.
    # For matching LDAP groups in user's groupMembership, assign the mapped Django/Wagtail group to the user
    # If it doesn't match revoke that group from the user
    if settings.XAUTH_LDAP_GROUPS_FROM_MEMBERSHIP:
        try:
            for group_name in settings.XAUTH_LDAP_GROUPS_FROM_MEMBERSHIP.keys():
                for valid_dn in settings.XAUTH_LDAP_GROUPS_FROM_MEMBERSHIP[group_name]:
                    is_member = valid_dn in kwargs['ldap_user'].attrs['groupMembership']
                    if is_member:
                        print(f'{kwargs["user"]} has groupMembership {valid_dn} so is added to group: {group_name}')
                        assign_groups.add(group_name)
                    else:
                        print(f'{kwargs["user"]} does not have groupMembership {valid_dn} so is NOT added to group: {group_name}')
                        revoke_groups.add(group_name)
        except ValueError as e:
            raise ImproperlyConfigured(
                "XAUTH_LDAP_GROUPS_FROM_MEMBERSHIP is not properly configured"
            )

    # settings.XAUTH_LDAP_GROUPS_FROM_NON_MEMBERSHIP is a dict containing keys that should match existing Django/Wagtail groups
    # Each value is an array of unacceptable LDAP dn entries.
    # For given LDAP groups not found within user's groupMembership, assign the given Django/Wagtail group
    # If it doesn't match build set of Django/Wagtail groups to revoke
    if settings.XAUTH_LDAP_GROUPS_FROM_NON_MEMBERSHIP:
        try:
            for group_name in settings.XAUTH_LDAP_GROUPS_FROM_NON_MEMBERSHIP.keys():
                for invalid_dn in settings.XAUTH_LDAP_GROUPS_FROM_NON_MEMBERSHIP[group_name]:
                    is_member = invalid_dn not in kwargs['ldap_user'].attrs['groupMembership']
                    if is_member:
                        print(f'{kwargs["user"]} does not have groupMembership {invalid_dn} so is added to group: {group_name}')
                        assign_groups.add(group_name)
                    else:
                        print(f'{kwargs["user"]} has groupMembership {invalid_dn} so is NOT added to group: {group_name}')
                        revoke_groups.add(group_name)
        except ValueError as e:
            raise ImproperlyConfigured(
                "XAUTH_LDAP_GROUPS_FROM_NON_MEMBERSHIP is not properly configured"
            )

    # Process sets of assign_groups and revoke_groups; order is allow/deny, ensuring deny takes precendence
    for group_name in assign_groups:
        group = Group.objects.get(name=group_name)
        kwargs['user'].groups.add(group)

    for group_name in revoke_groups:
        group = Group.objects.get(name=group_name)
        kwargs['user'].groups.remove(group)

    print("siteconfig/signals.py: @receiver(populate_user) / map_groupmembership_to_wagtail_groups() DONE")
