
import os
import django

from django.utils.text import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cspro.settings.settings")
django.setup()

import threading
import csv
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db import transaction
from api.zone.models import Countries
from django.utils.text import slugify


# def add_countries():
# 	print("-------------------")
# 	file_path = staticfiles_storage.path('hcp_connections.csv')
	# countriess = ['Germany', 'Austria', 'Belgium', 'Canada', 'China', 'Spain', 'Finland', 'France', 'Greece', 'Italy', 'Japan', 'Luxemburg', 'Netherlands', 'Poland', 'Portugal', 'Czech Republic', 'United Kingdom', 'Sweden', 'Switzerland', 'Denmark', 'United States', 'HongKong', 'Norway', 'Australia', 'Singapore', 'Ireland', 'New Zealand', 'South Korea', 'Israel', 'South Africa', 'Nigeria', 'Ivory Coast', 'Togo', 'Bolivia', 'Mauritius', 'Romania', 'Slovakia', 'Algeria', 'American Samoa', 'Andorra', 'Angola', 'Anguilla', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Aruba', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belize', 'Benin', 'Bermuda', 'Bhutan', 'Botswana', 'Brazil', 'Brunei', 'Burkina Faso', 'Burma (Myanmar)', 'Burundi', 'Cambodia', 'Cameroon', 'Cape Verde', 'Central African Republic', 'Chad', 'Chile', 'Colombia', 'Comoros', 'Congo, Dem. Republic', 'Congo, Republic', 'Costa Rica', 'Croatia', 'Cuba', 'Cyprus', 'Djibouti', 'Dominica', 'Dominican Republic', 'East Timor', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Ethiopia', 'Falkland Islands', 'Faroe Islands', 'Fiji', 'Gabon', 'Gambia', 'Georgia', 'Ghana', 'Grenada', 'Greenland', 'Gibraltar', 'Guadeloupe', 'Guam', 'Guatemala', 'Guernsey', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Heard Island and McDonald Islands', 'Vatican City State', 'Honduras', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Man Island', 'Jamaica', 'Jersey', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'Korea, Dem. Republic of', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Macau', 'Macedonia', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Martinique', 'Mauritania', 'Hungary', 'Mayotte', 'Mexico', 'Micronesia', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Montserrat', 'Morocco', 'Mozambique', 'Namibia', 'Nauru', 'Nepal', 'Netherlands Antilles', 'New Caledonia', 'Nicaragua', 'Niger', 'Niue', 'Norfolk Island', 'Northern Mariana Islands', 'Oman', 'Pakistan', 'Palau', 'Palestinian Territories', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Pitcairn', 'Puerto Rico', 'Qatar', 'Reunion Island', 'Russian Federation', 'Rwanda', 'Saint Barthelemy', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Martin', 'Saint Pierre and Miquelon', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 'São Tomé and Príncipe', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Georgia and the South Sandwich Islands', 'Sri Lanka', 'Sudan', 'Suriname', 'Svalbard and Jan Mayen', 'Swaziland', 'Syria', 'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Tokelau', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Turks and Caicos Islands', 'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Venezuela', 'Vietnam', 'Virgin Islands (British)', 'Virgin Islands (U.S.)', 'Wallis and Futuna', 'Western Sahara', 'Yemen', 'Zambia', 'Zimbabwe', 'Albania', 'Afghanistan', 'Antarctica', 'Bosnia and Herzegovina', 'Bouvet Island', 'British Indian Ocean Territory', 'Bulgaria', 'Cayman Islands', 'Christmas Island', 'Cocos (Keeling) Islands', 'Cook Islands', 'French Guiana', 'French Polynesia', 'French Southern Territories', 'Åland Islands']
	# for country in countriess:
	# 	cnt = {}
	# 	cnt['name'] = country
	# 	print(cnt)
	# 	x = Countries.objects.create(**cnt)
	# 	print(x)

# if __name__ == "__main__":

# add_countries()

def add_countries_thread():
    # data = Property.objects.all().update(canonical_link=None)
    t1 = threading.Thread(target=countries())
    t1.start()

def countries():
    try:
        print("==========New Cron=============")
        # italy = pytz.timezone("Europe/Rome")
        # a = datetime.now(italy)
        # print(f'Current Time of itally : {a}')
        file_path = staticfiles_storage.path('countries.csv')
        with open(file_path) as csv_file:
            counntries = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in counntries:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    if get_or_create_country(row):
                        print("Country Saved Successfully")
                    else:
                        print("Country Already Existed")
                    line_count += 1
    except Exception as e:
        print(f'Error : {e}')
        return e

def get_or_create_country(country_data):
    """
    Get or create a Country Object
    :param country_data: Country attributes in DICT
    :return: Country Object
    """

    try:
        # print(country_data)
        country = Countries.objects.get(name__iexact=country_data[1].lower())
        return False
    except Countries.DoesNotExist:
        print("No Country Found")
        country = Countries(
            id =int(country_data[0]),
            name=country_data[1],
            status = True
        )
        country.save()
        return True


add_countries_thread()