'''
File name: Views.py

Renders the html with the requested information

Calls ---> geo_code from geocoding_helper to get the geocode from the address given by user
      ---> get_viz from queries module to query the information requested

'''
from django.shortcuts import render
from django import forms
from queries import get_viz
from .geocoding_helper import geo_code

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
DAYS = [(x, x) for x in DAYS]
TYPES = [(1, 'walking'), (2, 'public transit'), [3, 'driving']]
IMAGE_URL_1 = '/viz/bar_week.png'
IMAGE_URL_2 = '/viz/bar_day.png'
MAP1_URL = '/viz/map_all.html'
MAP2_URL = '/viz/map_cuad.html'

class Multi(forms.widgets.MultiWidget):
    '''
    Helper class to build the hour range class
    '''
    def __init__(self, attrs=None):
        widget = (forms.widgets.NumberInput(attrs={'placeholder': 'default: 0'}),
                  forms.widgets.NumberInput(attrs={'placeholder': 'default: 23'})
                 )
        super(Multi, self).__init__(widget, attrs=attrs)

    def decompress(self, value):
        return value

class HourRange(forms.MultiValueField):
    '''
    Hour Range widget with the required conditions for the
    Mexico City crime data set.
    '''
    widget = Multi
    def __init__(self, *args, **kwargs):
        fields = (forms.IntegerField(min_value=0, max_value=22),
                  forms.IntegerField(min_value=1, max_value=23))
        super(HourRange, self).__init__(fields=fields,
                                        *args, **kwargs)
    def compress(self, data_list):
        for i, hour in enumerate(data_list):
            if hour and not (0 <= hour <= 23):
                raise forms.ValidationError(
                    'The hour must be between 0 and 23')
            if not hour:
                data_list[i] = 0 if i == 0 else 23
        if data_list and (data_list[1] <= data_list[0]):
            raise forms.ValidationError(
                'Lower hour bound must not exceed or equal the upper hour bound.')

        return data_list


class QueryForm(forms.Form):
    '''
    Class for Django Form
    -Inputs from user: address (str), day(list of days), hour(integer),
                      crime_type(categories)
    '''
    address = forms.CharField(label='Mexico city address',
                              help_text='e.g. Issac Newton 104 Mexico City',
                              max_length=150)

    day = forms.ChoiceField(label='Days', widget=forms.RadioSelect,
                            choices=DAYS)

    hour = HourRange(label='Hour Range',
                     help_text="e.g. 10 and 12 (meaning 10am-12pm)",
                     required=False)

    crime_type = forms.MultipleChoiceField(label='Getting around',
                                           widget=forms.CheckboxSelectMultiple,
                                           choices=TYPES)

    def clean(self):
        '''
        If the address is not in Mexico City returns an error in the form
        '''
        if 'address' in self.cleaned_data:
            ad = self.cleaned_data['address']
            g_code = geo_code(ad)
            if not g_code:
                raise forms.ValidationError('This address is not in Mexico City')

            self.cleaned_data["address"] = g_code
        return self.cleaned_data


def get(request):
    '''
    Renders the page with the initial form of Django or
    with the graphs requested from the user.
    '''
    context = {}
    res = None
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = QueryForm(request.GET)
            # check whether it's valid:
        if form.is_valid():
            # Convert form data to an args dictionary for get_maps
            args = {}
            address = form.cleaned_data['address']
            args['address'] = address
            args['day'] = form.cleaned_data['day']

            hour = form.cleaned_data['hour']
            if hour:
                args['hour'] = hour
            else:
                args['hour'] = [0, 23]

            args['crime_type'] = [int(x) for x in form.cleaned_data['crime_type']]

            try:
                res = get_viz(args)
                if res is False:
                    context['err'] = 'Data requested not found. Try other time ranges'
            except Exception as e:
                context['err'] = "Error was caught"
    else:
        form = QueryForm()

    if res is True:
        context['result'] = args
        context['IMAGE_URL_1'] = IMAGE_URL_1
        context['IMAGE_URL_2'] = IMAGE_URL_2
        context['map1'] = MAP1_URL
        context['map2'] = MAP2_URL
    else:
        context['result'] = None

    context['form'] = form

    return render(request, 'mexcrimespage.html', context)
