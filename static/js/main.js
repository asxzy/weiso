function setCurrentNav(index){
	$('.navbar .nav li').each(function(i){
		if(i === index){
			$(this).addClass('active');
		}
	});
}