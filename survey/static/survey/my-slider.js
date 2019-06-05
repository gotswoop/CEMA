$( document ).ready(function() {
	// console.log(document.getElementById("white_castle").value)
		$('#white_castle').slider({ 
			formater: function(value) {
				return this.calculateValue();
			} 
		});
		$('#white_castle').slider().on('slideStart', function(ev){
			originalVal = $('#white_castle').data('slider').getValue();
		});
		$('#white_castle').slider().on('slideStop', function(ev){
			var newVal = $('#white_castle').data('slider').getValue();
			if(originalVal != newVal) {
				// console.log(newVal);
				document.getElementById("question_response").value = newVal;
			}
		});

		$(".slider-horizontal").css("width", $("#legend_table").width());  
		
		$('#white_castle').val(''); 
		document.getElementById('white_castle').value='';
	});

	$( window ).resize(function() {
		$(".slider-horizontal").css("width", $("#legend_table").width());
});
