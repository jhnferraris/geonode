# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2012 OpenPlans
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import os
import tempfile
import taggit

from django import forms
from django.utils import simplejson as json
from django.utils.translation import ugettext as _
from modeltranslation.forms import TranslationModelForm

from mptt.forms import TreeNodeMultipleChoiceField
from bootstrap3_datetime.widgets import DateTimePicker

from geonode.eula.models import AnonDownloader

from captcha.fields import ReCaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML, Div, Column, Row, Field
from crispy_forms.bootstrap import PrependedText

import autocomplete_light
