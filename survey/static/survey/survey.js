// Used for questions 30
function clickColA(x,y){
	
	var choice_left = x;
	document.getElementsByName("question_response")[0].value = choice_left;
	console.log(choice_left);

	for (var i = 1; i <= y; i++) {

		if (i <= x) {
			document.getElementById('div' + i + 'a').style.backgroundColor = '#FFFF00';
	  		document.getElementById('div' + i + 'b').style.backgroundColor = '#FFFFFF';
	  	} else {
	  		document.getElementById('div' + i + 'a').style.backgroundColor = '#FFFFFF';
	  		document.getElementById('div' + i + 'b').style.backgroundColor = '#FFFF00';
	  	}
	}
}
function clickColB(x,y){
	
	var choice_right = x - 1;
	document.getElementsByName("question_response")[0].value = choice_right;
	console.log(choice_right);

	for (var i = 1; i <= y; i++) {

		if (i < x) {
			document.getElementById('div' + i + 'a').style.backgroundColor = '#FFFF00';
	  		document.getElementById('div' + i + 'b').style.backgroundColor = '#FFFFFF';
	  	} else {
	  		document.getElementById('div' + i + 'a').style.backgroundColor = '#FFFFFF';
	  		document.getElementById('div' + i + 'b').style.backgroundColor = '#FFFF00';
	  	}
	}
}

// For checkboxes
function clickCheckBox(){
	
	var chk_box_response = '';
	var len = document.getElementsByName("chk_box").length;
	var question_response = document.getElementsByName("chk_box");
	for(var x=0; x < len; x++)
	{
		if (question_response[x].checked == true) {
			chk_box_response += question_response[x].value + ',';
		}
	}
	if (chk_box_response == "") {
		chk_box_response = "-1";	
	}
	console.log(chk_box_response);
	document.getElementById("question_response").value = chk_box_response;
}

// For checkbox groups
function clickCheckBoxSpecial(x){
	
	var chk_box_response = '';
	var len = document.getElementsByName("chk_box").length;
	var question_response = document.getElementsByName("chk_box");
	// Dynamically setting checked vs unchecked for groups
	if (x == 1) {
		for(var x=1; x < len; x++)
		{
			question_response[x].checked = false;
		}
	} else {
		question_response[0].checked = false;
	}

	// Once everything is changed above, getting the latest checkboxes
	question_response = document.getElementsByName("chk_box");
	for(var x=0; x < len; x++)
	{
		if (question_response[x].checked == true) {
			chk_box_response += question_response[x].value + ',';
		}
	}
	if (chk_box_response == "") {
		chk_box_response = "-1";	
	}
	console.log(chk_box_response);
	document.getElementById("question_response").value = chk_box_response;

}

// For radios
function clickRadio(){
	// TODO: Do you trust this?
	var radio_response = document.querySelector('input[name=radio_btn]:checked').value;
	console.log(radio_response);
	document.getElementById("question_response").value = radio_response;

}

function updateSlider(sliderValue) {
	console.log(sliderValue);
	document.getElementById("question_response").value = sliderValue;
}
