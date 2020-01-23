import ddt
from django.urls import reverse
from six import text_type

from common.test.utils import XssTestMixin
from course_modes.models import CourseMode
from edxmako.shortcuts import render_to_response
from student.tests.factories import AdminFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

def intercept_renderer(path, context):
    """
    Intercept calls to `render_to_response` and attach the context dict to the
    response for examination in unit tests.
    """
    # I think Django already does this for you in their TestClient, except
    # we're bypassing that by using edxmako.  Probably edxmako should be
    # integrated better with Django's rendering and event system.
    response = render_to_response(path, context)
    response.mako_context = context
    response.mako_template = path
    return response


@ddt.ddt
class TestDatesDashboard(ModuleStoreTestCase, XssTestMixin):
    """
    Tests for the instructor dashboard (not legacy).
    """

    def setUp(self):
        """
        Set up tests
        """
        super(TestDatesDashboard, self).setUp()
        self.course = CourseFactory.create(
            grading_policy={"GRADE_CUTOFFS": {"A": 0.75, "B": 0.63, "C": 0.57, "D": 0.5}},
            display_name='<script>alert("XSS")</script>'
        )

        self.course_mode = CourseMode(
            course_id=self.course.id,
            mode_slug=CourseMode.DEFAULT_MODE_SLUG,
            mode_display_name=CourseMode.DEFAULT_MODE.name,
            min_price=40
        )
        self.course_info = CourseFactory.create(
            org="ACME",
            number="001",
            run="2017",
            name="How to defeat the Road Runner"
        )
        self.course_mode.save()
        # Create instructor account
        self.instructor = AdminFactory.create()
        self.client.login(username=self.instructor.username, password="test")

        # URL for instructor dash
        self.url = reverse('dates', kwargs={'course_id': text_type(self.course.id)})

    def test_hello(self):
        self.assertTrue(False)
