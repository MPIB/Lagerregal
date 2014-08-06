casper.test.comment('Casper+Django integration example');
var helper = require('./djangocasper.js');
helper.scenario('/devices/',
	function() {
		this.test.assertExists('table');
		this.test.assertElementCount("table tr", 31);
		this.test.assertExists('.pager');
		this.evaluate(function() {
        	$('.pageselect').val(2).change()
        	return true;
    	});
	},
	function() {
		helper.assertAbsUrl('/devices/page/2/department/all/sorting/name/filter/active');
		this.test.assertElementCount("table tr", 11);
		this.evaluate(function() {
        	$('#id_viewfilter').val("all").change()
        	return true;
    	});
	},
	function() {
		helper.assertAbsUrl('/devices/department/all/sorting/name/filter/all');
		this.evaluate(function() {
        	$('#id_viewsorting').val("created_at").change()
        	return true;
    	});
	},
	function() {
		helper.assertAbsUrl('/devices/department/all/sorting/created_at/filter/all');
	}
);
casper.on("page.error", function(msg, trace) {
    this.echo("Error: " + msg, "ERROR");
});
helper.run();