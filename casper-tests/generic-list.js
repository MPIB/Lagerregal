casper.test.comment('Casper+Django integration example');
var helper = require('./djangocasper.js');
helper.scenario('/' + casper.cli.options['basename'] + '/',
	function() {
		this.test.assertExists('.list-group');
		this.test.assertElementCount(".list-group-item", 30);
		this.test.assertExists('.pager');
		this.evaluate(function() {
        	$('.pageselect').val(2).change()
        	return true;
    	});
	},
	function() {
		helper.assertAbsUrl('/' + casper.cli.options['basename'] + '/page/2/sorting/name/filter/');
		this.test.assertElementCount(".list-group-item", 10);
		this.evaluate(function() {
        	$('#id_filterstring').val("abc").change()
        	return true;
    	});
	},
	function() {
		helper.assertAbsUrl('/' + casper.cli.options['basename'] + '/sorting/name/filter/abc');
		this.evaluate(function() {
        	$('#id_viewsorting').val("id").change()
        	return true;
    	});
	},
	function() {
		helper.assertAbsUrl('/' + casper.cli.options['basename'] + '/sorting/id/filter/abc');
	}
);
casper.on("page.error", function(msg, trace) {
    this.echo("Error: " + msg, "ERROR");
});
helper.run();