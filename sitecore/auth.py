'''
auth.py
-------

Summary:

Defines a custom LDAPGroupType "GroupMembershipDNGroupType" to handle
group membership authentication queries for approval/rejection.

Background:

The UoM/ITS implementation of LDAP groups is doesn't seem to match
any of the standard LDAPGroup approaches defined in the
django_auth_ldap documentation. It was therefore a challenge to test
if otherwise authenticated users are members of one (or more) groups
and set the necessary Django user flags.

User group membership is held within the individual user records,
rather than through the use of separate LDAP groups. Each user record
contains a list of groupMembership entries that the user belongs to.

Solution:

Setup django_auth_ldap settings as required for user authentication
(correct password etc.) and then use the same query as used for the
user authentication query to retrieve the same information - which
holds the groupMembership data.

The custom GroupMembershipDNGroupType GroupType class implements new
functionality to test if the returned user data has a groupMembership
attribute, which in turn has a list of entries for groupMembership
as returned by the LDAP server). It then checks if the group DN
being queried matches at least one of the entries.

Usage:

The default user authentication is specifed by the
AUTH_LDAP_REQUIRE_GROUP setting.

If that passes, authentication continues with additional tests for
entries in AUTH_LDAP_USER_FLAGS_BY_GROUP which will set flags based
on possibly multiple group memberships e.g., those for superuser
access.

Import:

For settings file e.g., settings/production.py use the following import:

from RSEAdmin.auth import GroupMembershipDNGroupType

'''

import ldap

from django_auth_ldap.config import LDAPSearch, LDAPGroupType
from django.conf import settings


class GroupMembershipDNGroupType(LDAPGroupType):
    """
    A group type that stores a list of groupMembership as distinguished names
    in an attribute of the user record returned by the LDAP server.
    """

    def __init__(self, member_attr="groupMembership", name_attr="cn"):
        """
        member_attr is the attribute on the user object that holds the list of
        member DNs.
        """
        self.member_attr = member_attr

        super().__init__(name_attr)

    def __repr__(self):
        return "<{}: {}>".format(type(self).__name__, self.member_attr)

    #def user_groups(self, ldap_user, group_search):
        #return None
        
        #print(f'user_groups(): CALLED WITH {ldap_user} {group_search}')
        #search = group_search.search_with_additional_terms(
        #    {self.member_attr: ldap_user.dn}
        #)
        #return [["Moderators", {"cn": ('Moderators',grp.lower())}] for grp in ldap_user.attrs[self.member_attr]]
        #return [grp.lower() for grp in ldap_user.attrs[self.member_attr]]
        #return search.execute(ldap_user.connection)

    #def group_name_from_info(self, group_info):
        #"""
        #Given the (DN, attrs) 2-tuple of an LDAP group, this returns the name of
        #the Django group. This may return None to indicate that a particular
        #LDAP group has no corresponding Django group.

        #The base implementation returns the value of the cn attribute, or
        #whichever attribute was given to __init__ in the name_attr
        #parameter.
        #"""

        #return None
        
        #try:
            #print()
            #print(f'GroupMembershipDNGroupType::group_name_from_info(): {self.name_attr}')
            #print(f'GroupMembershipDNGroupTypegroup_name_from_info(): {group_info}')
            #print(f'GroupMembershipDNGroupTypegroup_name_from_info(): {group_info[1]}')
            #print(f'GroupMembershipDNGroupTypegroup_name_from_info(): {group_info[1][self.name_attr]}')
            #print(f'GroupMembershipDNGroupTypegroup_name_from_info(): {group_info[1][self.name_attr][0]}')
            #name = group_info[1][self.name_attr][0]
        #except (KeyError, IndexError):
            #name = None

        #return 'Moderators'
        #return 'Editors'
            
        #return name

    def is_member(self, ldap_user, group_dn):
        """
        Test of groupMembership.
        Use lowercase for all tests e.g., passed group_dn *and* each entry in the list.
        Return True if at least one entry in the member_attr list matches the passed group_dn.
        """

        group_dn = group_dn.lower()

        try:
            result = group_dn in [grp.lower() for grp in ldap_user.attrs[self.member_attr]]
        except (ldap.UNDEFINED_TYPE, ldap.NO_SUCH_ATTRIBUTE):
            result = 0

        return result
