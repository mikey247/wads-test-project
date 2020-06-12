from django_auth_ldap.backend import populate_user
from django.conf import settings
from django.dispatch import receiver

@receiver(populate_user)
def user_callback(sender, **kwargs):
    '''
    Summary:
    Defines a user_callback method which is triggered by Django "populate_user"
    events to check group membership
    
    Background:
    The UoM/ITS implementation of LDAP groups is unusual and doesn't seem to follow
    any of the standard approaches as defined in the django_auth_ldap documentation.
    It was therefore a challenge to test if otherwise authenticated users are
    members of one (or more) groups.

    Solution:
    Setup django_auth_ldap settings as required for user authentication (correct
    password etc) and then call an additional user callback for the "populate_user"
    signal. The values of settings.XAUTH_LDAP_REQUIRE_IS_STAFF_GROUP and
    settings.XAUTH_LDAP_REQUIRE_IS_SUPERUSER_GROUP entries can then be tested
    against entries in the kwargs['ldap_user'].attrs['groupMembership'] object. The
    latter is returned by the UoM/ITS LDAP Active Directory service.

    Notes:
    Both settings.XAUTH_LDAP_REQUIRE_IS_STAFF_GROUP and settings.XAUTH_LDAP_REQUIRE_IS_SUPERUSER_GROUP
    settings are additional settings provided for this solution (hence the prefix of X) and are not
    standard settings for django_auth_ldap.

    '''
    # Debug prints that appear in ./manage.py runserver logs
    print("User Callback!")
    print(kwargs['user'])
    print(settings.XAUTH_LDAP_REQUIRE_IS_STAFF_GROUP)
    print(settings.XAUTH_LDAP_REQUIRE_IS_SUPERUSER_GROUP)

    # Additional debug statements that help track various states and settings
    
    #print(kwargs['user'].is_active)
    #print(kwargs['user'].is_staff)
    #print(kwargs['user'].is_superuser)
    #print(kwargs['ldap_user'].__dir__())
    #print(kwargs['ldap_user'].dn)
    #print(kwargs['ldap_user'].attrs['groupMembership'])

    # Original hardcoded test of membership; now replaced with test against settings.py values
    
    #kwargs['user'].is_staff = 'cn=admin-mc-ResearchIT-all,ou=mc,ou=admin,ou=uman,o=ac,c=uk' in kwargs['ldap_user'].attrs['groupMembership']
    #kwargs['user'].is_superuser = 'cn=admin-mc-ResearchIT-all,ou=mc,ou=admin,ou=uman,o=ac,c=uk' in kwargs['ldap_user'].attrs['groupMembership']

    # Set membership boolean against existence of specified group names in returned user data
    # is_active should be set by standard user authentication
    # is_staff checks against defined STAFF_GROUP and allows admin access (but not superuser)
    # is_superuser checks against SUPERUSER_GROUP and allows full control
    # TODO: Confirm is_staff/is_superuser do impart these permissions
    # Note: It is possible to define other wagtail/django permissions but these would normally be
    # assigned by site admins in the web admin UI
    
    kwargs['user'].is_staff = settings.XAUTH_LDAP_REQUIRE_IS_STAFF_GROUP in kwargs['ldap_user'].attrs['groupMembership']
    kwargs['user'].is_superuser = settings.XAUTH_LDAP_REQUIRE_IS_SUPERUSER_GROUP  in kwargs['ldap_user'].attrs['groupMembership']

    # Final debug to show correct assignment
    
    print(kwargs['user'].is_active)
    print(kwargs['user'].is_staff)
    print(kwargs['user'].is_superuser)

    print("User Callback DONE!")
