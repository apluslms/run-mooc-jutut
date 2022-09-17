import os
import sys
import random
from datetime import timedelta

import django
from django.utils import timezone


def create_test_feedback(root_user):
    # Create many feedback objects with fake A+ addresses/links.
    # These can be used to test the feedback lists, filtering and pagination.
    from aplus_client.client import AplusApiDict, AplusClient
    from feedback.models import Course, Exercise, Feedback, FeedbackForm, FeedbackTag, Site, Student, StudentTag

    client = AplusClient()
    course_api_url = "http://plus:8000/api/v2/courses/1/"
    site = Site.get_by_url(course_api_url)
    url, params = client.normalize_url(course_api_url)
    client.update_params(params)

    course_api_obj = AplusApiDict(
        client,
        data={
            'id': 1,
            'url': course_api_url,
        },
        source_url=course_api_url,
    )
    c = Course.objects.create(
        course_api_obj,
        code="CS-X0001",
        name="Test course 1",
        instance_name="Test",
        html_url="http://plus:8000/def/current/",
        language="en",
    )

    rand = random.Random(1337)

    student_tags = []
    fb_tags = []
    colors = [
        "#cc00cc",
        "#00cc00",
        "#0040ff",
        "#e60000",
        "#ffa31a",
        "#4d2600",
        "#0d0d0d",
        "#5200cc",
        "#ffff33",
        "#33cccc",
    ]
    len_colors = len(colors)
    for i in range(1, 6):
        # student tags
        student_tag_api_obj = AplusApiDict(
            client,
            data={
                'id': i,
                'url': course_api_url + f"usertags/{i}/",
            },
            source_url=course_api_url + f"usertags/{i}/",
        )
        student_tag = StudentTag.objects.create(
            student_tag_api_obj,
            course=c,
            name=f"student tag {i}",
            slug=f"studenttag-{i}",
            color=colors[((i - 1) * 2 ) % len_colors],
        )
        student_tags.append(student_tag)

        # feedback tags
        fb_tag = FeedbackTag.objects.create(
            course=c,
            name=f"fb tag {i}",
            slug=f"fbtag-{i}",
            color=colors[((i - 1) * 2 + 1) % len_colors],
        )
        fb_tags.append(fb_tag)

    students = []
    for i in range(1, 26):
        # Start from user id 4, which has been used for the student account
        # in the container apluslms/run-aplus-front.
        uid = i + 3
        student_api_obj = AplusApiDict(
            client,
            data={
                'id': uid,
                'url': f"http://plus:8000/api/v2/users/{uid}/",
            },
            source_url=f"http://plus:8000/api/v2/users/{uid}/",
        )
        stud = Student.objects.create(
            student_api_obj,
            username=f"student{i}",
            full_name=f"Tester{i} Teststudent{i}",
            student_id=f"109{i:0>3d}",
        )
        stud.tags.add(rand.choice(student_tags))
        students.append(stud)

    exercises = []
    for i in range(1, 21):
        exercise_api_obj = AplusApiDict(
            client,
            data={
                'id': i,
                'url': f"http://plus:8000/api/v2/exercises/{i}/",
            },
            source_url=f"http://plus:8000/api/v2/exercises/{i}/",
        )
        exercise_url_key = f"feedback{i}"
        e = Exercise.objects.create(
            exercise_api_obj,
            name=f"Feedback questionnaire {i}",
            display_name=f"{i}.1.1 Feedback questionnaire {i}",
            html_url=f"http://plus:8000/def/current/module{i}/chapter{i}/{exercise_url_key}/",
            course=c,
        )
        exercises.append((e, exercise_url_key))

    # Feedback form specs taken from the O1 course and slightly adapted here.
    # The text field question was changed to "required: True".
    form = FeedbackForm.objects.create(
        sha1="38a7bee173a54d3a3ca51f17bbb436a17af818a4",
        form_spec=[
        {
            'key': 'timespent',
            'type': 'number',
            'title': '',
            'minimum': 6,
            'required': True,
            'htmlClass': 'form-group time-usage-question required standard place-inline',
            'description': '<p><strong>Ajankäyttö:</strong> <span class="mustanswer">(*) Pakollinen</span></p>\n<p>Kirjoita alle, kuinka monta minuuttia olet käyttänyt kokonaisuudessaan oppimateriaalin\ntähän lukuun (materiaalin lukeminen, tehtävien tekeminen jne.). Viidentoista minuutin\ntai puolen tunnin tarkkuus riittää hyvin.</p>\n',
            'validationMessage': 'Anna aika minuutteina.',
        },
        {
            'key': 'understood',
            'enum': ['a', 'b', 'c', 'd', 'e'],
            'type': 'radio',
            'title': '',
            'required': True,
            'titleMap': {'a': 'täysin samaa mieltä', 'b': 'jokseenkin samaa mieltä', 'c': 'jokseenkin eri mieltä', 'd': 'täysin eri mieltä', 'e': 'en osaa sanoa / en kommentoi'},
            'htmlClass': 'form-group',
            'description': '<p><strong>&quot;Minusta tuntuu, että olen tajunnut oleellisimmat asiat tästä luvusta.&quot;</strong> <span class="mustanswer">(*) Pakollinen</span></p>\n',
        },
        {
            'key': 'field_2',
            'type': 'static',
            'title': '',
            'required': False,
            'description': '<div class="feedbackinstruction docutils container">\n<p><strong>Sanallinen kommentti tai kysymys:</strong></p>\n<p>Sanallinen palaute ei ole pakollista. Kysy silti mieluusti jotain,\nanna palautetta tai pohdiskele! (Oikea paikka kiireellisille\nkeskeneräisen tehtävän ratkaisemiseen liittyville pyynnöille on\nkuitenkin harjoitusryhmä tai Piazza, sillä emme välttämättä ehdi\nreagoida näihin palautteisiin kierroksen ollessa auki.)</p>\n</div>\n',
        },
        {
            'key': 'field_3',
            'type': 'textarea',
            'title': '',
            'required': True,
            'htmlClass': 'form-group main-feedback-question voluntary standard place-on-own-line',
        }
        ],
        form_i18n={
            "t\u00e4ysin eri mielt\u00e4": {
                "en": "fully disagree",
                "fi": "t\u00e4ysin eri mielt\u00e4",
            },
            "t\u00e4ysin samaa mielt\u00e4": {
                "en": "fully agree",
                "fi": "t\u00e4ysin samaa mielt\u00e4",
            },
            "Anna aika minuutteina.": {
                "en": "Please enter the time in minutes.",
                "fi": "Anna aika minuutteina.",
            },
            "jokseenkin eri mielt\u00e4": {
                "en": "somewhat disagree",
                "fi": "jokseenkin eri mielt\u00e4",
            },
            "jokseenkin samaa mielt\u00e4": {
                "en": "somewhat agree",
                "fi": "jokseenkin samaa mielt\u00e4",
            },
            "en osaa sanoa / en kommentoi": {
                "en": "I\u2019m unable to answer or don\u2019t want to comment.",
                "fi": "en osaa sanoa / en kommentoi",
            },
            "<p><strong>&quot;Minusta tuntuu, ett\u00e4 olen tajunnut oleellisimmat asiat t\u00e4st\u00e4 luvusta.&quot;</strong> <span class=\"mustanswer\">(*) Pakollinen</span></p>\n": {
                "en": "<p><strong>\u201cI feel that I have understood the most important things in this chapter.\u201d</strong> <span class=\"mustanswer\">(*) Required</span></p>\n",
                "fi": "<p><strong>&quot;Minusta tuntuu, ett\u00e4 olen tajunnut oleellisimmat asiat t\u00e4st\u00e4 luvusta.&quot;</strong> <span class=\"mustanswer\">(*) Pakollinen</span></p>\n",
            },
            "<p><strong>Ajank\u00e4ytt\u00f6:</strong> <span class=\"mustanswer\">(*) Pakollinen</span></p>\n<p>Kirjoita alle, kuinka monta minuuttia olet k\u00e4ytt\u00e4nyt kokonaisuudessaan oppimateriaalin\nt\u00e4h\u00e4n lukuun (materiaalin lukeminen, teht\u00e4vien tekeminen jne.). Viidentoista minuutin\ntai puolen tunnin tarkkuus riitt\u00e4\u00e4 hyvin.</p>\n": {
                "en": "<p><strong>Time spent:</strong> <span class=\"mustanswer\">(*) Required</span></p>\n<p>Please estimate the total number of minutes you spent on this chapter (reading, assignments,\netc.). You don\u2019t have to be exact, but if you can produce an estimate to within 15 minutes or\nhalf an hour, that would be great.</p>\n",
                "fi": "<p><strong>Ajank\u00e4ytt\u00f6:</strong> <span class=\"mustanswer\">(*) Pakollinen</span></p>\n<p>Kirjoita alle, kuinka monta minuuttia olet k\u00e4ytt\u00e4nyt kokonaisuudessaan oppimateriaalin\nt\u00e4h\u00e4n lukuun (materiaalin lukeminen, teht\u00e4vien tekeminen jne.). Viidentoista minuutin\ntai puolen tunnin tarkkuus riitt\u00e4\u00e4 hyvin.</p>\n",
            },
            "<div class=\"feedbackinstruction docutils container\">\n<p><strong>Sanallinen kommentti tai kysymys:</strong></p>\n<p>Sanallinen palaute ei ole pakollista. Kysy silti mieluusti jotain,\nanna palautetta tai pohdiskele! (Oikea paikka kiireellisille\nkeskener\u00e4isen teht\u00e4v\u00e4n ratkaisemiseen liittyville pyynn\u00f6ille on\nkuitenkin harjoitusryhm\u00e4 tai Piazza, sill\u00e4 emme v\u00e4ltt\u00e4m\u00e4tt\u00e4 ehdi\nreagoida n\u00e4ihin palautteisiin kierroksen ollessa auki.)</p>\n</div>\n": {
                "en": "<div class=\"feedbackinstruction docutils container\">\n<p><strong>Written comment or question:</strong></p>\n<p>You aren\u2019t required to give written feedback. Nevertheless, please\ndo ask something, give feedback, or reflect on your learning!\n(However, the right place to ask urgent questions about programs\nthat you\u2019re currently working on isn\u2019t this form but the lab sessions\nor Piazza. We can\u2019t guarantee that anyone will even see anything\nyou type here before the weekly deadline.)</p>\n</div>\n",
                "fi": "<div class=\"feedbackinstruction docutils container\">\n<p><strong>Sanallinen kommentti tai kysymys:</strong></p>\n<p>Sanallinen palaute ei ole pakollista. Kysy silti mieluusti jotain,\nanna palautetta tai pohdiskele! (Oikea paikka kiireellisille\nkeskener\u00e4isen teht\u00e4v\u00e4n ratkaisemiseen liittyville pyynn\u00f6ille on\nkuitenkin harjoitusryhm\u00e4 tai Piazza, sill\u00e4 emme v\u00e4ltt\u00e4m\u00e4tt\u00e4 ehdi\nreagoida n\u00e4ihin palautteisiin kierroksen ollessa auki.)</p>\n</div>\n",
            },
        },
    )
    # End FeedbackForm

    i = 1
    for student in students:
        for exercise, exercise_url_key in exercises:
            fb = Feedback.objects.create(
                exercise=exercise,
                submission_id=i,
                path_key=f"test/{exercise_url_key}",
                language="en",
                student=student,
                form=form,
                form_data={
                    'field_3': 'Testing testing',
                    'timespent': rand.randint(10, 120),
                    'understood':  rand.choice(['a', 'b', 'c', 'd', 'e']),
                },
                post_url=exercise.html_url,
                submission_url=f"http://plus:8000/api/v2/submissions/{i}/grader/?token=xyz",
                submission_html_url=exercise.html_url + f"submissions/{i}/",
            )
            if i % 3 == 0:
                # Set one tag to some Feedback objects.
                fbtag = rand.choice(fb_tags)
                fbtag.feedbacks.add(fb)

            i += 1


def create_default_users():
    #from django.contrib.auth.models import User
    from accounts.models import JututUser as User

    u1 = User.objects.create(
        username="root",
        email="root@localhost",
        first_name="Ruth",
        last_name="Robinson",
        is_superuser=True,
        is_staff=True,
    )
    u1.set_password("root")
    u1.save()
    return u1

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jutut.settings")
    sys.path.insert(0, '')
    django.setup()

    root_user = create_default_users()
    create_test_feedback(root_user)
