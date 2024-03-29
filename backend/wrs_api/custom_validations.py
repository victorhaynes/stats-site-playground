from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_region(value):
    if (value == "na1" or value == "br1" or value == "la1" or value == "la2") and self.context["region"] != "americas":
        raise ValidationError(_("%(value)s is not an even number"), params={"value": value},)    if (value == "na1" or value == "br1" or value == "la1" or value == "la2") and value != "americas":
    if (value == "jp1" or value == "kr1") and value != "americas":
