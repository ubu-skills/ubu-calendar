"""Module for the ubu-calendar skill
"""
import sys
from datetime import datetime, timedelta
from mycroft import MycroftSkill, intent_handler # type: ignore
sys.path.append("/usr/lib")
from UBUVoiceAssistant.util import util # type: ignore
from UBUVoiceAssistant.model.event import Event # type: ignore


class UbuCalendarSkill(MycroftSkill):
    """ubu-calendar skill class
    """

    def __init__(self):
        super().__init__()
        self.learning = True
        self.months = {'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5,
                       'junio': 6, 'julio': 7, 'agosto': 8, 'septiembre': 9,
                       'octubre': 10, 'noviembre': 11, 'diciembre': 12}

    def initialize(self):
        """Initializes 
        """
        self.web_service = util.get_data_from_server()

    @intent_handler('UpcomingEvents.intent')
    def handle_upcoming_events_intent(self, message):
        events = self.web_service.get_calendar_upcoming_view()
        events = [str(Event(event)) for event in events['events']]
        self.speak(util.text_to_speech(events))

    @intent_handler('DayEvents.intent')
    def handle_day_events_intent(self, message):
        self.month = str(self.months[message.data['month']])
        events = self.web_service.get_calendar_day_view(str(message.data['year']), self.month,
            str(message.data['day']))
        events = [str(Event(event)) for event in events['events']]
        self.speak(util.text_to_speech(events))

    @intent_handler('CourseEvents.intent')
    def handle_course_events_intent(self, message):
        course = message.data['course']
        course_id = util.get_course_id_by_name(course, self.web_service.get_user_courses())
        if course_id:
            course = self.web_service.get_user().get_course(course_id)
            course_events = course.get_events()
            # If the course events have never been looked up
            if not course_events:
                course_events = self.web_service.get_calendar_events_by_courseid(course_id)
                course_events = [Event(event) for event in course_events['events']]
                course.set_events(course_events)

            course_events = [str(event) for event in course_events]
            self.speak(util.text_to_speech(course_events))
        else:
            self.speak_dialog('no.course')

    @intent_handler('RecentUpdates.intent')
    def handle_course_updates(self, message):
        course = message.data['course']
        course_id = util.get_course_id_by_name(course, self.web_service.get_user_courses())
        cmids = self.web_service.get_course_updates_since(course_id,
            int(datetime.timestamp(datetime.today() - timedelta(days=1))))
        module_names = self.web_service.get_course_module(cmids)
        if module_names:
            self.speak(util.text_to_speech(module_names))
        else:
            self.speak_dialog('changes')


def create_skill():
    return UbuCalendarSkill()
