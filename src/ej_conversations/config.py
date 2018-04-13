from django.conf import settings

# Statistics configuration
# you can override this variable in django settings variable MATH_REFRESH_TIME
# passing a integer value in seconds
STATISTICS_REFRESH_TIME = \
    getattr(settings, 'CONVERSATION_STATISTICS_REFRESH_TIME', 0)
