from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import Account, UserProfile

# Register your models here.

class AccountAdmin(UserAdmin):
    """Custom admin interface for the Account model."""
    
    list_display = (
        'email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active'
        )
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined', )


    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class UserProfileAdmin(admin.ModelAdmin):
    """Custom admin interface for the UserProfile model."""
    def thumbnail(self, object):
        """Generates a thumbnail of the user's profile picture."""
        #BELOW: The 'format_html' function is a utility provided by Django that helps generate HTML code safely.
        #The image source (src) is set to the URL of the 'profile_picture' attribute of the object being passed as an argument.
        #The {} is a placeholder for the value of 'object.profile_picture.url'. The format method is called on the string to replace the placeholder with the actual URL value.
        return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(object.profile_picture.url)) 
    thumbnail.short_description = 'Profile Picture' #The label for a method when it appears as a column header in the list view of the admin page.
    list_display = ('thumbnail', 'user', 'city', 'state', 'country')


admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)