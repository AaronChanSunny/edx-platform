import os

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from intercom import intercom
import requests

from xmodule.modulestore.django import modulestore
from student.models import CourseEnrollment
from course_action_state.models import CourseRerunState

# try:
#     from course_creators.models import CourseCreator
# except ImportError:
#     # `course_creators` app is included only in the Studio
#     CourseCreator = None

intercom.Intercom.app_id = os.environ.get("INTERCOM_APP_ID", "")
intercom.Intercom.api_key = os.environ.get("INTERCOM_APP_SECRET", "")
INTERCOM_USER_EMAIL = os.environ.get("INTERCOM_USER_EMAIL", "")


def intercom_update(custom_data):
    try:
        intercom.Intercom.update_user(email=INTERCOM_USER_EMAIL, custom_data=custom_data)
    except (intercom.IntercomError, requests.exceptions.RequestException):
        pass


def update_user_statistics():
    custom_data = {
        'Users - total': User.objects.count(),
        'Users - active': User.objects.filter(is_active=True).count(),
        # TODO: Filter out inactive users?
        'Users - students': User.objects.filter(
            courseenrollment__is_active=True).distinct().count(),
    }
    # if CourseCreator:
    #     custom_data['Users - course creation rights granted'] = User.objects.filter(
    #         coursecreator__state=CourseCreator.GRANTED).count()
    intercom_update(custom_data=custom_data)


update_user_statistics()


@receiver(post_save, dispatch_uid='user_save_callback')
def user_save_callback(sender, instance, created, raw, **kwargs):
    if sender in (User, CourseEnrollment):  # CourseCreator
        update_user_statistics()


def update_course_statistics():
    custom_data = {
        # TODO: Figure out whether we need to filter out broken items or not
        #       https://github.com/edx/edx-platform/blob/d4de932c2b46dbe1ad6439731b4312fb36813d6d/cms/djangoapps/contentstore/views/course.py#L281
        'Courses - total': len(modulestore().get_courses()),

        # TODO: There might be some unfinished/broken reruns
        #       https://github.com/appsembler/edx-platform/blob/d4de932c2b46dbe1ad6439731b4312fb36813d6d/cms/djangoapps/contentstore/views/course.py#L295
        'Courses - reruns': CourseRerunState.objects.count(),
    }
    intercom_update(custom_data=custom_data)


update_course_statistics()


@receiver(post_save, sender=CourseRerunState, dispatch_uid='course_save_callback')
def course_save_callback(sender, instance, created, raw, **kwargs):
    if created:
        update_course_statistics()
