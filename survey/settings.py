survey_questions = {
	1: ('q_00', 'q_01', 'q_02', 'q_03', 'q_04', 'q_05', 'q_06', 'q_10', 'q_11', 'q_12'),
	2: ('q_00', 'q_01', 'q_02', 'q_03', 'q_04', 'q_05', 'q_06', 'q_20', 'q_21'),
	4: ('q_00', 'q_01', 'q_02', 'q_03', 'q_04', 'q_05'),
	14: ('q_00', 'q_01', 'q_02', 'q_03', 'q_04', 'q_05'),
	123: ('q_00', 'q_01', 'q_02', 'q_03', 'q_04', 'q_05', 'q_06', 'q_10', 'q_11', 'q_12', 'q_20', 'q_21', 'q_51'),
	223: ('q_00', 'qr_01', 'qr_02', 'qr_03', 'qr_04', 'qr_05', 'qr_06', 'qr_07', 'qr_08', 'qr_09', 'qr_10', 'qr_11', 'qr_12', 'qr_13', 'qr_14', 'qr_15', 'qr_16', 'qr_17', 'qr_18'),
}

survey_bonus_questions = [
	'qr_01', 'qr_02', 'qr_03', 'qr_04', 'qr_05', 'qr_06', 'qr_07', 'qr_08',
	'qr_09', 'qr_10', 'qr_11', 'qr_12', 'qr_13', 'qr_14', 'qr_15', 'qr_16', 'qr_17', 'qr_18',
]

survey_labels = {
	1: 'Time Preference',
	2: 'Risk Preference',
	4: 'Week 4',
	14: 'Week 14',
	123: 'Demo Survey (Risk + Time)',
	223: 'All Bonus Questions (combined)',
}

# Expiration time for untimed surveys
untimed_expiration_days = 7

sms_messages = {
	# English Invites
	'EN_survey_1': [
		"Good morning, _TO_FNAME_! This is _FROM_FNAME_ from USC. Your survey is ready and you have until _EXPIRES_AT_ to complete it. Earn up to $25 today for completing all surveys.",
		"Hi _TO_FNAME_. Your survey is ready. You have until _EXPIRES_AT_ to complete it. Get up to $25 today for completing all surveys.",
		"Good morning, _TO_FNAME_, this is _FROM_FNAME_ from USC. Please complete your survey by _EXPIRES_AT_. Thank you - your participation really helps us and earns you up to $25 each day!",
		"Good morning, _TO_FNAME_. Your survey is ready and you have until _EXPIRES_AT_ to complete it. Earn up to $25 today for completing all surveys.",
		"Hi _TO_FNAME_. This is _FROM_FNAME_. Your first USC survey is ready and you have until _EXPIRES_AT_ to complete it. Your participation helps us a lot and earns you up to $25/day. Thank you!",
		"Good morning _TO_FNAME_. Your first survey is ready now and you have until _EXPIRES_AT_ to complete it. Remember, you get up to $25/day if you complete all surveys!",
	],
	'EN_survey_2': [
		"Hi! Your survey is ready and you have until _EXPIRES_AT_ to complete it.",
		"Hi _TO_FNAME_, Please complete your next survey - you have until _EXPIRES_AT_. You got this!",
		"Your second survey of the day is ready and you have until _EXPIRES_AT_. Thank you!",
		"Hello, here is your next survey. Please complete it by _EXPIRES_AT_. Thanks :)",
		"Here is your next survey and you have until _EXPIRES_AT_. You're getting $2.50 per survey plus additional money!",
		"Hi _TO_FNAME_, your survey is ready. Please complete it by _EXPIRES_AT_ to earn $2.50 and more.",
	],
	'EN_survey_3': [
		"Your afternoon survey is up now. You have until _EXPIRES_AT_ to complete it.",
		"Hope you are having a good afternoon! Please complete our next survey by _EXPIRES_AT_.",
		"Good afternoon, _TO_FNAME_. Your survey is up and you have until _EXPIRES_AT_ to complete it. Thank you!",
		"Hello, here is your third survey today. Please finish it by _EXPIRES_AT_. Thanks for helping!",
		"Hi _TO_FNAME_. Your next survey is ready. Please complete it by _EXPIRES_AT_.",
		"Hello! Your next survey is ready. Please finish it by _EXPIRES_AT_. Thanks for your help.",
	],
	'EN_survey_4': [
		"Hi _TO_FNAME_, here’s today's last survey. You have until _EXPIRES_AT_ to complete it. Thanks and good night.",
		"Hi _TO_FNAME_ - please complete your survey by _EXPIRES_AT_. Have a good evening!",
		"Hi _TO_FNAME_, hope you had a great day. Please help by completing your survey by _EXPIRES_AT_. Good night!",
		"Good evening! Please complete your last survey of today by _EXPIRES_AT_. Thank you.",
		"Good evening _TO_FNAME_. Thanks for your help. Your last survey of today is ready. Please finish by _EXPIRES_AT_.",
		"Hello - your last survey of the day is ready. Please complete it by _EXPIRES_AT_. Thanks and good night.",
	],
	# Spanish invites
	'ES_survey_1': [
		"¡Buenos dias, _TO_FNAME_! Soy _FROM_FNAME_ de USC. Su encuesta esta lista y tiene hasta las _EXPIRES_AT_ para completerla. Gana hasta $25 hoy por completar toda las encuestas.",
		"Hola _TO_FNAME_. Su encuesta esta lista. Tiene hasta las _EXPIRES_AT_ para completarla. Gana hasta $25 hoy por completar toda las encuestas.",
		"Buenos dias, _TO_FNAME_, soy _FROM_FNAME_ de USC. Por favor completa su encuesta antes de las _EXPIRES_AT_. ¡Gracias - su participacion nos ayuda mucho y le gana hasta $25 cada dia!",
		"Buenos dias, _TO_FNAME_. Su encuesta esta lista y tiene hasta las _EXPIRES_AT_ para completarla. Gana hasta $25 hoy por completar todas las encuestas.",
		"Hola _TO_FNAME_. Soy _FROM_FNAME_. Su primera encuesta de USC esta lista y tiene hasta las _EXPIRES_AT_ para completarla. Su participación nos ayuda mucho y le gana hasta $25/dia. ¡Gracias!",
		"Buenos dias _TO_FNAME_. Su primer encuesta esta lista ya y tiene hasta las _EXPIRES_AT_ para completarla. ¡Recuerda, puede ganar hasta $25/dia si completa todas las encuestas!",
	],
	'ES_survey_2': [
		"¡Hola! Su encuesta esta lista y tiene hasta _EXPIRES_AT_ para completarla.",
		"Hola _TO_FNAME_, Por favor completa su proxima encuesta - tiene hasta _EXPIRES_AT_. ¡Si se puede!",
		"Su segunda encuesta del dia esta lista y tiene hasta _EXPIRES_AT_. ¡Gracias!",
		"Hola, aquí esta su proxima encuesta. Por favor completa la antes de _EXPIRES_AT_. Gracias :)",
		"Aquí esta su proxima encuesta y tiene hasta _EXPIRES_AT_. ¡Estás recibiendo $2.50 por encuesta más dinero adicional!",
		"Hola _TO_FNAME_, su encuesta esta lista. Por favor completa la antes de _EXPIRES_AT_ para ganar $2.50 y más.",
	],
	'ES_survey_3': [
		"Hola _TO_FNAME_, su próxima encuesta ya está lista. Tiene hasta las _EXPIRES_AT_ para completarla.",
		"¡Espero que estes teniendo un buen dia! Por favor completa nuestra próxima encuesta antes de _EXPIRES_AT_.",
		"Buenas tardes, _TO_FNAME_. Su encuesta esta lista y tiene hasta _EXPIRES_AT_ para completarla. ¡Gracias!",
		"Hola, aquí esta su tercera encuesta de hoy. Por favor completa la antes de _EXPIRES_AT_. ¡Gracias por ayudar!",
		"Hola _TO_FNAME_. Su proxima encuesta esta lista. Por favor completa la antes de _EXPIRES_AT_.",
		"¡Hola! Su proxima encuesta esta lista. Por favor terminala antes de _EXPIRES_AT_. Gracias por su ayda.",
	],
	'ES_survey_4': [
		"Hola _TO_FNAME_, aquí esta la ultima encuesta de hoy. Tiene hasta _EXPIRES_AT_ para completarla. Gracias y buenas noches.",
		"Hola _TO_FNAME_ - por favor completa su encuesta antes de las _EXPIRES_AT_. ¡Que tenga una buena noche!",
		"Hola _TO_FNAME_, espero que tuviste un buen dia. Por favor ayuda y termine su encuesta antes de _EXPIRES_AT_. ¡Buenas noches!",
		"¡Buenas tardes! Por favor completa su ultima encuesta de hoy antes de _EXPIRES_AT_. Gracias.",
		"Buenas tardes _TO_FNAME_. Gracias por su ayuda. Su ultima encuesta esta lista. Por favor terminala antes de _EXPIRES_AT_.",
		"Hola - su ultima encuesta de el dia esta lista. Por favor terminala antes de _EXPIRES_AT_. Gracias y buenas noches",
	],
}

sms_messages_week_4_14 = {
	'EN_wk4_d1_survey': "Hello _TO_FNAME_, _WK4_D1_SURVEY_TEXT_",
	'EN_wk4_d2_survey': "Hello _TO_FNAME_, _WK4_D2_SURVEY_TEXT_",
	'EN_wk4_d3_survey': "Hello _TO_FNAME_, _WK4_D3_SURVEY_TEXT_",
	'EN_wk14_d1_survey': "Hello _TO_FNAME_, _WK14_D1_SURVEY_TEXT_",
	'EN_wk14_d2_survey': "Hello _TO_FNAME_, _WK14_D2_SURVEY_TEXT_",
	'EN_wk14_d3_survey': "Hello _TO_FNAME_, _WK14_D3_SURVEY_TEXT_",

	'ES_wk4_d1_survey': "Hola _TO_FNAME_, _WK4_D1_SURVEY_TEXT_",
	'ES_wk4_d2_survey': "Hola _TO_FNAME_, _WK4_D2_SURVEY_TEXT_",
	'ES_wk4_d3_survey': "Hola _TO_FNAME_, _WK4_D3_SURVEY_TEXT_",
	'ES_wk14_d1_survey': "Hola _TO_FNAME_, _WK14_D1_SURVEY_TEXT_",
	'ES_wk14_d2_survey': "Hola _TO_FNAME_, _WK14_D2_SURVEY_TEXT_",
	'ES_wk14_d3_survey': "Hola _TO_FNAME_, _WK14_D3_SURVEY_TEXT_",
}
