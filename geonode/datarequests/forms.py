import os
import traceback

from django import forms
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _

from captcha.fields import ReCaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML, Div, Column, Row, Field
from crispy_forms.bootstrap import PrependedText, InlineRadios
from model_utils import Choices

from geonode.datarequests.models import DataRequestProfile
from geonode.layers.forms import NewLayerUploadForm, LayerUploadForm, JSONField
from geonode.documents.models import Document
from geonode.documents.forms import DocumentCreateForm
from geonode.people.models import OrganizationType, Profile

from .models import DataRequestProfile, RequestRejectionReason

from pprint import pprint

class DataRequestProfileForm(forms.ModelForm):

    captcha = ReCaptchaField(attrs={'theme': 'clean'})

    class Meta:
        model = DataRequestProfile
        fields = (
            'first_name',
            'middle_name',
            'last_name',
            'organization',
            # Non-commercial requester field
            'organization_type',
            'organization_other',
            # Academe requester fields
            'request_level',
            'funding_source',
            'is_consultant',

            'location',
            'email',
            'contact_number',
            'captcha'
        )
        widgets = {
            'organization_type': forms.RadioSelect,
        }

    ORGANIZATION_TYPE_CHOICES = Choices(
        (0, _('Phil-LiDAR 1 SUC')),
        (1, _('Phil-LiDAR 2 SUC' )),
        (2, _( 'Government Agency')),
        (3, _('Academe')),
        (4, _( 'International NGO')),
        (5, _('Local NGO')),
        (6, _('Private Insitution' )),
        (7, _('Other' )),
    )

    REQUEST_LEVEL_CHOICES = Choices(
        ('institution', _('Academic/ Research Institution')),
        ('faculty', _('Faculty')),
        ('student', _('Student')),
    )

    # organization_type = forms.ChoiceField(
    #     choices = ORGANIZATION_TYPE_CHOICES,
    #     required = False
    # )

    # request_level = forms.CharField(
    #     label=_('Level of the Request'),
    #     required = False
    # )

    # funding_source = forms.CharField(
    #     label = _('Source of Funding'),
    #     max_length=255,
    #     required=False
    # )
    #
    # is_consultant = forms.BooleanField(
    #     required=False
    # )

    def __init__(self, *args, **kwargs):

        super(DataRequestProfileForm, self).__init__(*args, **kwargs)
        self.fields['captcha'].error_messages = {'required': 'Please answer the Captcha to continue.'}
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.form_tag = False
        # self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Fieldset('User Information',
                Div(
                    Field('first_name', css_class='form-control'),
                    css_class='form-group'
                ),
                Div(
                    Field('middle_name', css_class='form-control'),
                    css_class='form-group'
                ),
                Div(
                    Field('last_name', css_class='form-control'),
                    css_class='form-group'
                ),
                Div(
                    Field('organization', css_class='form-control'),
                    css_class='form-group'
                ),
                Div(
                    Field('organization_type', css_class='form-control'),
                    css_class='form-group'
                ),
                Fieldset('Academe',
                    Div(
                        Field('request_level', css_class='form-control'),
                        css_class='form-group'
                    ),
                    Div(
                        Field('funding_source', css_class='form-control'),
                        css_class='form-group'
                    ),
                    Field('is_consultant'),
                    css_class='academe-fieldset',
                ),

                    Div(
                        Field('organization_other', css_class='form-control'),
                        css_class='form-group'
                    ),

                Div(
                    Field('location', css_class='form-control'),
                    css_class='form-group'
                ),
                Div(
                    Field('email', css_class='form-control'),
                    css_class='form-group'
                ),
                Div(
                    Field('contact_number', css_class='form-control'),
                    css_class='form-group'
                ),
            ),
            Div(
                HTML("<br/><section class=widget>"),
                Field('captcha'),
                HTML("</section>")
            ),
        )

    def clean_first_name(self):
        fname = self.cleaned_data.get('first_name').strip()
        if len(fname)<1:
            raise forms.ValidationError("You have entered an empty first name")

        return fname

    def clean_middle_name(self):
        mname = self.cleaned_data.get('middle_name').strip()
        if len(mname)<1 or not mname:
            mname = '_'
        return mname

    def clean_last_name(self):
        lname = self.cleaned_data.get('last_name').strip()
        if len(lname)<1:
            raise forms.ValidationError("You have entered an empty last name")

        return lname

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_emails = Profile.objects.all().values_list('email', flat=True)
        if email in user_emails:
            raise forms.ValidationError(
                'That email is already being used by a registered user. lease login with your account instead.')

        return email

    def clean_organization(self):
        organization = self.cleaned_data.get('organization')

        if len(organization) > 64:
            raise forms.ValidationError(
                'Organization name can only be 64 characters')

        return organization

    def clean_funding_source(self):
        funding_source = self.cleaned_data.get('funding_source')
        organization_type = self.cleaned_data.get('organization_type')
        #intended_use_of_dataset = self.cleaned_data.get('intended_use_of_dataset')
        if (#intended_use_of_dataset == 'noncommercial' and
                organization_type == OrganizationType.ACADEME and
                not funding_source):
            raise forms.ValidationError(
                'This field is required.')
        return funding_source
    def clean_organization_other(self):
        organization_other = self.cleaned_data.get('organization_other')
        organization_type = self.cleaned_data.get('organization_type')
        if (organization_type == OrganizationType.OTHER and
                not organization_other):
            raise forms.ValidationError(
                'This field is required.')
        return organization_other
    #def clean_letter_file(self):
    #    letter_file = self.cleaned_data.get('letter_file')
    #    split_filename =  os.path.splitext(str(letter_file.name))

    #    if letter_file and split_filename[len(split_filename)-1].lower()[1:] != "pdf":
    #        raise forms.ValidationError(_("This file type is not allowed"))
    #    return letter_file

    def save(self, commit=True, *args, **kwargs):
        data_request = super(
            DataRequestProfileForm, self).save(commit=False, *args, **kwargs)

        if commit:
            data_request.save()
        return data_request

class DataRequestDetailsForm(forms.ModelForm):

    INTENDED_USE_CHOICES = Choices(
        ('Disaster Risk Management', _('Disaster Risk Management')),
        ('Urban/Land Subdivision Planning',
            _('Urban/Land Subdivision Planning')),
        ('Road/Infrastracture Planning', _('Road/Infrastracture Planning')),
        ('Transport/Traffic Management', _('Transport/Traffic Management')),
        ('Oil/Gas/Geothermal/Quarries/Minerals Exploration',
            _('Oil/Gas/Geothermal/Quarries/Minerals Exploration')),
        ('Biological/Agricultural/Forestry/Marine/Natural Resource Planning',
            _('Biological/Agricultural/Forestry/Marine/Natural Resource Planning')),
        ('Cellular Network Mapping', _('Cellular Network Mapping')),
        ('other', _('Other, please specify:')),
    )

    project_summary = forms.CharField(
        widget=forms.Textarea,
        label=_('Project Summary'),
        required=True
    )

    purpose = forms.ChoiceField(
        label =_(u'Purpose of the Data'),
        choices = INTENDED_USE_CHOICES
    )

    purpose_other = forms.CharField(
        label=_(u'Your custom purpose for the data'),
        required=False
    )

    letter_file = forms.FileField(
        label=_('Formal Request Letter (PDF only)'),
        required = True
    )

    class Meta:
        model = DataRequestProfile
        fields=(
            #project_summary',
            'data_type_requested',
            'intended_use_of_dataset',

        )



    def __init__(self, *args, **kwargs):
        super(DataRequestDetailsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_class = 'form-horizontal'
        self.helper.form_tag = False
        # self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Div(
                Field('project_summary', css_class='form-control'),
                css_class='form-group'
            ),
            Div(
                Field('purpose', css_class='form-control'),
                Div(
                    Field('purpose_other', css_class='form-control'),
                    css_class='col-sm-11 col-sm-offset-1'
                ),
                css_class='form-group'
            ),
            Div(
               Field('data_type_requested', css_class='form-control'),
               css_class='form-group'
            ),
            Div(
                Field('intended_use_of_dataset', css_class='form-control'),
                css_class='form-group'
            ),
            # Fieldset('Non-commercial',
            #
            #    css_class='noncommercial-fieldset',
            # ),
            Div(
                Field('letter_file', css_class='form-control'),
                    css_class='form-group'
            ),
            #HTML("""
            #{% load i18n %}


            #"""),
        )

    def clean_letter_file(self):
        letter_file = self.cleaned_data.get('letter_file')
        split_filename =  os.path.splitext(str(letter_file.name))

        if letter_file and split_filename[len(split_filename)-1].lower()[1:] != "pdf":
            raise forms.ValidationError(_("This file type is not allowed"))
        return letter_file

class DataRequestProfileShapefileForm(NewLayerUploadForm):

    INTENDED_USE_CHOICES = Choices(
        ('Disaster Risk Management', _('Disaster Risk Management')),
        ('Urban/Land Subdivision Planning',
            _('Urban/Land Subdivision Planning')),
        ('Road/Infrastracture Planning', _('Road/Infrastracture Planning')),
        ('Transport/Traffic Management', _('Transport/Traffic Management')),
        ('Oil/Gas/Geothermal/Quarries/Minerals Exploration',
            _('Oil/Gas/Geothermal/Quarries/Minerals Exploration')),
        ('Biological/Agricultural/Forestry/Marine/Natural Resource Planning',
            _('Biological/Agricultural/Forestry/Marine/Natural Resource Planning')),
        ('Cellular Network Mapping', _('Cellular Network Mapping')),
        ('other', _('Other, please specify:')),
    )

    # ORGANIZATION_TYPE_CHOICES = Choices(
    #     (0, _('Phil-LiDAR 1 SUC')),
    #     (1, _('Phil-LiDAR 2 SUC' )),
    #     (2, _( 'Government Agency')),
    #     (3, _('Academe')),
    #     (4, _( 'International NGO')),
    #     (5, _('Local NGO')),
    #     (6, _('Private Insitution' )),
    #     (7, _('Other' )),
    # )

    DATASET_USE_CHOICES =Choices(
        ('commercial', _('Commercial')),
        ('noncommercial', _('Non-commercial')),
    )

    DATA_TYPE_CHOICES = Choices(
        ('interpreted', _('Interpreted')),
        ('raw', _('Raw')),
        ('processed', _('Processed')),
        ('other', _('Other')),
    )

    # REQUEST_LEVEL_CHOICES = Choices(
    #     ('institution', _('Institution')),
    #     ('faculty', _('Faculty')),
    #     ('student', _('Student')),
    # )

    abstract = forms.CharField(required=False)

    charset = forms.CharField(required=False)

    project_summary = forms.CharField(
        label=_('Project Summary'),
        required=True
    )

    purpose = forms.ChoiceField(
        label=_('Purpose/Intended Use of Data'),
        choices=INTENDED_USE_CHOICES
    )

    purpose_other = forms.CharField(
        label=_(u'Your custom purpose for the data'),
        required=False
    )

    data_type_requested = forms.TypedChoiceField(
        label = _('Types of Data Requested'),
        choices = DATA_TYPE_CHOICES,
    )

    intended_use_of_dataset = forms.ChoiceField(
        label = _('Intended Use of Data Set'),
        choices = DATASET_USE_CHOICES,
        required=True
    )

    letter_file = forms.FileField(
        label=_('Formal Request Letter (PDF only)'),
        required = True
    )

    def __init__(self, *args, **kwargs):
        super(DataRequestProfileShapefileForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned = self.cleaned_data
        if cleaned['base_file']:
            cleaned = super(NewLayerUploadForm, self).clean()

        cleaned[ 'purpose'] = self.clean_purpose()
        cleaned['purpose_other'] = self.clean_purpose_other()

        return cleaned

    def clean_letter_file(self):
        letter_file = self.cleaned_data.get('letter_file')
        split_filename =  os.path.splitext(str(letter_file.name))

        if letter_file and split_filename[len(split_filename)-1].lower()[1:] != "pdf":
            raise forms.ValidationError(_("This file type is not allowed"))
        return letter_file

    def clean_purpose_other(self):
        purpose = self.cleaned_data.get('purpose')
        purpose_other = self.cleaned_data.get('purpose_other')
        if purpose == self.INTENDED_USE_CHOICES.other:
            if not purpose_other:
                raise forms.ValidationError(
                    'Please state your purpose for the requested data.')
        return purpose_other

    def clean_purpose(self):
        purpose = self.cleaned_data.get('purpose')
        if purpose == self.INTENDED_USE_CHOICES.other:
            purpose_other = self.cleaned_data.get('purpose_other')
            if not purpose_other:
                return purpose
            else:
                return purpose_other
        return purpose


class DataRequestProfileRejectForm(forms.ModelForm):

    REJECTION_REASON_CHOICES = Choices(
        ('Invalid requirements', _('Invalid requirements')),
        ('Invalid purpose', _('Invalid purpose')),
        ('Invalid request', _('Invalid request')),
    )

    rejection_reason = forms.ChoiceField(
        label=_('Reason for Rejection'),
        choices=REJECTION_REASON_CHOICES
    )

    class Meta:
        model = DataRequestProfile
        fields = (
            'rejection_reason', 'additional_rejection_reason',
        )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        super(DataRequestProfileRejectForm, self).__init__(*args, **kwargs)
        rejection_reason_qs = RequestRejectionReason.objects.all()
        if rejection_reason_qs:
            self.fields['rejection_reason'].choices = [(r.reason, r.reason) for r in rejection_reason_qs]
