#!/bin/bash

# No longer used as survey Testing code is in place.
# mysql -s -r -e 'UPDATE uscstudy.survey_links SET start_datetime = NOW(), status = 0, last_answered_question = null WHERE survey_key LIKE "%-time" OR survey_key LIKE "%-risk"'
