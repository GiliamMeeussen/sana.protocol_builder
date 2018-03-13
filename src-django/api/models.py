from copy import deepcopy

from django.db import models
from django.contrib.auth.models import User
from django.db import IntegrityError
import uuid

class Procedure(models.Model):
    title = models.CharField(max_length=255, blank=True)
    author = models.CharField(max_length=255, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    version = models.PositiveIntegerField(default=1)

    class Meta():
        app_label = 'api'
        unique_together = (('uuid','version'))

    def validate(self):
        if self.pages.count() == 0:
            raise IndexError('Procedure {} does not have any pages!'.format(self.id))

        for page in self.pages.all():
            page.validate()

    def deepcopy(self, latest_version):
        copy = deepcopy(self)
        copy.id = None
        copy.created = None
        copy.last_modified = None
        copy.version = int(latest_version) + 1
        copy.save()

        new_id = copy.id

        for page in self.pages.all():
            page.deepcopy(new_id)

        return new_id

class Page(models.Model):
    display_index = models.PositiveIntegerField()
    procedure = models.ForeignKey(Procedure, related_name='pages', on_delete=models.CASCADE)
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, **kwargs):
        super(Page, self).save()

        self.procedure.last_modified = self.last_modified
        self.procedure.save()

    class Meta:
        app_label = 'api'
        ordering = ['procedure', 'display_index']

    def validate(self):
        if self.elements.count() == 0:
            raise IndexError('Page {} does not have any elements!'.format(self.display_index))

    def deepcopy(self, new_procedure_id):
        copy = deepcopy(self)
        copy.id = None
        copy.created = None
        copy.last_modified = None
        copy.procedure_id = new_procedure_id
        copy.save()

        new_page_id = copy.id

        for element in self.elements.all():
            element.deepcopy(new_page_id)

        for show_if in self.show_if.all():
            show_if.deepcopy(new_page_id)


class Concept(models.Model):
    TYPES = (
        ('string', 'string'),
        ('boolean', 'boolean'),
        ('number', 'number'),
        ('complex', 'complex')
    )

    uuid = models.UUIDField(default=uuid.uuid4, null=False, blank=False, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    display_name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    data_type = models.CharField(max_length=16, choices=TYPES, null=True, blank=True)
    mime_type = models.CharField(max_length=128, null=True, blank=True)
    constraint = models.TextField(null=True, blank=True)

    def save(self, **kwargs):
        if self.data_type and (self.data_type, self.data_type) not in self.TYPES:
            raise IntegrityError('Invalid data type')

        super(Concept, self).save()

    class Meta:
        app_label = 'api'


class Element(models.Model):
    TYPES = (
        ('DATE', 'DATE'),
        ('ENTRY', 'ENTRY'),
        ('SELECT', 'SELECT'),
        ('MULTI_SELECT', 'MULTI_SELECT'),
        ('RADIO', 'RADIO'),
        ('PICTURE', 'PICTURE'),
        ('PLUGIN', 'PLUGIN'),
        ('ENTRY_PLUGIN', 'ENTRY_PLUGIN')
    )

    CHOICE_TYPES = (
        'SELECT',
        'MULTI_SELECT',
        'RADIO'
    )

    PLUGIN_TYPES = (
        'PLUGIN',
        'ENTRY_PLUGIN'
    )

    display_index = models.PositiveIntegerField()
    element_type = models.CharField(max_length=12, choices=TYPES)
    choices = models.TextField(null=True, blank=True)
    concept = models.ForeignKey(Concept, null=True, related_name='elements')
    question = models.TextField(null=True, blank=True)
    answer = models.TextField(null=True, blank=True)

    required = models.BooleanField(default=False)
    image = models.TextField(null=True, blank=True)
    audio = models.TextField(null=True, blank=True)
    action = models.TextField(null=True, blank=True)
    mime_type = models.CharField(max_length=128, null=True, blank=True)

    page = models.ForeignKey(Page, related_name='elements', on_delete=models.CASCADE)
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'api'
        ordering = ['page', 'display_index']

    def save(self, **kwargs):
        if self.element_type:
            if (self.element_type, self.element_type) not in self.TYPES:
                raise IntegrityError('Invalid element type')

        super(Element, self).save()

        self.page.last_modified = self.last_modified
        self.page.save()    

    def deepcopy(self, new_page_id):
        copy = deepcopy(self)
        copy.id = None
        copy.last_modified = None
        copy.created = None
        copy.page_id = new_page_id
        copy.save()


class AbstractElement(models.Model):
    TYPES = (
        ('DATE', 'DATE'),
        ('ENTRY', 'ENTRY'),
        ('SELECT', 'SELECT'),
        ('MULTI_SELECT', 'MULTI_SELECT'),
        ('RADIO', 'RADIO'),
        ('PICTURE', 'PICTURE'),
        ('PLUGIN', 'PLUGIN'),
        ('ENTRY_PLUGIN', 'ENTRY_PLUGIN')
    )

    CHOICE_TYPES = (
        'SELECT',
        'MULTI_SELECT',
        'RADIO'
    )

    PLUGIN_TYPES = (
        'PLUGIN',
        'ENTRY_PLUGIN'
    )

    display_index = models.PositiveIntegerField()
    element_type = models.CharField(max_length=12, choices=TYPES)
    choices = models.TextField(null=True, blank=True)
    concept = models.ForeignKey(Concept, related_name='abstractelements', on_delete=models.CASCADE)
    question = models.TextField(null=True, blank=True)
    answer = models.TextField(null=True, blank=True)

    required = models.BooleanField(default=False)
    image = models.TextField(null=True, blank=True)
    audio = models.TextField(null=True, blank=True)
    action = models.TextField(null=True, blank=True)
    mime_type = models.CharField(max_length=128, null=True, blank=True)

    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, **kwargs):
        if self.element_type:
            if (self.element_type, self.element_type) not in self.TYPES:
                raise IntegrityError('Invalid element type')

        super(AbstractElement, self).save()

        self.concept.last_modified = self.last_modified
        self.concept.save()

    class Meta:
        app_label = 'api'
        ordering = ['concept', 'display_index']


class ShowIf(models.Model):
    LOGICAL_TYPES = (
        'AND',
        'OR',
        'NOT'
    )

    CRITERIA_TYPES = (
        'EQUALS',
        'GREATER',
        'LESS'
    )

    page = models.ForeignKey(Page, related_name='show_if', on_delete=models.CASCADE)
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    conditions = models.TextField()

    class Meta:
        app_label = 'api'

    def save(self, **kwargs):
        super(ShowIf, self).save()

        self.page.last_modified = self.last_modified
        self.page.save()

    def deepcopy(self, new_page_id):
        copy = deepcopy(self)
        copy.id = None
        copy.page_id = new_page_id
        copy.last_modified = None
        copy.created = None
        copy.save()


class Device(models.Model):
    registration_id = models.CharField(max_length=255, blank=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'api'


class PushEvent(models.Model):
    procedure = models.ForeignKey(Procedure, related_name='push_event', on_delete=models.CASCADE)    
    secret_key = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'api'

